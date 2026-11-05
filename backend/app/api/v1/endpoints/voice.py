"""Voice synthesis API routes."""
from fastapi import APIRouter, HTTPException, Response, status
from pydantic import BaseModel, Field
from backend.app.services.voice_service import synthesize_speech, VoiceSynthesisError

router = APIRouter(prefix="/voice", tags=["Voice"])


class VoiceSynthesisRequest(BaseModel):
    """Payload to synthesize speech from text."""
    text: str = Field(..., min_length=1, max_length=1000, description="Text to convert to speech")


@router.post(
    "/synthesize",
    summary="Synthesize Text to Speech Audio",
    description="Converts question text into spoken audio stream.",
    responses={
        200: {
            "content": {"audio/mpeg": {}},
            "description": "Binary audio stream of synthesized speech",
        }
    },
)
async def synthesize_voice_endpoint(request: VoiceSynthesisRequest):
    """Generate audio stream for interviewer question."""
    try:
        audio_bytes = synthesize_speech(request.text)
        return Response(content=audio_bytes, media_type="audio/mpeg")
    except VoiceSynthesisError as err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(err),
        ) from err
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Speech synthesis failed: {str(exc)}",
        ) from exc

