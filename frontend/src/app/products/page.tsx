'use client'

import { useEffect, useState, useCallback, Suspense } from 'react'
import Link from 'next/link'
import { useSearchParams } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import { Badge, MarketTypeBadge, ComplexityBadge } from '@/components/ui/Badge'
import { ProductLogo } from '@/components/ui/ProductLogo'
import { getStartups, getOpportunityProducts, getCategoryAnalysis, getCountries, type Country, type SortField, type SortOrder } from '@/lib/api'
import { formatCurrency, cn } from '@/lib/utils'
import { useLocale } from '@/contexts/LocaleContext'
import {
  Filter,
  Search,
  ChevronLeft,
  ChevronRight,
  Zap,
  Check,
  ExternalLink,
  LayoutGrid,
  List,
  ArrowDownWideNarrow,
  Globe,
  Package,
  ArrowUp,
  ArrowDown,
} from 'lucide-react'
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
  const { t } = useLocale()

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
    { value: 'revenue_30d', label: t('products.sort.revenue') },
    { value: 'scraped_at', label: t('products.sort.scrapedAt') },
    { value: 'name', label: t('products.sort.name') },
  ]

  const toggleSortOrder = () => {
    setSortOrder(prev => prev === 'desc' ? 'asc' : 'desc')
  }

  return (
    <div className="space-y-8">
      {/* 页面头部 - 统计信息整合在标题区 */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-display font-bold tracking-tight text-content-primary flex items-center gap-3">
            <div className="p-2 rounded-xl bg-gradient-to-br from-brand-500/20 to-accent-secondary/20">
              <Package className="h-6 w-6 text-brand-500" />
            </div>
            {t('products.title')}
          </h1>
          <p className="text-content-secondary mt-2 text-base">
            {t('common.total')} <span className="font-semibold text-brand-500">{total}</span> {t('products.subtitle')}
            {categories.length > 0 && (
              <span className="text-content-tertiary">，{t('products.coverCategories')} <span className="font-semibold text-content-primary">{categories.length}</span> {t('products.categoriesCount')}</span>
            )}
          </p>
        </div>

        {/* 布局切换 */}
        {viewMode === 'all' && (
          <div className="flex rounded-xl border border-surface-border/60 bg-surface/50 backdrop-blur-sm p-1 self-start sm:self-auto shadow-sm">
            <button
              onClick={() => setLayoutMode('grid')}
              className={cn(
                'p-2.5 rounded-lg transition-all duration-200',
                layoutMode === 'grid'
                  ? 'bg-brand-500 text-white shadow-sm'
                  : 'text-content-muted hover:text-content-primary hover:bg-surface-hover'
              )}
              title={t('products.gridView')}
            >
              <LayoutGrid className="h-4 w-4" />
            </button>
            <button
              onClick={() => setLayoutMode('list')}
              className={cn(
                'p-2.5 rounded-lg transition-all duration-200',
                layoutMode === 'list'
                  ? 'bg-brand-500 text-white shadow-sm'
                  : 'text-content-muted hover:text-content-primary hover:bg-surface-hover'
              )}
              title={t('products.listView')}
            >
              <List className="h-4 w-4" />
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
                ? 'bg-brand-500 text-white'
                : 'bg-surface-border/50 text-content-secondary hover:bg-surface-border'
            )}
          >
            {t('products.allProducts')}
          </button>
          <button
            onClick={() => setViewMode('opportunities')}
            className={cn(
              'px-3 py-1.5 rounded-full text-sm font-medium transition-all flex items-center gap-1.5',
              viewMode === 'opportunities'
                ? 'bg-gradient-to-r from-amber-500 to-orange-500 text-white'
                : 'bg-surface-border/50 text-content-secondary hover:bg-surface-border'
            )}
          >
            <Zap className="h-3 w-3" />
            {t('products.opportunities')}
          </button>
        </div>

        {/* 分类筛选 */}
        {viewMode === 'all' && (
          <>
            <div className="flex items-center gap-2 text-sm text-content-muted">
              <Filter className="h-4 w-4" />
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="select text-sm py-1.5"
              >
                <option value="all">{t('products.allCategories')}</option>
                {categories.map((cat) => (
                  <option key={cat.id} value={cat.category}>
                    {cat.category} ({cat.total_projects})
                  </option>
                ))}
              </select>
            </div>

            {/* 国家筛选 */}
            <div className="flex items-center gap-2 text-sm text-content-muted">
              <Globe className="h-4 w-4" />
              <select
                value={selectedCountry}
                onChange={(e) => setSelectedCountry(e.target.value)}
                className="select text-sm py-1.5"
              >
                <option value="all">{t('products.allCountries')}</option>
                {countries.map((country) => (
                  <option key={country.code} value={country.code}>
                    {country.name} ({country.count})
                  </option>
                ))}
              </select>
            </div>

            {/* 排序 */}
            <div className="flex items-center gap-1 text-sm text-content-muted">
              <ArrowDownWideNarrow className="h-4 w-4" />
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
                title={sortOrder === 'desc' ? t('products.order.desc') : t('products.order.asc')}
              >
                {sortOrder === 'desc' ? (
                  <ArrowDown className="h-4 w-4 text-content-muted" />
                ) : (
                  <ArrowUp className="h-4 w-4 text-content-muted" />
                )}
              </button>
            </div>

            {/* 搜索 */}
            <div className="relative flex-1 max-w-xs">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-content-muted h-4 w-4" />
              <input
                type="text"
                placeholder={t('common.search')}
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="input pl-10 py-1.5 text-sm"
              />
            </div>
          </>
        )}

        <span className="text-caption ml-auto">
          {t('common.total')} {total} {t('common.items')}
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
        <div className="flex items-center justify-center gap-3 pt-4">
          <button
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
            className={cn(
              'flex items-center gap-1.5 px-4 py-2.5 rounded-xl text-sm font-medium transition-all duration-200',
              'bg-surface/80 backdrop-blur-sm border border-surface-border/50',
              'hover:border-brand-500/30 hover:shadow-sm',
              'disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:border-surface-border/50 disabled:hover:shadow-none'
            )}
          >
            <ChevronLeft className="h-4 w-4" />
            {t('common.prevPage')}
          </button>
          <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-surface/60 border border-surface-border/40">
            <span className="text-sm font-semibold text-brand-500">{page}</span>
            <span className="text-sm text-content-muted">/</span>
            <span className="text-sm text-content-secondary">{totalPages}</span>
          </div>
          <button
            onClick={() => setPage(p => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
            className={cn(
              'flex items-center gap-1.5 px-4 py-2.5 rounded-xl text-sm font-medium transition-all duration-200',
              'bg-surface/80 backdrop-blur-sm border border-surface-border/50',
              'hover:border-brand-500/30 hover:shadow-sm',
              'disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:border-surface-border/50 disabled:hover:shadow-none'
            )}
          >
            {t('common.nextPage')}
            <ChevronRight className="h-4 w-4" />
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
      <div className="text-center py-16 text-content-muted rounded-2xl bg-surface/60 backdrop-blur-sm border border-surface-border/40">
        <div className="text-4xl mb-3">🔍</div>
        <p className="text-base font-medium">没有找到符合条件的产品</p>
      </div>
    )
  }

  if (layout === 'list') {
    return (
      <div className="space-y-3">
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
    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-5">
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
          'block h-full p-5 rounded-2xl transition-all duration-300',
          'bg-surface/80 backdrop-blur-sm border border-surface-border/50',
          'hover:border-brand-500/30 hover:shadow-lg hover:shadow-brand-500/5 hover:-translate-y-1'
        )}
      >
        <div className="flex items-start gap-4 mb-4">
          <ProductLogo
            name={product.name}
            logoUrl={product.logo_url}
            size="sm"
          />
          <div className="min-w-0 flex-1">
            <div className="flex items-start justify-between">
              <h3 className="text-base font-semibold text-content-primary truncate tracking-tight">
                {product.name}
              </h3>
              {product.website_url && (
                <a
                  href={product.website_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  onClick={(e) => e.stopPropagation()}
                  className="text-content-muted hover:text-brand-500 ml-2 flex-shrink-0 transition-colors"
                >
                  <ExternalLink className="h-3.5 w-3.5" />
                </a>
              )}
            </div>
            <div className="flex items-center gap-2 mt-1.5">
              {product.category && (
                <span className="text-xs text-content-tertiary font-medium">{product.category}</span>
              )}
              {categoryInfo && (
                <MarketTypeBadge type={categoryInfo.market_type} size="sm" showIcon={false} />
              )}
            </div>
          </div>
        </div>

        <p className="text-sm text-content-secondary leading-relaxed line-clamp-2 mb-5 min-h-[40px]">
          {product.description || '暂无描述'}
        </p>

        <div className="flex items-center justify-between pt-4 border-t border-surface-border/40">
          <div>
            <div className="font-mono font-bold text-lg text-content-primary tabular-nums tracking-tight">
              {formatCurrency(product.revenue_30d)}
            </div>
            <div className="text-xs text-content-muted font-medium">月收入</div>
          </div>
          {product.twitter_followers && (
            <div className="text-right">
              <div className="font-mono text-sm font-semibold text-content-secondary tabular-nums">
                {product.twitter_followers.toLocaleString()}
              </div>
              <div className="text-xs text-content-muted font-medium">关注者</div>
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
          'flex items-center gap-4 p-4 rounded-xl transition-all duration-200',
          'bg-surface/80 backdrop-blur-sm border border-surface-border/50',
          'hover:border-brand-500/30 hover:shadow-md hover:shadow-brand-500/5'
        )}
      >
        <ProductLogo
          name={product.name}
          logoUrl={product.logo_url}
          size="sm"
        />

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-semibold text-content-primary truncate tracking-tight">
              {product.name}
            </h3>
            {categoryInfo && (
              <MarketTypeBadge type={categoryInfo.market_type} size="sm" showIcon={false} />
            )}
          </div>
          <p className="text-xs text-content-tertiary truncate mt-0.5">
            {product.category || '未分类'} · {product.description || '暂无描述'}
          </p>
        </div>

        <div className="flex items-center gap-6 flex-shrink-0">
          {product.twitter_followers && (
            <div className="text-right hidden sm:block">
              <div className="font-mono text-sm font-semibold text-content-secondary tabular-nums">
                {product.twitter_followers.toLocaleString()}
              </div>
              <div className="text-xs text-content-muted font-medium">关注者</div>
            </div>
          )}
          <div className="text-right w-24">
            <div className="font-mono font-bold text-content-primary tabular-nums">
              {formatCurrency(product.revenue_30d)}
            </div>
            <div className="text-xs text-content-muted font-medium">月收入</div>
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
      <div className="text-center py-16 text-content-muted rounded-2xl bg-surface/60 backdrop-blur-sm border border-surface-border/40">
        <div className="text-4xl mb-3">🔍</div>
        <p className="text-base font-medium">暂无机会产品数据</p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
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
          'flex items-center gap-4 p-5 rounded-2xl transition-all duration-300',
          'bg-surface/80 backdrop-blur-sm border',
          isTop3
            ? 'border-amber-500/30 hover:border-amber-500/50 hover:shadow-lg hover:shadow-amber-500/10'
            : 'border-surface-border/50 hover:border-brand-500/30 hover:shadow-md hover:shadow-brand-500/5'
        )}
      >
        <div className={cn(
          'w-10 h-10 rounded-xl flex items-center justify-center font-display font-bold flex-shrink-0 text-base',
          isTop3
            ? 'bg-gradient-to-br from-amber-400 to-orange-500 text-white shadow-md shadow-amber-500/25'
            : 'bg-surface-hover text-content-muted'
        )}>
          {rank}
        </div>

        <ProductLogo
          name={startup.name}
          logoUrl={startup.logo_url}
          size="sm"
        />

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1.5">
            <span className="text-base font-semibold text-content-primary tracking-tight">{startup.name}</span>
            {analysis.is_product_driven && (
              <Badge variant="success" size="sm">
                <Zap className="h-2.5 w-2.5" />
                产品驱动
              </Badge>
            )}
            {analysis.is_small_and_beautiful && (
              <Badge variant="info" size="sm">小而美</Badge>
            )}
          </div>
          <div className="flex items-center gap-3 text-xs text-content-tertiary font-medium">
            <span>{startup.category || '未分类'}</span>
            {comboCount > 0 && (
              <span className="flex items-center gap-1 text-emerald-500">
                <Check className="h-3 w-3" />
                {comboCount} 组合匹配
              </span>
            )}
            <span className="text-content-muted">适合度 <span className="text-content-secondary font-semibold">{analysis.individual_dev_suitability.toFixed(1)}</span>/10</span>
          </div>
        </div>

        <div className="flex items-center gap-3 flex-shrink-0 hidden md:flex">
          <ComplexityBadge level={analysis.tech_complexity_level} />
          {analysis.uses_llm_api && (
            <Badge variant="muted" size="sm">LLM</Badge>
          )}
        </div>

        <div className="text-right flex-shrink-0 w-28">
          <div className={cn(
            'font-mono font-bold text-lg tabular-nums tracking-tight',
            isTop3 ? 'text-amber-500' : 'text-content-primary'
          )}>
            {formatCurrency(startup.revenue_30d)}
          </div>
          <div className="text-xs text-content-muted font-medium">月收入</div>
        </div>
      </Link>
    </motion.div>
  )
}

function ProductListSkeleton({ layout = 'grid' }: { layout?: LayoutMode }) {
  if (layout === 'list') {
    return (
      <div className="space-y-3">
        {Array.from({ length: 10 }).map((_, i) => (
          <div key={i} className="flex items-center gap-4 p-4 rounded-xl bg-surface/60 backdrop-blur-sm border border-surface-border/40">
            <div className="h-10 w-10 bg-surface-border/50 rounded-xl animate-pulse" />
            <div className="flex-1">
              <div className="h-4 w-32 bg-surface-border/50 rounded-lg animate-pulse mb-2" />
              <div className="h-3 w-48 bg-surface-border/40 rounded-lg animate-pulse" />
            </div>
            <div className="h-8 w-24 bg-surface-border/50 rounded-lg animate-pulse" />
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-5">
      {Array.from({ length: 9 }).map((_, i) => (
        <div key={i} className="p-5 rounded-2xl bg-surface/60 backdrop-blur-sm border border-surface-border/40">
          <div className="flex items-start gap-4 mb-4">
            <div className="h-10 w-10 bg-surface-border/50 rounded-xl animate-pulse" />
            <div className="flex-1">
              <div className="h-4 w-28 bg-surface-border/50 rounded-lg animate-pulse mb-2" />
              <div className="h-3 w-20 bg-surface-border/40 rounded-lg animate-pulse" />
            </div>
          </div>
          <div className="h-10 bg-surface-border/40 rounded-lg animate-pulse mb-5" />
          <div className="flex justify-between pt-4 border-t border-surface-border/30">
            <div className="h-10 w-20 bg-surface-border/50 rounded-lg animate-pulse" />
            <div className="h-10 w-16 bg-surface-border/40 rounded-lg animate-pulse" />
          </div>
        </div>
      ))}
    </div>
  )
}
