'use client'

import { useState, useRef, useEffect } from 'react'
import { Search, TrendingUp, Compass, Users, RefreshCw, Loader2 } from 'lucide-react'
import { cn } from '@/lib/utils'
import { useLocale } from '@/contexts/LocaleContext'

interface SuggestedPromptsProps {
  onSelect: (prompt: string) => void
}

// 默认问题（静态）
const getDefaultPrompts = (t: (key: string) => string) => ({
  product: [
    t('assistant.prompts.product1'),
    t('assistant.prompts.product2'),
    t('assistant.prompts.product3'),
    t('assistant.prompts.product4'),
  ],
  trend: [
    t('assistant.prompts.trend1'),
    t('assistant.prompts.trend2'),
    t('assistant.prompts.trend3'),
    t('assistant.prompts.trend4'),
  ],
  career: [
    t('assistant.prompts.career1'),
    t('assistant.prompts.career2'),
    t('assistant.prompts.career3'),
    t('assistant.prompts.career4'),
  ],
  developer: [
    t('assistant.prompts.developer1'),
    t('assistant.prompts.developer2'),
    t('assistant.prompts.developer3'),
    t('assistant.prompts.developer4'),
  ],
})

export function SuggestedPrompts({ onSelect }: SuggestedPromptsProps) {
  const { t } = useLocale()
  const [expandedId, setExpandedId] = useState<string | null>(null)
  const [dynamicPrompts, setDynamicPrompts] = useState<Record<string, string[]>>({})
  const [isRefreshing, setIsRefreshing] = useState(false)
  const panelRef = useRef<HTMLDivElement>(null)

  // 点击外部关闭弹出层
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (expandedId && panelRef.current && !panelRef.current.contains(e.target as Node)) {
        setExpandedId(null)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [expandedId])

  const defaultPrompts = getDefaultPrompts(t)

  const categories = [
    {
      id: 'product',
      icon: Search,
      label: t('assistant.categories.product'),
      description: t('assistant.categories.productDesc'),
    },
    {
      id: 'trend',
      icon: TrendingUp,
      label: t('assistant.categories.trend'),
      description: t('assistant.categories.trendDesc'),
    },
    {
      id: 'career',
      icon: Compass,
      label: t('assistant.categories.career'),
      description: t('assistant.categories.careerDesc'),
    },
    {
      id: 'developer',
      icon: Users,
      label: t('assistant.categories.developer'),
      description: t('assistant.categories.developerDesc'),
    },
  ]

  // 获取当前分类的问题列表
  const getPrompts = (categoryId: string): string[] => {
    return dynamicPrompts[categoryId] || defaultPrompts[categoryId as keyof typeof defaultPrompts] || []
  }

  // 换一批 - 调用后端生成新问题
  const handleRefresh = async (categoryId: string) => {
    if (isRefreshing) return
    
    setIsRefreshing(true)
    try {
      const response = await fetch('/api/chat/suggest-prompts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ category: categoryId })
      })
      
      if (response.ok) {
        const data = await response.json()
        if (data.prompts && Array.isArray(data.prompts)) {
          setDynamicPrompts(prev => ({
            ...prev,
            [categoryId]: data.prompts
          }))
        }
      }
    } catch (error) {
      console.error('Failed to refresh prompts:', error)
    } finally {
      setIsRefreshing(false)
    }
  }

  const handleClick = (id: string) => {
    setExpandedId(expandedId === id ? null : id)
  }

  const handlePromptSelect = (prompt: string) => {
    onSelect(prompt)
    setExpandedId(null)
  }

  const expandedCategory = categories.find(c => c.id === expandedId)
  const currentPrompts = expandedId ? getPrompts(expandedId) : []

  return (
    <div className="w-full">
      {/* 分类标签按钮 - 胶囊式设计 */}
      <div className="flex flex-wrap justify-center gap-3">
        {categories.map((category) => {
          const isExpanded = expandedId === category.id
          const Icon = category.icon
          return (
            <button
              key={category.id}
              onClick={() => handleClick(category.id)}
              className={cn(
                'group inline-flex items-center gap-2 px-4 py-2 rounded-full transition-all duration-200 text-sm border cursor-pointer',
                isExpanded
                  ? 'bg-gradient-to-r from-brand-500/15 to-accent-secondary/15 text-brand-600 dark:text-brand-400 border-brand-500/40 shadow-md shadow-brand-500/10 scale-[1.02]'
                  : 'bg-surface/80 border-surface-border/60 text-content-primary hover:border-brand-500/40 hover:bg-brand-500/5 hover:text-brand-600 dark:hover:text-brand-400 hover:shadow-md'
              )}
            >
              <Icon
                className={cn(
                  'h-3.5 w-3.5 transition-all duration-200',
                  isExpanded ? 'text-brand-500' : 'text-brand-400 group-hover:text-brand-500'
                )}
              />
              <span className="font-semibold tracking-wide">{category.label}</span>
            </button>
          )
        })}
      </div>

      {/* 展开的问题面板 - 向下弹出 */}
      {expandedCategory && (
        <div
          ref={panelRef}
          className={cn(
            'mt-4 z-20 max-h-[50vh] overflow-y-auto',
            'transition-all duration-300 ease-out origin-top',
            expandedId !== null
              ? 'opacity-100 scale-100 translate-y-0'
              : 'opacity-0 scale-95 -translate-y-2'
          )}
        >
          <div className="bg-surface/95 backdrop-blur-xl rounded-2xl border border-surface-border/80 shadow-xl shadow-black/10 overflow-hidden">
            {/* 内容区域 */}
            <div className="p-4">
              {/* 标题区 - 简洁风格 */}
              <div className="flex items-center gap-3 mb-3 pb-3 border-b border-surface-border/50">
                <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-brand-500/15 to-accent-secondary/15 flex items-center justify-center ring-1 ring-brand-500/10">
                  <expandedCategory.icon className="h-4 w-4 text-brand-500" />
                </div>
                <div className="flex-1">
                  <h3 className="text-sm font-bold text-content-primary tracking-tight">
                    {expandedCategory.label}
                  </h3>
                  <p className="text-xs text-content-tertiary mt-0.5 font-medium">
                    {expandedCategory.description}
                  </p>
                </div>
                {/* 换一批按钮 */}
                <button
                  onClick={() => handleRefresh(expandedCategory.id)}
                  disabled={isRefreshing}
                  className={cn(
                    'inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all',
                    'text-content-secondary hover:text-brand-600 dark:hover:text-brand-400',
                    'hover:bg-brand-500/10',
                    isRefreshing && 'opacity-50 cursor-not-allowed'
                  )}
                  title={t('assistant.refresh')}
                >
                  <RefreshCw className={cn('h-3.5 w-3.5', isRefreshing && 'animate-spin')} />
                  <span>{t('assistant.refresh')}</span>
                </button>
              </div>

              {/* 问题列表 - 简洁卡片风格 */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                {currentPrompts.map((prompt, idx) => (
                  <button
                    key={idx}
                    onClick={() => handlePromptSelect(prompt)}
                    className={cn(
                      'text-left text-[0.8125rem] px-3 py-2.5 rounded-xl transition-all duration-200',
                      'bg-background-tertiary/40 hover:bg-background-tertiary/70',
                      'text-content-secondary hover:text-content-primary',
                      'border border-transparent hover:border-brand-500/20',
                      'font-medium leading-relaxed'
                    )}
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
