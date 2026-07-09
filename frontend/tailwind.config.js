/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Geist', 'Arial', 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol', 'sans-serif'],
        mono: ['Geist Mono', 'ui-monospace', 'SFMono-Regular', 'Roboto Mono', 'Menlo', 'monospace'],
      },
      colors: {
        amber: {
          primary: '#f59e0b',
          hover: '#d97706',
        },
        ink: {
          DEFAULT: '#171717',
        },
        gray: {
          50: '#fafafa',
          100: '#f5f5f5',
          300: '#d4d4d4',
          500: '#737373',
          600: '#525252',
          700: '#404040',
          900: '#171717',
        },
        wave: {
          DEFAULT: '#f97316',
        },
        coral: {
          DEFAULT: '#ff6b35',
        },
        status: {
          success: '#22c55e',
          error: '#ef4444',
          info: '#3b82f6',
        },
      },
      letterSpacing: {
        'display': '-2.4px',
        'section': '-1.28px',
        'card': '-0.96px',
      },
      boxShadow: {
        'border': 'rgba(0, 0, 0, 0.08) 0px 0px 0px 1px',
        'card': 'rgba(0, 0, 0, 0.08) 0px 0px 0px 1px, rgba(0, 0, 0, 0.04) 0px 2px 4px, rgba(0, 0, 0, 0.04) 0px 8px 8px -8px, #fafafa 0px 0px 0px 1px',
        'warm-lift': 'rgba(245, 158, 11, 0.08) 0px 4px 12px',
        'input-focus': '0 0 0 2px hsla(38, 100%, 50%, 0.5)',
      },
      animation: {
        'pulse-slow': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'slide-in': 'slideIn 0.3s ease-out',
      },
      keyframes: {
        slideIn: {
          '0%': { opacity: '0', transform: 'translateY(8px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [],
}
