interface TextInputProps {
  value: string;
  onChange: (value: string) => void;
  maxLength?: number;
  placeholder?: string;
}

const MAX_CHARS = 5000;

export default function TextInput({ value, onChange, maxLength = MAX_CHARS, placeholder = '输入要合成的文本...' }: TextInputProps) {
  const charCount = value.length;
  const isNearLimit = charCount > maxLength * 0.9;
  const isAtLimit = charCount >= maxLength;

  return (
    <section className="rounded-lg shadow-card bg-white" aria-label="文本输入">
      <div className="px-4 pt-3 pb-1">
        <label htmlFor="tts-text-input" className="text-sm font-medium text-ink">
          文本内容
        </label>
      </div>
      <div className="px-4 pb-3">
        <textarea
          id="tts-text-input"
          value={value}
          onChange={(e) => onChange(e.target.value.slice(0, maxLength))}
          placeholder={placeholder}
          rows={5}
          className="w-full rounded-md bg-white text-base font-normal text-ink leading-relaxed resize-y min-h-[120px] outline-none transition-shadow focus:shadow-input-focus placeholder:text-gray-500"
          style={{ boxShadow: 'rgba(0, 0, 0, 0.08) 0px 0px 0px 1px' }}
          aria-describedby="char-counter"
        />
        <div className="flex justify-end mt-2" id="char-counter">
          <span
            className={`text-xs font-normal tabular-nums ${
              isAtLimit
                ? 'text-status-error'
                : isNearLimit
                ? 'text-amber-primary'
                : 'text-gray-500'
            }`}
            aria-live="polite"
          >
            {charCount} / {maxLength}
          </span>
        </div>
      </div>
    </section>
  );
}
