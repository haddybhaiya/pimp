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
        canvas: '#0C0F11',
        'surface-1': '#171A1C',
        'surface-2': '#202426',
        'surface-glass': 'rgba(32, 36, 38, 0.72)',
        'border-subtle': '#353B3D',
        'border-strong': '#4A5354',
        'text-primary': '#F4F5F4',
        'text-secondary': '#A7B0AA',
        'text-muted': '#737C77',
        brand: {
          DEFAULT: '#34D399',
          bright: '#6EE7B7',
          deep: '#059669',
        },
        primary: {
          DEFAULT: '#6EE7B7',
          foreground: '#07100D',
          bright: '#A7F3D0',
          deep: '#10B981',
        },
        secondary: {
          DEFAULT: '#202426',
          foreground: '#F4F5F4',
        },
        destructive: {
          DEFAULT: '#FB7185',
          foreground: '#FFFFFF',
        },
        muted: {
          DEFAULT: '#202426',
          foreground: '#A7B0AA',
        },
        accent: {
          DEFAULT: '#252A2C',
          foreground: '#F4F5F4',
        },
        card: {
          DEFAULT: '#171A1C',
          foreground: '#F4F5F4',
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
        glow: '0 0 25px -5px rgba(52, 211, 153, 0.24)',
        'glow-sm': '0 0 15px -3px rgba(52, 211, 153, 0.2)',
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

