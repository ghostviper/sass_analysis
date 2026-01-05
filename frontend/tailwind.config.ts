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
        // ============================================
        // 基础色彩系统 - 使用 CSS 变量支持主题切换
        // ============================================
        background: {
          DEFAULT: 'rgb(var(--background) / <alpha-value>)',
          secondary: 'rgb(var(--background-secondary) / <alpha-value>)',
          tertiary: 'rgb(var(--background-tertiary) / <alpha-value>)',
        },
        surface: {
          DEFAULT: 'rgb(var(--surface) / <alpha-value>)',
          hover: 'rgb(var(--surface-hover) / <alpha-value>)',
          border: 'rgb(var(--surface-border) / <alpha-value>)',
          elevated: 'rgb(var(--surface-elevated) / <alpha-value>)',
        },
        // 文本色彩层级
        content: {
          primary: 'rgb(var(--content-primary) / <alpha-value>)',
          secondary: 'rgb(var(--content-secondary) / <alpha-value>)',
          tertiary: 'rgb(var(--content-tertiary) / <alpha-value>)',
          muted: 'rgb(var(--content-muted) / <alpha-value>)',
        },

        // ============================================
        // 品牌主色 - 渐变蓝紫色调，现代 SaaS 风格
        // ============================================
        brand: {
          50: '#eef2ff',
          100: '#e0e7ff',
          200: '#c7d2fe',
          300: '#a5b4fc',
          400: '#818cf8',
          500: '#6366f1',  // 主色
          600: '#4f46e5',
          700: '#4338ca',
          800: '#3730a3',
          900: '#312e81',
          950: '#1e1b4b',
        },

        // ============================================
        // 强调色系统 - 精心调配的色彩
        // ============================================
        accent: {
          // 主强调色 - 靛蓝色
          primary: 'rgb(var(--accent-primary) / <alpha-value>)',
          'primary-hover': 'rgb(var(--accent-primary-hover) / <alpha-value>)',
          // 次强调色 - 紫罗兰
          secondary: 'rgb(var(--accent-secondary) / <alpha-value>)',
          // 功能色
          success: '#10b981',
          'success-light': '#d1fae5',
          warning: '#f59e0b',
          'warning-light': '#fef3c7',
          error: '#ef4444',
          'error-light': '#fee2e2',
          info: '#0ea5e9',
          'info-light': '#e0f2fe',
        },

        // ============================================
        // 市场类型色彩 - 数据可视化专用
        // ============================================
        market: {
          'blue-ocean': '#06b6d4',
          'red-ocean': '#f43f5e',
          'emerging': '#f59e0b',
          'moderate': '#64748b',
          'concentrated': '#a855f7',
          'weak-demand': '#475569',
        },

        // ============================================
        // 图表色板 - 数据可视化
        // ============================================
        chart: {
          1: '#6366f1',
          2: '#8b5cf6',
          3: '#06b6d4',
          4: '#10b981',
          5: '#f59e0b',
          6: '#f43f5e',
        },
      },

      // ============================================
      // 字体系统 - 使用 CSS 变量支持 Next.js 字体优化
      // ============================================
      fontFamily: {
        sans: ['var(--font-dm-sans)', 'var(--font-noto-sans-sc)', 'system-ui', '-apple-system', 'BlinkMacSystemFont', '"Segoe UI"', 'sans-serif'],
        display: ['var(--font-dm-sans)', 'var(--font-noto-sans-sc)', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['var(--font-jetbrains-mono)', '"SF Mono"', 'Monaco', 'Consolas', '"Liberation Mono"', 'monospace'],
      },

      // ============================================
      // 字号系统 - 模块化比例 1.2 (Minor Third)
      // ============================================
      fontSize: {
        // 微小文本
        '2xs': ['0.625rem', { lineHeight: '0.875rem', letterSpacing: '0.02em' }],
        // 标签/徽章
        'xs': ['0.75rem', { lineHeight: '1rem', letterSpacing: '0.01em' }],
        // 辅助文本
        'sm': ['0.8125rem', { lineHeight: '1.25rem', letterSpacing: '0' }],
        // 正文
        'base': ['0.9375rem', { lineHeight: '1.5rem', letterSpacing: '-0.01em' }],
        // 大正文
        'lg': ['1.0625rem', { lineHeight: '1.625rem', letterSpacing: '-0.01em' }],
        // 小标题
        'xl': ['1.25rem', { lineHeight: '1.75rem', letterSpacing: '-0.02em' }],
        // 标题
        '2xl': ['1.5rem', { lineHeight: '2rem', letterSpacing: '-0.02em' }],
        // 大标题
        '3xl': ['1.875rem', { lineHeight: '2.25rem', letterSpacing: '-0.025em' }],
        // 展示标题
        '4xl': ['2.25rem', { lineHeight: '2.5rem', letterSpacing: '-0.025em' }],
        // 大展示
        '5xl': ['3rem', { lineHeight: '3.25rem', letterSpacing: '-0.03em' }],
        // 超大展示
        '6xl': ['3.75rem', { lineHeight: '4rem', letterSpacing: '-0.03em' }],
      },

      // ============================================
      // 字重
      // ============================================
      fontWeight: {
        light: '300',
        normal: '400',
        medium: '500',
        semibold: '600',
        bold: '700',
      },

      // ============================================
      // 字间距
      // ============================================
      letterSpacing: {
        tighter: '-0.03em',
        tight: '-0.02em',
        snug: '-0.01em',
        normal: '0',
        wide: '0.01em',
        wider: '0.025em',
        widest: '0.05em',
      },

      // ============================================
      // 行高
      // ============================================
      lineHeight: {
        none: '1',
        tight: '1.2',
        snug: '1.35',
        normal: '1.5',
        relaxed: '1.625',
        loose: '1.75',
      },

      // ============================================
      // 圆角 - 统一的圆角系统
      // ============================================
      borderRadius: {
        'sm': '0.25rem',
        'DEFAULT': '0.375rem',
        'md': '0.5rem',
        'lg': '0.75rem',
        'xl': '1rem',
        '2xl': '1.25rem',
        '3xl': '1.5rem',
      },

      // ============================================
      // 阴影系统 - 精细的层次感
      // ============================================
      boxShadow: {
        // 基础阴影
        'xs': '0 1px 2px 0 rgb(0 0 0 / 0.03)',
        'sm': '0 1px 3px 0 rgb(0 0 0 / 0.05), 0 1px 2px -1px rgb(0 0 0 / 0.05)',
        'DEFAULT': '0 4px 6px -1px rgb(0 0 0 / 0.05), 0 2px 4px -2px rgb(0 0 0 / 0.05)',
        'md': '0 6px 12px -2px rgb(0 0 0 / 0.06), 0 3px 6px -3px rgb(0 0 0 / 0.06)',
        'lg': '0 10px 20px -3px rgb(0 0 0 / 0.08), 0 4px 8px -4px rgb(0 0 0 / 0.06)',
        'xl': '0 20px 40px -5px rgb(0 0 0 / 0.1), 0 8px 16px -6px rgb(0 0 0 / 0.08)',
        '2xl': '0 25px 50px -12px rgb(0 0 0 / 0.15)',
        // 卡片阴影
        'card': '0 1px 3px rgb(0 0 0 / 0.04), 0 1px 2px rgb(0 0 0 / 0.02)',
        'card-hover': '0 8px 24px rgb(0 0 0 / 0.08), 0 4px 8px rgb(0 0 0 / 0.04)',
        'card-dark': '0 2px 8px rgb(0 0 0 / 0.3), 0 1px 3px rgb(0 0 0 / 0.2)',
        'card-dark-hover': '0 12px 32px rgb(0 0 0 / 0.4), 0 6px 12px rgb(0 0 0 / 0.25)',
        // 发光效果
        'glow-brand': '0 0 24px rgb(99 102 241 / 0.25), 0 0 48px rgb(99 102 241 / 0.1)',
        'glow-success': '0 0 20px rgb(16 185 129 / 0.3)',
        'glow-warning': '0 0 20px rgb(245 158 11 / 0.3)',
        'glow-error': '0 0 20px rgb(239 68 68 / 0.3)',
        // 内阴影
        'inner-sm': 'inset 0 1px 2px 0 rgb(0 0 0 / 0.05)',
        'inner': 'inset 0 2px 4px 0 rgb(0 0 0 / 0.05)',
      },

      // ============================================
      // 背景渐变
      // ============================================
      backgroundImage: {
        // 品牌渐变
        'gradient-brand': 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a855f7 100%)',
        'gradient-brand-subtle': 'linear-gradient(135deg, rgb(99 102 241 / 0.1) 0%, rgb(139 92 246 / 0.1) 100%)',
        // 背景渐变
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-mesh': 'linear-gradient(135deg, #0a0f1a 0%, #111827 50%, #1f2937 100%)',
        // 网格背景
        'grid-pattern': 'linear-gradient(rgb(99 102 241 / 0.03) 1px, transparent 1px), linear-gradient(90deg, rgb(99 102 241 / 0.03) 1px, transparent 1px)',
        // 噪点纹理
        'noise': "url(\"data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E\")",
      },

      // ============================================
      // 动画
      // ============================================
      animation: {
        'fade-in': 'fadeIn 0.3s ease-out',
        'fade-in-up': 'fadeInUp 0.4s ease-out',
        'fade-in-down': 'fadeInDown 0.4s ease-out',
        'slide-in-left': 'slideInLeft 0.3s ease-out',
        'slide-in-right': 'slideInRight 0.3s ease-out',
        'scale-in': 'scaleIn 0.2s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'shimmer': 'shimmer 2s infinite',
        'float': 'float 6s ease-in-out infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        fadeInUp: {
          '0%': { opacity: '0', transform: 'translateY(16px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        fadeInDown: {
          '0%': { opacity: '0', transform: 'translateY(-16px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideInLeft: {
          '0%': { opacity: '0', transform: 'translateX(-20px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        slideInRight: {
          '0%': { opacity: '0', transform: 'translateX(20px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        scaleIn: {
          '0%': { opacity: '0', transform: 'scale(0.95)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        glow: {
          '0%': { boxShadow: '0 0 20px rgb(99 102 241 / 0.2)' },
          '100%': { boxShadow: '0 0 30px rgb(99 102 241 / 0.4)' },
        },
      },

      // ============================================
      // 过渡
      // ============================================
      transitionDuration: {
        '0': '0ms',
        '75': '75ms',
        '100': '100ms',
        '150': '150ms',
        '200': '200ms',
        '250': '250ms',
        '300': '300ms',
        '400': '400ms',
        '500': '500ms',
      },
      transitionTimingFunction: {
        'ease-out-expo': 'cubic-bezier(0.16, 1, 0.3, 1)',
        'ease-in-out-expo': 'cubic-bezier(0.87, 0, 0.13, 1)',
      },
    },
  },
  plugins: [],
}
export default config
