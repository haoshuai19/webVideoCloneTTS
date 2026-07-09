import os
from pathlib import Path

from pydub import AudioSegment


def convert_format(input_path: str, output_path: str, fmt: str, sample_rate: int) -> str:
    """Convert audio file to target format and sample rate.

    Args:
        input_path: Source audio file path.
        output_path: Destination file path.
        fmt: Target format — 'mp3', 'wav', or 'pcm'.
        sample_rate: Target sample rate — 8000 or 16000.

    Returns:
        The output_path.
    """
    import logging
    logger = logging.getLogger(__name__)

    audio = AudioSegment.from_file(input_path)
    logger.info(f"[DEBUG] convert_format: input={input_path}, input_sample_rate={audio.frame_rate}, target_sample_rate={sample_rate}")

    audio = audio.set_frame_rate(sample_rate).set_channels(1)
    logger.info(f"[DEBUG] convert_format: output={output_path}, output_sample_rate={audio.frame_rate}, format={fmt}")

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    if fmt == "mp3":
        audio.export(output_path, format="mp3")
    elif fmt == "wav":
        audio.export(output_path, format="wav")
    elif fmt == "pcm":
        raw = audio.set_sample_width(2).raw_data
        with open(output_path, "wb") as f:
            f.write(raw)
    else:
        raise ValueError(f"Unsupported format: {fmt}")

    return output_path


def generate_silent_wav(output_path: str, sample_rate: int = 16000, duration: float = 1.0) -> str:
    """Generate a silent WAV file for testing."""
    import struct
    import wave

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    num_samples = int(sample_rate * duration)

    with wave.open(output_path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        frames = struct.pack(f"<{num_samples}h", *[0] * num_samples)
        wf.writeframes(frames)

    return output_path
