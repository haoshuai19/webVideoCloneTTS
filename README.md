# TTS Studio — Web 语音合成与克隆平台

基于 Web 的智能语音合成平台，支持 **文本转语音 (TTS)** 和 **声音克隆**。

## 功能

- **语音合成**：8 种内置音色（中文 6 + 英文 2），支持语速/音调/音量调节，输出 MP3/WAV/PCM
- **声音克隆**：上传参考音频提取音色特征，自动注册到音色列表，克隆后可在 TTS 中使用
- **异步任务**：合成/克隆均异步执行，前端轮询进度

## 前置依赖

除本仓库代码外，还需要下载安装以下内容：

### 1. 运行环境

| 依赖 | 版本 | 说明 |
|------|------|------|
| Python | >= 3.10 | 后端运行环境 |
| Node.js | >= 18 | 前端运行环境 |
| ffmpeg | 最新版 | 音频格式转换（系统 PATH 可用） |

### 2. Python 依赖

```bash
cd backend
pip install -r requirements.txt
```

核心依赖：`fastapi`、`onnxruntime`、`sentencepiece`、`torch`、`librosa`、`soundfile`、`pydub`

### 3. 模型文件（需手动下载）

项目使用两个 ONNX 模型（Apache-2.0 许可），需从 Hugging Face 下载后放入对应目录：

**TTS 主模型**（~650MB）
```
下载地址：https://huggingface.co/OpenMOSS-Team/MOSS-TTS-Nano-100M-ONNX
放置路径：models/moss-tts-nano/
```
包含：`moss_tts_prefill.onnx`、`moss_tts_decode_step.onnx`、`moss_tts_global_shared.data`、`moss_tts_local_shared.data`、`tokenizer.model` 等约 11 个文件

**音频编码器**（~85MB）
```
下载地址：https://huggingface.co/OpenMOSS-Team/MOSS-Audio-Tokenizer-Nano-ONNX
放置路径：models/moss-audio-tokenizer/
```
包含：`moss_audio_tokenizer_encode.onnx`、`moss_audio_tokenizer_decode_full.onnx`、`moss_audio_tokenizer_decode_shared.data` 等约 6 个文件

**下载方式（任选其一）：**

```bash
# 方式 1：huggingface-cli（推荐）
huggingface-cli download OpenMOSS-Team/MOSS-TTS-Nano-100M-ONNX --local-dir models/moss-tts-nano
huggingface-cli download OpenMOSS-Team/MOSS-Audio-Tokenizer-Nano-ONNX --local-dir models/moss-audio-tokenizer

# 方式 2：国内镜像（无需翻墙）
set HF_ENDPOINT=https://hf-mirror.com
huggingface-cli download OpenMOSS-Team/MOSS-TTS-Nano-100M-ONNX --local-dir models/moss-tts-nano
huggingface-cli download OpenMOSS-Team/MOSS-Audio-Tokenizer-Nano-ONNX --local-dir models/moss-audio-tokenizer

# 方式 3：ModelScope（国内）
pip install modelscope
python -c "from modelscope import snapshot_download; snapshot_download('openmoss/MOSS-TTS-Nano-100M-ONNX', cache_dir='models/moss-tts-nano')"
python -c "from modelscope import snapshot_download; snapshot_download('openmoss/MOSS-Audio-Tokenizer-Nano-ONNX', cache_dir='models/moss-audio-tokenizer')"
```

> 模型文件（`.onnx`、`.data`）通过 Git LFS 存储，下载后请确认文件大小正确（非 LFS 指针文件）。

## 技术栈

| 层 | 技术 |
|---|------|
| 前端 | React + TypeScript + Vite + Tailwind CSS |
| 后端 | Python FastAPI |
| 推理 | MOSS-TTS-Nano (ONNX) |
| 部署 | Docker / Docker Compose |

## 快速启动

```bash
# 后端
cd backend && pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# 前端
cd frontend && npm install && npm run dev
# → http://localhost:5173
```

或使用 `start.ps1` 一键启动。

## 项目结构

```
├─ backend/          FastAPI 后端
│  ├─ app/api/       路由层
│  ├─ app/models/    ONNX 模型封装 / 音色定义
│  ├─ app/services/  合成 & 克隆业务逻辑
│  └─ tests/         API 测试
├─ frontend/         React 前端
│  ├─ src/components/   VoiceSelector / CloneVoicePanel / AudioPlayer 等
│  ├─ src/hooks/        useSynthesis（状态轮询）
│  ├─ src/services/     API 客户端
│  └─ tests/            单元 & E2E 测试
├─ models/           ONNX 模型文件（需自行下载）
└─ temp_moss_tts/    MOSS 官方推理代码
```

## API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/voices` | 音色列表 |
| POST | `/api/synthesize` | 文本转语音 |
| GET | `/api/synthesize/{task_id}` | 任务状态 |
| POST | `/api/clone-voice` | 声音克隆 |
| GET | `/outputs/{filename}` | 下载音频 |

> 模型文件（`models/`）因体积过大未纳入仓库，需从 Hugging Face 下载后放入对应目录。
