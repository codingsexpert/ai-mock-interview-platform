"""Shadow Evaluator Node: Silently grades candidate answers turn-by-turn."""
import json
import logging
from typing import Dict, Any
from backend.app.core.config import get_settings
from backend.app.graph.state import TurnEvaluation

logger = logging.getLogger(__name__)
settings = get_settings()

EVALUATOR_SYSTEM_PROMPT = """You are a rigorous, silent Executive Interview Evaluator and Bar Raiser.
Your task is to critically analyze the candidate's answer to an interview question.

Criteria:
1. Technical Accuracy (0.0 - 10.0): Did the candidate demonstrate genuine technical mastery and explain mechanics correctly?
2. Communication Clarity (0.0 - 10.0): Was the answer structured, concise, and articulate?
3. Key Strengths: Specific technical points or principles explained well.
4. Critical Deficits: Gaps, vague statements, missing edge cases, or buzzwords without depth.
5. Suggested Ideal Response: How a Staff/Principal level engineer would answer in 2-3 precise sentences.

Strict Rules:
- Return strictly valid JSON matching the schema. No commentary, no emojis.
"""


def _deterministic_evaluation(
    turn_index: int, question: str, candidate_answer: str
) -> TurnEvaluation:
    """Heuristic fallback evaluation when LLM key is absent during tests."""
    word_count = len(candidate_answer.split())

    # Basic heuristic scores based on content depth
    if word_count > 40:
        tech_score = 8.5
        comm_score = 8.0
        strengths = ["Comprehensive response covering architectural scope", "Clear terminology used"]
        deficits = ["Could provide deeper quantitative metrics on production performance"]
    elif word_count > 15:
        tech_score = 7.0
        comm_score = 7.0
        strengths = ["Addressed core premise of the question"]
        deficits = ["Lacks specific implementation details and failure handling"]
    else:
        tech_score = 5.0
        comm_score = 5.0
        strengths = ["Direct answer provided"]
        deficits = ["Response was brief; missed key architectural trade-offs"]

    ideal_response = (
        f"An optimal response would concisely articulate the underlying mechanism, "
        f"state trade-offs made in production, and reference operational monitoring."
    )

    return {
        "turn_index": turn_index,
        "question": question,
        "candidate_answer": candidate_answer,
        "technical_accuracy_score": tech_score,
        "communication_clarity_score": comm_score,
        "key_strengths": strengths,
        "critical_deficits": deficits,
        "suggested_ideal_response": ideal_response,
    }


async def evaluate_turn(
    turn_index: int,
    question: str,
    candidate_answer: str,
    target_role: str = "Software Engineer",
) -> TurnEvaluation:
    """Evaluate candidate answer using Gemini or deterministic fallback."""
    api_key = settings.gemini_api_key

    if not api_key:
        return _deterministic_evaluation(turn_index, question, candidate_answer)

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)

        prompt = f"""Target Role: {target_role}
Question Asked: {question}
Candidate Answer: {candidate_answer}

Return JSON with exact keys:
{{
  "turn_index": {turn_index},
  "question": "{question}",
  "candidate_answer": "{candidate_answer}",
  "technical_accuracy_score": 8.0,
  "communication_clarity_score": 8.5,
  "key_strengths": ["...", "..."],
  "critical_deficits": ["...", "..."],
  "suggested_ideal_response": "..."
}}
"""

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=EVALUATOR_SYSTEM_PROMPT,
                response_mime_type="application/json",
                temperature=0.1,
            ),
        )

        data = json.loads(response.text)
        return data

    except Exception as exc:
        logger.warning("LLM evaluation call failed: %s. Using heuristic evaluation.", exc)
        return _deterministic_evaluation(turn_index, question, candidate_answer)

