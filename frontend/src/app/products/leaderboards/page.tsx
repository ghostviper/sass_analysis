'use client'

import { useEffect, useState, useCallback } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import Link from 'next/link'
import { motion, AnimatePresence } from 'framer-motion'
import { Card } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { ProductLogo } from '@/components/ui/ProductLogo'
import { DataDisclaimer } from '@/components/ui/DataDisclaimer'
import { useLocale } from '@/contexts/LocaleContext'
import { formatCurrency, cn } from '@/lib/utils'
import {
  getProductLeaderboardStats,
  getLeaderboardProducts,
  type ProductLeaderboardStats,
  type LeaderboardProduct,
  type ProductLeaderboard,
} from '@/lib/api'
import {
  ChevronLeft,
  ChevronRight,
  TrendingUp,
  Sparkles,
  Zap,
  Shield,
  Rocket,
  Wrench,
  Package,
  BarChart3,
  ExternalLink,
  Info,
} from 'lucide-react'

const LEADERBOARD_ICONS: Record<string, React.ReactNode> = {
  revenue_verified: <BarChart3 className="w-5 h-5" />,
  quick_start: <Rocket className="w-5 h-5" />,
  small_beautiful: <Sparkles className="w-5 h-5" />,
  emerging: <TrendingUp className="w-5 h-5" />,
  low_risk: <Shield className="w-5 h-5" />,
  product_driven: <Zap className="w-5 h-5" />,
  b2d_tools: <Wrench className="w-5 h-5" />,
  no_ai: <Package className="w-5 h-5" />,
}

const LEADERBOARD_COLORS: Record<string, string> = {
  revenue_verified: 'from-emerald-500/20 to-emerald-500/5 border-emerald-500/30',
  quick_start: 'from-blue-500/20 to-blue-500/5 border-blue-500/30',
  small_beautiful: 'from-purple-500/20 to-purple-500/5 border-purple-500/30',
  emerging: 'from-orange-500/20 to-orange-500/5 border-orange-500/30',
  low_risk: 'from-green-500/20 to-green-500/5 border-green-500/30',
  product_driven: 'from-yellow-500/20 to-yellow-500/5 border-yellow-500/30',
  b2d_tools: 'from-cyan-500/20 to-cyan-500/5 border-cyan-500/30',
  no_ai: 'from-gray-500/20 to-gray-500/5 border-gray-500/30',
}

export default function LeaderboardsPage() {
  const { t, locale } = useLocale()
  const isZh = locale === 'zh-CN'
  const router = useRouter()
  const searchParams = useSearchParams()

  const [stats, setStats] = useState<ProductLeaderboardStats>({})
  const [activeTab, setActiveTab] = useState<string>(searchParams.get('tab') || 'quick_start')
  const [products, setProducts] = useState<LeaderboardProduct[]>([])
  const [leaderboardInfo, setLeaderboardInfo] = useState<ProductLeaderboard | null>(null)
  const [loading, setLoading] = useState(true)
  const [productsLoading, setProductsLoading] = useState(false)
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [total, setTotal] = useState(0)
  const pageSize = 20

  // 加载榜单统计
  useEffect(() => {
    async function fetchStats() {
      const data = await getProductLeaderboardStats()
      setStats(data)
      setLoading(false)
    }
    fetchStats()
  }, [])

  // 加载当前榜单产品
  const fetchProducts = useCallback(async () => {
    setProductsLoading(true)
    const response = await getLeaderboardProducts(activeTab, { page, page_size: pageSize })
    if (response) {
      setProducts(response.products)
      setLeaderboardInfo(response.leaderboard)
      setTotalPages(response.pagination.total_pages)
      setTotal(response.pagination.total)
    }
    setProductsLoading(false)
  }, [activeTab, page])

  useEffect(() => {
    fetchProducts()
  }, [fetchProducts])

  // 切换榜单时重置页码
  const handleTabChange = (tab: string) => {
    setActiveTab(tab)
    setPage(1)
    router.push(`/products/leaderboards?tab=${tab}`, { scroll: false })
  }

  const leaderboardKeys = Object.keys(stats)

  if (loading) {
    return <PageSkeleton />
  }

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-display font-bold text-content-primary tracking-tight">
            {t('leaderboards.title')}
          </h1>
          <p className="text-sm text-content-muted mt-1">
            {t('leaderboards.subtitle')}
          </p>
        </div>
        <Link
          href="/products"
          className="btn btn-secondary self-start sm:self-auto"
        >
          {isZh ? '返回产品库' : 'Back to Products'}
        </Link>
      </div>

      {/* 榜单卡片网格 */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {leaderboardKeys.map((key) => {
          const item = stats[key]
          const isActive = activeTab === key
          return (
            <button
              key={key}
              onClick={() => handleTabChange(key)}
              className={cn(
                'relative p-4 rounded-xl border transition-all text-left group',
                'bg-gradient-to-br',
                isActive
                  ? `${LEADERBOARD_COLORS[key]} ring-2 ring-brand-500/50`
                  : 'from-surface to-surface border-surface-border/50 hover:border-surface-border'
              )}
            >
              <div className={cn(
                'w-10 h-10 rounded-xl flex items-center justify-center mb-3 transition-colors',
                isActive ? 'bg-white/80 dark:bg-white/20 text-brand-600' : 'bg-surface-hover text-content-muted group-hover:text-content-secondary'
              )}>
                {LEADERBOARD_ICONS[key] || <Package className="w-5 h-5" />}
              </div>
              <div className="font-medium text-sm text-content-primary mb-0.5 truncate">
                {isZh ? item.name : item.name_en}
              </div>
              <div className="text-xs text-content-muted">
                {item.count} {isZh ? '个产品' : 'products'}
              </div>
              {isActive && (
                <motion.div
                  layoutId="activeIndicator"
                  className="absolute inset-0 rounded-xl ring-2 ring-brand-500"
                  transition={{ type: 'spring', bounce: 0.2, duration: 0.4 }}
                />
              )}
            </button>
          )
        })}
      </div>

      {/* 当前榜单信息 */}
      {leaderboardInfo && (
        <Card className="p-4 bg-gradient-to-r from-brand-500/5 to-transparent border-brand-500/20">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-xl bg-brand-500/10 flex items-center justify-center text-brand-600 flex-shrink-0">
              {LEADERBOARD_ICONS[activeTab] || <Package className="w-6 h-6" />}
            </div>
            <div className="flex-1 min-w-0">
              <h2 className="text-lg font-bold text-content-primary">
                {leaderboardInfo.icon} {isZh ? leaderboardInfo.name : leaderboardInfo.name_en}
              </h2>
              <p className="text-sm text-content-secondary mt-1">
                {isZh ? leaderboardInfo.description : leaderboardInfo.description_en}
              </p>
              <div className="flex items-center gap-4 mt-2 text-xs text-content-muted">
                <span>{isZh ? '共' : 'Total'} {total} {isZh ? '个产品' : 'products'}</span>
                <span>{isZh ? '第' : 'Page'} {page} / {totalPages} {isZh ? '页' : ''}</span>
              </div>
            </div>
          </div>
        </Card>
      )}

      {/* 产品列表 */}
      <div className="grid lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <AnimatePresence mode="wait">
            {productsLoading ? (
              <motion.div
                key="loading"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                <ProductListSkeleton />
              </motion.div>
            ) : products.length === 0 ? (
              <motion.div
                key="empty"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="text-center py-16"
              >
                <div className="text-4xl mb-4">📭</div>
                <p className="text-content-muted">{t('common.noData')}</p>
              </motion.div>
            ) : (
              <motion.div
                key={`${activeTab}-${page}`}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.2 }}
                className="space-y-3"
              >
                {products.map((product, index) => (
                  <ProductCard
                    key={product.id}
                    product={product}
                    rank={(page - 1) * pageSize + index + 1}
                    isZh={isZh}
                    t={t}
                  />
                ))}
              </motion.div>
            )}
          </AnimatePresence>

          {/* 分页 */}
          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2 mt-6">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="btn btn-secondary"
              >
                <ChevronLeft className="h-4 w-4" />
              </button>
              <span className="px-4 text-sm text-content-secondary">
                {page} / {totalPages}
              </span>
              <button
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="btn btn-secondary"
              >
                <ChevronRight className="h-4 w-4" />
              </button>
            </div>
          )}
        </div>

        {/* 侧边栏 */}
        <div className="space-y-4">
          {/* 数据说明 */}
          <DataDisclaimer variant="compact" />

          {/* 榜单说明 */}
          <Card className="p-4">
            <div className="flex items-center gap-2 mb-3">
              <Info className="w-4 h-4 text-brand-500" />
              <h3 className="text-sm font-semibold text-content-primary">
                {isZh ? '榜单说明' : 'About Rankings'}
              </h3>
            </div>
            <ul className="space-y-2 text-xs text-content-secondary">
              <li className="flex items-start gap-2">
                <span className="text-brand-500 mt-0.5">•</span>
                <span>{isZh ? '榜单基于产品标签自动筛选' : 'Rankings are auto-filtered by product tags'}</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-brand-500 mt-0.5">•</span>
                <span>{isZh ? '默认按月收入降序排列' : 'Sorted by monthly revenue by default'}</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-brand-500 mt-0.5">•</span>
                <span>{isZh ? '点击产品查看详细分析' : 'Click product for detailed analysis'}</span>
              </li>
            </ul>
          </Card>
        </div>
      </div>
    </div>
  )
}

interface ProductCardProps {
  product: LeaderboardProduct
  rank: number
  isZh: boolean
  t: (key: string) => string
}

function ProductCard({ product, rank, isZh, t }: ProductCardProps) {
  const getRankStyle = (r: number) => {
    if (r === 1) return 'bg-amber-500/10 text-amber-600 border-amber-500/30'
    if (r === 2) return 'bg-gray-400/10 text-gray-500 border-gray-400/30'
    if (r === 3) return 'bg-orange-500/10 text-orange-600 border-orange-500/30'
    return 'bg-surface-hover text-content-muted border-surface-border/50'
  }

  return (
    <Link href={`/products/${product.slug}`}>
      <Card className="p-4 hover:border-brand-500/30 hover:shadow-md transition-all group">
        <div className="flex items-center gap-4">
          {/* 排名 */}
          <div className={cn(
            'w-10 h-10 rounded-xl flex items-center justify-center text-sm font-bold border flex-shrink-0',
            getRankStyle(rank)
          )}>
            {rank}
          </div>

          {/* Logo */}
          <ProductLogo
            src={product.logo_url}
            name={product.name}
            size="md"
          />

          {/* 信息 */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <span className="font-semibold text-content-primary group-hover:text-brand-600 transition-colors truncate">
                {product.name}
              </span>
              {product.tags?.ai_dependency_level === 'none' && (
                <Badge variant="secondary" size="sm">
                  {isZh ? '非AI' : 'Non-AI'}
                </Badge>
              )}
              {product.tags?.feature_complexity === 'simple' && (
                <Badge variant="success" size="sm">
                  {isZh ? '简单' : 'Simple'}
                </Badge>
              )}
            </div>
            <div className="flex items-center gap-3 text-xs text-content-muted">
              <span>{product.category || t('common.uncategorized')}</span>
              {product.country_code && (
                <span className="flex items-center gap-1">
                  <span className="text-base">{getFlagEmoji(product.country_code)}</span>
                  {product.country}
                </span>
              )}
            </div>
            {product.description && (
              <p className="text-xs text-content-secondary mt-1.5 line-clamp-1">
                {product.description}
              </p>
            )}
          </div>

          {/* 收入和增长 */}
          <div className="text-right flex-shrink-0">
            <div className="text-lg font-mono font-bold text-content-primary tabular-nums">
              {formatCurrency(product.revenue_30d)}
            </div>
            <div className="text-xs text-content-muted">
              {isZh ? '月收入' : 'MRR'}
            </div>
            {product.growth_rate > 0 && (
              <div className="text-xs text-accent-success flex items-center justify-end gap-0.5 mt-1">
                <TrendingUp className="w-3 h-3" />
                +{product.growth_rate.toFixed(1)}%
              </div>
            )}
          </div>

          {/* 外链 */}
          <a
            href={product.website_url}
            target="_blank"
            rel="noopener noreferrer"
            onClick={(e) => e.stopPropagation()}
            className="p-2 rounded-lg hover:bg-surface-hover text-content-muted hover:text-brand-500 transition-colors flex-shrink-0"
          >
            <ExternalLink className="w-4 h-4" />
          </a>
        </div>
      </Card>
    </Link>
  )
}

function getFlagEmoji(countryCode: string): string {
  const codePoints = countryCode
    .toUpperCase()
    .split('')
    .map((char) => 127397 + char.charCodeAt(0))
  return String.fromCodePoint(...codePoints)
}

function PageSkeleton() {
  return (
    <div className="space-y-6 animate-pulse">
      <div className="flex justify-between">
        <div>
          <div className="h-8 w-48 bg-surface-border rounded mb-2" />
          <div className="h-4 w-64 bg-surface-border rounded" />
        </div>
        <div className="h-10 w-32 bg-surface-border rounded" />
      </div>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {Array.from({ length: 8 }).map((_, i) => (
          <div key={i} className="h-28 bg-surface-border rounded-xl" />
        ))}
      </div>
      <ProductListSkeleton />
    </div>
  )
}

function ProductListSkeleton() {
  return (
    <div className="space-y-3">
      {Array.from({ length: 10 }).map((_, i) => (
        <Card key={i} className="p-4">
          <div className="flex items-center gap-4">
            <div className="w-10 h-10 bg-surface-border rounded-xl" />
            <div className="w-12 h-12 bg-surface-border rounded-xl" />
            <div className="flex-1">
              <div className="h-5 w-40 bg-surface-border rounded mb-2" />
              <div className="h-3 w-24 bg-surface-border rounded" />
            </div>
            <div className="text-right">
              <div className="h-6 w-20 bg-surface-border rounded mb-1" />
              <div className="h-3 w-12 bg-surface-border rounded ml-auto" />
            </div>
          </div>
        </Card>
      ))}
    </div>
  )
}
