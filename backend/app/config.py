import os
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings

# Get the project root (parent of backend/)
PROJECT_ROOT = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    """Application configuration."""

    model_path: str = str(PROJECT_ROOT / "models" / "moss-tts-nano")
    models_root: str = str(PROJECT_ROOT / "models")
    tokenizer_path: str = str(PROJECT_ROOT / "models" / "moss-audio-tokenizer")
    output_dir: str = str(PROJECT_ROOT / "outputs")
    default_sample_rates: tuple[int, ...] = (8000, 16000)
    supported_formats: tuple[str, ...] = ("mp3", "wav", "pcm")
    host: str = "0.0.0.0"
    port: int = 8000

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()

os.makedirs(settings.output_dir, exist_ok=True)
