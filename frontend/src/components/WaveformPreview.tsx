import { useTranslation } from 'react-i18next';

interface WaveformPreviewProps {
  waveform: number[] | null;
  status: string;
  isPlaying: boolean;
}

export default function WaveformPreview({ waveform, status, isPlaying }: WaveformPreviewProps) {
  const { t } = useTranslation();
  const isSynthesizing = status === 'synthesizing';
  const isCompleted = status === 'completed';

  return (
    <section className="bg-white rounded-2xl shadow-lg shadow-gray-200/50 overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-100">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-indigo-100 rounded-xl flex items-center justify-center">
            <svg className="w-5 h-5 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
            </svg>
          </div>
          <div>
            <h2 className="text-lg font-semibold text-gray-900">{t('waveform.label')}</h2>
            <p className="text-xs text-gray-500">
              {isSynthesizing ? t('waveform.synthesizing') : isCompleted ? t('waveform.completed') : t('waveform.ready')}
            </p>
          </div>
        </div>
      </div>
      <div className="p-6">
        <div className="h-24 bg-gray-50 rounded-xl overflow-hidden relative">
          {isSynthesizing ? (
            <div className="absolute inset-0 flex items-center justify-center gap-1">
              {Array.from({ length: 40 }).map((_, i) => (
                <div
                  key={i}
                  className="w-2 bg-amber-400 rounded-full animate-pulse"
                  style={{
                    height: `${20 + Math.random() * 60}%`,
                    animationDelay: `${i * 0.05}s`,
                    opacity: 0.6 + Math.random() * 0.4,
                  }}
                />
              ))}
            </div>
          ) : waveform ? (
            <div className="absolute inset-0 flex items-center gap-0.5 px-4">
              {waveform.map((value, index) => (
                <div
                  key={index}
                  className={`flex-1 rounded-full transition-all duration-300 ${
                    isPlaying
                      ? 'bg-gradient-to-t from-amber-500 to-orange-400'
                      : 'bg-gradient-to-t from-amber-400 to-amber-300'
                  }`}
                  style={{
                    height: `${value * 80}%`,
                    opacity: 0.7 + value * 0.3,
                  }}
                />
              ))}
            </div>
          ) : (
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="flex items-center gap-3 text-gray-300">
                <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
                </svg>
                <span className="text-sm">{t('waveform.waiting')}</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
