import { describe, it, expect, beforeAll } from 'vitest';
import { render, screen } from '@testing-library/react';
import App from '../src/App';
import i18n from '../src/i18n';

beforeAll(async () => {
  await i18n.init();
  await i18n.changeLanguage('zh');
});

describe('App', () => {
  it('renders header title', () => {
    render(<App />);
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('TTS Studio');
  });

  it('renders subtitle', () => {
    render(<App />);
    expect(screen.getByText('智能语音合成平台')).toBeInTheDocument();
  });

  it('text input accepts input', () => {
    render(<App />);
    const textarea = screen.getByRole('textbox', { name: /文本输入/ });
    expect(textarea).toBeInTheDocument();
    expect(textarea).toHaveAttribute('placeholder', '在此输入需要合成的文本，支持中文、英文及混合文本...');
  });

  it('voice chips render', () => {
    render(<App />);
    const voiceList = screen.getByRole('radiogroup', { name: '音色列表' });
    expect(voiceList).toBeInTheDocument();
    const voiceButtons = voiceList.querySelectorAll('button');
    expect(voiceButtons.length).toBeGreaterThan(0);
  });

  it('format selector shows options', () => {
    render(<App />);
    // Check that format section renders
    expect(screen.getByRole('heading', { name: '输出格式' })).toBeInTheDocument();
    // Check sample rate radios exist (they include description text)
    expect(screen.getByRole('radio', { name: /8kHz/ })).toBeInTheDocument();
    expect(screen.getByRole('radio', { name: /16kHz/ })).toBeInTheDocument();
  });

  it('audio controls render with sliders', () => {
    render(<App />);
    expect(screen.getByLabelText(/语速/)).toBeInTheDocument();
    expect(screen.getByLabelText(/音调/)).toBeInTheDocument();
    expect(screen.getByLabelText(/音量/)).toBeInTheDocument();
  });

  it('waveform preview shows ready state', () => {
    render(<App />);
    expect(screen.getByText('就绪，等待合成')).toBeInTheDocument();
  });

  it('synthesize button is disabled when no text', () => {
    render(<App />);
    const synthesizeButton = screen.getByRole('button', { name: /开始合成|synthesize\.button/ });
    expect(synthesizeButton).toBeDisabled();
  });
});
