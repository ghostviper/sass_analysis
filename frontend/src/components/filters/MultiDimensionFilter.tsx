'use client'

import { useState, useCallback } from 'react'
import { ChevronDown, ChevronUp, X, Filter, SlidersHorizontal } from 'lucide-react'
import { useLocale } from '@/contexts/LocaleContext'
import { cn } from '@/lib/utils'
import type { FilterDimensions } from '@/types'

interface FilterState {
  [key: string]: string[]
}

interface MultiDimensionFilterProps {
  dimensions: FilterDimensions
  value: FilterState
  onChange: (filters: FilterState) => void
  className?: string
}

export function MultiDimensionFilter({
  dimensions,
  value,
  onChange,
  className = '',
}: MultiDimensionFilterProps) {
  const { locale } = useLocale()
  const [expandedDimensions, setExpandedDimensions] = useState<string[]>([])

  const toggleDimension = useCallback((dimensionKey: string) => {
    setExpandedDimensions(prev =>
      prev.includes(dimensionKey)
        ? prev.filter(k => k !== dimensionKey)
        : [...prev, dimensionKey]
    )
  }, [])

  const toggleOption = useCallback((dimensionKey: string, optionValue: string) => {
    const currentValues = value[dimensionKey] || []
    const newValues = currentValues.includes(optionValue)
      ? currentValues.filter(v => v !== optionValue)
      : [...currentValues, optionValue]

    onChange({
      ...value,
      [dimensionKey]: newValues,
    })
  }, [value, onChange])

  const clearDimension = useCallback((dimensionKey: string) => {
    const newValue = { ...value }
    delete newValue[dimensionKey]
    onChange(newValue)
  }, [value, onChange])

  const clearAll = useCallback(() => {
    onChange({})
  }, [onChange])

  // 计算已选择的筛选条件数量
  const selectedCount = Object.values(value).reduce(
    (sum, arr) => sum + (arr?.length || 0),
    0
  )

  const getLabel = (dimension: { label: string; label_en: string }) => {
    return locale === 'zh-CN' ? dimension.label : dimension.label_en
  }

  const getOptionLabel = (option: { label: string; label_en: string }) => {
    return locale === 'zh-CN' ? option.label : option.label_en
  }

  return (
    <div className={cn(
      'rounded-2xl border border-surface-border/50 bg-surface/80 backdrop-blur-sm',
      className
    )}>
      {/* 头部 */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-surface-border/40">
        <div className="flex items-center gap-2">
          <SlidersHorizontal className="w-4 h-4 text-content-muted" />
          <span className="text-sm font-medium text-content-primary">
            {locale === 'zh-CN' ? '多维度筛选' : 'Multi-dimension Filter'}
          </span>
          {selectedCount > 0 && (
            <span className="px-2 py-0.5 text-xs bg-brand-500 text-white rounded-full font-medium">
              {selectedCount}
            </span>
          )}
        </div>
        {selectedCount > 0 && (
          <button
            onClick={clearAll}
            className="text-xs text-content-muted hover:text-brand-500 transition-colors font-medium"
          >
            {locale === 'zh-CN' ? '清除全部' : 'Clear All'}
          </button>
        )}
      </div>

      {/* 已选择的标签 */}
      {selectedCount > 0 && (
        <div className="px-4 py-2.5 border-b border-surface-border/40 flex flex-wrap gap-2">
          {Object.entries(value).map(([dimensionKey, selectedValues]) =>
            selectedValues?.map(optionValue => {
              const dimension = dimensions[dimensionKey as keyof FilterDimensions]
              const option = dimension?.options.find(o => o.value === optionValue)
              if (!dimension || !option) return null

              return (
                <span
                  key={`${dimensionKey}-${optionValue}`}
                  className="inline-flex items-center gap-1.5 px-2.5 py-1 text-xs bg-brand-500/10 text-brand-600 dark:text-brand-400 rounded-full font-medium"
                >
                  <span className="text-content-muted">{getLabel(dimension)}:</span>
                  {getOptionLabel(option)}
                  <button
                    onClick={() => toggleOption(dimensionKey, optionValue)}
                    className="ml-0.5 hover:text-red-500 transition-colors"
                  >
                    <X className="w-3 h-3" />
                  </button>
                </span>
              )
            })
          )}
        </div>
      )}

      {/* 筛选维度列表 */}
      <div className="divide-y divide-surface-border/40">
        {Object.entries(dimensions).map(([dimensionKey, dimension]) => {
          const isExpanded = expandedDimensions.includes(dimensionKey)
          const selectedValues = value[dimensionKey] || []
          const hasSelection = selectedValues.length > 0

          return (
            <div key={dimensionKey}>
              {/* 维度标题 */}
              <button
                onClick={() => toggleDimension(dimensionKey)}
                className="w-full flex items-center justify-between px-4 py-3 hover:bg-surface-hover/50 transition-colors"
              >
                <div className="flex items-center gap-2">
                  <span className="text-sm text-content-primary font-medium">
                    {getLabel(dimension)}
                  </span>
                  {hasSelection && (
                    <span className="px-1.5 py-0.5 text-xs bg-brand-500/10 text-brand-500 rounded font-medium">
                      {selectedValues.length}
                    </span>
                  )}
                </div>
                {isExpanded ? (
                  <ChevronUp className="w-4 h-4 text-content-muted" />
                ) : (
                  <ChevronDown className="w-4 h-4 text-content-muted" />
                )}
              </button>

              {/* 选项列表 */}
              {isExpanded && (
                <div className="px-4 pb-3 flex flex-wrap gap-2">
                  {dimension.options.map(option => {
                    const isSelected = selectedValues.includes(option.value)

                    return (
                      <button
                        key={option.value}
                        onClick={() => toggleOption(dimensionKey, option.value)}
                        className={cn(
                          'px-3 py-1.5 text-xs rounded-full border transition-all duration-200 font-medium',
                          isSelected
                            ? 'bg-brand-500 text-white border-brand-500 shadow-sm'
                            : 'bg-surface/60 text-content-secondary border-surface-border/60 hover:border-brand-500/50 hover:text-brand-500'
                        )}
                      >
                        {getOptionLabel(option)}
                      </button>
                    )
                  })}
                  {hasSelection && (
                    <button
                      onClick={() => clearDimension(dimensionKey)}
                      className="px-3 py-1.5 text-xs text-content-muted hover:text-red-500 transition-colors font-medium"
                    >
                      {locale === 'zh-CN' ? '清除' : 'Clear'}
                    </button>
                  )}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}

// 紧凑版筛选器（用于移动端或侧边栏）
export function CompactFilter({
  dimensions,
  value,
  onChange,
  className = '',
}: MultiDimensionFilterProps) {
  const { locale } = useLocale()
  const [isOpen, setIsOpen] = useState(false)

  const selectedCount = Object.values(value).reduce(
    (sum, arr) => sum + (arr?.length || 0),
    0
  )

  return (
    <div className={cn('relative', className)}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          'flex items-center gap-2 px-4 py-2 rounded-xl border transition-all duration-200',
          'bg-surface/80 backdrop-blur-sm border-surface-border/50',
          'hover:border-brand-500/30 hover:shadow-sm',
          selectedCount > 0 && 'border-brand-500/30'
        )}
      >
        <Filter className="w-4 h-4 text-content-muted" />
        <span className="text-sm text-content-primary font-medium">
          {locale === 'zh-CN' ? '高级筛选' : 'Advanced Filter'}
        </span>
        {selectedCount > 0 && (
          <span className="px-2 py-0.5 text-xs bg-brand-500 text-white rounded-full font-medium">
            {selectedCount}
          </span>
        )}
      </button>

      {isOpen && (
        <>
          {/* 遮罩层 */}
          <div
            className="fixed inset-0 bg-black/40 backdrop-blur-sm z-40"
            onClick={() => setIsOpen(false)}
          />
          {/* 筛选面板 */}
          <div className="fixed inset-x-4 bottom-4 top-auto max-h-[70vh] overflow-auto bg-surface rounded-2xl shadow-xl border border-surface-border/50 z-50 md:absolute md:inset-auto md:right-0 md:top-full md:mt-2 md:w-80">
            <MultiDimensionFilter
              dimensions={dimensions}
              value={value}
              onChange={onChange}
            />
            <div className="sticky bottom-0 p-4 bg-surface border-t border-surface-border/40">
              <button
                onClick={() => setIsOpen(false)}
                className="w-full py-2.5 bg-brand-500 text-white rounded-xl hover:bg-brand-600 transition-colors font-medium shadow-sm"
              >
                {locale === 'zh-CN' ? '确定' : 'Apply'}
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  )
}

export default MultiDimensionFilter
