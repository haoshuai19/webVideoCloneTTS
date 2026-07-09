import { test, expect } from '@playwright/test';

test.describe('TTS Studio E2E', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('loads the application', async ({ page }) => {
    await expect(page).toHaveTitle(/TTS Studio/);
    await expect(page.getByRole('heading', { name: 'TTS Studio' })).toBeVisible();
  });

  test('displays all form sections', async ({ page }) => {
    await expect(page.getByRole('textbox', { name: /文本输入/ })).toBeVisible();
    await expect(page.getByRole('radiogroup', { name: '音色列表' })).toBeVisible();
    await expect(page.getByLabel(/音频参数/)).toBeVisible();
    await expect(page.getByRole('radiogroup', { name: '音频格式' })).toBeVisible();
  });

  test('user can type into text input', async ({ page }) => {
    const textarea = page.getByRole('textbox', { name: /文本输入/ });
    await textarea.fill('你好世界');
    await expect(textarea).toHaveValue('你好世界');
  });

  test('character counter updates', async ({ page }) => {
    const textarea = page.getByRole('textbox', { name: /文本输入/ });
    await textarea.fill('测试文本');
    const counter = page.getByText('4 / 5000');
    await expect(counter).toBeVisible();
  });

  test('voice selector shows voices', async ({ page }) => {
    const voiceList = page.getByRole('radiogroup', { name: '音色列表' });
    await expect(voiceList).toBeVisible();
    await expect(page.getByText('小媛')).toBeVisible();
    await expect(page.getByText('小贝')).toBeVisible();
  });

  test('format selector displays all options', async ({ page }) => {
    const formatGroup = page.getByRole('radiogroup', { name: '音频格式' });
    await expect(formatGroup.getByRole('radio', { name: 'MP3' })).toBeVisible();
    await expect(formatGroup.getByRole('radio', { name: 'WAV' })).toBeVisible();
    await expect(formatGroup.getByRole('radio', { name: 'PCM' })).toBeVisible();
    await expect(page.getByRole('radio', { name: '8kHz' })).toBeVisible();
    await expect(page.getByRole('radio', { name: '16kHz' })).toBeVisible();
  });

  test('audio controls have sliders', async ({ page }) => {
    await expect(page.getByLabel(/语速/)).toBeVisible();
    await expect(page.getByLabel(/音调/)).toBeVisible();
    await expect(page.getByLabel(/音量/)).toBeVisible();
  });

  test('waveform preview shows ready state', async ({ page }) => {
    await expect(page.getByText('就绪，等待合成')).toBeVisible();
  });

  test('synthesize button disabled without text', async ({ page }) => {
    const button = page.getByRole('button', { name: /开始合成/ });
    await expect(button).toBeDisabled();
  });
});
