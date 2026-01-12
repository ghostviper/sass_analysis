'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { motion, AnimatePresence } from 'framer-motion'
import { Card } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { ProductLogo } from '@/components/ui/ProductLogo'
import { useLocale } from '@/contexts/LocaleContext'
import { formatCurrency, cn } from '@/lib/utils'
import {
  getProductLeaderboardStats,
  getLeaderboardProducts,
  type ProductLeaderboardStats,
  type LeaderboardProduct,
} from '@/lib/api'
import {
  ChevronRight,
  TrendingUp,
  Sparkles,
  Zap,
  Shield,
  Rocket,
  Wrench,
  Package,
  BarChart3,
} from 'lucide-react'

interface LeaderboardSwitcherProps {
  className?: string
  limit?: number
}

const LEADERBOARD_ICONS: Record<string, React.ReactNode> = {
  revenue_verified: <BarChart3 className="w-4 h-4" />,
  quick_start: <Rocket className="w-4 h-4" />,
  small_beautiful: <Sparkles className="w-4 h-4" />,
  emerging: <TrendingUp className="w-4 h-4" />,
  low_risk: <Shield className="w-4 h-4" />,
  product_driven: <Zap className="w-4 h-4" />,
  b2d_tools: <Wrench className="w-4 h-4" />,
  no_ai: <Package className="w-4 h-4" />,
}

export function LeaderboardSwitcher({ className, limit = 5 }: LeaderboardSwitcherProps) {
  const { t, locale } = useLocale()
  const isZh = locale === 'zh-CN'

  const [stats, setStats] = useState<ProductLeaderboardStats>({})
  const [activeLeaderboard, setActiveLeaderboard] = useState<string>('quick_start')
  const [products, setProducts] = useState<LeaderboardProduct[]>([])
  const [loading, setLoading] = useState(true)
  const [productsLoading, setProductsLoading] = useState(false)

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
  useEffect(() => {
    async function fetchProducts() {
      setProductsLoading(true)
      const response = await getLeaderboardProducts(activeLeaderboard, { page_size: limit })
      if (response) {
        setProducts(response.products)
      }
      setProductsLoading(false)
    }
    fetchProducts()
  }, [activeLeaderboard, limit])

  const leaderboardKeys = Object.keys(stats)

  if (loading) {
    return <LeaderboardSwitcherSkeleton />
  }

  return (
    <Card className={cn('overflow-hidden', className)}>
      {/* 标题 */}
      <div className="px-5 pt-5 pb-4 border-b border-surface-border/50">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-base font-display font-bold text-content-primary tracking-tight">
              {t('leaderboards.title')}
            </h3>
            <p className="text-xs text-content-muted mt-0.5">
              {t('leaderboards.subtitle')}
            </p>
          </div>
          <Link
            href="/products/leaderboards"
            className="text-xs text-brand-500 hover:text-brand-600 font-medium flex items-center gap-1 transition-colors"
          >
            {isZh ? '查看全部' : 'View All'}
            <ChevronRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </div>

      {/* 榜单切换标签 */}
      <div className="px-5 py-3 border-b border-surface-border/30 overflow-x-auto">
        <div className="flex gap-2 min-w-max">
          {leaderboardKeys.map((key) => {
            const item = stats[key]
            const isActive = activeLeaderboard === key
            return (
              <button
                key={key}
                onClick={() => setActiveLeaderboard(key)}
                className={cn(
                  'flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-all whitespace-nowrap',
                  isActive
                    ? 'bg-brand-500 text-white shadow-sm'
                    : 'bg-surface-hover/60 text-content-secondary hover:bg-surface-hover hover:text-content-primary'
                )}
              >
                {LEADERBOARD_ICONS[key] || <Package className="w-3.5 h-3.5" />}
                <span>{isZh ? item.name : item.name_en}</span>
                <span className={cn(
                  'px-1.5 py-0.5 rounded-full text-[10px] tabular-nums',
                  isActive ? 'bg-white/20' : 'bg-surface-border/50'
                )}>
                  {item.count}
                </span>
              </button>
            )
          })}
        </div>
      </div>

      {/* 产品列表 */}
      <div className="p-4">
        <AnimatePresence mode="wait">
          {productsLoading ? (
            <motion.div
              key="loading"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="space-y-2"
            >
              {Array.from({ length: limit }).map((_, i) => (
                <div key={i} className="flex items-center gap-3 p-2 animate-pulse">
                  <div className="w-8 h-8 bg-surface-border rounded-lg" />
                  <div className="flex-1">
                    <div className="h-4 w-32 bg-surface-border rounded mb-1" />
                    <div className="h-3 w-20 bg-surface-border rounded" />
                  </div>
                  <div className="h-4 w-16 bg-surface-border rounded" />
                </div>
              ))}
            </motion.div>
          ) : products.length === 0 ? (
            <motion.div
              key="empty"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="text-center py-8 text-content-muted text-sm"
            >
              {t('common.noData')}
            </motion.div>
          ) : (
            <motion.div
              key={activeLeaderboard}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.2 }}
              className="space-y-1"
            >
              {products.map((product, index) => (
                <Link
                  key={product.id}
                  href={`/products/${product.slug}`}
                  className="flex items-center gap-3 p-2 rounded-xl hover:bg-surface-hover/60 transition-colors group"
                >
                  {/* 排名 */}
                  <div className={cn(
                    'w-6 h-6 rounded-lg flex items-center justify-center text-xs font-bold',
                    index === 0 ? 'bg-amber-500/10 text-amber-600' :
                    index === 1 ? 'bg-gray-400/10 text-gray-500' :
                    index === 2 ? 'bg-orange-500/10 text-orange-600' :
                    'bg-surface-hover text-content-muted'
                  )}>
                    {index + 1}
                  </div>

                  {/* Logo */}
                  <ProductLogo
                    logoUrl={product.logo_url}
                    name={product.name}
                    size="sm"
                  />

                  {/* 信息 */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium text-content-primary truncate group-hover:text-brand-600 transition-colors">
                        {product.name}
                      </span>
                      {product.tags?.ai_dependency_level === 'none' && (
                        <Badge variant="secondary" size="sm">
                          {isZh ? '非AI' : 'Non-AI'}
                        </Badge>
                      )}
                    </div>
                    <div className="text-xs text-content-muted truncate">
                      {product.category || t('common.uncategorized')}
                    </div>
                  </div>

                  {/* 收入 */}
                  <div className="text-right flex-shrink-0">
                    <div className="text-sm font-mono font-semibold text-content-primary tabular-nums">
                      {formatCurrency(product.revenue_30d)}
                    </div>
                    {product.growth_rate > 0 && (
                      <div className="text-xs text-accent-success flex items-center justify-end gap-0.5">
                        <TrendingUp className="w-3 h-3" />
                        +{product.growth_rate.toFixed(1)}%
                      </div>
                    )}
                  </div>
                </Link>
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* 底部链接 */}
      <div className="px-5 py-3 border-t border-surface-border/30 bg-surface-hover/30">
        <Link
          href={`/products/leaderboards?tab=${activeLeaderboard}`}
          className="text-xs text-content-secondary hover:text-brand-500 font-medium flex items-center justify-center gap-1 transition-colors"
        >
          {isZh ? `查看完整${stats[activeLeaderboard]?.name || '榜单'}` : `View full ${stats[activeLeaderboard]?.name_en || 'leaderboard'}`}
          <ChevronRight className="w-3.5 h-3.5" />
        </Link>
      </div>
    </Card>
  )
}

function LeaderboardSwitcherSkeleton() {
  return (
    <Card className="overflow-hidden animate-pulse">
      <div className="px-5 pt-5 pb-4 border-b border-surface-border/50">
        <div className="h-5 w-32 bg-surface-border rounded mb-2" />
        <div className="h-3 w-48 bg-surface-border rounded" />
      </div>
      <div className="px-5 py-3 border-b border-surface-border/30">
        <div className="flex gap-2">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-7 w-24 bg-surface-border rounded-full" />
          ))}
        </div>
      </div>
      <div className="p-4 space-y-2">
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="flex items-center gap-3 p-2">
            <div className="w-6 h-6 bg-surface-border rounded-lg" />
            <div className="w-8 h-8 bg-surface-border rounded-lg" />
            <div className="flex-1">
              <div className="h-4 w-32 bg-surface-border rounded mb-1" />
              <div className="h-3 w-20 bg-surface-border rounded" />
            </div>
            <div className="h-4 w-16 bg-surface-border rounded" />
          </div>
        ))}
      </div>
    </Card>
  )
}

export default LeaderboardSwitcher
