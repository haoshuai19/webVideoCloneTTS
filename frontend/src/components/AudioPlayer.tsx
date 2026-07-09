import { useRef, useEffect, useState, useCallback } from 'react';
import { useTranslation } from 'react-i18next';

interface AudioPlayerProps {
  audioUrl: string | null;
  isPlaying: boolean;
  onPlay?: () => void;
  onPause?: () => void;
  onEnded?: () => void;
}

export default function AudioPlayer({ audioUrl, isPlaying, onPlay, onPause, onEnded }: AudioPlayerProps) {
  const { t } = useTranslation();
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [audioError, setAudioError] = useState<string | null>(null);

  const buildAudioUrl = useCallback((url: string) => {
    const base = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    return base.replace(/\/+$/, '') + '/' + url.replace(/^\//, '');
  }, []);

  useEffect(() => {
    if (audioRef.current && audioUrl) {
      setAudioError(null);
      audioRef.current.src = buildAudioUrl(audioUrl);
      audioRef.current.load();
    }
  }, [audioUrl, buildAudioUrl]);

  useEffect(() => {
    if (isPlaying && audioRef.current) {
      audioRef.current.play().catch(() => {
        setAudioError('浏览器已阻止自动播放，请点击播放按钮');
      });
    } else if (audioRef.current) {
      audioRef.current.pause();
    }
  }, [isPlaying]);

  const handlePlayPause = () => {
    if (isPlaying) {
      onPause?.();
    } else {
      setAudioError(null);
      onPlay?.();
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (!audioUrl) {
    return (
      <section className="bg-white rounded-2xl shadow-lg shadow-gray-200/50 overflow-hidden">
        <div className="px-6 py-8 text-center text-gray-400">
          <svg className="w-12 h-12 mx-auto mb-3 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p className="text-sm">{t('player.noAudio')}</p>
        </div>
      </section>
    );
  }

  return (
    <section className="bg-white rounded-2xl shadow-lg shadow-gray-200/50 overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-100">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-pink-100 rounded-xl flex items-center justify-center">
            <svg className="w-5 h-5 text-pink-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div>
            <h2 className="text-lg font-semibold text-gray-900">{t('player.label')}</h2>
            <p className="text-xs text-gray-500">{t('player.description')}</p>
          </div>
        </div>
      </div>
      <div className="p-6">
        <div className="flex items-center gap-4">
          <button
            onClick={handlePlayPause}
            className="w-14 h-14 bg-gradient-to-br from-amber-500 to-orange-500 rounded-2xl flex items-center justify-center text-white shadow-lg shadow-amber-500/30 hover:shadow-xl hover:shadow-amber-500/40 transition-all hover:-translate-y-0.5 active:translate-y-0"
          >
            {isPlaying ? (
              <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z" />
              </svg>
            ) : (
              <svg className="w-6 h-6 ml-1" fill="currentColor" viewBox="0 0 24 24">
                <path d="M8 5v14l11-7z" />
              </svg>
            )}
          </button>

          <div className="flex-1 space-y-2">
            <div className="flex items-center justify-between text-sm text-gray-500">
              <span className="font-mono">{formatTime(currentTime)}</span>
              <span className="font-mono">{formatTime(duration)}</span>
            </div>
            <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-amber-500 to-orange-500 rounded-full transition-all duration-150"
                style={{ width: duration ? `${(currentTime / duration) * 100}%` : '0%' }}
              />
            </div>
          </div>
        </div>

        {audioError && (
          <p className="text-sm text-red-500 mt-2">{audioError}</p>
        )}
        <audio
          ref={audioRef}
          onTimeUpdate={(e) => setCurrentTime((e.target as HTMLAudioElement).currentTime)}
          onLoadedMetadata={(e) => setDuration((e.target as HTMLAudioElement).duration)}
          onEnded={onEnded}
          onError={() => setAudioError('音频加载失败，请检查后端服务或尝试下载文件')}
          className="hidden"
        />
      </div>
    </section>
  );
}
