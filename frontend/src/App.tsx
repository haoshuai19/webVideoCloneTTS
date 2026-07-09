import { useState, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import VoiceSelector from './components/VoiceSelector';
import AudioControls from './components/AudioControls';
import FormatSelector from './components/FormatSelector';
import WaveformPreview from './components/WaveformPreview';
import AudioPlayer from './components/AudioPlayer';
import DownloadButton from './components/DownloadButton';
import CloneVoicePanel from './components/CloneVoicePanel';
import { useSynthesis } from './hooks/useSynthesis';

type GenderFilter = 'all' | 'male' | 'female';
type AgeFilter = 'all' | 'child' | 'young' | 'middle' | 'old';
type AppMode = 'tts' | 'clone';

interface ClonedVoice {
  id: string;
  name: string;
  gender: 'male' | 'female' | 'custom';
  age_group: 'child' | 'young' | 'middle' | 'old' | 'custom';
  language: 'zh' | 'en' | 'jp' | 'custom';
  cloned: true;
}

export default function App() {
  const { t, i18n } = useTranslation();
  const [mode, setMode] = useState<AppMode>('tts');
  const [text, setText] = useState('');
  const [selectedVoiceId, setSelectedVoiceId] = useState('xiaoyuan');
  const [genderFilter, setGenderFilter] = useState<GenderFilter>('all');
  const [ageFilter, setAgeFilter] = useState<AgeFilter>('all');
  const [speed, setSpeed] = useState(1.0);
  const [pitch, setPitch] = useState(0);
  const [volume, setVolume] = useState(100);
  const [format, setFormat] = useState('mp3');
  const [sampleRate, setSampleRate] = useState(16000);
  const [clonedVoices, setClonedVoices] = useState<ClonedVoice[]>([]);

  const {
    status,
    audioUrl,
    waveform,
    error,
    synthesize: doSynthesize,
  } = useSynthesis();

  const [isPlaying, setIsPlaying] = useState(false);

  const handleFormatChange = useCallback((formatId: string, rate: number) => {
    setFormat(formatId);
    setSampleRate(rate);
  }, []);

  const handleSynthesize = useCallback(() => {
    if (!text.trim()) return;
    doSynthesize(text, selectedVoiceId, speed, pitch, volume, format, sampleRate);
    setIsPlaying(false);
  }, [text, selectedVoiceId, speed, pitch, volume, format, sampleRate, doSynthesize]);

  const handleCloneSuccess = useCallback((voiceId: string, voiceName: string) => {
    setClonedVoices(prev => [...prev, {
      id: voiceId,
      name: voiceName,
      gender: 'custom',
      age_group: 'custom',
      language: 'custom',
      cloned: true,
    }]);
    setSelectedVoiceId(voiceId);
    setMode('tts');
  }, []);

  const handleCloneError = useCallback((err: string) => {
    console.error('Clone error:', err);
  }, []);

  const handlePlay = useCallback(() => setIsPlaying(true), []);
  const handlePause = useCallback(() => setIsPlaying(false), []);
  const handleEnded = useCallback(() => setIsPlaying(false), []);

  const isSynthesizing = status === 'synthesizing';
  const isCompleted = status === 'completed';
  const isFailed = status === 'failed';
  const charCount = text.length;

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-amber-50/30">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-gray-200/50 sticky top-0 z-50">
        <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 tracking-tight">
              {t('title')}
            </h1>
            <p className="text-sm text-gray-500 mt-0.5">{t('subtitle')}</p>
          </div>
          <div className="flex items-center gap-3">
            {/* Mode Toggle */}
            <div className="flex bg-gray-100 rounded-lg p-1 mr-3">
              <button
                onClick={() => setMode('tts')}
                className={`px-4 py-1.5 text-sm font-medium rounded-md transition-all ${
                  mode === 'tts'
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                语音合成
              </button>
              <button
                onClick={() => setMode('clone')}
                className={`px-4 py-1.5 text-sm font-medium rounded-md transition-all ${
                  mode === 'clone'
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                声音克隆
              </button>
            </div>

            {['zh', 'en'].map((lang) => (
              <button
                key={lang}
                onClick={() => i18n.changeLanguage(lang)}
                className={`px-4 py-2 text-sm font-medium rounded-lg transition-all ${
                  i18n.language === lang
                    ? 'bg-amber-500 text-white shadow-lg shadow-amber-500/25'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {lang === 'zh' ? '中文' : 'English'}
              </button>
            ))}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-5xl mx-auto px-6 py-8 space-y-8">
        {mode === 'tts' ? (
          <>
            {/* Text Input Section */}
            <section className="bg-white rounded-2xl shadow-lg shadow-gray-200/50 overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-100">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-amber-100 rounded-xl flex items-center justify-center">
                      <svg className="w-5 h-5 text-amber-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                    </div>
                    <div>
                      <h2 className="text-lg font-semibold text-gray-900">{t('textInput.label')}</h2>
                      <p className="text-xs text-gray-500">{t('textInput.description')}</p>
                    </div>
                  </div>
                  <span className={`text-sm font-medium px-3 py-1 rounded-full ${
                    charCount > 4500 ? 'bg-red-100 text-red-600' : 'bg-gray-100 text-gray-600'
                  }`}>
                    {t('textInput.counter', { count: charCount })}
                  </span>
                </div>
              </div>
              <div className="p-6">
                <textarea
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  placeholder={t('textInput.placeholder')}
                  rows={8}
                  className="w-full px-4 py-3 bg-gray-50 border-2 border-gray-200 rounded-xl text-gray-900 text-base leading-relaxed resize-none focus:outline-none focus:border-amber-400 focus:ring-4 focus:ring-amber-400/20 transition-all placeholder:text-gray-400"
                  aria-label={t('textInput.label')}
                />
              </div>
            </section>

            {/* Voice & Controls Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Voice Selector */}
              <VoiceSelector
                selectedVoiceId={selectedVoiceId}
                onSelectVoice={setSelectedVoiceId}
                gender={genderFilter}
                onGenderChange={setGenderFilter}
                age={ageFilter}
                onAgeChange={setAgeFilter}
                clonedVoices={clonedVoices}
              />

              {/* Audio Controls + Format */}
              <div className="space-y-6">
                <AudioControls
                  speed={speed}
                  onSpeedChange={setSpeed}
                  pitch={pitch}
                  onPitchChange={setPitch}
                  volume={volume}
                  onVolumeChange={setVolume}
                />
                <FormatSelector
                  format={format}
                  sampleRate={sampleRate}
                  onSelectFormat={handleFormatChange}
                />
              </div>
            </div>

            {/* Synthesize Button */}
            <div className="flex justify-center py-4">
              <button
                onClick={handleSynthesize}
                disabled={!text.trim() || isSynthesizing}
                className={`group relative px-12 py-4 text-lg font-semibold rounded-2xl transition-all duration-300 ${
                  !text.trim() || isSynthesizing
                    ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                    : 'bg-gradient-to-r from-amber-500 to-orange-500 text-white shadow-xl shadow-amber-500/30 hover:shadow-2xl hover:shadow-amber-500/40 hover:-translate-y-0.5 active:translate-y-0'
                }`}
              >
                {isSynthesizing ? (
                  <span className="flex items-center gap-3">
                    <svg className="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    {t('synthesize.processing')}
                  </span>
                ) : (
                  <span className="flex items-center gap-2">
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                    {t('synthesize.button')}
                  </span>
                )}
              </button>
            </div>

            {/* Error Message */}
            {isFailed && error && (
              <div className="bg-red-50 border-2 border-red-200 rounded-2xl p-5">
                <div className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <div>
                    <p className="font-semibold text-red-800">{t('error.title')}</p>
                    <p className="text-sm text-red-600 mt-1">{error}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Waveform Preview */}
            <WaveformPreview
              waveform={waveform}
              status={status}
              isPlaying={isPlaying}
            />

            {/* Audio Player */}
            <AudioPlayer
              audioUrl={audioUrl}
              isPlaying={isPlaying}
              onPlay={handlePlay}
              onPause={handlePause}
              onEnded={handleEnded}
            />

            {/* Download Button */}
            <DownloadButton
              audioUrl={audioUrl}
              format={format}
              sampleRate={sampleRate}
              disabled={!isCompleted}
            />
          </>
        ) : (
          <CloneVoicePanel
            onSuccess={handleCloneSuccess}
            onError={handleCloneError}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="text-center py-8 text-sm text-gray-400">
        <p>{t('footer')}</p>
      </footer>
    </div>
  );
}
