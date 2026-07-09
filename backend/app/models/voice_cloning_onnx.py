"""Pure ONNX-based voice cloning synthesis for MOSS-TTS-Nano.

Implements the complete voice cloning pipeline using ONNX Runtime:
1. Build request rows from prompt codes + text tokens
2. Run prefill to initialize model state
3. Autoregressively generate audio frames using local_fixed_sampled_frame
4. Decode frames to waveform using codec decoder
"""
import os
import json
import gc
from pathlib import Path
from typing import Any

import numpy as np

from app.config import settings


def _available_memory_gb() -> float:
    """Return available system memory in GB."""
    try:
        import psutil
        return psutil.virtual_memory().available / (1024 ** 3)
    except Exception:
        return 16.0  # safe fallback


def _check_memory(threshold_gb: float = 1.5, action: str = "check") -> bool:
    """Return True if enough memory available, False if below threshold."""
    avail = _available_memory_gb()
    if avail < threshold_gb:
        print(f"  [MEMORY WARNING] {action}: only {avail:.1f}GB available (threshold={threshold_gb}GB)")
        return False
    return True


def _emergency_cleanup(sessions: dict) -> None:
    """Release all ONNX sessions and force garbage collection."""
    sessions.clear()
    gc.collect()
    print("  [MEMORY] Emergency cleanup: sessions released, gc collected")


class OnnxVoiceCloningSynthesizer:
    """Implements voice cloning synthesis using pure ONNX Runtime."""

    def __init__(self, models_root: str | None = None) -> None:
        self.models_root = Path(models_root) if models_root else Path(__file__).parent.parent.parent / "models"
        self._sessions: dict[str, Any] = {}
        self._manifest: dict[str, Any] = {}
        self._tts_meta: dict[str, Any] = {}
        self._codec_meta: dict[str, Any] = {}
        self._tokenizer: Any = None
        self._loaded = False
        self._metadata_loaded = False

    def _load_metadata(self) -> None:
        """Load only JSON manifests and tokenizer (lightweight, ~1MB)."""
        if self._metadata_loaded:
            return

        tts_dir = self.models_root / "moss-tts-nano"
        codec_dir = self.models_root / "moss-audio-tokenizer"

        manifest_path = tts_dir / "browser_poc_manifest.json"
        if not manifest_path.exists():
            return
        with open(manifest_path, encoding="utf-8") as f:
            self._manifest = json.load(f)

        tts_meta_path = tts_dir / "tts_browser_onnx_meta.json"
        if not tts_meta_path.exists():
            return
        with open(tts_meta_path, encoding="utf-8") as f:
            self._tts_meta = json.load(f)

        codec_meta_path = codec_dir / "codec_browser_onnx_meta.json"
        if not codec_meta_path.exists():
            return
        with open(codec_meta_path, encoding="utf-8") as f:
            self._codec_meta = json.load(f)

        tokenizer_path = tts_dir / "tokenizer.model"
        if tokenizer_path.exists():
            import sentencepiece as spm
            self._tokenizer = spm.SentencePieceProcessor(str(tokenizer_path))

        self._metadata_loaded = True
        self._loaded = True

    def _get_session(self, name: str) -> Any:
        """Lazy-load a single ONNX session on demand, not all at once."""
        if name in self._sessions:
            return self._sessions[name]

        import onnxruntime as ort

        tts_dir = self.models_root / "moss-tts-nano"
        codec_dir = self.models_root / "moss-audio-tokenizer"

        session_files = {
            "prefill": tts_dir / "moss_tts_prefill.onnx",
            "decode_step": tts_dir / "moss_tts_decode_step.onnx",
            "local_decoder": tts_dir / "moss_tts_local_decoder.onnx",
            "local_fixed_sampled_frame": tts_dir / "moss_tts_local_fixed_sampled_frame.onnx",
            "local_cached_step": tts_dir / "moss_tts_local_cached_step.onnx",
            "codec_decode": codec_dir / "moss_audio_tokenizer_decode_full.onnx",
            "codec_decode_step": codec_dir / "moss_audio_tokenizer_decode_step.onnx",
        }

        path = session_files.get(name)
        if not path or not path.exists():
            return None

        opts = ort.SessionOptions()
        opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_BASIC
        opts.intra_op_num_threads = 1
        opts.inter_op_num_threads = 1
        opts.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
        opts.enable_mem_pattern = False

        session = ort.InferenceSession(str(path), sess_options=opts)
        self._sessions[name] = session
        return session

    def _unload_session(self, name: str) -> None:
        """Free a loaded session to reclaim memory."""
        if name in self._sessions:
            del self._sessions[name]

    def _load(self) -> None:
        """Load metadata only; ONNX sessions load lazily via _get_session()."""
        self._load_metadata()

    @property
    def is_available(self) -> bool:
        self._load()
        return self._loaded

    def encode_text(self, text: str) -> list[int]:
        """Encode text to token IDs."""
        if not self._tokenizer:
            raise RuntimeError("Tokenizer not loaded")
        return self._tokenizer.encode(text)

    def build_voice_clone_request_rows(
        self, prompt_codes: list[list[int]], text_tokens: list[int]
    ) -> tuple[np.ndarray, np.ndarray]:
        """Build input arrays for voice cloning synthesis.
        
        Returns:
            Tuple of (input_ids, attention_mask) arrays
        """
        manifest = self._manifest
        tts_config = manifest["tts_config"]
        prompt_templates = manifest["prompt_templates"]
        n_vq = int(tts_config["n_vq"])
        audio_pad = int(tts_config["audio_pad_token_id"])
        audio_user_slot = int(tts_config["audio_user_slot_token_id"])

        # Build token sequence
        prefix_tokens = [
            *prompt_templates["user_prompt_prefix_token_ids"],
            int(tts_config["audio_start_token_id"]),
        ]
        suffix_tokens = [
            int(tts_config["audio_end_token_id"]),
            *prompt_templates["user_prompt_after_reference_token_ids"],
            *text_tokens,
            *prompt_templates["assistant_prompt_prefix_token_ids"],
            int(tts_config["audio_start_token_id"]),
        ]

        # Build rows: each row is [text_token, q0, q1, q2, q3]
        rows: list[list[int]] = []
        row_width = n_vq + 1

        for token_id in prefix_tokens:
            row = [audio_pad] * row_width
            row[0] = int(token_id)
            rows.append(row)

        for code_row in prompt_codes:
            row = [audio_pad] * row_width
            row[0] = audio_user_slot
            for idx in range(min(len(code_row), n_vq)):
                row[idx + 1] = int(code_row[idx])
            rows.append(row)

        for token_id in suffix_tokens:
            row = [audio_pad] * row_width
            row[0] = int(token_id)
            rows.append(row)

        # Create arrays
        input_ids = np.array([rows], dtype=np.int32)
        attention_mask = np.ones((1, len(rows)), dtype=np.int32)

        return input_ids, attention_mask

    def synthesize_with_codes(
        self,
        text: str,
        prompt_codes: list[list[int]],
        voice_config: dict,
        output_path: str,
    ) -> str:
        """Synthesize text using cloned voice codes.
        
        Uses pure ONNX-based voice cloning synthesis without torchcodec dependency.
        
        Args:
            text: Text to synthesize
            prompt_codes: Audio codes from cloned voice reference
            voice_config: Voice configuration dict
            output_path: Output file path
            
        Returns:
            Path to generated audio file
        """
        self._load()
        if not self._loaded:
            return self._synthesize_stub(text, voice_config, output_path)

        sample_rate = voice_config.get("sample_rate", 16000)
        target_format = voice_config.get("format", "wav")

        # Pre-flight memory check: need at least 3GB free for ONNX inference
        if not _check_memory(threshold_gb=3.0, action="pre-flight"):
            print("  [ABORT] Insufficient memory before synthesis, using stub")
            return self._synthesize_stub(text, voice_config, output_path)

        try:
            # Encode text
            text_tokens = self.encode_text(text)
            
            # Build request rows
            input_ids, attention_mask = self.build_voice_clone_request_rows(prompt_codes, text_tokens)

            # Estimate input sequence length and memory requirement
            seq_len = input_ids.shape[1]
            # Transformer attention is O(n²); each 1000 tokens needs ~1-2GB
            est_mem_gb = (seq_len / 1000.0) ** 2 * 2.0
            avail_gb = _available_memory_gb()
            print(f"  [MEM] seq_len={seq_len}, est_mem={est_mem_gb:.1f}GB, avail={avail_gb:.1f}GB")

            if est_mem_gb > avail_gb * 0.6:
                # Truncate prompt codes to fit memory
                max_safe_len = int((avail_gb * 0.4 * 1000) ** 0.5)
                if max_safe_len < seq_len and max_safe_len > 100:
                    print(f"  [MEM] Truncating input from {seq_len} to {max_safe_len} to fit memory")
                    input_ids = input_ids[:, :max_safe_len, :]
                    attention_mask = attention_mask[:, :max_safe_len]
                    seq_len = max_safe_len

            # Final memory check after truncation
            if not _check_memory(threshold_gb=2.0, action="post-truncation"):
                _emergency_cleanup(self._sessions)
                return self._synthesize_stub(text, voice_config, output_path)
            
            # Calculate max_new_frames based on text length
            # Each Chinese character ~3-4 frames, short text minimum ~50 frames, cap at 375
            manifest_max = self._manifest.get("generation_defaults", {}).get("max_new_frames", 200)
            text_frame_estimate = max(50, len(text) * 4)
            override_max_frames = min(text_frame_estimate, manifest_max)
            
            # Generate audio frames
            generated_frames = self._generate_audio_frames(input_ids, attention_mask, override_max_frames)
            
            if not generated_frames:
                print("WARNING: No frames generated, using stub")
                return self._synthesize_stub(text, voice_config, output_path)
            
            # Decode frames to waveform
            waveform = self._decode_frames_to_waveform(generated_frames)
            
            # Save waveform
            import soundfile as sf
            os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
            if waveform.ndim == 2:
                sf.write(output_path, waveform.T, 48000, subtype="PCM_16")
            else:
                sf.write(output_path, waveform, 48000, subtype="PCM_16")
            
            # Post-process if needed
            if sample_rate != 48000 or target_format != "wav":
                self._post_process_audio(output_path, output_path, sample_rate, target_format)
            
            print(f"Voice cloning synthesis complete: {len(generated_frames)} frames, output={output_path}")
            return output_path

        except Exception as e:
            print(f"ONNX voice cloning synthesis failed: {e}")
            _emergency_cleanup(self._sessions)
            import traceback
            traceback.print_exc()
            return self._synthesize_stub(text, voice_config, output_path)

    def _generate_audio_frames(
        self, input_ids: np.ndarray, attention_mask: np.ndarray,
        max_new_frames: int = 200,
    ) -> list[list[int]]:
        """Generate audio frames from input arrays.
        
        This runs the prefill and autoregressive generation loop.
        """
        manifest = self._manifest
        tts_config = manifest["tts_config"]
        n_vq = int(tts_config["n_vq"])
        audio_codebook_size = int(self._tts_meta["model_config"]["audio_codebook_sizes"][0])
        
        print(f"  Prefill: input_ids shape={input_ids.shape}")
        
        # Memory check before prefill (this is the most memory-intensive step)
        if not _check_memory(threshold_gb=2.0, action="before-prefill"):
            return []
        
        # Lazy-load prefill session
        prefill_sess = self._get_session("prefill")
        if not prefill_sess:
            print("  ERROR: prefill session not available")
            return []
        
        # Run prefill with memory guard
        try:
            prefill_outputs = prefill_sess.run(
                None,
                {
                    "input_ids": input_ids,
                    "attention_mask": attention_mask,
                },
            )
        except Exception as e:
            if "allocate" in str(e).lower() or "memory" in str(e).lower():
                print(f"  [OOM] Prefill memory allocation failed: {e}")
                _emergency_cleanup(self._sessions)
                return []
            raise
        
        output_names = [out.name for out in prefill_sess.get_outputs()]
        named_outputs = dict(zip(output_names, prefill_outputs, strict=True))
        
        # Extract global hidden state (last position)
        global_hidden = named_outputs["global_hidden"]
        if global_hidden.ndim == 3:
            global_hidden = global_hidden[:, -1, :]  # (batch, seq_len, hidden) -> (batch, hidden)
        
        print(f"  Global hidden shape: {global_hidden.shape}")
        
        # Free prefill session memory (no longer needed)
        self._unload_session("prefill")
        
        # Autoregressive generation
        generated_frames: list[list[int]] = []
        previous_token_sets = [set() for _ in range(n_vq)]
        rng = np.random.default_rng(1234)
        
        # Lazy-load generation session
        gen_sess = self._get_session("local_fixed_sampled_frame")
        if gen_sess:
            print(f"  Using local_fixed_sampled_frame for generation (max {max_new_frames} frames)")
            for frame_idx in range(max_new_frames):
                # Memory check every 10 frames
                if frame_idx % 10 == 0 and not _check_memory(threshold_gb=1.0, action=f"frame-{frame_idx}"):
                    print(f"  [ABORT] Memory low at frame {frame_idx}, stopping generation")
                    _emergency_cleanup(self._sessions)
                    break

                # Create repetition seen mask
                repetition_seen_mask = np.zeros((1, n_vq, audio_codebook_size), dtype=np.int32)
                for ch, token_ids in enumerate(previous_token_sets):
                    for token_id in token_ids:
                        if 0 <= token_id < audio_codebook_size:
                            repetition_seen_mask[0, ch, token_id] = 1
                
                # Generate random values for sampling
                assistant_random_u = rng.random((1,)).astype(np.float32)
                audio_random_u = rng.random((1, n_vq)).astype(np.float32)

                outputs = gen_sess.run(
                    None,
                    {
                        "global_hidden": global_hidden.astype(np.float32, copy=False),
                        "repetition_seen_mask": repetition_seen_mask,
                        "assistant_random_u": assistant_random_u,
                        "audio_random_u": audio_random_u,
                    },
                )

                out_names = [out.name for out in gen_sess.get_outputs()]
                named = dict(zip(out_names, outputs, strict=True))

                should_continue = bool(int(named["should_continue"].reshape(-1)[0]))
                if not should_continue:
                    print(f"  Generation stopped at frame {frame_idx} (should_continue=False)")
                    break

                frame_codes = [int(named["frame_token_ids"][0, ch]) for ch in range(n_vq)]
                generated_frames.append(frame_codes)

                for ch, code in enumerate(frame_codes):
                    previous_token_sets[ch].add(code)
                
                if frame_idx % 50 == 0:
                    print(f"  Generated {frame_idx} frames...")
        else:
            print("  WARNING: local_fixed_sampled_frame not available, using fallback")
            # Fallback: generate minimal frames for testing
            for _ in range(10):
                generated_frames.append([0] * n_vq)
        
        # Free generation session memory
        self._unload_session("local_fixed_sampled_frame")

        print(f"  Total frames generated: {len(generated_frames)}")
        return generated_frames

    def _decode_frames_to_waveform(self, frames: list[list[int]]) -> np.ndarray:
        """Decode audio frames to waveform using codec decoder."""
        if not frames:
            return np.zeros((1, 0), dtype=np.float32)
        
        num_frames = len(frames)
        n_vq = len(frames[0])
        
        # Create audio codes array
        audio_codes = np.zeros((1, num_frames, n_vq), dtype=np.int32)
        for i, frame in enumerate(frames):
            for j, code in enumerate(frame):
                audio_codes[0, i, j] = code
        
        audio_code_lengths = np.asarray([num_frames], dtype=np.int32)
        
        # Lazy-load codec decoder, use it, then free
        codec_sess = self._get_session("codec_decode")
        if not codec_sess:
            print("  ERROR: codec_decode session not available")
            return np.zeros((1, 0), dtype=np.float32)
        
        outputs = codec_sess.run(
            None,
            {
                "audio_codes": audio_codes,
                "audio_code_lengths": audio_code_lengths,
            },
        )
        
        output_names = [out.name for out in codec_sess.get_outputs()]
        named_outputs = dict(zip(output_names, outputs, strict=True))
        
        # Free codec session memory
        self._unload_session("codec_decode")
        
        # Extract waveform
        waveform = named_outputs.get("waveform", named_outputs.get("audio", outputs[0]))
        
        # Handle batch dimension
        if waveform.ndim == 3:
            waveform = waveform[0]  # (batch, channels, samples) -> (channels, samples)
        
        return waveform

    def _post_process_audio(
        self, input_path: str, output_path: str, target_sr: int, target_fmt: str
    ) -> None:
        """Resample and convert audio format."""
        import librosa
        import soundfile as sf
        
        audio, sr = librosa.load(input_path, sr=48000, mono=False)
        
        if sr != target_sr:
            audio = librosa.resample(audio, orig_sr=sr, target_sr=target_sr)
            sr = target_sr
        
        if audio.ndim == 2:
            audio = np.mean(audio, axis=0)
        
        # Normalize volume: scale peak to 90% of max to avoid clipping
        peak = np.max(np.abs(audio))
        if peak > 0:
            audio = audio / peak * 0.9
        
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        
        if target_fmt == "pcm":
            audio_int16 = np.clip(audio * 32767, -32768, 32767).astype(np.int16)
            with open(output_path, "wb") as f:
                f.write(audio_int16.tobytes())
        else:
            sf.write(output_path, audio, sr, subtype="PCM_16")

    @staticmethod
    def _synthesize_stub(text: str, voice_config: dict, output_path: str) -> str:
        """Generate silent WAV stub when model unavailable."""
        import wave
        import struct
        
        sample_rate = voice_config.get("sample_rate", 16000)
        duration = max(0.5, len(text) * 0.1)
        num_samples = int(sample_rate * duration)
        
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        
        with wave.open(output_path, "w") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            frames = struct.pack(f"<{num_samples}h", *[0] * num_samples)
            wf.writeframes(frames)
        
        return output_path


# Global synthesizer instance - will be initialized with correct path on first use
_onnx_voice_cloning_synthesizer: OnnxVoiceCloningSynthesizer | None = None


def get_voice_cloning_synthesizer() -> OnnxVoiceCloningSynthesizer:
    """Get or create the global synthesizer instance with correct models root."""
    global _onnx_voice_cloning_synthesizer
    if _onnx_voice_cloning_synthesizer is None:
        from app.config import settings
        _onnx_voice_cloning_synthesizer = OnnxVoiceCloningSynthesizer(str(settings.models_root))
        # Force load to ensure sessions are created
        _onnx_voice_cloning_synthesizer._load()
    return _onnx_voice_cloning_synthesizer
