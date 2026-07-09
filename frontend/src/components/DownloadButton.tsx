import { useTranslation } from 'react-i18next';

interface DownloadButtonProps {
  audioUrl: string | null;
  format: string;
  sampleRate: number;
  disabled: boolean;
}

export default function DownloadButton({ audioUrl, format, sampleRate, disabled }: DownloadButtonProps) {
  const { t } = useTranslation();
  const handleDownload = () => {
    if (!audioUrl) return;
    const base = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/+$/, '');
    const fullUrl = base + '/' + audioUrl.replace(/^\//, '');
    const link = document.createElement('a');
    link.href = fullUrl;
    link.download = `tts_${Date.now()}.${format}`;
    link.click();
  };

  return (
    <section className="bg-white rounded-2xl shadow-lg shadow-gray-200/50 overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-100">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-emerald-100 rounded-xl flex items-center justify-center">
            <svg className="w-5 h-5 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
          </div>
          <div>
            <h2 className="text-lg font-semibold text-gray-900">{t('download.label')}</h2>
            <p className="text-xs text-gray-500">{t('download.description')}</p>
          </div>
        </div>
      </div>
      <div className="p-6">
        <button
          onClick={handleDownload}
          disabled={disabled}
          className={`w-full flex items-center justify-center gap-3 px-6 py-4 text-lg font-semibold rounded-xl transition-all duration-300 ${
            disabled
              ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
              : 'bg-gradient-to-r from-gray-800 to-gray-900 text-white shadow-lg shadow-gray-900/20 hover:shadow-xl hover:shadow-gray-900/30 hover:-translate-y-0.5 active:translate-y-0'
          }`}
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          <span>
            {disabled ? (
              t('download.disabled')
            ) : (
              <>
                {t('download.button')} {format.toUpperCase()} · {sampleRate / 1000}kHz
              </>
            )}
          </span>
        </button>
      </div>
    </section>
  );
}
