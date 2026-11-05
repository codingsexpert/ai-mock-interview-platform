"""FastAPI application entrypoint for Mock Interview Platform."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# CORS middleware for Streamlit frontend interaction
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", tags=["System"])
async def health_check():
    """Verify backend service health and runtime environment."""
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "environment": settings.environment,
        "version": "1.0.0",
    }
