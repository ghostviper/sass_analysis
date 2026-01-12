'use client'

/**
 * Dashboard 布局
 * 
 * 包含侧边栏和主内容区的标准应用布局
 * 用于所有需要登录的页面
 */

import { useState, useEffect } from 'react'
import { Sidebar } from '@/components/layout/Sidebar'
import { MainContent } from '@/components/layout/MainContent'
import { useAuth } from '@/hooks/useAuth'

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const { isLoading } = useAuth()
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  // 服务端渲染和客户端首次渲染都显示 loading
  if (!mounted || isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-brand-500 border-t-transparent" />
      </div>
    )
  }

  return (
    <>
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
    </>
  )
}
