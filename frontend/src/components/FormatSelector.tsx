interface FormatOption {
  id: string;
  label: string;
  description: string;
  defaultSampleRate: number;
}

const FORMATS: FormatOption[] = [
  { id: 'mp3', label: 'MP3', description: '压缩格式，文件较小', defaultSampleRate: 16000 },
  { id: 'wav', label: 'WAV', description: '无损格式，音质最佳', defaultSampleRate: 16000 },
  { id: 'pcm', label: 'PCM', description: '原始音频，适合开发', defaultSampleRate: 16000 },
];

interface FormatSelectorProps {
  format: string;
  sampleRate: number;
  onSelectFormat: (formatId: string, sampleRate: number) => void;
}

export default function FormatSelector({ format, sampleRate, onSelectFormat }: FormatSelectorProps) {
  const sampleRates = [
    { value: 8000, label: '8kHz', desc: '电话质量' },
    { value: 16000, label: '16kHz', desc: '语音识别' },
  ];

  return (
    <section className="bg-white rounded-2xl shadow-lg shadow-gray-200/50 overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-100">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-green-100 rounded-xl flex items-center justify-center">
            <svg className="w-5 h-5 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
          </div>
          <div>
            <h2 className="text-lg font-semibold text-gray-900">输出格式</h2>
            <p className="text-xs text-gray-500">选择音频格式和采样率</p>
          </div>
        </div>
      </div>
      <div className="p-6 space-y-5">
        {/* Format Options */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">音频格式</label>
          <div className="grid grid-cols-3 gap-3" role="radiogroup" aria-label="音频格式">
            {FORMATS.map((fmt) => {
              const isActive = format === fmt.id;
              return (
                <button
                  key={fmt.id}
                  onClick={() => onSelectFormat(fmt.id, fmt.defaultSampleRate)}
                  role="radio"
                  aria-checked={isActive}
                  className={`relative p-4 rounded-xl text-center transition-all duration-200 ${
                    isActive
                      ? 'bg-gradient-to-br from-amber-50 to-orange-50 border-2 border-amber-400 shadow-lg shadow-amber-100'
                      : 'bg-gray-50 border-2 border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className={`text-lg font-bold mb-1 ${isActive ? 'text-amber-600' : 'text-gray-700'}`}>
                    {fmt.label}
                  </div>
                  <div className={`text-xs ${isActive ? 'text-amber-500' : 'text-gray-500'}`}>
                    {fmt.description}
                  </div>
                  {isActive && (
                    <div className="absolute -top-2 -right-2 w-6 h-6 bg-amber-500 rounded-full flex items-center justify-center">
                      <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                      </svg>
                    </div>
                  )}
                </button>
              );
            })}
          </div>
        </div>

        {/* Sample Rate */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">采样率</label>
          <div className="grid grid-cols-2 gap-3" role="radiogroup" aria-label="采样率选择">
            {sampleRates.map((rate) => {
              const isActive = sampleRate === rate.value;
              return (
                <button
                  key={rate.value}
                  onClick={() => onSelectFormat(format, rate.value)}
                  role="radio"
                  aria-checked={isActive}
                  className={`p-4 rounded-xl text-center transition-all duration-200 ${
                    isActive
                      ? 'bg-gradient-to-br from-amber-50 to-orange-50 border-2 border-amber-400 shadow-lg shadow-amber-100'
                      : 'bg-gray-50 border-2 border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className={`text-lg font-bold font-mono ${isActive ? 'text-amber-600' : 'text-gray-700'}`}>
                    {rate.label}
                  </div>
                  <div className={`text-xs ${isActive ? 'text-amber-500' : 'text-gray-500'}`}>
                    {rate.desc}
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}
