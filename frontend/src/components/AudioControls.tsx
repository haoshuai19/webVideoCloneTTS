interface AudioControlsProps {
  speed: number;
  onSpeedChange: (speed: number) => void;
  pitch: number;
  onPitchChange: (pitch: number) => void;
  volume: number;
  onVolumeChange: (volume: number) => void;
}

function Slider({
  label,
  value,
  min,
  max,
  step,
  unit,
  onChange,
  color = 'amber',
}: {
  label: string;
  value: number;
  min: number;
  max: number;
  step: number;
  unit: string;
  onChange: (val: number) => void;
  color?: 'amber' | 'blue' | 'green';
}) {
  const colorClasses = {
    amber: 'from-amber-400 to-orange-500',
    blue: 'from-blue-400 to-indigo-500',
    green: 'from-green-400 to-emerald-500',
  };

  const percentage = ((value - min) / (max - min)) * 100;

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <label className="text-sm font-medium text-gray-700">{label}</label>
        <span className="text-sm font-mono font-semibold text-gray-900 bg-gray-100 px-3 py-1 rounded-lg">
          {value.toFixed(step < 1 ? 1 : 0)}{unit}
        </span>
      </div>
      <div className="relative h-3 bg-gray-100 rounded-full overflow-hidden">
        <div
          className={`absolute inset-y-0 left-0 rounded-full bg-gradient-to-r ${colorClasses[color]} transition-all duration-150`}
          style={{ width: `${percentage}%` }}
        />
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={value}
          onChange={(e) => onChange(parseFloat(e.target.value))}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          aria-label={`${label}: ${value}${unit}`}
        />
        <div
          className="absolute top-1/2 w-5 h-5 bg-white rounded-full shadow-md border-2 border-gray-300 pointer-events-none transition-all duration-150 -translate-y-1/2 -translate-x-1/2"
          style={{ left: `${percentage}%` }}
        />
      </div>
      <div className="flex justify-between text-xs text-gray-400">
        <span>{min}{unit}</span>
        <span>{max}{unit}</span>
      </div>
    </div>
  );
}

export default function AudioControls({
  speed,
  onSpeedChange,
  pitch,
  onPitchChange,
  volume,
  onVolumeChange,
}: AudioControlsProps) {
  return (
    <section className="bg-white rounded-2xl shadow-lg shadow-gray-200/50 overflow-hidden" aria-label="音频参数">
      <div className="px-6 py-4 border-b border-gray-100">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-blue-100 rounded-xl flex items-center justify-center">
            <svg className="w-5 h-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
            </svg>
          </div>
          <div>
            <h2 className="text-lg font-semibold text-gray-900">音频参数</h2>
            <p className="text-xs text-gray-500">调整语速、音调和音量</p>
          </div>
        </div>
      </div>
      <div className="p-6 space-y-6">
        <Slider
          label="语速"
          value={speed}
          min={0.5}
          max={2.0}
          step={0.1}
          unit="x"
          onChange={onSpeedChange}
          color="amber"
        />
        <Slider
          label="音调"
          value={pitch}
          min={-12}
          max={12}
          step={1}
          unit=""
          onChange={onPitchChange}
          color="blue"
        />
        <Slider
          label="音量"
          value={volume}
          min={0}
          max={100}
          step={1}
          unit="%"
          onChange={onVolumeChange}
          color="green"
        />
      </div>
    </section>
  );
}
