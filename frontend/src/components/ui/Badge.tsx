'use client'

import { cn } from '@/lib/utils'
import {
  Waves,
  Rocket,
  Scale,
  Crown,
  Flame,
  AlertTriangle,
  LucideIcon,
} from 'lucide-react'
import { MarketType, MARKET_TYPE_CONFIG } from '@/types'

interface BadgeProps {
  children: React.ReactNode
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info' | 'muted'
  size?: 'sm' | 'md'
  className?: string
}

export function Badge({
  children,
  variant = 'default',
  size = 'sm',
  className,
}: BadgeProps) {
  const variantStyles = {
    default: 'bg-surface text-content-secondary border border-surface-border',
    success: 'bg-accent-success/10 text-accent-success',
    warning: 'bg-accent-warning/10 text-accent-warning',
    danger: 'bg-accent-danger/10 text-accent-danger',
    info: 'bg-accent-primary/10 text-accent-primary',
    muted: 'bg-background-tertiary text-content-muted',
  }

  const sizeStyles = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-3 py-1 text-sm',
  }

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 rounded-full font-medium',
        variantStyles[variant],
        sizeStyles[size],
        className
      )}
    >
      {children}
    </span>
  )
}

// 市场类型专用 Badge
interface MarketTypeBadgeProps {
  type: MarketType
  showIcon?: boolean
  size?: 'sm' | 'md'
  className?: string
}

const marketIcons: Record<string, LucideIcon> = {
  water: Waves,
  rocket: Rocket,
  'scale-balanced': Scale,
  crown: Crown,
  fire: Flame,
  'triangle-exclamation': AlertTriangle,
}

export function MarketTypeBadge({
  type,
  showIcon = true,
  size = 'sm',
  className,
}: MarketTypeBadgeProps) {
  const config = MARKET_TYPE_CONFIG[type]
  const Icon = marketIcons[config.icon]

  const colorStyles: Record<MarketType, string> = {
    blue_ocean: 'bg-market-blue-ocean/10 text-market-blue-ocean border border-market-blue-ocean/20',
    emerging: 'bg-market-emerging/10 text-market-emerging border border-market-emerging/20',
    moderate: 'bg-market-moderate/10 text-market-moderate border border-market-moderate/20',
    concentrated: 'bg-market-concentrated/10 text-market-concentrated border border-market-concentrated/20',
    red_ocean: 'bg-market-red-ocean/10 text-market-red-ocean border border-market-red-ocean/20',
    weak_demand: 'bg-market-weak-demand/10 text-market-weak-demand border border-market-weak-demand/20',
  }

  const sizeStyles = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-3 py-1 text-sm',
  }

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 rounded-full font-medium',
        colorStyles[type],
        sizeStyles[size],
        className
      )}
    >
      {showIcon && Icon && (
        <Icon className="w-3 h-3" />
      )}
      {config.label}
    </span>
  )
}

// 复杂度 Badge
interface ComplexityBadgeProps {
  level: 'low' | 'medium' | 'high'
  size?: 'sm' | 'md'
  className?: string
}

export function ComplexityBadge({
  level,
  size = 'sm',
  className,
}: ComplexityBadgeProps) {
  const config = {
    low: { label: '低复杂度', color: 'bg-accent-success/10 text-accent-success' },
    medium: { label: '中复杂度', color: 'bg-accent-warning/10 text-accent-warning' },
    high: { label: '高复杂度', color: 'bg-accent-danger/10 text-accent-danger' },
  }

  const sizeStyles = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-3 py-1 text-sm',
  }

  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full font-medium',
        config[level].color,
        sizeStyles[size],
        className
      )}
    >
      {config[level].label}
    </span>
  )
}
