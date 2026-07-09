interface HeaderProps {
  title?: string;
  subtitle?: string;
}

export default function Header({ title = 'TTS Studio', subtitle = '智能语音合成工作室' }: HeaderProps) {
  return (
    <header className="text-center pt-12 pb-8" role="banner">
      <h1
        className="text-5xl font-semibold text-ink tracking-[-2.4px] leading-[1.17] mb-2"
        style={{ fontFamily: "'Geist', sans-serif" }}
      >
        {title}
      </h1>
      <p className="text-base font-normal text-gray-600 tracking-normal">
        {subtitle}
      </p>
    </header>
  );
}
