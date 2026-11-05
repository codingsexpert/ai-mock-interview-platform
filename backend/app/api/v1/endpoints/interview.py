"""API routes for interview planning and session orchestration."""
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status
from backend.app.graph.nodes.evaluator import evaluate_turn
from backend.app.graph.nodes.interviewer import generate_interviewer_turn, PHASE_TRANSITIONS
from backend.app.graph.nodes.planner import plan_interview
from backend.app.schemas.interview import InterviewPlanRequest, InterviewPlanResponse
from backend.app.schemas.session import (
    SessionStartRequest,
    SessionStartResponse,
    TurnRequest,
    TurnResponse,
)
from backend.app.services.session_store import session_store

router = APIRouter(prefix="/interview", tags=["Interview"])


@router.post(
    "/plan",
    response_model=InterviewPlanResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Interview Plan and Gap Analysis",
)
async def create_interview_plan(request: InterviewPlanRequest):
    """Generate gap analysis and structured interview plan."""
    try:
        plan = await plan_interview(
            resume_text=request.resume_text,
            job_description=request.job_description,
            target_role=request.target_role or "Software Engineer",
        )
        return plan
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate interview plan: {str(error)}",
        ) from error


@router.post(
    "/start",
    response_model=SessionStartResponse,
    status_code=status.HTTP_200_OK,
    summary="Start Live Interview Session",
)
async def start_interview_session(request: SessionStartRequest):
    """Initialize stateful interview session and yield first opening question."""
    try:
        initial_phase, first_question = PHASE_TRANSITIONS[0]

        state = session_store.create_session(
            resume_text=request.resume_text,
            job_description=request.job_description,
            target_role=request.target_role or "Software Engineer",
            max_turns=request.max_turns or 5,
        )

        # Log first question in conversation history
        now = datetime.now(timezone.utc).isoformat()
        state["messages"].append({
            "role": "assistant",
            "content": first_question,
            "timestamp": now,
        })
        session_store.update_session(state["session_id"], state)

        return SessionStartResponse(
            session_id=state["session_id"],
            target_role=state["target_role"],
            first_question=first_question,
            current_phase=initial_phase,
            max_turns=state["max_turns"],
        )
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start interview session: {str(error)}",
        ) from error


@router.post(
    "/turn",
    response_model=TurnResponse,
    status_code=status.HTTP_200_OK,
    summary="Process Candidate Answer and Generate Next Turn",
)
async def process_interview_turn(request: TurnRequest):
    """Record candidate answer, perform shadow evaluation, and generate subsequent question."""
    state = session_store.get_session(request.session_id)
    if not state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with ID '{request.session_id}' not found.",
        )

    now = datetime.now(timezone.utc).isoformat()

    # Find the question being answered (last assistant message)
    last_question = ""
    for msg in reversed(state["messages"]):
        if msg["role"] == "assistant":
            last_question = msg["content"]
            break

    # Record user response
    state["messages"].append({
        "role": "user",
        "content": request.user_answer,
        "timestamp": now,
    })

    # Perform silent shadow evaluation
    current_turn_index = state["current_turn"]
    evaluation = await evaluate_turn(
        turn_index=current_turn_index,
        question=last_question,
        candidate_answer=request.user_answer,
        target_role=state["target_role"],
    )
    state["evaluations"].append(evaluation)

    # Advance turn index
    state["current_turn"] += 1
    is_completed = state["current_turn"] >= state["max_turns"]

    # Generate next question / closure
    next_phase, next_question = await generate_interviewer_turn(state, request.user_answer)
    state["current_phase"] = next_phase

    # Record interviewer question
    state["messages"].append({
        "role": "assistant",
        "content": next_question,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

    session_store.update_session(request.session_id, state)

    return TurnResponse(
        session_id=request.session_id,
        turn_index=state["current_turn"],
        current_phase=next_phase,
        interviewer_question=next_question,
        is_completed=is_completed,
    )


@router.get(
    "/session/{session_id}",
    status_code=status.HTTP_200_OK,
    summary="Retrieve Interview Session State",
)
async def get_session_state(session_id: str):
    """Fetch current state and transcript history for an active session."""
    state = session_store.get_session(session_id)
    if not state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with ID '{session_id}' not found.",
        )
    return state
