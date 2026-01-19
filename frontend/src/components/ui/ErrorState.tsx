'use client'

import { AlertCircle } from 'lucide-react'
import { Card } from '@/components/ui/Card'
import { useLocale } from '@/contexts/LocaleContext'

interface ErrorStateProps {
  title?: string
  message?: string
  onRetry?: () => void
  className?: string
}

export function ErrorState({ 
  title, 
  message, 
  onRetry,
  className 
}: ErrorStateProps) {
  const { locale } = useLocale()
  const isEn = locale === 'en'
  
  return (
    <Card className={`text-center py-12 ${className || ''}`}>
      <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-red-500/10 flex items-center justify-center">
        <AlertCircle className="h-8 w-8 text-red-500" />
      </div>
      <h3 className="text-lg font-semibold text-content-primary mb-2">
        {title || (isEn ? 'Failed to load' : '加载失败')}
      </h3>
      <p className="text-sm text-slate-600 dark:text-slate-400 mb-4 max-w-md mx-auto">
        {message || (isEn ? 'Something went wrong. Please try again.' : '出了点问题，请重试')}
      </p>
      {onRetry && (
        <button 
          onClick={onRetry}
          className="inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium bg-brand-500 text-white hover:bg-brand-600 active:bg-brand-700 active:scale-95 transition-all duration-150 cursor-pointer"
        >
          {isEn ? 'Retry' : '重试'}
        </button>
      )}
    </Card>
  )
}
