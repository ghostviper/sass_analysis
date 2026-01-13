import type { Metadata } from 'next'
import { DM_Sans, Noto_Sans_SC, JetBrains_Mono } from 'next/font/google'
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
  icons: {
    icon: '/icon.svg',
  },
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
          {children}
        </Providers>
      </body>
    </html>
  )
}
