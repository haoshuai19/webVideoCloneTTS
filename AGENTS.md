# AGENTS.md — TTS Studio

## Project Overview

TTS Studio 是一个基于 Web 的智能语音合成平台。后端使用 Python FastAPI + MOSS-TTS-Nano 模型，前端使用 React + TypeScript + Vite + Tailwind CSS。

## Quick Commands

### Backend (Python FastAPI)
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend (React + Vite)
```bash
cd frontend
npm install
npm run dev          # Dev server (proxies API to :8000)
npm run build        # Production build
```

### Run Tests
```bash
# Backend
cd backend && python -m pytest tests/ -v

# Frontend unit tests
cd frontend && npx vitest run

# Frontend E2E (Chrome)
cd frontend && npx playwright test
```

## Architecture

- **Backend**: FastAPI, async synthesis pipeline, in-memory task management
- **Frontend**: React 18, Vite 6, Tailwind CSS 3, Geist fonts
- **Model**: MOSS-TTS-Nano (lazy-loaded, stub mode when model files missing)
- **Audio**: pydub for format conversion (mp3/wav/pcm at 8k/16k)
- **API**: REST API with async task pattern (POST → task_id → poll → download)

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/api/voices` | List voices (filter: gender, age_group, language) |
| POST | `/api/synthesize` | Async text-to-speech |
| GET | `/api/synthesize/{task_id}` | Task status |
| POST | `/api/clone-voice` | Voice cloning (stub) |

## Key Conventions

- **TDD required**: No production code without a failing test first
- **DESIGN.md**: All UI follows `DESIGN.md` at project root (Vercel-style + audio warmth)
- **Shadow-as-border**: No CSS borders; use `box-shadow` for borders
- **Type hints**: Backend Python code uses type hints everywhere
- **TypeScript strict**: Frontend uses strict mode
- **API field mapping**: Backend uses snake_case (`voice_id`), frontend uses camelCase (`voiceId`) - mapped in `api.ts`
- **Audio processing**: librosa returns `(channels, samples)` format, use `axis=0` for mono conversion
- **ONNX inference**: Use `--sample-mode fixed` (greedy hangs), 180s timeout, subprocess execution

## Setup Gotchas

- MOSS-TTS-Nano ONNX model downloaded to `models/moss-tts-nano/` (12 files, 5 ONNX sessions)
- Full ONNX inference requires companion `MOSS-Audio-Tokenizer-Nano-ONNX` model
- Currently uses silent WAV stub for testing (ONNX model loaded but codec pipeline pending)
- If model missing, stub generates silent WAV files for testing
- Frontend dev server proxies `/api/*` to `http://localhost:8000`
- Outputs saved to `backend/outputs/` directory

## Model Status

- **ONNX Model**: ✅ Downloaded and loaded (5 sessions: prefill, decode_step, local_decoder, fixed_sampled, local_cached)
- **Audio Codec**: ✅ Downloaded (encode, decode_step, decode_full)
- **Text Tokenizer**: ✅ SentencePiece tokenizer loaded (vocab: 16384)
- **Built-in Voices**: ✅ 18 voices from manifest (CN/EN/JP), 8 mapped to frontend IDs
- **Full Inference**: ✅ Working via subprocess (48kHz native → resampled to target)
- **Reference Code**: `temp_moss_tts/` (cloned from OpenMOSS/MOSS-TTS-Nano)
- **Model Files**: `models/` directory (moss-tts-nano + moss-audio-tokenizer + directory aliases)
- **Inference Settings**: `--sample-mode fixed` (greedy hangs), 180s timeout, 4 CPU threads

## Voice Mapping

Frontend voice IDs map to MOSS-TTS-Nano manifest voices:

| Frontend ID | Name | Gender | Age | Manifest Voice | Group |
|------------|------|--------|-----|----------------|-------|
| xiaoyuan | 小媛 | female | young | Xiaoyu | Chinese Female |
| xiaobei | 小贝 | female | young | Yuewen | Chinese Female |
| xiaogang | 小刚 | male | young | Junhao | Chinese Male |
| xiaoxue | 小雪 | female | middle | Lingyu | Chinese Female |
| laoli | 老李 | male | old | Zhiming | Chinese Male |
| emma | Emma | female | young | Bella | English Female |
| james | James | male | middle | Adam | English Male |
| xiaoming | 小明 | male | child | Weiguo | Chinese Male |

All 8 voices verified working with RMS > 0.03 (well above 0.001 silence threshold).

## Voice Cloning

- **Process**: Reference audio → ONNX codec encoder → discrete codes → stored in memory
- **Storage**: Cloned voices stored in `voice_clone_service._cloned_voices` (in-memory)
- **No output file**: Cloning does NOT generate an audio file; it extracts voice characteristics
- **Synthesis**: Audio file generated when using cloned voice via `/api/synthesize`
- **Output location**: `backend/outputs/{task_id}.wav` (served at `/outputs/{task_id}.wav`)

## Troubleshooting

### Silent Audio Issues

If user reports silent audio:

1. **Verify backend synthesis**: Direct `tts_model.synthesize()` calls work correctly for all voices
2. **Check API flow**: All 8 voices pass API test with RMS > 0.03
3. **Browser playback**: May be browser-specific; suggest downloading file directly
4. **File verification**: Use `scipy.io.wavfile` or `wave` module to verify RMS > 0.001
5. **Leading silence**: First ~0.084s may have very low volume (normal for TTS models)

### Voice Cloning

- Cloning extracts voice characteristics as discrete codes
- Codes stored in memory, not as audio files
- Synthesis with cloned voice generates audio to `outputs/` directory
- Verified working with RMS > 0.6 for cloned voices
