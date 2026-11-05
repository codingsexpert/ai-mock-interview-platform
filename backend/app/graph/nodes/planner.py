"""Planner node for LangGraph: Gap analysis and interview syllabus generation."""
import json
import logging
from typing import Dict, Any
from backend.app.core.config import get_settings
from backend.app.schemas.interview import GapAnalysis, InterviewPlanResponse

logger = logging.getLogger(__name__)
settings = get_settings()

PLANNER_SYSTEM_PROMPT = """You are an elite Principal Technical Recruiter and Engineering Lead.
Analyze the candidate's RESUME against the target JOB DESCRIPTION.
Conduct a rigorous gap analysis and design a structured 5-stage technical interview syllabus.

Strict Constraints:
1. Identify true technical matches and specific critical requirements missing or weak in the resume.
2. Formulate 5 progressive stage objectives for the interview:
   Stage 1: Introduction & background calibration
   Stage 2: Deep dive into flagship project architecture & trade-offs
   Stage 3: Core technical competencies & edge-case challenges
   Stage 4: System design / scenario problem solving
   Stage 5: Synthesis and professional closure
3. Output MUST be valid JSON strictly matching the requested schema. No markdown backticks, no emojis, no commentary.
"""


def _generate_deterministic_fallback(resume: str, jd: str, role: str) -> InterviewPlanResponse:
    """Fallback planner when LLM key is absent or unreachable during unit tests."""
    resume_lower = resume.lower()
    jd_lower = jd.lower()

    common_keywords = [
        "python", "fastapi", "django", "postgresql", "sql", "redis",
        "docker", "kubernetes", "aws", "gcp", "react", "next.js", "rest", "graphql"
    ]

    matched = [kw.upper() for kw in common_keywords if kw in resume_lower and kw in jd_lower]
    missing = [kw.upper() for kw in common_keywords if kw in jd_lower and kw not in resume_lower]

    if not matched:
        matched = ["CORE SOFTWARE ENGINEERING", "BACKEND ARCHITECTURE"]
    if not missing:
        missing = ["HIGH SCALE DISTRIBUTED SYSTEMS", "PERFORMANCE OPTIMIZATION"]

    return InterviewPlanResponse(
        target_role=role,
        focus_areas=matched[:4],
        candidate_strengths=[f"Demonstrated practical exposure to {m}" for m in matched[:3]],
        gap_analysis=GapAnalysis(
            matched_skills=matched,
            missing_or_weak_skills=missing,
            primary_risks=[f"Probe technical depth in {m}" for m in missing[:2]],
        ),
        question_syllabus=[
            f"Stage 1: Candidate introduction and technical journey calibration for {role}",
            "Stage 2: Architectural dissection of primary project, technical decisions, and failure modes",
            f"Stage 3: Core technical evaluation focusing on {', '.join(matched[:2])}",
            f"Stage 4: Scenario and resilience challenge addressing {', '.join(missing[:2])}",
            "Stage 5: Final technical synthesis, candidate queries, and interview conclusion",
        ],
    )


async def plan_interview(resume_text: str, job_description: str, target_role: str = "Software Engineer") -> InterviewPlanResponse:
    """
    Generate gap analysis and structured interview plan using Gemini or deterministic fallback.
    """
    api_key = settings.gemini_api_key

    if not api_key:
        logger.info("GEMINI_API_KEY not configured. Using deterministic planning engine.")
        return _generate_deterministic_fallback(resume_text, job_description, target_role)

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)

        prompt = f"""Target Role: {target_role}

JOB DESCRIPTION:
{job_description}

CANDIDATE RESUME:
{resume_text}

Return JSON with exact keys:
{{
  "target_role": "{target_role}",
  "focus_areas": ["area1", "area2"],
  "candidate_strengths": ["strength1", "strength2"],
  "gap_analysis": {{
    "matched_skills": ["skill1"],
    "missing_or_weak_skills": ["skill2"],
    "primary_risks": ["risk1"]
  }},
  "question_syllabus": [
    "Stage 1: ...",
    "Stage 2: ...",
    "Stage 3: ...",
    "Stage 4: ...",
    "Stage 5: ..."
  ]
}}
"""

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=PLANNER_SYSTEM_PROMPT,
                response_mime_type="application/json",
                temperature=0.2,
            ),
        )

        data = json.loads(response.text)
        return InterviewPlanResponse(**data)

    except Exception as exc:
        logger.warning("LLM planning call failed: %s. Falling back to deterministic planner.", exc)
        return _generate_deterministic_fallback(resume_text, job_description, target_role)
