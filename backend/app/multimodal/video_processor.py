"""
Video Processor — frame extraction and audio transcription from video
"""
import os
import base64
from typing import Dict, Any, List
from app.utils.logger import logger


class VideoProcessor:
    FRAME_INTERVAL_SEC = 30  # extract one frame every 30s

    async def process(self, file_path: str) -> Dict[str, Any]:
        result = {"frames": [], "transcript": "", "metadata": {}, "modality": "video"}

        try:
            import cv2

            cap = cv2.VideoCapture(file_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps if fps > 0 else 0

            result["metadata"] = {
                "fps": fps,
                "total_frames": total_frames,
                "duration_seconds": duration,
            }

            frame_step = int(fps * self.FRAME_INTERVAL_SEC)
            frame_num = 0
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                if frame_num % frame_step == 0:
                    # Encode frame as JPEG base64
                    _, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
                    b64 = base64.b64encode(buffer).decode()
                    result["frames"].append({
                        "frame_number": frame_num,
                        "timestamp_seconds": frame_num / fps if fps > 0 else 0,
                        "image_base64": b64,
                        "mime_type": "image/jpeg",
                        "modality": "image",
                    })
                frame_num += 1
            cap.release()
        except Exception as e:
            logger.error(f"[VideoProcessor] Frame extraction failed: {e}")

        # Extract audio and transcribe
        try:
            audio_path = file_path.rsplit(".", 1)[0] + "_audio.wav"
            os.system(f"ffmpeg -i {file_path} -ac 1 -ar 16000 {audio_path} -y -loglevel quiet")

            if os.path.exists(audio_path):
                from app.multimodal.audio_processor import AudioProcessor
                audio_result = await AudioProcessor().transcribe(audio_path)
                result["transcript"] = audio_result.get("text", "")
                os.remove(audio_path)
        except Exception as e:
            logger.warning(f"[VideoProcessor] Audio extraction failed: {e}")

        return result
