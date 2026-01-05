import type { Config } from 'tailwindcss'

const config: Config = {
  darkMode: 'class',
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Base colors - using CSS variables for theme support
        background: {
          DEFAULT: 'rgb(var(--background) / <alpha-value>)',
          secondary: 'rgb(var(--background-secondary) / <alpha-value>)',
          tertiary: 'rgb(var(--background-tertiary) / <alpha-value>)',
        },
        surface: {
          DEFAULT: 'rgb(var(--surface) / <alpha-value>)',
          hover: 'rgb(var(--surface-hover) / <alpha-value>)',
          border: 'rgb(var(--surface-border) / <alpha-value>)',
        },
        // Market type colors (static - same in both themes)
        market: {
          'blue-ocean': '#06b6d4',
          'red-ocean': '#f43f5e',
          'emerging': '#f59e0b',
          'moderate': '#64748b',
          'concentrated': '#a855f7',
          'weak-demand': '#475569',
        },
        // Accent colors (static - same in both themes)
        accent: {
          primary: '#3b82f6',
          secondary: '#8b5cf6',
          success: '#10b981',
          warning: '#f59e0b',
          danger: '#ef4444',
        },
        // Text colors - using CSS variables for theme support
        content: {
          primary: 'rgb(var(--content-primary) / <alpha-value>)',
          secondary: 'rgb(var(--content-secondary) / <alpha-value>)',
          tertiary: 'rgb(var(--content-tertiary) / <alpha-value>)',
          muted: 'rgb(var(--content-muted) / <alpha-value>)',
        },
      },
      // Typography system
      fontFamily: {
        sans: ['"DM Sans"', '"Noto Sans SC"', 'system-ui', '-apple-system', 'BlinkMacSystemFont', '"Segoe UI"', 'sans-serif'],
        display: ['"DM Sans"', '"Noto Sans SC"', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['"JetBrains Mono"', '"SF Mono"', 'Monaco', 'Consolas', '"Liberation Mono"', 'monospace'],
      },
      fontSize: {
        // Caption / Small text
        'xs': ['0.75rem', { lineHeight: '1.125rem', letterSpacing: '0.01em' }],
        // Body small
        'sm': ['0.8125rem', { lineHeight: '1.375rem', letterSpacing: '0' }],
        // Body default - 加大到 15px
        'base': ['0.9375rem', { lineHeight: '1.65', letterSpacing: '-0.01em' }],
        // Body large / Subheading
        'lg': ['1.0625rem', { lineHeight: '1.65', letterSpacing: '-0.01em' }],
        // Heading small
        'xl': ['1.1875rem', { lineHeight: '1.5', letterSpacing: '-0.02em' }],
        // Heading medium
        '2xl': ['1.375rem', { lineHeight: '1.4', letterSpacing: '-0.02em' }],
        // Heading large
        '3xl': ['1.625rem', { lineHeight: '1.35', letterSpacing: '-0.025em' }],
        // Display small
        '4xl': ['2rem', { lineHeight: '1.3', letterSpacing: '-0.025em' }],
        // Display medium
        '5xl': ['2.5rem', { lineHeight: '1.2', letterSpacing: '-0.03em' }],
        // Display large
        '6xl': ['3.25rem', { lineHeight: '1.15', letterSpacing: '-0.03em' }],
      },
      fontWeight: {
        light: '300',
        normal: '400',
        medium: '500',
        semibold: '600',
        bold: '700',
      },
      letterSpacing: {
        tighter: '-0.03em',
        tight: '-0.02em',
        snug: '-0.01em',
        normal: '0',
        wide: '0.01em',
        wider: '0.02em',
        widest: '0.05em',
      },
      lineHeight: {
        none: '1',
        tight: '1.2',
        snug: '1.35',
        normal: '1.5',
        relaxed: '1.625',
        loose: '1.75',
      },
      boxShadow: {
        'glow-blue': '0 0 20px rgba(59, 130, 246, 0.3)',
        'glow-cyan': '0 0 20px rgba(6, 182, 212, 0.3)',
        'glow-purple': '0 0 20px rgba(139, 92, 246, 0.3)',
        'card': '0 1px 3px rgba(0, 0, 0, 0.04), 0 1px 2px rgba(0, 0, 0, 0.02)',
        'card-hover': '0 4px 12px rgba(0, 0, 0, 0.06), 0 2px 4px rgba(0, 0, 0, 0.03)',
        'card-dark': '0 2px 8px rgba(0, 0, 0, 0.25), 0 1px 3px rgba(0, 0, 0, 0.15)',
        'card-dark-hover': '0 8px 24px rgba(0, 0, 0, 0.35), 0 4px 8px rgba(0, 0, 0, 0.2)',
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-mesh': 'linear-gradient(135deg, #0a0f1a 0%, #111827 50%, #1f2937 100%)',
        'grid-pattern': 'linear-gradient(rgba(59, 130, 246, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(59, 130, 246, 0.03) 1px, transparent 1px)',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-out',
        'slide-up': 'slideUp 0.5s ease-out',
        'slide-in-left': 'slideInLeft 0.3s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'shimmer': 'shimmer 2s infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideInLeft: {
          '0%': { opacity: '0', transform: 'translateX(-20px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
      },
    },
  },
  plugins: [],
}
export default config
