import os
import wave
import struct
import shutil
from pathlib import Path
from typing import Any

import numpy as np

from app.config import settings


class MossTTSNanoONNX:
    """MOSS-TTS-Nano ONNX runtime via official inference pipeline."""

    def __init__(
        self,
        model_path: str | None = None,
        models_root: str | None = None,
    ) -> None:
        self.model_path = model_path or settings.model_path
        self.models_root = models_root or settings.models_root
        self._manifest: dict[str, Any] = {}
        self._loaded = False

    def _load(self) -> None:
        if self._loaded:
            return

        model_dir = Path(self.model_path)
        manifest_path = model_dir / "browser_poc_manifest.json"
        if not manifest_path.exists():
            self._loaded = False
            return

        import json

        with open(manifest_path, encoding="utf-8") as f:
            self._manifest = json.load(f)

        # Verify ONNX files exist
        required_onnx = [
            "moss_tts_prefill.onnx",
            "moss_tts_decode_step.onnx",
            "moss_tts_local_decoder.onnx",
        ]
        all_exist = all((model_dir / fn).exists() for fn in required_onnx)

        # Verify codec files exist
        codec_dir = Path(self.models_root) / "moss-audio-tokenizer"
        codec_exists = (codec_dir / "moss_audio_tokenizer_decode_full.onnx").exists()

        self._loaded = all_exist and codec_exists

    @property
    def is_available(self) -> bool:
        self._load()
        return self._loaded

    @property
    def builtin_voices(self) -> list[dict[str, str]]:
        """List built-in voices from manifest."""
        self._load()
        voices = self._manifest.get("builtin_voices", [])
        result = []
        for v in voices:
            result.append({
                "id": v.get("voice", ""),
                "name": v.get("display_name", ""),
                "group": v.get("group", ""),
            })
        return result

    def synthesize(
        self,
        text: str,
        voice_config: dict,
        output_path: str,
    ) -> str:
        """Synthesize text using official ONNX pipeline."""
        self._load()
        if self.is_available:
            return self._synthesize_official(text, voice_config, output_path)
        return self._synthesize_stub(text, voice_config, output_path)

    def synthesize_with_codes(
        self,
        text: str,
        prompt_codes: list[list[int]],
        voice_config: dict,
        output_path: str,
        prompt_audio_path: str | None = None,
    ) -> str:
        """Synthesize text using cloned voice.

        Prefers official infer_onnx.py with --prompt-audio-path for best quality
        (includes text chunking, proper codec handling). Falls back to custom
        ONNX pipeline if reference audio file is not available.

        Args:
            text: Text to synthesize
            prompt_codes: Audio codes from cloned voice reference
            voice_config: Voice configuration dict
            output_path: Output file path
            prompt_audio_path: Path to original reference audio file

        Returns:
            Path to generated audio file
        """
        # Use official inference script with reference audio for best quality
        if prompt_audio_path and os.path.exists(prompt_audio_path):
            return self._synthesize_official_clone(text, voice_config, output_path, prompt_audio_path)

        # Fallback to custom ONNX pipeline
        from app.models.voice_cloning_onnx import get_voice_cloning_synthesizer

        synthesizer = get_voice_cloning_synthesizer()

        if synthesizer.is_available:
            return synthesizer.synthesize_with_codes(
                text=text,
                prompt_codes=prompt_codes,
                voice_config=voice_config,
                output_path=output_path,
            )

        return self._synthesize_stub(text, voice_config, output_path)

    def _synthesize_official_clone(
        self, text: str, voice_config: dict, output_path: str, prompt_audio_path: str
    ) -> str:
        """Run official ONNX inference with reference audio for voice cloning."""
        sample_rate = voice_config.get("sample_rate", 16000)
        target_format = voice_config.get("format", "wav")

        # Generate temp WAV at native 48kHz
        temp_path = output_path + ".native48k.wav"

        result = self._run_inference_clone(text, prompt_audio_path, temp_path)
        if not result or not os.path.exists(temp_path):
            raise RuntimeError(
                "Voice clone inference failed to produce output. "
                "The ONNX subprocess may have timed out or crashed. "
                "Check backend logs for details."
            )

        try:
            self._post_process_audio(temp_path, output_path, sample_rate, target_format)
            return output_path
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def _run_inference_clone(
        self, text: str, prompt_audio_path: str, output_path: str
    ) -> dict[str, Any] | None:
        """Run official inference via subprocess for voice cloning."""
        import subprocess
        import sys
        import tempfile

        project_root = Path(__file__).parent.parent.parent.parent
        temp_moss_dir = project_root / "temp_moss_tts"
        infer_script = temp_moss_dir / "infer_onnx.py"

        if not infer_script.exists():
            temp_moss_dir = Path(__file__).parent.parent / "temp_moss_tts"
            infer_script = temp_moss_dir / "infer_onnx.py"

        if not infer_script.exists():
            print(f"ERROR: infer_onnx.py not found at {infer_script}")
            return None

        # Convert reference audio to WAV if not already (torchaudio needs WAV, not MP3)
        ref_path = prompt_audio_path
        temp_wav = None
        if not prompt_audio_path.lower().endswith('.wav'):
            try:
                from pydub import AudioSegment
                audio = AudioSegment.from_file(prompt_audio_path)
                audio = audio.set_channels(2).set_frame_rate(48000)
                temp_wav = output_path + ".ref.wav"
                audio.export(temp_wav, format="wav")
                ref_path = temp_wav
                print(f"  Converted ref audio to WAV: {temp_wav}")
            except Exception as e:
                print(f"  Failed to convert ref audio: {e}")
                return None

        env = os.environ.copy()
        env["HF_ENDPOINT"] = "https://hf-mirror.com"

        cmd = [
            sys.executable,
            str(infer_script),
            "--text", text,
            "--prompt-audio-path", ref_path,
            "--output-audio-path", output_path,
            "--model-dir", str(self.models_root),
            "--cpu-threads", "2",
            "--max-new-frames", "1200",
            "--execution-provider", "cpu",
            "--sample-mode", "fixed",
            "--voice-clone-max-text-tokens", "9999",
            "--disable-wetext-processing",
            "--disable-normalize-tts-text",
        ]

        print(f"  Running official clone inference: {Path(ref_path).name}")
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600,
                env=env,
                cwd=str(temp_moss_dir),
            )
            if temp_wav and os.path.exists(temp_wav):
                os.remove(temp_wav)
            if result.returncode != 0:
                print(f"  inference stderr: {result.stderr[-500:]}")
                return None
            if result.stdout:
                print(f"  inference stdout: {result.stdout[-300:]}")
            return {"success": True}
        except subprocess.TimeoutExpired:
            if temp_wav and os.path.exists(temp_wav):
                os.remove(temp_wav)
            print("  inference timed out")
            return None

    def _synthesize_official(
        self, text: str, voice_config: dict, output_path: str
    ) -> str:
        """Run official ONNX inference and post-process output."""
        voice_id = voice_config.get("voice_id", "Xiaoyu")
        sample_rate = voice_config.get("sample_rate", 16000)
        # Always produce WAV as intermediate format; _run_synthesis in tts_service
        # handles the final format conversion (MP3/PCM) from the WAV file.
        target_format = "wav"

        # Map our voice IDs to manifest voice names
        voice_map = self._get_voice_map()
        manifest_voice = voice_map.get(voice_id, "Xiaoyu")

        # Generate temp WAV at native 48kHz
        temp_path = output_path + ".native48k.wav"

        result = self._run_inference(text, manifest_voice, temp_path)
        if not result or not os.path.exists(temp_path):
            raise RuntimeError(
                "Model inference failed to produce output. "
                "The ONNX subprocess may have timed out or crashed. "
                "Check backend logs for details."
            )

        try:
            self._post_process_audio(temp_path, output_path, sample_rate, target_format)
            return output_path
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def _run_inference(
        self, text: str, voice: str, output_path: str
    ) -> dict[str, Any] | None:
        """Run official inference via subprocess to use their pipeline."""
        import subprocess
        import sys

        # Find temp_moss_tts directory
        project_root = Path(__file__).parent.parent.parent.parent
        temp_moss_dir = project_root / "temp_moss_tts"
        infer_script = temp_moss_dir / "infer_onnx.py"

        if not infer_script.exists():
            # Try alternate path
            temp_moss_dir = Path(__file__).parent.parent / "temp_moss_tts"
            infer_script = temp_moss_dir / "infer_onnx.py"

        if not infer_script.exists():
            print(f"ERROR: infer_onnx.py not found at {infer_script}")
            return None

        # Set environment for HF mirror
        env = os.environ.copy()
        env["HF_ENDPOINT"] = "https://hf-mirror.com"

        cmd = [
            sys.executable,
            str(infer_script),
            "--text", text,
            "--voice", voice,
            "--output-audio-path", output_path,
            "--model-dir", str(self.models_root),
            "--cpu-threads", "2",
            "--max-new-frames", "900",
            "--execution-provider", "cpu",
            "--sample-mode", "fixed",
            "--voice-clone-max-text-tokens", "40",
            "--disable-wetext-processing",
            "--disable-normalize-tts-text",
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env=env,
                cwd=str(temp_moss_dir),
                timeout=600,
            )

            if result.returncode == 0 and os.path.exists(output_path):
                # Validate that audio is not silent
                try:
                    import wave
                    import struct
                    
                    with wave.open(output_path, 'rb') as wf:
                        n_frames = wf.getnframes()
                        if n_frames == 0:
                            print(f"WARNING: Generated audio has 0 frames, using stub fallback")
                            return None
                        
                        # Read ALL frames for accurate RMS calculation
                        # (first frames might be silence, so we need to check the whole file)
                        sample_width = wf.getsampwidth()
                        n_channels = wf.getnchannels()
                        raw_frames = wf.readframes(n_frames)
                        
                        # Convert to samples
                        if sample_width == 2:
                            fmt = f'<{len(raw_frames) // 2}h'
                            samples = struct.unpack(fmt, raw_frames)
                            samples_float = np.array(samples, dtype=np.float32) / 32768.0
                        else:
                            samples_float = np.frombuffer(raw_frames, dtype=np.float32)
                        
                        # For multi-channel audio, convert to mono
                        if n_channels > 1:
                            samples_float = samples_float.reshape(-1, n_channels).mean(axis=1)
                        
                        rms = float(np.sqrt(np.mean(samples_float**2)))
                        if rms < 0.001:
                            print(f"WARNING: Generated audio is silent (RMS={rms:.6f}), using stub fallback")
                            return None
                        else:
                            print(f"Audio validation passed: RMS={rms:.6f}, frames={n_frames}")
                except Exception as e:
                    print(f"WARNING: Could not validate audio: {e}")
                    import traceback
                    traceback.print_exc()
                
                return {"audio_path": output_path}
            else:
                print(f"Subprocess failed: rc={result.returncode}")
                if result.stderr:
                    print(f"Stderr: {result.stderr[-300:]}")
                return None
        except subprocess.TimeoutExpired:
            print("Subprocess timed out after 180s")
            return None

    def _post_process_audio(
        self, input_path: str, output_path: str, target_sr: int, target_fmt: str
    ) -> None:
        """Resample from 48kHz to target rate and convert format."""
        try:
            import librosa
            import soundfile as sf

            # Load 48kHz audio
            audio, sr = librosa.load(input_path, sr=48000, mono=False)

            # Resample if needed
            if sr != target_sr:
                audio = librosa.resample(audio, orig_sr=sr, target_sr=target_sr)
                sr = target_sr

            # Convert to mono if stereo
            # librosa returns (channels, samples) format
            if audio.ndim == 2:
                audio = np.mean(audio, axis=0)

            # Save in target format
            os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

            if target_fmt == "mp3":
                try:
                    from pydub import AudioSegment
                    import tempfile

                    # Save as WAV first, then convert
                    temp_wav = output_path + ".tmp.wav"
                    sf.write(temp_wav, audio, sr, subtype="PCM_16")
                    seg = AudioSegment.from_wav(temp_wav)
                    seg.export(output_path, format="mp3")
                    os.remove(temp_wav)
                except Exception as e:
                    print(f"MP3 conversion failed ({e}), saving as WAV instead")
                    # Fallback: save as WAV with .mp3 extension warning
                    sf.write(output_path, audio, sr, subtype="PCM_16")
            elif target_fmt == "pcm":
                # Raw PCM: 16-bit little-endian
                audio_int16 = np.clip(audio * 32767, -32768, 32767).astype(np.int16)
                with open(output_path, "wb") as f:
                    f.write(audio_int16.tobytes())
            else:  # wav
                sf.write(output_path, audio, sr, subtype="PCM_16")
        except ImportError:
            # Fallback: just copy the file
            shutil.copy2(input_path, output_path)
        except Exception as e:
            print(f"ERROR: Post-processing failed: {e}")
            import traceback
            traceback.print_exc()
            raise

    def _get_voice_map(self) -> dict[str, str]:
        """Map our voice IDs to manifest voice names."""
        voices = self.builtin_voices
        cn_male = [v for v in voices if "Chinese Male" in v.get("group", "")]
        cn_female = [v for v in voices if "Chinese Female" in v.get("group", "")]
        en_male = [v for v in voices if "English Male" in v.get("group", "")]
        en_female = [v for v in voices if "English Female" in v.get("group", "")]
        jp_female = [v for v in voices if "Japanese Female" in v.get("group", "")]

        return {
            # Chinese Female
            "xiaoyuan": cn_female[0]["id"] if cn_female else "Xiaoyu",
            "xiaobei": cn_female[1]["id"] if len(cn_female) > 1 else "Yuewen",
            "xiaoxue": cn_female[2]["id"] if len(cn_female) > 2 else "Lingyu",
            # Chinese Male
            "xiaogang": cn_male[0]["id"] if cn_male else "Junhao",
            "laoli": cn_male[1]["id"] if len(cn_male) > 1 else "Zhiming",
            "xiaoming": cn_male[2]["id"] if len(cn_male) > 2 else "Weiguo",
            # English Female
            "emma": en_female[1]["id"] if len(en_female) > 1 else "Bella",
            "ava": en_female[0]["id"] if en_female else "Ava",
            # English Male
            "james": en_male[1]["id"] if len(en_male) > 1 else "Adam",
            "trump": en_male[0]["id"] if en_male else "Trump",
            "nathan": en_male[2]["id"] if len(en_male) > 2 else "Nathan",
            # Japanese Female
            "soyo": jp_female[0]["id"] if len(jp_female) > 0 else "Soyo",
            "saki": jp_female[1]["id"] if len(jp_female) > 1 else "Saki",
            "mortis": jp_female[2]["id"] if len(jp_female) > 2 else "Mortis",
            "umiri": jp_female[3]["id"] if len(jp_female) > 3 else "Umiri",
            "mei": jp_female[4]["id"] if len(jp_female) > 4 else "Mei",
            "anon": jp_female[5]["id"] if len(jp_female) > 5 else "Anon",
            "arisa": jp_female[6]["id"] if len(jp_female) > 6 else "Arisa",
        }

    @staticmethod
    def _synthesize_stub(text: str, voice_config: dict, output_path: str) -> str:
        """Generate silent WAV stub when model unavailable."""
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


tts_model = MossTTSNanoONNX()
