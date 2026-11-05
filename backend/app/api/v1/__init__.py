"""Version 1 API router."""
from fastapi import APIRouter
from backend.app.api.v1.endpoints.resume import router as resume_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(resume_router)
