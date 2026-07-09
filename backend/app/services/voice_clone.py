"""Voice cloning service using MOSS-TTS-Nano audio codec."""
import os
import uuid
from pathlib import Path
from typing import Any

from app.services.audio_codec import audio_encoder
from app.config import settings


class VoiceCloneService:
    """Manages voice cloning tasks and stores cloned voice data."""

    def __init__(self) -> None:
        # Store cloned voices: {voice_id: {"name": str, "codes": list[list[int]], "reference_text": str}}
        self._cloned_voices: dict[str, dict[str, Any]] = {}
        # Store active tasks: {task_id: {"status": str, "voice_id": str | None, "error": str | None}}
        self._tasks: dict[str, dict[str, Any]] = {}

    def create_clone_task(
        self,
        audio_file_path: str,
        voice_name: str,
        reference_text: str = "",
    ) -> str:
        """Create a voice cloning task.

        Args:
            audio_file_path: Path to uploaded audio file
            voice_name: Display name for the cloned voice
            reference_text: Optional text spoken in the reference audio

        Returns:
            Task ID for polling status
        """
        task_id = uuid.uuid4().hex[:12]
        self._tasks[task_id] = {
            "status": "processing",
            "voice_id": None,
            "error": None,
        }

        try:
            # Encode audio to codes
            codes = audio_encoder.encode(audio_file_path)

            if not codes:
                raise ValueError("Failed to encode audio: no codes produced")

            # Limit prompt codes to prevent OOM during synthesis
            # Each frame adds ~0.025s; 200 frames ≈ 5s of reference audio
            # Transformer attention is O(n²), so longer prompts cause exponential memory growth
            MAX_PROMPT_FRAMES = 200
            if len(codes) > MAX_PROMPT_FRAMES:
                print(f"  Truncating prompt codes: {len(codes)} -> {MAX_PROMPT_FRAMES} frames")
                codes = codes[:MAX_PROMPT_FRAMES]

            # Generate voice ID
            voice_id = f"cloned_{task_id}"

            # Store cloned voice
            self._cloned_voices[voice_id] = {
                "name": voice_name,
                "codes": codes,
                "reference_text": reference_text,
                "num_frames": len(codes),
                "duration_seconds": len(codes) * 0.025,
                "audio_path": audio_file_path,  # Keep for official inference script
            }

            # Update task status
            self._tasks[task_id] = {
                "status": "completed",
                "voice_id": voice_id,
                "error": None,
            }

            # Note: do NOT delete audio_file_path, needed for synthesis

        except Exception as e:
            self._tasks[task_id] = {
                "status": "failed",
                "voice_id": None,
                "error": str(e),
            }
            # Cleanup on failure too
            if os.path.exists(audio_file_path):
                os.remove(audio_file_path)

        return task_id

    def get_task_status(self, task_id: str) -> dict[str, Any] | None:
        """Get cloning task status."""
        return self._tasks.get(task_id)

    def get_cloned_voice(self, voice_id: str) -> dict[str, Any] | None:
        """Get cloned voice data by ID."""
        return self._cloned_voices.get(voice_id)

    def list_cloned_voices(self) -> list[dict[str, Any]]:
        """List all cloned voices."""
        return [
            {
                "id": vid,
                "name": vdata["name"],
                "num_frames": vdata["num_frames"],
                "duration_seconds": vdata["duration_seconds"],
            }
            for vid, vdata in self._cloned_voices.items()
        ]

    def get_voice_codes(self, voice_id: str) -> list[list[int]] | None:
        """Get audio codes for a cloned voice."""
        voice = self._cloned_voices.get(voice_id)
        if voice:
            return voice["codes"]
        return None


# Global clone service instance
voice_clone_service = VoiceCloneService()
