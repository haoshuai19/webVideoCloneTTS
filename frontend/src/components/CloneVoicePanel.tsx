import { useState, useRef, useCallback } from 'react';
import { cloneVoice } from '../services/api';

interface CloneVoiceProps {
  onSuccess: (voiceId: string, voiceName: string) => void;
  onError: (error: string) => void;
}

export default function CloneVoicePanel({ onSuccess, onError }: CloneVoiceProps) {
  const [voiceName, setVoiceName] = useState('');
  const [referenceText, setReferenceText] = useState('');
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [isCloning, setIsCloning] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setAudioFile(file);
    }
  }, []);

  const handleClone = useCallback(async () => {
    if (!audioFile || !voiceName.trim()) {
      onError('请上传音频文件并填写音色名称');
      return;
    }
    setIsCloning(true);
    try {
      const result = await cloneVoice(audioFile, voiceName, referenceText);
      onSuccess(`cloned_${result.taskId}`, voiceName);
    } catch (err) {
      onError(err instanceof Error ? err.message : '克隆失败');
    } finally {
      setIsCloning(false);
    }
  }, [audioFile, voiceName, referenceText, onSuccess, onError]);

  return (
    <div className="space-y-8">
      <section className="bg-white rounded-2xl shadow-lg shadow-gray-200/50 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-100">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-amber-100 rounded-xl flex items-center justify-center">
              <svg className="w-5 h-5 text-amber-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
            </div>
            <div>
              <h2 className="text-lg font-semibold text-gray-900">克隆信息</h2>
              <p className="text-xs text-gray-500">填写音色名称和参考文本</p>
            </div>
          </div>
        </div>
        <div className="p-6 space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">音色名称</label>
            <input
              type="text"
              value={voiceName}
              onChange={(e) => setVoiceName(e.target.value)}
              placeholder="例如：我的声音"
              disabled={isCloning}
              className="w-full px-4 py-3 bg-gray-50 border-2 border-gray-200 rounded-xl text-gray-900 text-base leading-relaxed focus:outline-none focus:border-amber-400 focus:ring-4 focus:ring-amber-400/20 transition-all placeholder:text-gray-400 disabled:opacity-50 disabled:cursor-not-allowed"
              aria-label="音色名称"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              参考文本<span className="text-gray-400 font-normal">(可选)</span>
            </label>
            <input
              type="text"
              value={referenceText}
              onChange={(e) => setReferenceText(e.target.value)}
              placeholder="音频中对应的文字内容"
              disabled={isCloning}
              className="w-full px-4 py-3 bg-gray-50 border-2 border-gray-200 rounded-xl text-gray-900 text-base leading-relaxed focus:outline-none focus:border-amber-400 focus:ring-4 focus:ring-amber-400/20 transition-all placeholder:text-gray-400 disabled:opacity-50 disabled:cursor-not-allowed"
              aria-label="参考文本"
            />
          </div>
        </div>
      </section>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <section className="bg-white rounded-2xl shadow-lg shadow-gray-200/50 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-100">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-purple-100 rounded-xl flex items-center justify-center">
                <svg className="w-5 h-5 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
              </div>
              <div>
                <h2 className="text-lg font-semibold text-gray-900">参考音频</h2>
                <p className="text-xs text-gray-500">上传参考音频文件</p>
              </div>
            </div>
          </div>
          <div className="p-6">
            <div
              className={`border-2 border-dashed rounded-xl p-8 text-center transition-all cursor-pointer ${
                audioFile
                  ? 'border-amber-400 bg-amber-50'
                  : 'border-gray-300 hover:border-amber-400 hover:bg-gray-50'
              } ${isCloning ? 'opacity-50 cursor-not-allowed' : ''}`}
              onClick={() => !isCloning && fileInputRef.current?.click()}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept="audio/*"
                onChange={handleFileChange}
                className="hidden"
                disabled={isCloning}
              />
              {audioFile ? (
                <div className="flex flex-col items-center gap-2">
                  <div className="w-12 h-12 bg-amber-100 rounded-full flex items-center justify-center">
                    <svg className="w-6 h-6 text-amber-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <p className="text-sm font-medium text-gray-900">{audioFile.name}</p>
                  <p className="text-xs text-gray-500">{(audioFile.size / 1024 / 1024).toFixed(2)} MB</p>
                </div>
              ) : (
                <div className="flex flex-col items-center gap-2">
                  <svg className="w-12 h-12 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                  <p className="text-sm text-gray-500">点击上传音频文件</p>
                  <p className="text-xs text-gray-400">支持 WAV, MP3, M4A (建议 10 秒以上清晰人声)</p>
                </div>
              )}
            </div>
          </div>
        </section>

        <section className="bg-white rounded-2xl shadow-lg shadow-gray-200/50 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-100">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-blue-100 rounded-xl flex items-center justify-center">
                <svg className="w-5 h-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </div>
              <div>
                <h2 className="text-lg font-semibold text-gray-900">克隆设置</h2>
                <p className="text-xs text-gray-500">克隆完成后将声音应用到合成</p>
              </div>
            </div>
          </div>
          <div className="p-6 space-y-4 text-sm text-gray-500">
            <div className="p-4 bg-gray-50 rounded-xl">
              <p className="font-medium text-gray-700 mb-1">输出说明</p>
              <p className="text-gray-500">克隆完成后自动切换到合成页面，您可以选择刚克隆的音色进行语音合成。</p>
            </div>
            <div className="p-4 bg-amber-50 border border-amber-200 rounded-xl">
              <p className="font-medium text-amber-800 mb-1">💡 提示</p>
              <p className="text-amber-700">建议使用 10-15 秒的清晰人声，环境噪音越小，克隆效果越好。</p>
            </div>
          </div>
        </section>
      </div>

      <div className="flex justify-center">
        {isCloning ? (
          <div className="w-full max-w-md mx-auto space-y-4 py-2">
            <div className="flex items-center gap-3 justify-center">
              <svg className="animate-spin h-5 w-5 text-indigo-500" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              <span className="text-lg font-semibold text-gray-900">正在提取音色特征...</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
              <div className="bg-gradient-to-r from-indigo-500 to-purple-500 h-full rounded-full animate-pulse" style={{width: '60%'}}></div>
            </div>
            <p className="text-sm text-gray-400 text-center">正在编码参考音频，请稍候</p>
          </div>
        ) : (
          <div className="flex justify-center py-4">
            <button
              onClick={handleClone}
              disabled={!audioFile || !voiceName.trim()}
              className={`group relative px-12 py-4 text-lg font-semibold rounded-2xl transition-all duration-300 ${
                !audioFile || !voiceName.trim()
                  ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                  : 'bg-gradient-to-r from-indigo-500 to-purple-500 text-white shadow-xl shadow-indigo-500/30 hover:shadow-2xl hover:shadow-indigo-500/40 hover:-translate-y-0.5 active:translate-y-0'
              }`}
            >
              <span className="flex items-center gap-2">
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                </svg>
                开始克隆
              </span>
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
