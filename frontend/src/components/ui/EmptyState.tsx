'use client'

import { Card } from '@/components/ui/Card'
import { LucideIcon } from 'lucide-react'
import Link from 'next/link'

interface EmptyStateProps {
  icon: LucideIcon
  title: string
  description: string
  actionLabel?: string
  actionHref?: string
  className?: string
}

export function EmptyState({
  icon: Icon,
  title,
  description,
  actionLabel,
  actionHref,
  className
}: EmptyStateProps) {
  return (
    <Card className={`text-center py-16 ${className || ''}`}>
      <div className="w-20 h-20 mx-auto mb-4 rounded-full bg-brand-500/10 flex items-center justify-center">
        <Icon className="h-10 w-10 text-brand-500" />
      </div>
      <h3 className="text-lg font-semibold text-content-primary mb-2">
        {title}
      </h3>
      <p className="text-sm text-slate-600 dark:text-slate-400 mb-6 max-w-md mx-auto">
        {description}
      </p>
      {actionLabel && actionHref && (
        <Link 
          href={actionHref} 
          className="inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium bg-surface text-content-secondary border border-surface-border hover:bg-surface-hover hover:text-content-primary active:bg-surface-hover active:scale-95 transition-all duration-150 cursor-pointer"
        >
          {actionLabel}
        </Link>
      )}
    </Card>
  )
}
