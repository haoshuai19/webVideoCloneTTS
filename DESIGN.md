# TTS Studio — Design System

## 1. Visual Theme & Atmosphere

TTS Studio 的界面融合了 Vercel 的工程精确性与 ElevenLabs 的音频产品温度感。整体采用纯白画布（`#ffffff`）搭配近黑文字（`#171717`），通过暖色调点缀传递声音产品的亲和力。设计哲学：界面是工具而非装饰——每个像素都服务于功能。

**Key Characteristics:**
- Geist Sans + Geist Mono 字体体系，display 尺寸负字间距（-2.4px 至 -2.88px）
- 音频产品特有暖色调：琥珀色（`#f59e0b`）用于主操作，珊瑚色（`#f97316`）用于波形强调
- Shadow-as-border 技术替代传统 CSS 边框
- 多层层叠阴影系统，不透明度低于 0.1
- 波形可视化作为核心视觉元素
- 波形动画微交互（生成中播放状态）

## 2. Color Palette & Roles

### Primary
- **Canvas White** (`#ffffff`): 主背景、卡片表面、按钮背景
- **Ink Black** (`#171717`): 主文字、标题、深色表面
- **Warm Gray** (`#78716c`): 次要文字、描述文案

### Accent (Audio-themed)
- **Amber Primary** (`#f59e0b`): 主操作按钮、活跃状态、波形主色
- **Orange Wave** (`#f97316`): 波形强调、音频播放指示器
- **Coral Active** (`#ff6b35`): 生成中动画、进度指示

### Neutral Scale
- **Gray 900** (`#171717`): 主文字、标题
- **Gray 700** (`#404040`): 次要文字
- **Gray 500** (`#737373`): 占位符、禁用状态
- **Gray 300** (`#d4d4d4`): 分割线
- **Gray 100** (`#f5f5f5`): 微妙表面底色
- **Gray 50** (`#fafafa`): 最浅表面、内部阴影高光

### Status
- **Success Green** (`#22c55e`): 合成完成、下载可用
- **Error Red** (`#ef4444`): 合成失败、验证错误
- **Info Blue** (`#3b82f6`): 处理中提示

### Shadows & Depth
- **Border Shadow** (`rgba(0,0,0,0.08) 0px 0px 0px 1px`): 替代传统边框
- **Card Shadow** (`rgba(0,0,0,0.08) 0px 0px 0px 1px, rgba(0,0,0,0.04) 0px 2px 4px, rgba(0,0,0,0.04) 0px 8px 8px -8px, #fafafa 0px 0px 0px 1px`): 完整卡片阴影
- **Warm Lift** (`rgba(245,158,11,0.08) 0px 4px 12px`): 暖色提升（CTA 按钮）

## 3. Typography Rules

### Font Family
- **Primary**: `Geist`, fallbacks: `Arial, Apple Color Emoji, Segoe UI Emoji, Segoe UI Symbol`
- **Monospace**: `Geist Mono`, fallbacks: `ui-monospace, SFMono-Regular, Roboto Mono, Menlo`
- **OpenType**: `"liga"` 全局启用

### Hierarchy

| Role | Font | Size | Weight | Line Height | Letter Spacing |
|------|------|------|--------|-------------|----------------|
| Display Hero | Geist | 48px (3.00rem) | 600 | 1.00–1.17 | -2.4px to -2.88px |
| Section Heading | Geist | 32px (2.00rem) | 600 | 1.20 | -1.28px |
| Card Title | Geist | 24px (1.50rem) | 600 | 1.33 | -0.96px |
| Body Large | Geist | 20px (1.25rem) | 400 | 1.80 | normal |
| Body | Geist | 16px (1.00rem) | 400 | 1.50 | normal |
| UI Text | Geist | 14px (0.88rem) | 500 | 1.43 | normal |
| Caption | Geist | 12px (0.75rem) | 400–500 | 1.33 | normal |
| Mono Body | Geist Mono | 16px (1.00rem) | 400 | 1.50 | normal |
| Mono Caption | Geist Mono | 12px (0.75rem) | 500 | 1.00 | normal |

### Principles
- 压缩即身份：display 尺寸使用激进负字间距
- 三档字重：400（阅读）、500（交互）、600（标题）
- 等宽字体用于技术参数标签（采样率、格式）

## 4. Component Stylings

### Buttons

**Primary Amber CTA**
- Background: `#f59e0b`
- Text: `#171717`
- Padding: 8px 16px
- Radius: 6px
- Shadow: `rgba(245,158,11,0.08) 0px 4px 12px`
- Hover: `#d97706`
- Use: 合成按钮、主操作

**Secondary (Shadow-bordered)**
- Background: `#ffffff`
- Text: `#171717`
- Radius: 6px
- Shadow: `rgb(235,235,235) 0px 0px 0px 1px`
- Hover: `#f5f5f5`
- Use: 次要操作、取消

**Dark CTA**
- Background: `#171717`
- Text: `#ffffff`
- Padding: 8px 16px
- Radius: 6px
- Use: 下载按钮、导出

### Cards & Containers
- Background: `#ffffff`
- Border: shadow-as-border technique
- Radius: 8px
- Shadow: full card shadow stack
- Hover: shadow intensification

### Inputs & Forms
- Background: `#ffffff`
- Border: shadow-as-border
- Radius: 6px
- Padding: 8px 12px
- Focus: `2px solid hsla(38, 100%, 50%, 0.5)` (amber ring)
- Textarea min-height: 120px

### Waveform Display
- Height: 64px
- Background: `#fafafa` with subtle grid
- Wave color: `#f97316` (amber-orange gradient)
- Playhead: `#f59e0b` vertical line
- Border-radius: 8px
- Shadow: inset shadow for depth

### Voice Selector
- Pill-style selection chips
- Active: amber background, dark text
- Inactive: white background, shadow border
- Radius: 9999px
- Padding: 6px 14px

### Sliders (Speed/Pitch/Volume)
- Track: `#e5e5e5`, height 4px, radius 2px
- Fill: `#f59e0b`, radius 2px
- Thumb: `#ffffff`, 16px diameter, shadow border
- Active thumb: warm shadow

## 5. Layout Principles

### Spacing System
- Base unit: 8px
- Scale: 4px, 8px, 12px, 16px, 24px, 32px, 48px, 64px

### Grid & Container
- Max content width: 960px
- Centered layout
- 2-column grid for voice selection
- Single column for controls and output

### Section Layout (TTS Panel)
1. Header: "TTS Studio" title + subtitle
2. Text Input: large textarea with character counter
3. Voice Settings: gender/age/voice selector
4. Audio Controls: speed, pitch, volume sliders
5. Output Format: MP3/WAV/PCM selector + sample rate
6. Synthesize Button: primary amber CTA
7. Waveform Preview: generated audio visualization
8. Audio Player: play/pause controls
9. Download: dark CTA with format info

### Whitespace Philosophy
- 工程精确 + 画廊留白
- 各功能区块用阴影边框分隔
- 垂直间距 32px–48px
- 文本压缩 + 空间扩展的对比

## 6. Depth & Elevation

| Level | Treatment | Use |
|-------|-----------|-----|
| Flat (0) | No shadow | 页面背景、文字块 |
| Ring (1) | `rgba(0,0,0,0.08) 0px 0px 0px 1px` | 大部分元素的基础边框 |
| Card (2) | Ring + subtle elevation | 面板、表单 |
| Elevated (3) | Full card shadow stack | 突出面板 |
| Warm Lift | `rgba(245,158,11,0.08) 0px 4px 12px` | CTA 按钮 |
| Focus | `2px solid hsla(38, 100%, 50%, 0.5)` | 键盘焦点 |

## 7. Do's and Don'ts

### Do
- 使用 shadow-as-border 替代 CSS border
- Geist 字体 display 尺寸使用负字间距
- 琥珀色 `#f59e0b` 作为主操作色
- 三档字重：400/500/600
- 技术参数使用等宽字体标注
- 波形可视化作为音频反馈

### Don't
- 不使用正字间距于 Geist
- 不使用字重 700 于正文
- 不使用传统 CSS border 于卡片
- 不引入紫色/蓝色等无关品牌色
- 不跳过内部 `#fafafa` 光环阴影
