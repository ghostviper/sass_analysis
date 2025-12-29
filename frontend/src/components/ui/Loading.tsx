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
