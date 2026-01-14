'use client'

import { useState, useRef, useEffect } from 'react'
import { cn } from '@/lib/utils'
import {
  Search,
  X,
  Check,
  ChevronDown,
  Loader2,
  Package,
  User,
  Link,
  Trash2,
} from 'lucide-react'
import { useLocale } from '@/contexts/LocaleContext'
import type { Startup } from '@/types'

// 创作者类型
interface Creator {
  id: number
  username: string
  display_name?: string
  avatar_url?: string
  total_revenue?: number
  product_count?: number
}

// 已选择的项目
export interface SelectedItem {
  type: 'product' | 'url' | 'creator'
  id: string
  name: string
  data?: Startup | Creator | string // 原始数据
}

interface ContextSelectorProps {
  selectedItems: SelectedItem[]
  onItemsChange: (items: SelectedItem[]) => void
  products: Startup[]
  onProductSearch: (query: string) => void
  isSearchingProducts: boolean
  creators?: Creator[]
  onCreatorSearch?: (query: string) => void
  isSearchingCreators?: boolean
  maxItems?: number
}

export function ContextSelector({
  selectedItems,
  onItemsChange,
  products,
  onProductSearch,
  isSearchingProducts,
  creators = [],
  onCreatorSearch,
  isSearchingCreators = false,
  maxItems = 5,
}: ContextSelectorProps) {
  const { t } = useLocale()
  const [isOpen, setIsOpen] = useState(false)
  const [activeTab, setActiveTab] = useState<'product' | 'creator'>('product')
  const [productQuery, setProductQuery] = useState('')
  const [creatorQuery, setCreatorQuery] = useState('')
  const [urlInput, setUrlInput] = useState('')
  const menuRef = useRef<HTMLDivElement>(null)

  // 点击外部关闭
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setIsOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  // 产品搜索 - 直接调用，父组件处理防抖
  const handleProductQueryChange = (query: string) => {
    setProductQuery(query)
    onProductSearch(query)
  }

  // 创作者搜索 - 直接调用，父组件处理防抖
  const handleCreatorQueryChange = (query: string) => {
    setCreatorQuery(query)
    if (onCreatorSearch) {
      onCreatorSearch(query)
    }
  }

  const toggleProduct = (product: Startup) => {
    const exists = selectedItems.find(item => item.type === 'product' && item.id === String(product.id))
    if (exists) {
      onItemsChange(selectedItems.filter(item => !(item.type === 'product' && item.id === String(product.id))))
    } else if (selectedItems.length < maxItems) {
      onItemsChange([...selectedItems, {
        type: 'product',
        id: String(product.id),
        name: product.name,
        data: product,
      }])
    }
  }

  const toggleCreator = (creator: Creator) => {
    const exists = selectedItems.find(item => item.type === 'creator' && item.id === String(creator.id))
    if (exists) {
      onItemsChange(selectedItems.filter(item => !(item.type === 'creator' && item.id === String(creator.id))))
    } else if (selectedItems.length < maxItems) {
      onItemsChange([...selectedItems, {
        type: 'creator',
        id: String(creator.id),
        name: creator.display_name || `@${creator.username}`,
        data: creator,
      }])
    }
  }

  const addUrl = () => {
    if (!urlInput.trim()) return
    try {
      const url = new URL(urlInput.startsWith('http') ? urlInput : `https://${urlInput}`)
      const exists = selectedItems.find(item => item.type === 'url' && item.data === url.href)
      if (!exists && selectedItems.length < maxItems) {
        onItemsChange([...selectedItems, {
          type: 'url',
          id: `url-${Date.now()}`,
          name: url.hostname,
          data: url.href,
        }])
        setUrlInput('')
      }
    } catch {
      // Invalid URL
    }
  }

  const removeItem = (item: SelectedItem) => {
    onItemsChange(selectedItems.filter(i => i.id !== item.id))
  }

  const clearAll = () => {
    onItemsChange([])
  }

  // 按钮显示文本
  const getButtonText = () => {
    if (selectedItems.length === 0) {
      return t('assistant.contextSelector.title') || '关联分析'
    }
    if (selectedItems.length === 1) {
      const item = selectedItems[0]
      if (item.type === 'creator') {
        return `分析 ${item.name}`
      }
      return `分析 ${item.name}`
    }
    return `对比 ${selectedItems.length} 个对象`
  }

  const hasSelection = selectedItems.length > 0

  return (
    <div className="relative" ref={menuRef}>
      {/* 触发按钮 */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          'relative inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all duration-200',
          hasSelection
            ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 ring-1 ring-emerald-500/20'
            : 'text-content-muted hover:text-content-secondary hover:bg-surface-hover/50'
        )}
      >
        <Package className="h-3 w-3" />
        <span className="max-w-[120px] truncate">{getButtonText()}</span>
        <ChevronDown className={cn('h-2 w-2 transition-transform duration-200', isOpen && 'rotate-180')} />
        {hasSelection && (
          <span
            onClick={(e) => { e.stopPropagation(); clearAll() }}
            className="absolute -top-1.5 -right-1.5 w-4 h-4 flex items-center justify-center bg-content-muted hover:bg-content-secondary text-white rounded-full cursor-pointer transition-colors"
            title={t('assistant.contextSelector.clear') || '清空'}
          >
            <X className="h-2 w-2" />
          </span>
        )}
      </button>

      {/* 下拉面板 */}
      {isOpen && (
        <div className="absolute left-0 top-full mt-2 w-80 bg-background/95 backdrop-blur-xl border border-surface-border/80 rounded-xl shadow-xl z-50 overflow-hidden animate-in fade-in slide-in-from-top-2 duration-200">
          {/* Tab 切换 */}
          <div className="flex gap-1 p-2 border-b border-surface-border/50">
            <button
              onClick={() => setActiveTab('product')}
              className={cn(
                'flex-1 flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg text-xs font-semibold transition-all',
                activeTab === 'product'
                  ? 'bg-brand-500/10 text-brand-600 dark:text-brand-400'
                  : 'text-content-muted hover:bg-surface/60'
              )}
            >
              <Package className="h-3 w-3" />
              {t('assistant.contextSelector.products') || '产品'}
            </button>
            <button
              onClick={() => setActiveTab('creator')}
              className={cn(
                'flex-1 flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg text-xs font-semibold transition-all',
                activeTab === 'creator'
                  ? 'bg-brand-500/10 text-brand-600 dark:text-brand-400'
                  : 'text-content-muted hover:bg-surface/60'
              )}
            >
              <User className="h-3 w-3" />
              {t('assistant.contextSelector.creators') || '创作者'}
            </button>
          </div>

          {/* 内容区域 - 限制最大高度并允许滚动 */}
          <div className="p-2.5 max-h-[360px] overflow-y-auto">
            {activeTab === 'product' && (
              <div className="space-y-3">
                {/* 搜索已有产品 */}
                <div>
                  <div className="relative mb-2">
                    {isSearchingProducts ? (
                      <Loader2 className="absolute left-2.5 top-1/2 -translate-y-1/2 h-3 w-3 text-brand-500 animate-spin" />
                    ) : (
                      <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-3 w-3 text-content-muted" />
                    )}
                    <input
                      type="text"
                      value={productQuery}
                      onChange={(e) => handleProductQueryChange(e.target.value)}
                      placeholder={t('assistant.contextSelector.searchProducts') || '搜索已有产品...'}
                      className="w-full pl-8 pr-3 py-2 bg-surface/60 rounded-lg text-sm font-medium focus:outline-none focus:ring-1 focus:ring-brand-500/30 placeholder:text-content-muted/60"
                    />
                  </div>
                  <div className="max-h-28 overflow-y-auto space-y-0.5">
                    {products.length > 0 ? products.map((product) => {
                      const isSelected = selectedItems.some(item => item.type === 'product' && item.id === String(product.id))
                      return (
                        <button
                          key={product.id}
                          onClick={() => toggleProduct(product)}
                          disabled={!isSelected && selectedItems.length >= maxItems}
                          className={cn(
                            'w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left transition-all',
                            isSelected ? 'bg-brand-500/10' : 'hover:bg-surface/60',
                            !isSelected && selectedItems.length >= maxItems && 'opacity-50 cursor-not-allowed'
                          )}
                        >
                          <div className="w-7 h-7 rounded-lg bg-surface/60 flex items-center justify-center flex-shrink-0 overflow-hidden">
                            {product.logo_url ? (
                              <img src={product.logo_url} alt={product.name} className="w-full h-full object-cover" />
                            ) : (
                              <span className="text-[10px] font-semibold text-content-muted">
                                {product.name.slice(0, 2).toUpperCase()}
                              </span>
                            )}
                          </div>
                          <div className="flex-1 min-w-0">
                            <span className={cn('text-sm truncate block', isSelected ? 'text-content-primary font-semibold' : 'text-content-primary font-medium')}>
                              {product.name}
                            </span>
                            {product.revenue_30d && (
                              <span className="text-[10px] text-content-muted">
                                ${(product.revenue_30d / 1000).toFixed(1)}K/mo
                              </span>
                            )}
                          </div>
                          <div className={cn(
                            'w-4 h-4 rounded border-2 flex items-center justify-center transition-all flex-shrink-0',
                            isSelected ? 'bg-brand-500 border-brand-500' : 'border-content-muted/30'
                          )}>
                            {isSelected && <Check className="h-2.5 w-2.5 text-white" />}
                          </div>
                        </button>
                      )
                    }) : (
                      <p className="text-xs text-content-muted text-center py-3 font-medium">
                        {isSearchingProducts ? (t('assistant.searching') || '搜索中...') : (t('assistant.noProducts') || '暂无产品')}
                      </p>
                    )}
                  </div>
                </div>

                {/* 分隔线 */}
                <div className="flex items-center gap-2">
                  <div className="flex-1 h-px bg-surface-border/50" />
                  <span className="text-[10px] text-content-muted font-medium">
                    {t('assistant.contextSelector.orAddUrl') || '或添加外部链接'}
                  </span>
                  <div className="flex-1 h-px bg-surface-border/50" />
                </div>

                {/* 添加外部链接 */}
                <div className="flex gap-2">
                  <div className="relative flex-1">
                    <Link className="absolute left-2.5 top-1/2 -translate-y-1/2 h-3 w-3 text-content-muted" />
                    <input
                      type="url"
                      value={urlInput}
                      onChange={(e) => setUrlInput(e.target.value)}
                      onKeyDown={(e) => e.key === 'Enter' && addUrl()}
                      placeholder="https://..."
                      className="w-full pl-8 pr-3 py-2 bg-surface/60 rounded-lg text-sm font-medium focus:outline-none focus:ring-1 focus:ring-brand-500/30 placeholder:text-content-muted/60"
                    />
                  </div>
                  <button
                    onClick={addUrl}
                    disabled={!urlInput.trim() || selectedItems.length >= maxItems}
                    className={cn(
                      'px-3 py-2 rounded-lg text-xs font-semibold transition-all',
                      urlInput.trim() && selectedItems.length < maxItems
                        ? 'bg-brand-500/10 text-brand-600 dark:text-brand-400 hover:bg-brand-500/20'
                        : 'bg-surface/60 text-content-muted cursor-not-allowed'
                    )}
                  >
                    {t('assistant.contextSelector.add') || '添加'}
                  </button>
                </div>
              </div>
            )}

            {activeTab === 'creator' && (
              <div>
                <div className="relative mb-2">
                  {isSearchingCreators ? (
                    <Loader2 className="absolute left-2.5 top-1/2 -translate-y-1/2 h-3 w-3 text-brand-500 animate-spin" />
                  ) : (
                    <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-3 w-3 text-content-muted" />
                  )}
                  <input
                    type="text"
                    value={creatorQuery}
                    onChange={(e) => handleCreatorQueryChange(e.target.value)}
                    placeholder={t('assistant.contextSelector.searchCreators') || '搜索创作者...'}
                    className="w-full pl-8 pr-3 py-2 bg-surface/60 rounded-lg text-sm font-medium focus:outline-none focus:ring-1 focus:ring-brand-500/30 placeholder:text-content-muted/60"
                  />
                </div>
                <div className="max-h-48 overflow-y-auto space-y-0.5">
                  {creators.length > 0 ? creators.map((creator) => {
                    const isSelected = selectedItems.some(item => item.type === 'creator' && item.id === String(creator.id))
                    return (
                      <button
                        key={creator.id}
                        onClick={() => toggleCreator(creator)}
                        disabled={!isSelected && selectedItems.length >= maxItems}
                        className={cn(
                          'w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left transition-all',
                          isSelected ? 'bg-blue-500/10' : 'hover:bg-surface/60',
                          !isSelected && selectedItems.length >= maxItems && 'opacity-50 cursor-not-allowed'
                        )}
                      >
                        <div className="w-7 h-7 rounded-full bg-surface/60 flex items-center justify-center flex-shrink-0 overflow-hidden">
                          {creator.avatar_url ? (
                            <img src={creator.avatar_url} alt={creator.username} className="w-full h-full object-cover" />
                          ) : (
                            <User className="h-3.5 w-3.5 text-content-muted" />
                          )}
                        </div>
                        <div className="flex-1 min-w-0">
                          <span className={cn('text-sm truncate block', isSelected ? 'text-content-primary font-semibold' : 'text-content-primary font-medium')}>
                            {creator.display_name || `@${creator.username}`}
                          </span>
                          <span className="text-[10px] text-content-muted">
                            {creator.product_count || 0} 个产品
                            {creator.total_revenue && ` · $${(creator.total_revenue / 1000).toFixed(0)}K`}
                          </span>
                        </div>
                        <div className={cn(
                          'w-4 h-4 rounded border-2 flex items-center justify-center transition-all flex-shrink-0',
                          isSelected ? 'bg-blue-500 border-blue-500' : 'border-content-muted/30'
                        )}>
                          {isSelected && <Check className="h-2.5 w-2.5 text-white" />}
                        </div>
                      </button>
                    )
                  }) : (
                    <p className="text-xs text-content-muted text-center py-3 font-medium">
                      {isSearchingCreators ? (t('assistant.searching') || '搜索中...') : (t('assistant.contextSelector.noCreators') || '暂无创作者')}
                    </p>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* 已选择区域 */}
          {selectedItems.length > 0 && (
            <div className="px-2.5 pb-2.5">
              <div className="p-2 bg-surface/40 rounded-lg">
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-[10px] text-content-muted font-medium">
                    {t('assistant.contextSelector.selected') || '已选择'} ({selectedItems.length}/{maxItems})
                  </span>
                  <button
                    onClick={clearAll}
                    className="text-[10px] text-content-muted hover:text-rose-500 font-medium transition-colors"
                  >
                    {t('assistant.contextSelector.clearAll') || '清空'}
                  </button>
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {selectedItems.map((item) => (
                    <span
                      key={item.id}
                      className={cn(
                        'inline-flex items-center gap-1 px-2 py-1 rounded-md text-[11px] font-medium',
                        item.type === 'product' && 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400',
                        item.type === 'url' && 'bg-amber-500/10 text-amber-600 dark:text-amber-400',
                        item.type === 'creator' && 'bg-blue-500/10 text-blue-600 dark:text-blue-400'
                      )}
                    >
                      {item.type === 'product' && <Package className="h-2.5 w-2.5" />}
                      {item.type === 'url' && <Link className="h-2.5 w-2.5" />}
                      {item.type === 'creator' && <User className="h-2.5 w-2.5" />}
                      <span className="max-w-[80px] truncate">{item.name}</span>
                      <button
                        onClick={() => removeItem(item)}
                        className="hover:text-rose-500 transition-colors"
                      >
                        <X className="h-2.5 w-2.5" />
                      </button>
                    </span>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
