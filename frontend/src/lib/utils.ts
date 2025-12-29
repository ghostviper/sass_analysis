import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

// 合并 Tailwind CSS 类名
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// 格式化货币
export function formatCurrency(value: number | null | undefined): string {
  if (value === null || value === undefined) return '-'
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value)
}

// 格式化数字
export function formatNumber(value: number | null | undefined): string {
  if (value === null || value === undefined) return '-'
  return new Intl.NumberFormat('en-US').format(value)
}

// 格式化百分比
export function formatPercent(value: number | null | undefined): string {
  if (value === null || value === undefined) return '-'
  return `${value.toFixed(1)}%`
}

// 格式化评分 (0-10)
export function formatScore(value: number | null | undefined): string {
  if (value === null || value === undefined) return '-'
  return value.toFixed(1)
}

// 获取评分颜色
export function getScoreColor(score: number): string {
  if (score >= 7) return 'text-accent-success'
  if (score >= 5) return 'text-accent-warning'
  return 'text-accent-danger'
}

// 获取评分背景颜色
export function getScoreBgColor(score: number): string {
  if (score >= 7) return 'bg-accent-success'
  if (score >= 5) return 'bg-accent-warning'
  return 'bg-accent-danger'
}

// 格式化日期
export function formatDate(dateString: string | null | undefined): string {
  if (!dateString) return '-'
  try {
    const date = new Date(dateString)
    // 检查日期是否有效
    if (isNaN(date.getTime())) return '-'
    return new Intl.DateTimeFormat('zh-CN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    }).format(date)
  } catch {
    return '-'
  }
}

// 格式化相对时间
export function formatRelativeTime(dateString: string | null | undefined): string {
  if (!dateString) return '-'
  try {
    const date = new Date(dateString)
    if (isNaN(date.getTime())) return '-'
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

    if (diffDays === 0) return '今天'
    if (diffDays === 1) return '昨天'
    if (diffDays < 7) return `${diffDays}天前`
    if (diffDays < 30) return `${Math.floor(diffDays / 7)}周前`
    if (diffDays < 365) return `${Math.floor(diffDays / 30)}个月前`
    return `${Math.floor(diffDays / 365)}年前`
  } catch {
    return '-'
  }
}

// 截断文本
export function truncateText(text: string | null | undefined, maxLength: number): string {
  if (!text) return '-'
  if (text.length <= maxLength) return text
  return text.slice(0, maxLength) + '...'
}

// 计算收入变化百分比
export function calculateRevenueChange(
  current: number | null | undefined,
  previous: number | null | undefined
): number | null {
  if (current === null || current === undefined) return null
  if (previous === null || previous === undefined || previous === 0) return null
  return ((current - previous) / previous) * 100
}

// 获取收入趋势图标
export function getRevenueTrendIcon(change: number | null): 'up' | 'down' | 'neutral' {
  if (change === null) return 'neutral'
  if (change > 5) return 'up'
  if (change < -5) return 'down'
  return 'neutral'
}

// 延迟函数
export function delay(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms))
}

// 生成动画延迟样式
export function getAnimationDelay(index: number, baseDelay: number = 50): string {
  return `${index * baseDelay}ms`
}
