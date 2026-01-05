'use client'

import { cn } from '@/lib/utils'
import { Check, LucideIcon } from 'lucide-react'

interface QuickActionCardProps {
  icon: LucideIcon
  title: string
  description: string
  isActive?: boolean
  onClick: () => void
  gradient?: string
}

export function QuickActionCard({
  icon: Icon,
  title,
  description,
  isActive = false,
  onClick,
  gradient = 'from-accent-primary to-accent-secondary',
}: QuickActionCardProps) {
  return (
    <button
      onClick={onClick}
      className={cn(
        'w-full flex items-center gap-3 p-3 rounded-xl border transition-all duration-200 text-left',
        isActive
          ? 'bg-accent-primary/10 border-accent-primary/30'
          : 'bg-surface/50 border-surface-border/50 hover:bg-surface hover:border-surface-border'
      )}
    >
      <div
        className={cn(
          'w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0',
          isActive
            ? `bg-gradient-to-br ${gradient}`
            : 'bg-background-secondary'
        )}
      >
        <Icon
          className={cn(
            'h-4 w-4',
            isActive ? 'text-white' : 'text-content-muted'
          )}
        />
      </div>
      <div className="flex-1 min-w-0">
        <div className={cn(
          'text-sm font-medium',
          isActive ? 'text-accent-primary' : 'text-content-primary'
        )}>
          {title}
        </div>
        <div className="text-xs text-content-muted truncate">
          {description}
        </div>
      </div>
      {isActive && (
        <div className="w-5 h-5 rounded-full bg-accent-primary flex items-center justify-center flex-shrink-0">
          <Check className="h-3 w-3 text-white" />
        </div>
      )}
    </button>
  )
}
