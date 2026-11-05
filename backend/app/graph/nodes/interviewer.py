"""Interviewer Node: Formulates natural, conversational interview questions."""
import logging
from typing import Tuple
from backend.app.core.config import get_settings
from backend.app.graph.state import InterviewState

logger = logging.getLogger(__name__)
settings = get_settings()

INTERVIEWER_SYSTEM_PROMPT = """You are a seasoned Principal Engineer conducting a live technical interview.
You speak like a real human engineering lead on a call: calm, inquisitive, sharp, and natural.

Strict Rules:
1. Speak in MAXIMUM 1 TO 2 SENTENCES. Never recite long paragraphs, lectures, or lists.
2. Acknowledge the candidate's previous response briefly before asking your question (e.g. "Got it.", "That makes sense.", "Understood.").
3. Ask sharp, direct follow-up questions challenging assumptions, edge cases, failure scenarios, or architectural trade-offs.
4. ZERO EMOJIS. Maintain a professional, conversational tone.
"""

PHASE_TRANSITIONS = {
    0: ("introduction", "Welcome to the interview. To get started, briefly walk me through your engineering background and the primary project you have led recently."),
    1: ("project_deepdive", "In that project, what was the most complex technical bottleneck you personally resolved, and why did you choose that specific architecture?"),
    2: ("technical_core", "Understood. When traffic spikes significantly, how does your backend maintain data consistency and prevent database exhaustion?"),
    3: ("situational_architecture", "Let us shift to a practical scenario. If one of your dependent microservices begins returning 504 gateway timeouts under peak load, how would your system gracefully degrade?"),
    4: ("conclusion", "Makes sense. Finally, looking back at the trade-offs in your recent work, what is one major architectural decision you would redesign today and why?"),
    5: ("completed", "Thank you for the detailed discussion today. We have concluded all interview rounds, and your evaluation scorecard is ready."),
}


def _deterministic_interviewer_turn(turn_index: int) -> Tuple[str, str]:
    """Fallback phase and question selector when LLM key is absent."""
    phase, question = PHASE_TRANSITIONS.get(
        turn_index,
        ("completed", "The interview session has concluded. Your comprehensive assessment report is available."),
    )
    return phase, question


async def generate_interviewer_turn(state: InterviewState, user_answer: str) -> Tuple[str, str]:
    """Generate the next question and determine the active interview phase."""
    current_turn = state["current_turn"]
    max_turns = state["max_turns"]

    if current_turn >= max_turns:
        return "completed", "Thank you for your time today. That concludes our technical interview session."

    next_turn_index = current_turn

    api_key = settings.gemini_api_key
    if not api_key:
        return _deterministic_interviewer_turn(next_turn_index)

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)

        phase_names = [
            "introduction",
            "project_deepdive",
            "technical_core",
            "situational_architecture",
            "conclusion",
        ]
        target_phase = phase_names[min(next_turn_index, len(phase_names) - 1)]

        conversation_snippet = ""
        for msg in state["messages"][-4:]:
            conversation_snippet += f"{msg['role'].upper()}: {msg['content']}\n"

        prompt = f"""Target Role: {state['target_role']}
Current Interview Phase: {target_phase}
Turn Number: {next_turn_index + 1} of {max_turns}

Recent Conversation:
{conversation_snippet}
CANDIDATE: {user_answer}

Formulate your next response as the interviewer.
Remember: 1 to 2 sentences maximum. Professional, natural, direct. No emojis.
"""

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=INTERVIEWER_SYSTEM_PROMPT,
                temperature=0.3,
            ),
        )

        question_text = response.text.strip()
        return target_phase, question_text

    except Exception as exc:
        logger.warning("LLM interviewer generation failed: %s. Using deterministic fallback.", exc)
        return _deterministic_interviewer_turn(next_turn_index)

