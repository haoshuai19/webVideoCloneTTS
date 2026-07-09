"""Audio codec encoder using MOSS Audio Tokenizer ONNX model."""
import os
from pathlib import Path
from typing import Any

import numpy as np
from pydub import AudioSegment


class AudioCodecEncoder:
    """Encodes reference audio into discrete token codes using ONNX."""

    TARGET_SAMPLE_RATE = 48000

    def __init__(self, codec_dir: str | None = None) -> None:
        if codec_dir:
            self.codec_dir = Path(codec_dir)
        else:
            # Search for the codec directory in multiple locations
            project_root = Path(__file__).parent.parent.parent.parent
            candidates = [
                project_root / "models" / "moss-audio-tokenizer",
                project_root / "backend" / "models" / "moss-audio-tokenizer",
            ]
            for candidate in candidates:
                if candidate.exists():
                    self.codec_dir = candidate
                    break
            else:
                # Fallback to default
                self.codec_dir = Path(__file__).parent.parent.parent.parent / "models" / "moss-audio-tokenizer"
        self._session: Any = None
        self._codec_meta: dict[str, Any] = {}
        self._loaded = False

    def _load(self) -> None:
        if self._loaded:
            return

        encode_path = self.codec_dir / "moss_audio_tokenizer_encode.onnx"
        meta_path = self.codec_dir / "codec_browser_onnx_meta.json"

        if not encode_path.exists() or not meta_path.exists():
            self._loaded = False
            return

        import json
        import onnxruntime as ort

        with open(meta_path, encoding="utf-8") as f:
            self._codec_meta = json.load(f)

        opts = ort.SessionOptions()
        opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        self._session = ort.InferenceSession(str(encode_path), sess_options=opts)
        self._loaded = True

    @property
    def is_available(self) -> bool:
        self._load()
        return self._loaded

    @property
    def num_quantizers(self) -> int:
        """Number of quantizers (codebook layers)."""
        return int(self._codec_meta.get("codec_config", {}).get("num_quantizers", 4))

    @property
    def target_channels(self) -> int:
        """Target number of channels from codec config."""
        return int(self._codec_meta.get("codec_config", {}).get("channels", 2))

    def encode(self, audio_path: str | Path) -> list[list[int]]:
        """Encode audio file to discrete token codes.

        Args:
            audio_path: Path to audio file (WAV, MP3, M4A, etc.)

        Returns:
            List of [quantizer_0_code, quantizer_1_code, ...] for each frame
        """
        self._load()
        if not self._loaded or not self._session:
            raise RuntimeError("Audio codec encoder not available")

        # Load and preprocess audio
        waveform = self._prepare_audio(audio_path)

        # Run encoder
        waveform_length = int(waveform.shape[-1])
        outputs = self._session.run(
            None,
            {
                "waveform": waveform,
                "input_lengths": np.asarray([waveform_length], dtype=np.int32),
            },
        )

        output_names = [out.name for out in self._session.get_outputs()]
        named_outputs = dict(zip(output_names, outputs, strict=True))

        audio_codes = np.asarray(named_outputs["audio_codes"], dtype=np.int32)
        audio_code_lengths = np.asarray(named_outputs["audio_code_lengths"], dtype=np.int32)
        code_length = int(audio_code_lengths.reshape(-1)[0])
        num_quantizers = self.num_quantizers

        # Convert to list of [q0, q1, q2, q3] for each frame
        prompt_audio_codes: list[list[int]] = []
        for frame_index in range(code_length):
            prompt_audio_codes.append(
                [int(audio_codes[0, frame_index, q]) for q in range(num_quantizers)]
            )

        return prompt_audio_codes

    def _prepare_audio(self, audio_path: str | Path) -> np.ndarray:
        """Load audio file and convert to target format.

        Returns:
            numpy array of shape (batch, channels, samples) with float32 values
        """
        path = Path(audio_path)
        if not path.exists():
            raise FileNotFoundError(f"Audio file not found: {path}")

        # Use pydub to load and convert audio
        audio = AudioSegment.from_file(str(path))

        # Truncate to max 8 seconds to prevent OOM during encoding and synthesis
        # 8 seconds ≈ 320 frames, which keeps prefill memory under 2GB
        MAX_DURATION_MS = 8000
        if len(audio) > MAX_DURATION_MS:
            print(f"  [MEM] Truncating audio from {len(audio)/1000:.1f}s to {MAX_DURATION_MS/1000:.1f}s")
            audio = audio[:MAX_DURATION_MS]

        # Convert to target channels
        target_channels = self.target_channels
        if audio.channels != target_channels:
            if target_channels == 2 and audio.channels == 1:
                # Convert mono to stereo by duplicating
                audio = audio.set_channels(2)
            elif target_channels == 1 and audio.channels > 1:
                # Convert to mono
                audio = audio.set_channels(1)
            else:
                # Try to convert anyway
                audio = audio.set_channels(target_channels)

        # Convert to 48kHz
        if audio.frame_rate != self.TARGET_SAMPLE_RATE:
            audio = audio.set_frame_rate(self.TARGET_SAMPLE_RATE)

        # Convert to float32 normalized [-1, 1]
        samples = np.array(audio.get_array_of_samples(), dtype=np.float32)
        
        # Normalize based on original bit depth
        if audio.sample_width == 2:  # 16-bit
            samples = samples / 32768.0
        elif audio.sample_width == 4:  # 32-bit
            samples = samples / 2147483648.0
        else:  # 8-bit or other
            max_val = 2 ** (audio.sample_width * 8 - 1)
            samples = samples / float(max_val)

        # Reshape to (batch=1, channels, samples)
        return samples.reshape(1, target_channels, -1)


# Global encoder instance
audio_encoder = AudioCodecEncoder()
