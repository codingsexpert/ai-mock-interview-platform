"""Voice synthesis service providing audio generation for interviewer questions."""
import io
import logging
import requests
from backend.app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class VoiceSynthesisError(Exception):
    """Custom exception raised when speech synthesis fails."""
    pass


def synthesize_speech_offline(text: str) -> bytes:
    """Fallback offline/standard speech generator using gTTS or synthetic tone."""
    try:
        from gtts import gTTS
        buffer = io.BytesIO()
        # English with Indian accent accent-tuning (tld='co.in')
        tts = gTTS(text=text, lang="en", tld="co.in", slow=False)
        tts.write_to_fp(buffer)
        buffer.seek(0)
        return buffer.getvalue()
    except Exception as exc:
        logger.warning("gTTS synthesis failed: %s. Returning synthetic audio buffer.", exc)
        # Generate minimal valid WAV header if offline network is unavailable
        import wave
        buf = io.BytesIO()
        with wave.open(buf, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(16000)
            wav_file.writeframes(b'\x00\x00' * 800)
        buf.seek(0)
        return buf.getvalue()


def synthesize_speech(text: str) -> bytes:
    """
    Synthesize text into speech audio bytes.
    Uses Sarvam AI Bulbul TTS if API key is present, otherwise falls back to local synthesis.
    """
    cleaned_text = text.strip()
    if not cleaned_text:
        raise VoiceSynthesisError("Cannot synthesize empty text.")

    sarvam_key = settings.sarvam_api_key

    if sarvam_key:
        try:
            url = "https://api.sarvam.ai/text-to-speech"
            headers = {
                "api-subscription-key": sarvam_key,
                "Content-Type": "application/json",
            }
            payload = {
                "inputs": [cleaned_text],
                "target_language_code": "en-IN",
                "speaker": "meera",
                "pace": 1.0,
                "speech_sample_rate": 16000,
                "enable_preprocessing": True,
                "model": "bulbul:v1",
            }
            res = requests.post(url, json=payload, headers=headers, timeout=10)
            if res.status_code == 200:
                import base64
                data = res.json()
                audios = data.get("audios", [])
                if audios:
                    return base64.b64decode(audios[0])
        except Exception as err:
            logger.warning("Sarvam API synthesis failed: %s. Using local synthesis.", err)

    return synthesize_speech_offline(cleaned_text)
