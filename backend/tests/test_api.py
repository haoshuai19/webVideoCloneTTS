import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.config import settings


@pytest.fixture
def client():
    return TestClient(app)


class TestHealthEndpoint:
    def test_health_returns_ok(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["status"] == "ok"
        assert data["error"] is None


class TestVoicesEndpoint:
    def test_list_all_voices(self, client):
        resp = client.get("/api/voices")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert len(data["data"]) >= 6

    def test_filter_by_gender(self, client):
        resp = client.get("/api/voices?gender=female")
        data = resp.json()
        assert all(v["gender"] == "female" for v in data["data"])

    def test_filter_by_age_group(self, client):
        resp = client.get("/api/voices?age_group=young")
        data = resp.json()
        assert all(v["age_group"] == "young" for v in data["data"])

    def test_filter_by_language(self, client):
        resp = client.get("/api/voices?language=en")
        data = resp.json()
        for v in data["data"]:
            assert v["language"] == "en"

    def test_combined_filters(self, client):
        resp = client.get("/api/voices?gender=male&age_group=young")
        data = resp.json()
        for v in data["data"]:
            assert v["gender"] == "male"
            assert v["age_group"] == "young"


class TestSynthesizeEndpoint:
    @pytest.fixture(autouse=True)
    def mock_synthesis(self, monkeypatch):
        from app.models import moss_tts

        def fast_synthesize(text, voice_config, output_path):
            import wave
            import struct
            import os
            sample_rate = voice_config.get("sample_rate", 16000)
            num_samples = int(sample_rate * 0.5)
            os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
            with wave.open(output_path, "w") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sample_rate)
                wf.writeframes(struct.pack(f"<{num_samples}h", *[0] * num_samples))
            return output_path

        monkeypatch.setattr(moss_tts.tts_model, "synthesize", fast_synthesize)

    def test_synthesize_request_returns_task_id(self, client):
        resp = client.post(
            "/api/synthesize",
            json={
                "text": "Hello world",
                "voice_id": "xiaoyuan",
                "format": "mp3",
                "sample_rate": 16000,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert "task_id" in data["data"]

    def test_synthesize_invalid_voice(self, client):
        resp = client.post(
            "/api/synthesize",
            json={
                "text": "Hello",
                "voice_id": "nonexistent",
                "format": "mp3",
            },
        )
        data = resp.json()
        assert data["success"] is False
        assert "error" in data

    def test_synthesize_invalid_sample_rate(self, client):
        resp = client.post(
            "/api/synthesize",
            json={
                "text": "Hello",
                "voice_id": "xiaoyuan",
                "sample_rate": 44100,
            },
        )
        data = resp.json()
        assert data["success"] is False
        assert "sample_rate" in data["error"].lower()

    def test_synthesize_empty_text_rejected(self, client):
        resp = client.post(
            "/api/synthesize",
            json={
                "text": "",
                "voice_id": "xiaoyuan",
            },
        )
        assert resp.status_code == 422

    def test_synthesize_invalid_format(self, client):
        resp = client.post(
            "/api/synthesize",
            json={
                "text": "Hello",
                "voice_id": "xiaoyuan",
                "format": "flac",
            },
        )
        assert resp.status_code == 422


class TestTaskStatusEndpoint:
    def test_task_not_found(self, client):
        resp = client.get("/api/synthesize/nonexistent123")
        data = resp.json()
        assert data["success"] is False
        assert "error" in data

    def _poll_until_done(self, client, task_id):
        import time
        for _ in range(30):
            resp = client.get(f"/api/synthesize/{task_id}")
            data = resp.json()
            if data["data"]["status"] == "completed":
                return data
            elif data["data"]["status"] == "failed":
                pytest.fail(f"Task failed: {data['data']['error']}")
            time.sleep(0.5)
        pytest.fail(f"Task {task_id} did not complete within 15s")

    def test_task_status_flow_wav(self, client, monkeypatch):
        from app.models import moss_tts

        def fast_synth(text, voice_config, output_path):
            import wave, struct, os
            sr = voice_config.get("sample_rate", 16000)
            with wave.open(output_path, "w") as wf:
                wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(sr)
                wf.writeframes(struct.pack(f"<{int(sr*0.5)}h", *[0] * int(sr*0.5)))
            return output_path

        monkeypatch.setattr(moss_tts.tts_model, "synthesize", fast_synth)

        resp = client.post("/api/synthesize", json={
            "text": "Test audio", "voice_id": "xiaobei",
            "format": "wav", "sample_rate": 8000,
        })
        task_id = resp.json()["data"]["task_id"]
        data = self._poll_until_done(client, task_id)

        assert data["data"]["result_url"].endswith(".wav")
        # Verify .wav file has RIFF header (true WAV, not MP3 mislabeled)
        import os
        wav_path = os.path.join(settings.output_dir, f"{task_id}.wav")
        with open(wav_path, "rb") as f:
            assert f.read(4) == b"RIFF", f"{wav_path} is not a valid WAV file"

    def test_task_status_flow_mp3(self, client, monkeypatch):
        from app.models import moss_tts

        def fast_synth(text, voice_config, output_path):
            import wave, struct, os
            sr = voice_config.get("sample_rate", 16000)
            with wave.open(output_path, "w") as wf:
                wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(sr)
                wf.writeframes(struct.pack(f"<{int(sr*0.5)}h", *[0] * int(sr*0.5)))
            return output_path

        monkeypatch.setattr(moss_tts.tts_model, "synthesize", fast_synth)

        resp = client.post("/api/synthesize", json={
            "text": "Test audio", "voice_id": "xiaoyuan",
            "format": "mp3", "sample_rate": 16000,
        })
        task_id = resp.json()["data"]["task_id"]
        data = self._poll_until_done(client, task_id)

        assert data["data"]["result_url"].endswith(".mp3")
        import os
        # Verify .wav intermediate is still valid WAV (not corrupted by format pipeline)
        wav_path = os.path.join(settings.output_dir, f"{task_id}.wav")
        assert os.path.exists(wav_path), f"Intermediate WAV {wav_path} missing"
        with open(wav_path, "rb") as f:
            assert f.read(4) == b"RIFF", f"Intermediate WAV {wav_path} has wrong format"
        # Verify .mp3 output is valid MP3
        mp3_path = os.path.join(settings.output_dir, f"{task_id}.mp3")
        with open(mp3_path, "rb") as f:
            header = f.read(3)
            assert header == b"ID3" or header[:2] == b"\xff\xfb", f"{mp3_path} is not valid MP3"
            f.seek(0)
            assert f.read(4)[:3] == b"ID3", f"{mp3_path} missing ID3 header"


class TestCloneVoiceEndpoint:
    def test_clone_voice_returns_task_id(self, client):
        import numpy as np
        import soundfile as sf
        import os
        from io import BytesIO
        
        # Create a real audio file with actual sine wave content (440Hz, 1 second)
        sr = 48000
        duration = 1.0
        t = np.linspace(0, duration, int(sr * duration), False)
        audio = np.sin(2 * np.pi * 440 * t).astype(np.float32)
        
        # Save to WAV
        test_audio_path = "outputs/test_clone_input.wav"
        os.makedirs("outputs", exist_ok=True)
        sf.write(test_audio_path, audio, sr, subtype="PCM_16")
        
        # Read the WAV file as bytes
        with open(test_audio_path, "rb") as f:
            audio_bytes = f.read()
        
        resp = client.post(
            "/api/clone-voice",
            data={
                "voice_name": "my_cloned_voice",
                "reference_text": "你好世界",
            },
            files={"audio_file": ("test.wav", BytesIO(audio_bytes), "audio/wav")},
        )
        
        # Clean up test file
        if os.path.exists(test_audio_path):
            os.remove(test_audio_path)
        
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert "task_id" in data["data"]
        assert data["data"]["status"] == "completed"
        assert "voice_id" in data["data"]
        
        # Verify the cloned voice can be retrieved
        voice_id = data["data"]["voice_id"]
        assert voice_id.startswith("cloned_")
        
        # Test that the cloned voice appears in voice list
        voices_resp = client.get("/api/voices")
        voices_data = voices_resp.json()
        voice_ids = [v["id"] for v in voices_data["data"]]
        assert voice_id in voice_ids
