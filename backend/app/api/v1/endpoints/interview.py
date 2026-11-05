"""API routes for interview planning and session orchestration."""
from fastapi import APIRouter, HTTPException, status
from backend.app.graph.nodes.planner import plan_interview
from backend.app.schemas.interview import InterviewPlanRequest, InterviewPlanResponse

router = APIRouter(prefix="/interview", tags=["Interview"])


@router.post(
    "/plan",
    response_model=InterviewPlanResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Interview Plan and Gap Analysis",
    description="Compares candidate resume against job description to generate tailored focus areas, gap analysis, and 5-stage syllabus.",
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

