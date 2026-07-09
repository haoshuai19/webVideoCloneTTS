import asyncio
import os
import uuid
import threading
from dataclasses import dataclass, field
from typing import Literal

from app.config import settings
from app.models.moss_tts import tts_model
from app.models.voice import get_voice
from app.services.voice_clone import voice_clone_service
from app.utils.audio import convert_format


TaskStatus = Literal["pending", "processing", "completed", "failed"]


@dataclass
class SynthesisTask:
    task_id: str
    text: str
    voice_id: str
    speed: float
    pitch: float
    volume: float
    fmt: str
    sample_rate: int
    status: TaskStatus = "pending"
    result_url: str | None = None
    error: str | None = None


class TTSService:
    """Manages TTS synthesis tasks."""

    def __init__(self) -> None:
        self._tasks: dict[str, SynthesisTask] = {}
        self._executor = None

    def _get_executor(self):
        if self._executor is None:
            self._executor = __import__("concurrent.futures").futures.ThreadPoolExecutor(max_workers=1)
        return self._executor

    def create_task(
        self,
        text: str,
        voice_id: str,
        speed: float = 1.0,
        pitch: float = 1.0,
        volume: float = 1.0,
        fmt: str = "mp3",
        sample_rate: int = 16000,
    ) -> SynthesisTask:
        task_id = uuid.uuid4().hex[:12]
        task = SynthesisTask(
            task_id=task_id,
            text=text,
            voice_id=voice_id,
            speed=speed,
            pitch=pitch,
            volume=volume,
            fmt=fmt,
            sample_rate=sample_rate,
        )
        self._tasks[task_id] = task

        self._get_executor().submit(self._run_synthesis, task)
        return task

    def get_task(self, task_id: str) -> SynthesisTask | None:
        return self._tasks.get(task_id)

    def _run_synthesis(self, task: SynthesisTask) -> None:
        task.status = "processing"
        try:
            # Pre-flight memory check
            import psutil
            avail_gb = psutil.virtual_memory().available / (1024 ** 3)
            if avail_gb < 2.0:
                raise MemoryError(f"Insufficient memory: only {avail_gb:.1f}GB available (need 2GB+)")

            cloned_voice = voice_clone_service.get_cloned_voice(task.voice_id)

            voice_config = {
                "voice_id": task.voice_id,
                "speed": task.speed,
                "pitch": task.pitch,
                "volume": task.volume,
                "sample_rate": task.sample_rate,
                "format": task.fmt,
            }

            wav_path = os.path.join(settings.output_dir, f"{task.task_id}.wav")

            if cloned_voice:
                tts_model.synthesize_with_codes(
                    text=task.text,
                    prompt_codes=cloned_voice["codes"],
                    voice_config=voice_config,
                    output_path=wav_path,
                    prompt_audio_path=cloned_voice.get("audio_path"),
                )
            else:
                voice = get_voice(task.voice_id)
                if not voice:
                    raise ValueError(f"Unknown voice: {task.voice_id}")

                tts_model.synthesize(task.text, voice_config, wav_path)

            if task.fmt != "wav" or task.sample_rate != 48000:
                final_path = os.path.join(
                    settings.output_dir,
                    f"{task.task_id}.{task.fmt}",
                )
                convert_format(wav_path, final_path, task.fmt, task.sample_rate)
                output_file = final_path
            else:
                output_file = wav_path

            task.result_url = f"/outputs/{os.path.basename(output_file)}"
            task.status = "completed"

        except Exception as e:
            task.status = "failed"
            task.error = str(e)


tts_service = TTSService()
