import type { Metadata } from 'next'
import { Sidebar } from '@/components/layout/Sidebar'
import { MainContent } from '@/components/layout/MainContent'
import { Providers } from '@/components/providers/Providers'
import './globals.css'

// FontAwesome 配置
import { config } from '@fortawesome/fontawesome-svg-core'
import '@fortawesome/fontawesome-svg-core/styles.css'
config.autoAddCss = false

export const metadata: Metadata = {
  title: 'SaaS 产品分析 - 发现独立开发者的产品机会',
  description: '基于数据驱动的 SaaS 产品分析平台，帮助独立开发者发现蓝海市场和可复制的产品机会',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh-CN" suppressHydrationWarning>
      <body className="min-h-screen">
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
