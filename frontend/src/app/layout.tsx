import type { Metadata } from 'next'
import { DM_Sans, Noto_Sans_SC, JetBrains_Mono } from 'next/font/google'
import { Sidebar } from '@/components/layout/Sidebar'
import { MainContent } from '@/components/layout/MainContent'
import { Providers } from '@/components/providers/Providers'
import './globals.css'

// 主要西文字体 - DM Sans
const dmSans = DM_Sans({
  subsets: ['latin'],
  weight: ['300', '400', '500', '600', '700'],
  variable: '--font-dm-sans',
  display: 'swap',
})

// 中文字体 - Noto Sans SC
const notoSansSC = Noto_Sans_SC({
  subsets: ['latin'],
  weight: ['300', '400', '500', '600', '700'],
  variable: '--font-noto-sans-sc',
  display: 'swap',
})

// 等宽字体 - JetBrains Mono
const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  weight: ['400', '500', '600'],
  variable: '--font-jetbrains-mono',
  display: 'swap',
})

export const metadata: Metadata = {
  title: 'BuildWhat - 发现独立开发者的产品机会',
  description: '基于数据驱动的 SaaS 产品分析平台，帮助独立开发者发现蓝海市场和可复制的产品机会',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh-CN" suppressHydrationWarning>
      <body className={`${dmSans.variable} ${notoSansSC.variable} ${jetbrainsMono.variable} min-h-screen`}>
        <Providers>
          {/* 背景装饰 */}
          <div className="fixed inset-0 -z-10 overflow-hidden">
            {/* 顶部光晕 */}
            <div className="absolute -top-40 -right-40 h-80 w-80 rounded-full bg-accent-primary/10 blur-3xl" />
            <div className="absolute -top-20 left-1/4 h-60 w-60 rounded-full bg-accent-secondary/5 blur-3xl" />
            {/* 网格背景 */}
            <div className="absolute inset-0 bg-grid opacity-30" />
          </div>

          {/* 侧边栏 */}
          <Sidebar />

          {/* 主内容区 */}
          <MainContent>{children}</MainContent>
        </Providers>
      </body>
    </html>
  )
}
