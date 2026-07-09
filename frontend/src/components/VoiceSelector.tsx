import { useState, useEffect } from 'react';

interface Voice {
  id: string;
  name: string;
  gender: 'male' | 'female' | 'custom';
  age_group: 'child' | 'young' | 'middle' | 'old' | 'custom';
  language: 'zh' | 'en' | 'jp' | 'custom';
  cloned?: boolean;
}

const DEFAULT_VOICES: Voice[] = [
  { id: 'xiaoyuan', name: '小媛', gender: 'female', age_group: 'young', language: 'zh' },
  { id: 'xiaobei', name: '小贝', gender: 'female', age_group: 'young', language: 'zh' },
  { id: 'xiaogang', name: '小刚', gender: 'male', age_group: 'young', language: 'zh' },
  { id: 'xiaoxue', name: '小雪', gender: 'female', age_group: 'middle', language: 'zh' },
  { id: 'laoli', name: '老李', gender: 'male', age_group: 'old', language: 'zh' },
  { id: 'xiaoming', name: '小明', gender: 'male', age_group: 'child', language: 'zh' },
];

type Gender = 'all' | 'male' | 'female';
type Age = 'all' | 'child' | 'young' | 'middle' | 'old';

interface VoiceSelectorProps {
  selectedVoiceId: string;
  onSelectVoice: (voiceId: string) => void;
  gender: Gender;
  onGenderChange: (gender: Gender) => void;
  age: Age;
  onAgeChange: (age: Age) => void;
  clonedVoices?: Voice[];
}

function GenderIcon({ gender }: { gender: Voice['gender'] }) {
  if (gender === 'custom') {
    return (
      <svg className="w-4 h-4 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
        <circle cx="12" cy="12" r="3" strokeWidth={2} />
      </svg>
    );
  }
  return gender === 'male' ? (
    <svg className="w-4 h-4 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <circle cx="10" cy="14" r="5" strokeWidth={2} />
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 5l-5.4 5.4M19 5h-4M19 5v4" />
    </svg>
  ) : (
    <svg className="w-4 h-4 text-pink-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <circle cx="12" cy="9" r="5" strokeWidth={2} />
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 14v7M9 18h6" />
    </svg>
  );
}

const ageLabels: Record<Age, string> = {
  all: '全部',
  child: '儿童',
  young: '青年',
  middle: '中年',
  old: '老年',
};

export default function VoiceSelector({
  selectedVoiceId,
  onSelectVoice,
  gender,
  onGenderChange,
  age,
  onAgeChange,
  clonedVoices = [],
}: VoiceSelectorProps) {
  const [voices, setVoices] = useState<Voice[]>(DEFAULT_VOICES);

  useEffect(() => {
      fetch('/api/voices')
        .then((r) => r.json())
        .then((d) => {
          if (d.success && d.data) {
            setVoices(d.data.map((v: any) => ({
              id: v.id,
              name: v.name,
              gender: v.gender,
              age_group: v.age_group || v.age,
              language: v.language,
              cloned: v.cloned || false,
            })));
          }
        })
        .catch(() => {});
    }, []);

  const allVoices = [...voices, ...clonedVoices].filter(
    (v, i, arr) => arr.findIndex(x => x.id === v.id) === i
  );
  const filteredVoices = allVoices.filter((v) => {
    if (gender !== 'all' && v.gender !== gender && v.gender !== 'custom') return false;
    if (age !== 'all' && v.age_group !== age && v.age_group !== 'custom') return false;
    return true;
  });

  return (
    <section className="bg-white rounded-2xl shadow-lg shadow-gray-200/50 overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-100">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-purple-100 rounded-xl flex items-center justify-center">
            <svg className="w-5 h-5 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
            </svg>
          </div>
          <div>
            <h2 className="text-lg font-semibold text-gray-900">音色选择</h2>
            <p className="text-xs text-gray-500">选择发音人和筛选条件</p>
          </div>
        </div>
      </div>

      <div className="p-6 space-y-5">
        {/* Gender Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">性别筛选</label>
          <div className="flex gap-2">
            {([
              { key: 'all' as Gender, label: '全部', icon: '' },
              { key: 'male' as Gender, label: '男声', icon: '♂️' },
              { key: 'female' as Gender, label: '女声', icon: '♀️' },
            ]).map((g) => (
              <button
                key={g.key}
                onClick={() => onGenderChange(g.key)}
                className={`flex-1 px-4 py-3 text-sm font-medium rounded-xl transition-all ${
                  gender === g.key
                    ? 'bg-gradient-to-r from-amber-500 to-orange-500 text-white shadow-lg shadow-amber-500/25'
                    : 'bg-gray-50 text-gray-600 hover:bg-gray-100 border-2 border-gray-200'
                }`}
              >
                <span className="mr-1.5">{g.icon}</span>
                {g.label}
              </button>
            ))}
          </div>
        </div>

        {/* Age Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">年龄筛选</label>
          <div className="flex gap-2 flex-wrap">
            {(['all', 'child', 'young', 'middle', 'old'] as Age[]).map((a) => (
              <button
                key={a}
                onClick={() => onAgeChange(a)}
                className={`px-4 py-2 text-sm font-medium rounded-xl transition-all ${
                  age === a
                    ? 'bg-gradient-to-r from-amber-500 to-orange-500 text-white shadow-lg shadow-amber-500/25'
                    : 'bg-gray-50 text-gray-600 hover:bg-gray-100 border-2 border-gray-200'
                }`}
              >
                {ageLabels[a]}
              </button>
            ))}
          </div>
        </div>

        {/* Voice Grid */}
        <div className="grid grid-cols-2 gap-3" role="radiogroup" aria-label="音色列表">
          {filteredVoices.map((voice) => (
            <button
              key={voice.id}
              onClick={() => onSelectVoice(voice.id)}
              className={`relative p-4 rounded-xl text-left transition-all duration-200 ${
                selectedVoiceId === voice.id
                  ? 'bg-gradient-to-br from-amber-50 to-orange-50 border-2 border-amber-400 shadow-lg shadow-amber-100'
                  : 'bg-gray-50 border-2 border-gray-200 hover:border-gray-300 hover:bg-gray-100'
              }`}
            >
              {selectedVoiceId === voice.id && (
                <div className="absolute top-2 right-2 w-5 h-5 bg-amber-500 rounded-full flex items-center justify-center">
                  <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
              )}
              <div className="flex items-center gap-2 mb-2">
                <GenderIcon gender={voice.gender} />
                <span className="text-base font-semibold text-gray-900">{voice.name}</span>
                {voice.cloned && (
                  <span className="text-xs px-1.5 py-0.5 rounded-full bg-green-100 text-green-700 font-medium">克隆</span>
                )}
              </div>
              <div className="flex items-center gap-2">
                <span className={`text-xs px-2 py-0.5 rounded-full ${
                  selectedVoiceId === voice.id ? 'bg-amber-200/50 text-amber-700' : 'bg-gray-200 text-gray-600'
                }`}>
                  {voice.gender === 'male' ? '男' : voice.gender === 'female' ? '女' : '自定义'} · {(voice.age_group === 'custom' ? '自定义' : ageLabels[voice.age_group as Age])}
                </span>
                <span className={`text-xs px-2 py-0.5 rounded-full font-mono ${
                  selectedVoiceId === voice.id ? 'bg-amber-200/50 text-amber-700' : 'bg-gray-200 text-gray-600'
                }`}>
                  {voice.language === 'custom' ? 'CUSTOM' : voice.language === 'jp' ? 'JP' : voice.language.toUpperCase()}
                </span>
              </div>
            </button>
          ))}
        </div>

        {filteredVoices.length === 0 && (
          <div className="text-center py-8 text-gray-400">
            <svg className="w-12 h-12 mx-auto mb-3 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p className="text-sm">没有匹配的音色，请调整筛选条件</p>
          </div>
        )}
      </div>
    </section>
  );
}
