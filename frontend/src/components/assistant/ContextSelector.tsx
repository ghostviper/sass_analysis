'use client'

import { useState, useEffect } from 'react'
import { Card } from '@/components/ui/Card'
import { cn } from '@/lib/utils'
import { Database, Globe, Search, Loader2, Check } from 'lucide-react'
import { getStartups } from '@/lib/api'
import type { Startup } from '@/types'

interface ContextSelectorProps {
  contextType: 'database' | 'url' | null
  setContextType: (type: 'database' | 'url' | null) => void
  selectedProduct: string | null
  setSelectedProduct: (product: string | null) => void
  urlInput: string
  setUrlInput: (url: string) => void
}

export function ContextSelector({
  contextType,
  setContextType,
  selectedProduct,
  setSelectedProduct,
  urlInput,
  setUrlInput,
}: ContextSelectorProps) {
  const [products, setProducts] = useState<Startup[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [isSearching, setIsSearching] = useState(false)
  const [showDropdown, setShowDropdown] = useState(false)

  // 搜索产品
  useEffect(() => {
    if (contextType !== 'database') return

    const search = async () => {
      setIsSearching(true)
      try {
        const data = await getStartups({
          page: 1,
          page_size: 10,
          search: searchQuery || undefined,
        })
        setProducts(data.items)
      } catch (error) {
        console.error('Failed to search products:', error)
      } finally {
        setIsSearching(false)
      }
    }

    const debounce = setTimeout(search, 300)
    return () => clearTimeout(debounce)
  }, [searchQuery, contextType])

  return (
    <Card padding="sm">
      <h3 className="text-sm font-medium text-content-primary mb-3 flex items-center gap-2">
        <Database className="h-3.5 w-3.5 text-accent-success" />
        分析上下文
      </h3>

      {/* 类型切换 */}
      <div className="flex rounded-lg bg-background-secondary p-1 mb-3">
        <button
          onClick={() => {
            setContextType('database')
            setUrlInput('')
          }}
          className={cn(
            'flex-1 py-1.5 rounded-md text-xs font-medium transition-all flex items-center justify-center gap-1.5',
            contextType === 'database'
              ? 'bg-surface text-content-primary shadow'
              : 'text-content-muted hover:text-content-secondary'
          )}
        >
          <Database className="h-3 w-3" />
          从数据库
        </button>
        <button
          onClick={() => {
            setContextType('url')
            setSelectedProduct(null)
            setSearchQuery('')
          }}
          className={cn(
            'flex-1 py-1.5 rounded-md text-xs font-medium transition-all flex items-center justify-center gap-1.5',
            contextType === 'url'
              ? 'bg-surface text-content-primary shadow'
              : 'text-content-muted hover:text-content-secondary'
          )}
        >
          <Globe className="h-3 w-3" />
          输入链接
        </button>
      </div>

      {/* 数据库选择 */}
      {contextType === 'database' && (
        <div className="relative">
          <div className="relative">
            {isSearching ? (
              <Loader2 className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-content-muted animate-spin" />
            ) : (
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-content-muted" />
            )}
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value)
                setShowDropdown(true)
              }}
              onFocus={() => setShowDropdown(true)}
              placeholder="搜索产品..."
              className="input pl-9 py-2 text-sm w-full"
            />
          </div>

          {/* 下拉列表 */}
          {showDropdown && products.length > 0 && (
            <div className="absolute z-10 w-full mt-1 bg-surface border border-surface-border rounded-lg shadow-lg max-h-48 overflow-y-auto">
              {products.map((product) => (
                <button
                  key={product.id}
                  onClick={() => {
                    setSelectedProduct(product.name)
                    setSearchQuery(product.name)
                    setShowDropdown(false)
                  }}
                  className={cn(
                    'w-full flex items-center gap-2 px-3 py-2 text-left text-sm transition-colors',
                    selectedProduct === product.name
                      ? 'bg-accent-primary/10 text-accent-primary'
                      : 'hover:bg-surface-hover text-content-primary'
                  )}
                >
                  <span className="flex-1 truncate">{product.name}</span>
                  {product.category && (
                    <span className="text-xs text-content-muted">{product.category}</span>
                  )}
                  {selectedProduct === product.name && (
                    <Check className="h-3 w-3 text-accent-primary" />
                  )}
                </button>
              ))}
            </div>
          )}

          {/* 已选择提示 */}
          {selectedProduct && (
            <div className="mt-2 text-xs text-accent-success flex items-center gap-1">
              <Check className="h-3 w-3" />
              已选择: {selectedProduct}
            </div>
          )}
        </div>
      )}

      {/* URL 输入 */}
      {contextType === 'url' && (
        <div>
          <div className="relative">
            <Globe className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-content-muted" />
            <input
              type="url"
              value={urlInput}
              onChange={(e) => setUrlInput(e.target.value)}
              placeholder="https://example.com"
              className="input pl-9 py-2 text-sm w-full"
            />
          </div>
          <p className="mt-2 text-xs text-content-muted">
            输入产品官网链接，AI 将实时抓取分析
          </p>
        </div>
      )}

      {/* 无选择提示 */}
      {!contextType && (
        <p className="text-xs text-content-muted text-center py-2">
          选择数据来源以获得更精准的分析
        </p>
      )}
    </Card>
  )
}
