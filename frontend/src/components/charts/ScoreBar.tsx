'use client'

import { cn } from '@/lib/utils'
import { formatScore, getScoreColor, getScoreBgColor } from '@/lib/utils'

interface ScoreBarProps {
  label: string
  score: number
  maxScore?: number
  showValue?: boolean
  size?: 'sm' | 'md' | 'lg'
  className?: string
  delay?: number
}

export function ScoreBar({
  label,
  score,
  maxScore = 10,
  showValue = true,
  size = 'md',
  className,
  delay = 0,
}: ScoreBarProps) {
  const percentage = (score / maxScore) * 100
  const scoreColor = getScoreColor(score)
  const scoreBgColor = getScoreBgColor(score)

  const sizeStyles = {
    sm: { bar: 'h-1.5', text: 'text-xs' },
    md: { bar: 'h-2', text: 'text-sm' },
    lg: { bar: 'h-3', text: 'text-base' },
  }

  return (
    <div className={cn('space-y-1.5', className)}>
      <div className="flex items-center justify-between">
        <span className={cn('text-content-secondary', sizeStyles[size].text)}>{label}</span>
        {showValue && (
          <span className={cn('font-mono font-medium', scoreColor, sizeStyles[size].text)}>
            {formatScore(score)}
          </span>
        )}
      </div>
      <div className={cn('score-bar', sizeStyles[size].bar)}>
        <div
          className={cn('score-bar-fill', scoreBgColor)}
          style={{
            width: `${percentage}%`,
            animationDelay: `${delay}ms`,
          }}
        />
      </div>
    </div>
  )
}

// 评分卡片组件
interface ScoreCardProps {
  label: string
  score: number
  description?: string
  icon?: React.ReactNode
  className?: string
}

export function ScoreCard({
  label,
  score,
  description,
  icon,
  className,
}: ScoreCardProps) {
  const scoreColor = getScoreColor(score)
  const percentage = (score / 10) * 100

  return (
    <div className={cn('card relative overflow-hidden', className)}>
      {/* 背景进度条 */}
      <div
        className={cn(
          'absolute bottom-0 left-0 h-1 transition-all duration-700',
          getScoreBgColor(score)
        )}
        style={{ width: `${percentage}%` }}
      />

      <div className="relative">
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-2">
            {icon && (
              <span className="text-content-muted">{icon}</span>
            )}
            <span className="text-sm text-content-secondary">{label}</span>
          </div>
          <span className={cn('text-2xl font-display font-bold', scoreColor)}>
            {formatScore(score)}
          </span>
        </div>

        {description && (
          <p className="text-xs text-content-muted">{description}</p>
        )}
      </div>
    </div>
  )
}

// 综合评分展示
interface OverallScoreProps {
  score: number
  label?: string
  subtitle?: string
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

export function OverallScore({
  score,
  label = '综合评分',
  subtitle,
  size = 'md',
  className,
}: OverallScoreProps) {
  const percentage = (score / 10) * 100
  const scoreColor = getScoreColor(score)
  const circumference = 2 * Math.PI * 45

  const sizeStyles = {
    sm: { container: 'w-24 h-24', text: 'text-2xl', label: 'text-xs' },
    md: { container: 'w-32 h-32', text: 'text-3xl', label: 'text-sm' },
    lg: { container: 'w-40 h-40', text: 'text-4xl', label: 'text-base' },
  }

  const getStrokeColor = (score: number) => {
    if (score >= 7) return '#10b981' // accent-success
    if (score >= 5) return '#f59e0b' // accent-warning
    return '#ef4444' // accent-danger
  }

  return (
    <div className={cn('flex flex-col items-center', className)}>
      <div className={cn('relative', sizeStyles[size].container)}>
        {/* 背景圆环 */}
        <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
          <circle
            cx="50"
            cy="50"
            r="45"
            fill="none"
            stroke="currentColor"
            strokeWidth="8"
            className="text-background-tertiary"
          />
          {/* 进度圆环 */}
          <circle
            cx="50"
            cy="50"
            r="45"
            fill="none"
            stroke={getStrokeColor(score)}
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={circumference - (percentage / 100) * circumference}
            className="transition-all duration-1000 ease-out"
          />
        </svg>

        {/* 中心内容 */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className={cn('font-display font-bold', scoreColor, sizeStyles[size].text)}>
            {formatScore(score)}
          </span>
          <span className={cn('text-content-muted', sizeStyles[size].label)}>{label}</span>
        </div>
      </div>

      {subtitle && (
        <p className="mt-2 text-sm text-content-tertiary text-center">{subtitle}</p>
      )}
    </div>
  )
}
