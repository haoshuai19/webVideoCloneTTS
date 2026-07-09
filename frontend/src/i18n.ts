import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

const resources = {
  zh: {
    translation: {
      'title': 'TTS Studio',
      'subtitle': '智能语音合成平台',
      'textInput': {
        'label': '文本输入',
        'description': '输入需要合成的文本内容',
        'placeholder': '在此输入需要合成的文本，支持中文、英文及混合文本...',
        'counter': '{{count}} / 5000',
      },
      'voice': {
        'label': '音色选择',
        'description': '选择发音人和筛选条件',
        'gender': '性别筛选',
        'all': '全部',
        'male': '男声',
        'female': '女声',
        'age': {
          'label': '年龄筛选',
          'all': '全部',
          'child': '儿童',
          'young': '青年',
          'middle': '中年',
          'old': '老年',
        },
        'noMatch': '没有匹配的音色，请调整筛选条件',
      },
      'controls': {
        'label': '音频参数',
        'description': '调整语速、音调和音量',
        'speed': '语速',
        'pitch': '音调',
        'volume': '音量',
      },
      'format': {
        'label': '输出格式',
        'description': '选择音频格式和采样率',
        'formatLabel': '音频格式',
        'sampleRate': '采样率',
        'mp3': { desc: '压缩格式，文件较小' },
        'wav': { desc: '无损格式，音质最佳' },
        'pcm': { desc: '原始音频，适合开发' },
      },
      'synthesize': {
        'button': '开始合成',
        'processing': '正在合成...',
      },
      'waveform': {
        'label': '音频波形',
        'synthesizing': '正在生成音频...',
        'completed': '合成完成，可以播放',
        'ready': '就绪，等待合成',
        'waiting': '等待生成音频...',
      },
      'player': {
        'label': '音频播放',
        'description': '试听合成结果',
        'noAudio': '合成完成后可播放音频',
      },
      'download': {
        'label': '下载音频',
        'description': '保存到本地使用',
        'button': '下载',
        'disabled': '合成完成后可下载',
      },
      'error': {
        'title': '合成失败',
      },
      'footer': 'TTS Studio © 2026 — Powered by MOSS-TTS-Nano',
    },
  },
  en: {
    translation: {
      'title': 'TTS Studio',
      'subtitle': 'Intelligent Voice Synthesis Platform',
      'textInput': {
        'label': 'Text Input',
        'description': 'Enter text to synthesize',
        'placeholder': 'Enter text here, supports Chinese, English, and mixed content...',
        'counter': '{{count}} / 5000',
      },
      'voice': {
        'label': 'Voice Selection',
        'description': 'Choose voice and filters',
        'gender': 'Gender Filter',
        'all': 'All',
        'male': 'Male',
        'female': 'Female',
        'age': {
          'label': 'Age Filter',
          'all': 'All',
          'child': 'Child',
          'young': 'Young',
          'middle': 'Middle',
          'old': 'Old',
        },
        'noMatch': 'No matching voices, please adjust filters',
      },
      'controls': {
        'label': 'Audio Parameters',
        'description': 'Adjust speed, pitch, and volume',
        'speed': 'Speed',
        'pitch': 'Pitch',
        'volume': 'Volume',
      },
      'format': {
        'label': 'Output Format',
        'description': 'Select audio format and sample rate',
        'formatLabel': 'Audio Format',
        'sampleRate': 'Sample Rate',
        'mp3': { desc: 'Compressed, smaller file' },
        'wav': { desc: 'Lossless, best quality' },
        'pcm': { desc: 'Raw audio, for development' },
      },
      'synthesize': {
        'button': 'Start Synthesis',
        'processing': 'Processing...',
      },
      'waveform': {
        'label': 'Audio Waveform',
        'synthesizing': 'Generating audio...',
        'completed': 'Synthesis complete, ready to play',
        'ready': 'Ready, waiting for synthesis',
        'waiting': 'Waiting for audio...',
      },
      'player': {
        'label': 'Audio Player',
        'description': 'Preview synthesis result',
        'noAudio': 'Audio will be available after synthesis',
      },
      'download': {
        'label': 'Download Audio',
        'description': 'Save to local device',
        'button': 'Download',
        'disabled': 'Available after synthesis',
      },
      'error': {
        'title': 'Synthesis Failed',
      },
      'footer': 'TTS Studio © 2026 — Powered by MOSS-TTS-Nano',
    },
  },
};

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: 'zh',
    fallbackLng: 'zh',
    interpolation: {
      escapeValue: false,
    },
  });

export default i18n;
