/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ['class'],
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        canvas: '#070B14',
        'surface-1': '#0D1424',
        'surface-2': '#141D31',
        'surface-glass': 'rgba(20, 29, 49, 0.72)',
        'border-subtle': '#24314A',
        'border-strong': '#344566',
        'text-primary': '#F4F7FF',
        'text-secondary': '#A9B7D0',
        'text-muted': '#72819B',
        brand: {
          DEFAULT: '#7C5CFF',
          bright: '#A78BFA',
          deep: '#4F46E5',
        },
        primary: {
          DEFAULT: '#7C5CFF',
          foreground: '#FFFFFF',
          bright: '#A78BFA',
          deep: '#4F46E5',
        },
        secondary: {
          DEFAULT: '#141D31',
          foreground: '#F4F7FF',
        },
        destructive: {
          DEFAULT: '#FB7185',
          foreground: '#FFFFFF',
        },
        muted: {
          DEFAULT: '#141D31',
          foreground: '#A9B7D0',
        },
        accent: {
          DEFAULT: '#1E293B',
          foreground: '#F4F7FF',
        },
        card: {
          DEFAULT: '#0D1424',
          foreground: '#F4F7FF',
        },
        success: {
          DEFAULT: '#34D399',
          foreground: '#070B14',
        },
        warning: {
          DEFAULT: '#FBBF24',
          foreground: '#070B14',
        },
        danger: {
          DEFAULT: '#FB7185',
          foreground: '#FFFFFF',
        },
        info: {
          DEFAULT: '#38BDF8',
          foreground: '#070B14',
        },
      },
      borderRadius: {
        lg: '12px',
        md: '10px',
        sm: '6px',
        pill: '9999px',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        display: ['Space Grotesk', 'Manrope', 'Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      boxShadow: {
        glass: '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
        glow: '0 0 25px -5px rgba(124, 92, 255, 0.3)',
        'glow-sm': '0 0 15px -3px rgba(124, 92, 255, 0.25)',
        'glow-success': '0 0 20px -5px rgba(52, 211, 153, 0.3)',
        'glow-warning': '0 0 20px -5px rgba(251, 191, 36, 0.3)',
      },
      animation: {
        'pulse-subtle': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'float-slow': 'float 6s ease-in-out infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-8px)' },
        },
      },
    },
  },
  plugins: [],
}

