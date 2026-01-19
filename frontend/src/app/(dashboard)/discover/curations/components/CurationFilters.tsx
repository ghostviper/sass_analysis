'use client'

import { useLocale } from '@/contexts/LocaleContext'
import { Filter, SortAsc, Sparkles, Brain, TrendingUp, Zap, Target } from 'lucide-react'

interface CurationFiltersProps {
  selectedType: string
  onTypeChange: (type: string) => void
  sortBy: 'date' | 'products'
  onSortChange: (sort: 'date' | 'products') => void
  totalCount: number
  filteredCount: number
}

export function CurationFilters({
  selectedType,
  onTypeChange,
  sortBy,
  onSortChange,
  totalCount,
  filteredCount,
}: CurationFiltersProps) {
  const { locale } = useLocale()
  const isEn = locale === 'en'

  const types = [
    { 
      value: 'all', 
      label: isEn ? 'All' : '全部',
      icon: Sparkles,
      color: 'violet'
    },
    { 
      value: 'contrast', 
      label: isEn ? 'Contrast' : '对比反差',
      icon: TrendingUp,
      color: 'amber'
    },
    { 
      value: 'cognitive', 
      label: isEn ? 'Cognitive' : '认知颠覆',
      icon: Brain,
      color: 'emerald'
    },
    { 
      value: 'action', 
      label: isEn ? 'Action' : '行动建议',
      icon: Zap,
      color: 'green'
    },
    { 
      value: 'niche', 
      label: isEn ? 'Niche' : '利基场景',
      icon: Target,
      color: 'teal'
    },
  ]

  return (
    <div className="space-y-4">
      {/* 类型筛选 */}
      <div className="flex flex-wrap items-center gap-3">
        <div className="flex items-center gap-2 text-sm font-medium text-content-secondary">
          <Filter className="h-4 w-4" />
          <span>{isEn ? 'Type' : '类型'}</span>
        </div>
        <div className="flex flex-wrap gap-2">
          {types.map((type) => {
            const Icon = type.icon
            const isActive = selectedType === type.value
            
            // 定义完整的类名映射
            const activeColorClasses: Record<string, string> = {
              violet: 'bg-violet-500/10 text-violet-600 dark:text-violet-400 border border-violet-500/20',
              amber: 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20',
              emerald: 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20',
              blue: 'bg-blue-500/10 text-blue-600 dark:text-blue-400 border border-blue-500/20',
              green: 'bg-green-500/10 text-green-600 dark:text-green-400 border border-green-500/20',
              teal: 'bg-teal-500/10 text-teal-600 dark:text-teal-400 border border-teal-500/20',
            }
            
            return (
              <button
                key={type.value}
                onClick={() => onTypeChange(type.value)}
                className={`
                  flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-all
                  ${isActive 
                    ? activeColorClasses[type.color] || activeColorClasses.violet
                    : 'bg-surface/50 text-content-muted hover:bg-surface hover:text-content-primary border border-surface-border/50'
                  }
                `}
              >
                <Icon className="h-3.5 w-3.5" />
                <span>{type.label}</span>
                {isActive && type.value !== 'all' && (
                  <span className="ml-1 px-1.5 py-0.5 rounded text-xs bg-current/10">
                    {filteredCount}
                  </span>
                )}
              </button>
            )
          })}
        </div>
      </div>

      {/* 排序 */}
      <div className="flex flex-wrap items-center gap-3">
        <div className="flex items-center gap-2 text-sm font-medium text-content-secondary">
          <SortAsc className="h-4 w-4" />
          <span>{isEn ? 'Sort by' : '排序'}</span>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => onSortChange('date')}
            className={`
              px-3 py-1.5 rounded-lg text-sm font-medium transition-all
              ${sortBy === 'date'
                ? 'bg-brand-500/10 text-brand-600 dark:text-brand-400 border border-brand-500/20'
                : 'bg-surface/50 text-content-muted hover:bg-surface hover:text-content-primary border border-surface-border/50'
              }
            `}
          >
            {isEn ? 'Latest' : '最新'}
          </button>
          <button
            onClick={() => onSortChange('products')}
            className={`
              px-3 py-1.5 rounded-lg text-sm font-medium transition-all
              ${sortBy === 'products'
                ? 'bg-brand-500/10 text-brand-600 dark:text-brand-400 border border-brand-500/20'
                : 'bg-surface/50 text-content-muted hover:bg-surface hover:text-content-primary border border-surface-border/50'
              }
            `}
          >
            {isEn ? 'Most Products' : '产品最多'}
          </button>
        </div>
      </div>

      {/* 结果统计 */}
      {selectedType !== 'all' && (
        <div className="flex items-center gap-2 text-sm text-content-muted">
          <span>
            {isEn 
              ? `Showing ${filteredCount} of ${totalCount} curations`
              : `显示 ${filteredCount} / ${totalCount} 条策展`
            }
          </span>
          {filteredCount < totalCount && (
            <button
              onClick={() => onTypeChange('all')}
              className="text-brand-500 hover:text-brand-600 font-medium"
            >
              {isEn ? 'Clear filter' : '清除筛选'}
            </button>
          )}
        </div>
      )}
    </div>
  )
}
