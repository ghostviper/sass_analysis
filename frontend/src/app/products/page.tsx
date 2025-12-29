'use client'

import { useEffect, useState, useCallback, Suspense } from 'react'
import Link from 'next/link'
import { useSearchParams } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import { Badge, MarketTypeBadge, ComplexityBadge } from '@/components/ui/Badge'
import { ProductLogo } from '@/components/ui/ProductLogo'
import { getStartups, getOpportunityProducts, getCategoryAnalysis, getCountries, type Country, type SortField, type SortOrder } from '@/lib/api'
import { formatCurrency, cn } from '@/lib/utils'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import {
  faFilter,
  faMagnifyingGlass,
  faChevronLeft,
  faChevronRight,
  faBolt,
  faCheck,
  faExternalLink,
  faGrip,
  faList,
  faArrowDownWideShort,
  faGlobe,
  faBoxesStacked,
  faArrowUp,
  faArrowDown,
} from '@fortawesome/free-solid-svg-icons'
import type { Startup, OpportunityProduct, CategoryAnalysis } from '@/types'

type ViewMode = 'all' | 'opportunities'
type LayoutMode = 'grid' | 'list'

export default function ProductsPage() {
  return (
    <Suspense fallback={<ProductListSkeleton />}>
      <ProductsContent />
    </Suspense>
  )
}

function ProductsContent() {
  const searchParams = useSearchParams()
  const filterParam = searchParams.get('filter')

  const [viewMode, setViewMode] = useState<ViewMode>(
    filterParam === 'opportunities' ? 'opportunities' : 'all'
  )
  const [layoutMode, setLayoutMode] = useState<LayoutMode>('grid')
  const [products, setProducts] = useState<Startup[]>([])
  const [opportunities, setOpportunities] = useState<OpportunityProduct[]>([])
  const [categories, setCategories] = useState<CategoryAnalysis[]>([])
  const [countries, setCountries] = useState<Country[]>([])
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const [search, setSearch] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [selectedCountry, setSelectedCountry] = useState<string>('all')
  const [sortBy, setSortBy] = useState<SortField>('revenue_30d')
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc')
  const pageSize = 20

  useEffect(() => {
    // 分开请求，避免一个失败导致全部失败
    getCategoryAnalysis()
      .then(setCategories)
      .catch((err) => console.error('Failed to load categories:', err))

    getCountries()
      .then(setCountries)
      .catch((err) => console.error('Failed to load countries:', err))
  }, [])

  const fetchProducts = useCallback(async () => {
    setLoading(true)
    try {
      if (viewMode === 'opportunities') {
        const data = await getOpportunityProducts({ limit: 100 })
        setOpportunities(data)
        setTotal(data.length)
      } else {
        const data = await getStartups({
          page,
          page_size: pageSize,
          category: selectedCategory !== 'all' ? selectedCategory : undefined,
          country_code: selectedCountry !== 'all' ? selectedCountry : undefined,
          search: search || undefined,
          sort_by: sortBy,
          sort_order: sortOrder,
        })
        setProducts(data.items)
        setTotal(data.total)
      }
    } catch (err) {
      console.error('Failed to fetch products:', err)
    } finally {
      setLoading(false)
    }
  }, [viewMode, page, selectedCategory, selectedCountry, search, sortBy, sortOrder])

  useEffect(() => {
    fetchProducts()
  }, [fetchProducts])

  useEffect(() => {
    setPage(1)
  }, [viewMode, selectedCategory, selectedCountry, search, sortBy, sortOrder])

  const totalPages = Math.ceil(total / pageSize)

  // 排序选项
  const sortOptions: { value: SortField; label: string }[] = [
    { value: 'revenue_30d', label: '收入' },
    { value: 'scraped_at', label: '收录时间' },
    { value: 'name', label: '名称' },
  ]

  const toggleSortOrder = () => {
    setSortOrder(prev => prev === 'desc' ? 'asc' : 'desc')
  }

  return (
    <div className="space-y-6">
      {/* 页面头部 - 统计信息整合在标题区 */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-display font-bold text-content-primary flex items-center gap-3">
            <FontAwesomeIcon icon={faBoxesStacked} className="text-accent-primary" />
            产品库
          </h1>
          <p className="text-body mt-1">
            共 <span className="font-medium text-content-primary">{total}</span> 个产品，
            {categories.length > 0 && (
              <span>覆盖 <span className="font-medium text-content-primary">{categories.length}</span> 个分类</span>
            )}
          </p>
        </div>

        {/* 布局切换 */}
        {viewMode === 'all' && (
          <div className="flex rounded-lg border border-surface-border p-0.5 self-start sm:self-auto">
            <button
              onClick={() => setLayoutMode('grid')}
              className={cn(
                'p-2 rounded-md transition-colors',
                layoutMode === 'grid'
                  ? 'bg-surface text-content-primary'
                  : 'text-content-muted hover:text-content-secondary'
              )}
              title="卡片视图"
            >
              <FontAwesomeIcon icon={faGrip} className="h-4 w-4" />
            </button>
            <button
              onClick={() => setLayoutMode('list')}
              className={cn(
                'p-2 rounded-md transition-colors',
                layoutMode === 'list'
                  ? 'bg-surface text-content-primary'
                  : 'text-content-muted hover:text-content-secondary'
              )}
              title="列表视图"
            >
              <FontAwesomeIcon icon={faList} className="h-4 w-4" />
            </button>
          </div>
        )}
      </div>

      {/* 筛选栏 */}
      <div className="flex flex-wrap items-center gap-3">
        {/* 视图切换 - pill按钮样式 */}
        <div className="flex gap-2">
          <button
            onClick={() => setViewMode('all')}
            className={cn(
              'px-3 py-1.5 rounded-full text-sm font-medium transition-all',
              viewMode === 'all'
                ? 'bg-accent-primary text-white'
                : 'bg-surface-border/50 text-content-secondary hover:bg-surface-border'
            )}
          >
            全部产品
          </button>
          <button
            onClick={() => setViewMode('opportunities')}
            className={cn(
              'px-3 py-1.5 rounded-full text-sm font-medium transition-all flex items-center gap-1.5',
              viewMode === 'opportunities'
                ? 'bg-accent-warning text-white'
                : 'bg-surface-border/50 text-content-secondary hover:bg-surface-border'
            )}
          >
            <FontAwesomeIcon icon={faBolt} className="h-3 w-3" />
            机会产品
          </button>
        </div>

        {/* 分类筛选 */}
        {viewMode === 'all' && (
          <>
            <div className="flex items-center gap-2">
              <FontAwesomeIcon icon={faFilter} className="text-content-muted h-4 w-4" />
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="select text-sm py-1.5"
              >
                <option value="all">全部分类</option>
                {categories.map((cat) => (
                  <option key={cat.id} value={cat.category}>
                    {cat.category} ({cat.total_projects})
                  </option>
                ))}
              </select>
            </div>

            {/* 国家筛选 */}
            <div className="flex items-center gap-2">
              <FontAwesomeIcon icon={faGlobe} className="text-content-muted h-4 w-4" />
              <select
                value={selectedCountry}
                onChange={(e) => setSelectedCountry(e.target.value)}
                className="select text-sm py-1.5"
              >
                <option value="all">全部国家</option>
                {countries.map((country) => (
                  <option key={country.code} value={country.code}>
                    {country.name} ({country.count})
                  </option>
                ))}
              </select>
            </div>

            {/* 排序 */}
            <div className="flex items-center gap-1">
              <FontAwesomeIcon icon={faArrowDownWideShort} className="text-content-muted h-4 w-4" />
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as SortField)}
                className="select text-sm py-1.5"
              >
                {sortOptions.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
              <button
                onClick={toggleSortOrder}
                className="p-1.5 rounded-md hover:bg-surface-border/50 transition-colors"
                title={sortOrder === 'desc' ? '降序' : '升序'}
              >
                <FontAwesomeIcon
                  icon={sortOrder === 'desc' ? faArrowDown : faArrowUp}
                  className="h-4 w-4 text-content-muted"
                />
              </button>
            </div>

            {/* 搜索 */}
            <div className="relative flex-1 max-w-xs">
              <FontAwesomeIcon
                icon={faMagnifyingGlass}
                className="absolute left-3 top-1/2 -translate-y-1/2 text-content-muted h-4 w-4"
              />
              <input
                type="text"
                placeholder="搜索产品..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="input pl-10 py-1.5 text-sm"
              />
            </div>
          </>
        )}

        <span className="text-caption ml-auto">
          共 {total} 个
        </span>
      </div>

      {/* 产品列表 */}
      <div className="min-h-[400px]">
        <AnimatePresence mode="wait">
          {loading ? (
            <motion.div
              key="skeleton"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.15 }}
            >
              <ProductListSkeleton layout={layoutMode} />
            </motion.div>
          ) : viewMode === 'opportunities' ? (
            <motion.div
              key="opportunities"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.15 }}
            >
              <OpportunityProductList products={opportunities} />
            </motion.div>
          ) : (
            <motion.div
              key={`products-${layoutMode}`}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.15 }}
            >
              <ProductList products={products} categories={categories} layout={layoutMode} />
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* 分页 */}
      {viewMode === 'all' && totalPages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <button
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
            className="btn btn-secondary"
          >
            <FontAwesomeIcon icon={faChevronLeft} className="h-4 w-4" />
          </button>
          <span className="px-4 text-sm text-content-secondary">
            {page} / {totalPages}
          </span>
          <button
            onClick={() => setPage(p => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
            className="btn btn-secondary"
          >
            <FontAwesomeIcon icon={faChevronRight} className="h-4 w-4" />
          </button>
        </div>
      )}
    </div>
  )
}

interface ProductListProps {
  products: Startup[]
  categories: CategoryAnalysis[]
  layout: LayoutMode
}

function ProductList({ products, categories, layout }: ProductListProps) {
  const categoryMap = new Map(categories.map(c => [c.category, c]))

  if (products.length === 0) {
    return (
      <div className="text-center py-12 text-content-muted rounded-xl bg-surface border border-surface-border/50">
        没有找到符合条件的产品
      </div>
    )
  }

  if (layout === 'list') {
    return (
      <div className="space-y-2">
        {products.map((product, index) => {
          const categoryInfo = product.category ? categoryMap.get(product.category) : null
          return (
            <ProductRow
              key={product.id}
              product={product}
              categoryInfo={categoryInfo}
              index={index}
            />
          )
        })}
      </div>
    )
  }

  return (
    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
      {products.map((product, index) => {
        const categoryInfo = product.category ? categoryMap.get(product.category) : null
        return (
          <ProductCard
            key={product.id}
            product={product}
            categoryInfo={categoryInfo}
            index={index}
          />
        )
      })}
    </div>
  )
}

interface ProductCardProps {
  product: Startup
  categoryInfo?: CategoryAnalysis | null
  index: number
}

function ProductCard({ product, categoryInfo, index }: ProductCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2, delay: index * 0.03 }}
    >
      <Link
        href={`/products/${product.slug}`}
        className={cn(
          'block h-full p-4 rounded-xl transition-all',
          'bg-surface border border-surface-border/50',
          'hover:border-surface-border hover:shadow-sm'
        )}
      >
        <div className="flex items-start gap-3 mb-3">
          <ProductLogo
            name={product.name}
            logoUrl={product.logo_url}
            size="sm"
          />
          <div className="min-w-0 flex-1">
            <div className="flex items-start justify-between">
              <h3 className="text-sm font-medium text-content-primary truncate">
                {product.name}
              </h3>
              {product.website_url && (
                <a
                  href={product.website_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  onClick={(e) => e.stopPropagation()}
                  className="text-content-muted hover:text-accent-primary ml-2 flex-shrink-0"
                >
                  <FontAwesomeIcon icon={faExternalLink} className="h-3 w-3" />
                </a>
              )}
            </div>
            <div className="flex items-center gap-2 mt-1">
              {product.category && (
                <span className="text-caption">{product.category}</span>
              )}
              {categoryInfo && (
                <MarketTypeBadge type={categoryInfo.market_type} size="sm" showIcon={false} />
              )}
            </div>
          </div>
        </div>

        <p className="text-body-sm line-clamp-2 mb-4 min-h-[40px]">
          {product.description || '暂无描述'}
        </p>

        <div className="flex items-center justify-between pt-3 border-t border-surface-border/50">
          <div>
            <div className="font-mono font-medium text-content-primary tabular-nums">
              {formatCurrency(product.revenue_30d)}
            </div>
            <div className="text-caption">月收入</div>
          </div>
          {product.twitter_followers && (
            <div className="text-right">
              <div className="font-mono text-sm text-content-secondary tabular-nums">
                {product.twitter_followers.toLocaleString()}
              </div>
              <div className="text-caption">关注者</div>
            </div>
          )}
        </div>
      </Link>
    </motion.div>
  )
}

function ProductRow({ product, categoryInfo, index }: ProductCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.2, delay: index * 0.02 }}
    >
      <Link
        href={`/products/${product.slug}`}
        className={cn(
          'flex items-center gap-4 p-4 rounded-xl transition-all',
          'bg-surface border border-surface-border/50',
          'hover:border-surface-border hover:shadow-sm'
        )}
      >
        <ProductLogo
          name={product.name}
          logoUrl={product.logo_url}
          size="sm"
        />

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-medium text-content-primary truncate">
              {product.name}
            </h3>
            {categoryInfo && (
              <MarketTypeBadge type={categoryInfo.market_type} size="sm" showIcon={false} />
            )}
          </div>
          <p className="text-caption truncate mt-0.5">
            {product.category || '未分类'} · {product.description || '暂无描述'}
          </p>
        </div>

        <div className="flex items-center gap-6 flex-shrink-0">
          {product.twitter_followers && (
            <div className="text-right hidden sm:block">
              <div className="font-mono text-sm text-content-secondary tabular-nums">
                {product.twitter_followers.toLocaleString()}
              </div>
              <div className="text-caption">关注者</div>
            </div>
          )}
          <div className="text-right w-20">
            <div className="font-mono font-medium text-content-primary tabular-nums">
              {formatCurrency(product.revenue_30d)}
            </div>
            <div className="text-caption">月收入</div>
          </div>
        </div>
      </Link>
    </motion.div>
  )
}

interface OpportunityProductListProps {
  products: OpportunityProduct[]
}

function OpportunityProductList({ products }: OpportunityProductListProps) {
  if (products.length === 0) {
    return (
      <div className="text-center py-12 text-content-muted rounded-xl bg-surface border border-surface-border/50">
        暂无机会产品数据
      </div>
    )
  }

  return (
    <div className="space-y-2">
      {products.map((item, index) => (
        <OpportunityProductRow key={item.startup.id} item={item} rank={index + 1} />
      ))}
    </div>
  )
}

interface OpportunityProductRowProps {
  item: OpportunityProduct
  rank: number
}

function OpportunityProductRow({ item, rank }: OpportunityProductRowProps) {
  const { startup, analysis } = item
  const comboCount = [analysis.combo1_match, analysis.combo2_match, analysis.combo3_match].filter(Boolean).length
  const isTop3 = rank <= 3

  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.2, delay: rank * 0.02 }}
    >
      <Link
        href={`/products/${startup.slug}`}
        className={cn(
          'flex items-center gap-4 p-4 rounded-xl transition-all',
          'bg-surface border border-surface-border/50',
          'hover:border-surface-border hover:shadow-sm',
          isTop3 && 'border-accent-warning/20'
        )}
      >
        <div className={cn(
          'w-8 h-8 rounded-lg flex items-center justify-center font-display font-bold flex-shrink-0 text-sm',
          isTop3
            ? 'bg-gradient-to-br from-accent-warning to-accent-warning/70 text-background'
            : 'bg-surface-border/50 text-content-muted'
        )}>
          {rank}
        </div>

        <ProductLogo
          name={startup.name}
          logoUrl={startup.logo_url}
          size="sm"
        />

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-sm font-medium text-content-primary">{startup.name}</span>
            {analysis.is_product_driven && (
              <Badge variant="success" size="sm">
                <FontAwesomeIcon icon={faBolt} className="h-2.5 w-2.5" />
                产品驱动
              </Badge>
            )}
            {analysis.is_small_and_beautiful && (
              <Badge variant="info" size="sm">小而美</Badge>
            )}
          </div>
          <div className="flex items-center gap-3 text-caption">
            <span>{startup.category || '未分类'}</span>
            {comboCount > 0 && (
              <span className="flex items-center gap-1 text-accent-success">
                <FontAwesomeIcon icon={faCheck} className="h-3 w-3" />
                {comboCount} 组合匹配
              </span>
            )}
            <span>适合度 {analysis.individual_dev_suitability.toFixed(1)}/10</span>
          </div>
        </div>

        <div className="flex items-center gap-2 flex-shrink-0 hidden md:flex">
          <ComplexityBadge level={analysis.tech_complexity_level} />
          {analysis.uses_llm_api && (
            <Badge variant="muted" size="sm">LLM</Badge>
          )}
        </div>

        <div className="text-right flex-shrink-0 w-24">
          <div className={cn(
            'font-mono font-medium tabular-nums',
            isTop3 ? 'text-accent-warning' : 'text-content-primary'
          )}>
            {formatCurrency(startup.revenue_30d)}
          </div>
          <div className="text-caption">月收入</div>
        </div>
      </Link>
    </motion.div>
  )
}

function ProductListSkeleton({ layout = 'grid' }: { layout?: LayoutMode }) {
  if (layout === 'list') {
    return (
      <div className="space-y-2">
        {Array.from({ length: 10 }).map((_, i) => (
          <div key={i} className="flex items-center gap-4 p-4 rounded-xl bg-surface border border-surface-border/50">
            <div className="h-10 w-10 bg-surface-border rounded-lg animate-pulse" />
            <div className="flex-1">
              <div className="h-4 w-32 bg-surface-border rounded animate-pulse mb-2" />
              <div className="h-3 w-48 bg-surface-border rounded animate-pulse" />
            </div>
            <div className="h-8 w-20 bg-surface-border rounded animate-pulse" />
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
      {Array.from({ length: 9 }).map((_, i) => (
        <div key={i} className="p-4 rounded-xl bg-surface border border-surface-border/50">
          <div className="flex items-start gap-3 mb-3">
            <div className="h-10 w-10 bg-surface-border rounded-lg animate-pulse" />
            <div className="flex-1">
              <div className="h-4 w-24 bg-surface-border rounded animate-pulse mb-2" />
              <div className="h-3 w-16 bg-surface-border rounded animate-pulse" />
            </div>
          </div>
          <div className="h-10 bg-surface-border rounded animate-pulse mb-4" />
          <div className="flex justify-between pt-3 border-t border-surface-border/50">
            <div className="h-8 w-16 bg-surface-border rounded animate-pulse" />
            <div className="h-8 w-12 bg-surface-border rounded animate-pulse" />
          </div>
        </div>
      ))}
    </div>
  )
}
