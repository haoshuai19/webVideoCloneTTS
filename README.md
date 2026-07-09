# TTS Studio — Web 语音合成与克隆平台

基于 Web 的智能语音合成平台，支持 **文本转语音 (TTS)** 和 **声音克隆**。

## 功能

- **语音合成**：8 种内置音色（中文 6 + 英文 2），支持语速/音调/音量调节，输出 MP3/WAV/PCM
- **声音克隆**：上传参考音频提取音色特征，自动注册到音色列表，克隆后可在 TTS 中使用
- **异步任务**：合成/克隆均异步执行，前端轮询进度

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
