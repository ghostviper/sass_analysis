'use client'

import { cn } from '@/lib/utils'

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

export function LoadingSpinner({ size = 'md', className }: LoadingSpinnerProps) {
  const sizeStyles = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  }

  return (
    <div
      className={cn(
        'animate-spin rounded-full border-2 border-surface-border border-t-accent-primary',
        sizeStyles[size],
        className
      )}
    />
  )
}

interface LoadingPageProps {
  message?: string
}

export function LoadingPage({ message = '加载中...' }: LoadingPageProps) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[400px] gap-4">
      <LoadingSpinner size="lg" />
      <p className="text-content-muted animate-pulse">{message}</p>
    </div>
  )
}

// 骨架屏组件
interface SkeletonProps {
  className?: string
}

export function Skeleton({ className }: SkeletonProps) {
  return (
    <div
      className={cn(
        'animate-pulse bg-surface-border rounded',
        className
      )}
    />
  )
}

// 卡片骨架屏
export function CardSkeleton() {
  return (
    <div className="card animate-pulse">
      <div className="flex items-center justify-between mb-4">
        <Skeleton className="h-5 w-24" />
        <Skeleton className="h-8 w-8 rounded-lg" />
      </div>
      <Skeleton className="h-10 w-32 mb-2" />
      <Skeleton className="h-4 w-20" />
    </div>
  )
}

// 列表骨架屏
export function ListSkeleton({ rows = 5 }: { rows?: number }) {
  return (
    <div className="card space-y-4">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="flex items-center gap-4">
          <Skeleton className="w-8 h-8 rounded-full" />
          <div className="flex-1">
            <Skeleton className="h-4 w-3/4 mb-2" />
            <Skeleton className="h-3 w-1/2" />
          </div>
          <Skeleton className="h-6 w-16 rounded-full" />
        </div>
      ))}
    </div>
  )
}

// 表格骨架屏
export function TableSkeleton({ rows = 5, cols = 4 }: { rows?: number; cols?: number }) {
  return (
    <div className="card p-0 overflow-hidden">
      {/* 表头 */}
      <div className="flex gap-4 p-4 border-b border-surface-border bg-background-secondary/50">
        {Array.from({ length: cols }).map((_, i) => (
          <Skeleton key={i} className="h-4 flex-1" />
        ))}
      </div>
      {/* 表体 */}
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="flex gap-4 p-4 border-b border-surface-border/50">
          {Array.from({ length: cols }).map((_, j) => (
            <Skeleton key={j} className="h-4 flex-1" />
          ))}
        </div>
      ))}
    </div>
  )
}

// 产品详情骨架屏
export function ProductDetailSkeleton() {
  return (
    <div className="space-y-6">
      {/* 头部 */}
      <div className="card">
        <div className="flex items-start gap-6">
          <Skeleton className="w-16 h-16 rounded-xl" />
          <div className="flex-1">
            <Skeleton className="h-8 w-48 mb-2" />
            <Skeleton className="h-4 w-32 mb-4" />
            <Skeleton className="h-20 w-full" />
          </div>
        </div>
      </div>

      {/* 评分网格 */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {Array.from({ length: 6 }).map((_, i) => (
          <CardSkeleton key={i} />
        ))}
      </div>

      {/* 详情区块 */}
      <div className="grid md:grid-cols-2 gap-6">
        <ListSkeleton rows={4} />
        <ListSkeleton rows={4} />
      </div>
    </div>
  )
}

// 策展卡片骨架屏
export function CurationCardSkeleton() {
  return (
    <div className="card animate-pulse">
      {/* 标签 */}
      <Skeleton className="h-6 w-32 rounded-lg mb-3" />
      
      {/* 标题 */}
      <Skeleton className="h-5 w-full mb-2" />
      <Skeleton className="h-5 w-3/4 mb-4" />
      
      {/* 描述 */}
      <Skeleton className="h-4 w-full mb-2" />
      <Skeleton className="h-4 w-5/6 mb-4" />
      
      {/* 产品列表 */}
      <div className="space-y-2 mb-4">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="flex items-center justify-between p-2.5 rounded-lg bg-surface/50 border border-surface-border/50">
            <div className="flex items-center gap-2.5">
              <Skeleton className="w-6 h-6 rounded" />
              <Skeleton className="h-4 w-24" />
            </div>
            <Skeleton className="h-4 w-16" />
          </div>
        ))}
      </div>
      
      {/* 洞察 */}
      <Skeleton className="h-12 w-full rounded-lg mb-4" />
      
      {/* CTA 按钮 */}
      <Skeleton className="h-10 w-full rounded-xl" />
    </div>
  )
}

// 主题卡片骨架屏
export function TopicCardSkeleton() {
  return (
    <div className="flex-shrink-0 w-80 snap-start">
      <div className="card animate-pulse h-full">
        {/* 图标 + 标题 */}
        <div className="flex items-start gap-3 mb-3">
          <Skeleton className="w-9 h-9 rounded-xl" />
          <div className="flex-1">
            <Skeleton className="h-5 w-full mb-2" />
            <Skeleton className="h-5 w-3/4" />
          </div>
        </div>
        
        {/* 描述 */}
        <Skeleton className="h-3 w-full mb-2" />
        <Skeleton className="h-3 w-5/6 mb-4" />
        
        {/* 产品列表 */}
        <div className="space-y-1.5 mb-4 py-3 border-y border-surface-border/30">
          {Array.from({ length: 2 }).map((_, i) => (
            <div key={i} className="flex items-center justify-between">
              <Skeleton className="h-3 w-32" />
              <Skeleton className="h-3 w-16" />
            </div>
          ))}
        </div>
        
        {/* 底部 */}
        <div className="flex items-center justify-between">
          <Skeleton className="h-3 w-20" />
          <Skeleton className="h-3 w-16" />
        </div>
      </div>
    </div>
  )
}

// Discover 页面骨架屏
export function DiscoverPageSkeleton() {
  return (
    <div className="space-y-8">
      {/* 页面标题 */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-violet-500/10 via-brand-500/5 to-amber-500/10 border border-violet-500/20 p-6 md:p-8 animate-pulse">
        <div className="flex items-center gap-4 mb-4">
          <Skeleton className="w-14 h-14 rounded-2xl" />
          <div className="flex-1">
            <Skeleton className="h-8 w-48 mb-2" />
            <Skeleton className="h-4 w-64" />
          </div>
        </div>
        <Skeleton className="h-8 w-80" />
      </div>

      {/* 今日策展 */}
      <section>
        <div className="flex items-center justify-between mb-5">
          <div className="flex items-center gap-3">
            <Skeleton className="w-10 h-10 rounded-xl" />
            <div>
              <Skeleton className="h-5 w-32 mb-1" />
              <Skeleton className="h-3 w-48" />
            </div>
          </div>
          <Skeleton className="h-4 w-20" />
        </div>
        <div className="grid md:grid-cols-2 gap-5">
          <CurationCardSkeleton />
          <CurationCardSkeleton />
        </div>
      </section>

      {/* 主题合集 */}
      <section>
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <Skeleton className="w-1 h-6 rounded-full" />
            <div>
              <Skeleton className="h-5 w-32 mb-1" />
              <Skeleton className="h-3 w-48" />
            </div>
          </div>
          <div className="flex items-center gap-1.5">
            <Skeleton className="w-8 h-8 rounded-lg" />
            <Skeleton className="w-8 h-8 rounded-lg" />
          </div>
        </div>
        <div className="flex gap-4 overflow-x-auto scrollbar-hide pb-2">
          <TopicCardSkeleton />
          <TopicCardSkeleton />
          <TopicCardSkeleton />
        </div>
      </section>

      {/* 其他区块 */}
      <div className="space-y-8">
        {Array.from({ length: 2 }).map((_, i) => (
          <section key={i}>
            <div className="flex items-center gap-3 mb-5">
              <Skeleton className="w-1 h-6 rounded-full" />
              <div>
                <Skeleton className="h-5 w-32 mb-1" />
                <Skeleton className="h-3 w-48" />
              </div>
            </div>
            <div className="grid md:grid-cols-3 gap-4">
              {Array.from({ length: 3 }).map((_, j) => (
                <CardSkeleton key={j} />
              ))}
            </div>
          </section>
        ))}
      </div>
    </div>
  )
}

// 策展列表页骨架屏
export function CurationsPageSkeleton() {
  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-violet-500/10 via-brand-500/5 to-purple-500/10 border border-violet-500/20 p-6 md:p-8 animate-pulse">
        <div className="flex items-center gap-4 mb-3">
          <Skeleton className="w-14 h-14 rounded-2xl" />
          <div className="flex-1">
            <Skeleton className="h-8 w-48 mb-2" />
            <Skeleton className="h-4 w-64" />
          </div>
        </div>
        <Skeleton className="h-8 w-80" />
      </div>

      {/* 筛选器 */}
      <div className="card">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex flex-wrap gap-2">
            {Array.from({ length: 4 }).map((_, i) => (
              <Skeleton key={i} className="h-9 w-24 rounded-lg" />
            ))}
          </div>
          <Skeleton className="h-9 w-32 rounded-lg" />
        </div>
      </div>

      {/* 策展列表 */}
      <div className="grid md:grid-cols-2 gap-5">
        {Array.from({ length: 6 }).map((_, i) => (
          <CurationCardSkeleton key={i} />
        ))}
      </div>
    </div>
  )
}
