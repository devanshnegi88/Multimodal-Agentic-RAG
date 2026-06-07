"""
Audio Processor — transcription and feature extraction
"""
from typing import Dict, Any
from app.utils.logger import logger


class AudioProcessor:
    async def transcribe(self, file_path: str) -> Dict[str, Any]:
        """Transcribe audio using OpenAI Whisper."""
        try:
            from openai import AsyncOpenAI
            from app.config import settings

            client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            with open(file_path, "rb") as audio_file:
                transcript = await client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="verbose_json",
                )
            return {
                "text": transcript.text,
                "language": getattr(transcript, "language", "en"),
                "duration": getattr(transcript, "duration", 0.0),
                "segments": getattr(transcript, "segments", []),
                "modality": "audio",
            }
        except Exception as e:
            logger.error(f"[AudioProcessor] Transcription failed: {e}")
            return {"text": "", "error": str(e), "modality": "audio"}

    async def extract_features(self, file_path: str) -> Dict[str, Any]:
        """Extract audio features using librosa."""
        try:
            import librosa
            import numpy as np

            y, sr = librosa.load(file_path, sr=None, duration=60)
            duration = librosa.get_duration(y=y, sr=sr)
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)

            return {
                "duration_seconds": duration,
                "sample_rate": sr,
                "tempo_bpm": float(tempo),
                "rms_energy": float(np.sqrt(np.mean(y ** 2))),
            }
        except Exception as e:
            logger.warning(f"[AudioProcessor] Feature extraction failed: {e}")
            return {}
