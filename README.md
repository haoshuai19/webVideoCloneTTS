# TTS Studio

基于 Web 的智能语音合成平台，后端使用 Python FastAPI + MOSS-TTS-Nano 模型，前端使用 React + TypeScript + Vite + Tailwind CSS。

## 架构

```
┌─────────────────────────────────────────────────┐
│  Frontend (React + Vite, :5173)                  │
│  ┌──────────┐ ┌──────────┐ ┌────────────────┐   │
│  │ TTS Page  │ │ Clone   │ │ Waveform/Audio │   │
│  │ Voice+Text│ │ Panel   │ │ Player/Download│   │
│  └────┬─────┘ └────┬─────┘ └────────────────┘   │
│       │            │                             │
│       └─────┬──────┘                             │
│             │ HTTP (Vite proxy /api/* → :8000)    │
└─────────────┼───────────────────────────────────┘
              │
┌─────────────┼───────────────────────────────────┐
│  Backend (FastAPI, :8000)                        │
│  ┌──────────┴──────────┐                        │
│  │ /api/synthesize      │  Async TTS + Clone     │
│  │ /api/clone-voice     │  synthesis             │
│  │ /api/voices          │                        │
│  └──────────┬──────────┘                        │
│             │                                    │
│  ┌──────────┴──────────┐  ┌──────────────────┐  │
│  │ tts_model           │  │ voice_clone       │  │
│  │ (OnnxTtsRuntime)    │  │ service           │  │
│  └─────────────────────┘  └──────────────────┘  │
│             │                                    │
│  ┌──────────┴──────────┐                        │
│  │ infer_onnx.py        │  Subprocess for        │
│  │ (official pipeline)  │  clone voice TTS       │
│  └─────────────────────┘                        │
└─────────────────────────────────────────────────┘
```

## 快速开始

### 前置要求

- Python 3.10+
- Node.js 18+
- 模型文件：`models/moss-tts-nano/`、`models/moss-audio-tokenizer/`

### 启动后端

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 启动前端

```bash
cd frontend
npm install
npm run dev           # Dev server → http://localhost:5173
npm run build         # Production build
```

Vite 开发服务器自动代理 `/api/*` 到 `http://localhost:8000`。

也可使用项目根目录的一键启动脚本 `start.ps1`（PowerShell 双窗口启动）。

## 功能

### 语音合成 (TTS)

选择内置音色 → 输入文本 → 合成 → 播放 / 下载。

- 8 种内置音色（中文 6 + 英文 2），支持性别/年龄筛选
- 输出格式：MP3 / WAV / PCM，采样率 8kHz / 16kHz
- 可调节语速 (0.25–4.0)、音调 (0.5–2.0)、音量 (0–200%)

### 声音克隆

上传参考音频 → 提取音色特征 → 克隆音色自动注册到音色列表 → 在 TTS 中使用。

- 支持 WAV / MP3 / M4A 格式
- 建议使用 10–15 秒清晰人声
- 克隆完成后自动切换到 TTS 页面，克隆音色带 "克隆" 标签
- 克隆音色合成使用 ONNX 子进程，CPU 下约 5–8 分钟/百字

## API 端点

| 方法 | 路径 | 说明 |
|--------|------|-------------|
| GET | `/health` | 健康检查 |
| GET | `/api/voices` | 列出音色（支持 gender/age_group/language 筛选） |
| POST | `/api/synthesize` | 文本转语音（异步任务） |
| GET | `/api/synthesize/{task_id}` | 查询任务状态 |
| POST | `/api/clone-voice` | 声音克隆（multipart/form-data） |
| GET | `/outputs/{filename}` | 音频文件下载 |

### 合成请求示例

```json
POST /api/synthesize
{
  "text": "你好世界",
  "voice_id": "xiaoyuan",
  "speed": 1.0,
  "pitch": 1.0,
  "volume": 1.0,
  "format": "mp3",
  "sample_rate": 16000
}
```

### 克隆请求示例

```
POST /api/clone-voice
Content-Type: multipart/form-data

audio_file: (音频文件)
voice_name: "我的声音"
reference_text: "" (可选)
```

## 音色映射

所有音色均经过实测验证（12/12 通过，WAV+MP3 格式均正常）。

| 前端 ID | 名称 | 性别 | 年龄 | 清单音色 | 组 |
|-----------|------|--------|-----|--------------|-------|
| xiaoyuan | 小媛 | female | young | Xiaoyu | Chinese Female |
| xiaobei | 小贝 | female | young | Yuewen | Chinese Female |
| xiaogang | 小刚 | male | young | Junhao | Chinese Male |
| xiaoxue | 小雪 | female | middle | Lingyu | Chinese Female |
| laoli | 老李 | male | old | Zhiming | Chinese Male |
| xiaoming | 小明 | male | child | Weiguo | Chinese Male |

克隆音色 ID 格式：`cloned_{task_id}`。

## 项目结构

```
F:\webVideoCloneTTS\
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py        # FastAPI 路由
│   │   ├── models/
│   │   │   ├── moss_tts.py      # ONNX TTS 模型封装
│   │   │   ├── voice.py         # 音色定义
│   │   │   └── voice_cloning_onnx.py  # 克隆 ONNX 管线
│   │   ├── services/
│   │   │   ├── tts_service.py   # 合成任务管理
│   │   │   └── voice_clone.py   # 克隆服务
│   │   ├── utils/
│   │   │   └── audio.py         # 音频格式转换
│   │   ├── config.py
│   │   └── main.py
│   ├── tests/
│   │   └── test_api.py          # API 测试 (15 个)
│   └── outputs/                 # 输出音频文件
├── frontend/
│   ├── src/
│   │   ├── App.tsx              # 主应用 (TTS/Clone 双模式)
│   │   ├── components/
│   │   │   ├── VoiceSelector.tsx    # 音色选择器
│   │   │   ├── CloneVoicePanel.tsx  # 声音克隆面板
│   │   │   ├── AudioPlayer.tsx      # 音频播放器
│   │   │   ├── WaveformPreview.tsx  # 波形预览
│   │   │   ├── AudioControls.tsx    # 语速/音调/音量
│   │   │   ├── FormatSelector.tsx   # 输出格式
│   │   │   └── DownloadButton.tsx   # 下载按钮
│   │   ├── hooks/
│   │   │   └── useSynthesis.ts  # 合成状态轮询
│   │   ├── services/
│   │   │   └── api.ts           # API 客户端
│   │   ├── styles/
│   │   │   └── index.css        # Tailwind + 自定义样式
│   │   ├── i18n.ts
│   │   └── main.tsx
│   └── tests/
│       ├── App.test.tsx         # 单元测试 (8 个)
│       └── e2e/
│           └── synthesis.spec.ts # Playwright E2E 测试
├── temp_moss_tts/               # MOSS-TTS-Nano 官方代码
│   ├── onnx_tts_runtime.py      # ONNX 运行时封装
│   └── infer_onnx.py            # 官方推理入口
├── models/                      # ONNX 模型文件
├── DESIGN.md                    # 设计系统
├── AGENTS.md                    # AI 代理指南
└── README.md                    # 本文件
```

## 测试

```bash
# 后端
cd backend && python -m pytest tests/ -v

# 前端单元测试
cd frontend && npx vitest run

# 前端 E2E (Chrome)
cd frontend && npx playwright test
```

## 设计系统

详见 [DESIGN.md](./DESIGN.md)。

- Vercel 风格 + 音频产品温度感
- Geist 字体体系
- Shadow-as-border 替代 CSS border
- 琥珀色主色 + 波形可视化

## 已知限制

- 克隆音色合成分离线流程，CPU 下较慢（5–8 分钟/百字）
- 内置音色合成通过子进程调用，首次加载模型需约 30s
- 系统内存建议 16GB+（ONNX 加载约 4.5GB）
- 长文本（>200 字）合成约需 1-5 分钟，请耐心等待

## 历史修复

| 问题 | 修复 |
|------|--------|
| MP3 格式下 `.wav` 文件被写入 MP3 数据导致无声 | `_synthesize_official` 中固定 `target_format = "wav"` |
| 后端子进程缺少 `cwd` 参数导致长文本推理失败 | `_run_inference` 添加 `cwd=str(temp_moss_dir)` |
| 子进程超时不足（180s）导致长文本合成被截断 | 超时提升至 600s |
| 男声（小刚）最后一句缺失：chunk 过大导致模型过早生成 EOS | `--voice-clone-max-text-tokens 40` 拆分更小 chunk |
| 浏览器自动播放策略导致播放静默失败 | `AudioPlayer` 添加 `play()` Promise 错误处理 |
| 音色列表切换年龄段时选项重复累加 | `VoiceSelector` 列表按 `id` 去重 |
