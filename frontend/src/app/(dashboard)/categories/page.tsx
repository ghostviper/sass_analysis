'use client'

import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Card, CardHeader } from '@/components/ui/Card'
import { MarketTypeBadge } from '@/components/ui/Badge'
import { MarketRadarChart } from '@/components/charts/RadarChart'
import { getCategoryAnalysis } from '@/lib/api'
import { formatCurrency, formatNumber, formatPercent, cn } from '@/lib/utils'
import { useLocale } from '@/contexts/LocaleContext'
import { Layers, ArrowDownWideNarrow, ArrowUp, ArrowDown } from 'lucide-react'
import type { CategoryAnalysis, MarketType } from '@/types'
import { MARKET_TYPE_CONFIG } from '@/types'

type SortField = 'category' | 'total_projects' | 'total_revenue' | 'median_revenue' | 'market_type'
type SortOrder = 'asc' | 'desc'

export default function CategoriesPage() {
  const { t } = useLocale()
  const [categories, setCategories] = useState<CategoryAnalysis[]>([])
  const [loading, setLoading] = useState(true)
  const [filterType, setFilterType] = useState<MarketType | 'all'>('all')
  const [sortField, setSortField] = useState<SortField>('market_type')
  const [sortOrder, setSortOrder] = useState<SortOrder>('asc')
  const [selectedCategory, setSelectedCategory] = useState<CategoryAnalysis | null>(null)

  useEffect(() => {
    async function fetchData() {
      try {
        const data = await getCategoryAnalysis()
        setCategories(data)
        if (data.length > 0) {
          setSelectedCategory(data[0])
        }
      } catch (err) {
        console.error('Failed to fetch categories:', err)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  const typeOrder: Record<MarketType, number> = {
    blue_ocean: 0,
    emerging: 1,
    moderate: 2,
    concentrated: 3,
    red_ocean: 4,
    weak_demand: 5,
  }

  const filteredAndSorted = categories
    .filter(c => filterType === 'all' || c.market_type === filterType)
    .sort((a, b) => {
      let cmp = 0
      switch (sortField) {
        case 'category':
          cmp = a.category.localeCompare(b.category)
          break
        case 'total_projects':
          cmp = a.total_projects - b.total_projects
          break
        case 'total_revenue':
          cmp = a.total_revenue - b.total_revenue
          break
        case 'median_revenue':
          cmp = a.median_revenue - b.median_revenue
          break
        case 'market_type':
          cmp = typeOrder[a.market_type] - typeOrder[b.market_type]
          break
      }
      return sortOrder === 'asc' ? cmp : -cmp
    })

  const stats = {
    total: categories.length,
    blueOcean: categories.filter(c => c.market_type === 'blue_ocean').length,
    emerging: categories.filter(c => c.market_type === 'emerging').length,
    redOcean: categories.filter(c => c.market_type === 'red_ocean').length,
  }

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortOrder('desc')
    }
  }

  if (loading) {
    return <CategoriesPageSkeleton />
  }

  // 市场类型筛选选项
  const filterOptions: { key: MarketType | 'all'; label: string }[] = [
    { key: 'all', label: t('categories.filter.all') },
    ...Object.entries(MARKET_TYPE_CONFIG).map(([key, config]) => ({
      key: key as MarketType,
      label: t(`marketType.${key}`),
    })),
  ]

  // 排序选项
  const sortOptions: { value: SortField; label: string }[] = [
    { value: 'market_type', label: t('categories.sort.marketType') },
    { value: 'total_revenue', label: t('categories.sort.totalRevenue') },
    { value: 'median_revenue', label: t('categories.sort.medianRevenue') },
    { value: 'total_projects', label: t('categories.sort.totalProjects') },
    { value: 'category', label: t('categories.sort.name') },
  ]

  return (
    <div className="space-y-6">
      {/* 页面头部 - 统计信息整合在标题区 */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-display font-bold text-content-primary flex items-center gap-3 tracking-tight">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-brand-500/15 to-accent-secondary/15 flex items-center justify-center ring-1 ring-brand-500/10">
              <Layers className="h-5 w-5 text-brand-500" />
            </div>
            {t('categories.title')}
          </h1>
          <p className="text-sm text-content-secondary mt-2 font-medium">
            {t('common.total')} <span className="font-bold text-content-primary">{stats.total}</span> {t('categories.stats.total')}，
            <span className="text-cyan-500 font-bold">{stats.blueOcean}</span> {t('categories.stats.blueOcean')}，
            <span className="text-amber-500 font-bold">{stats.emerging}</span> {t('categories.stats.emerging')}，
            <span className="text-rose-500 font-bold">{stats.redOcean}</span> {t('categories.stats.redOcean')}
          </p>
        </div>
      </div>

      {/* 筛选栏 */}
      <div className="flex flex-wrap items-center gap-3">
        {/* 市场类型筛选 - 使用pill按钮 */}
        <div className="flex flex-wrap gap-2">
          {filterOptions.map((opt) => (
            <button
              key={opt.key}
              onClick={() => setFilterType(opt.key)}
              className={cn(
                'px-3.5 py-1.5 rounded-full text-sm font-semibold transition-all duration-200',
                filterType === opt.key
                  ? 'bg-gradient-to-r from-brand-500 to-brand-600 text-white shadow-md shadow-brand-500/25'
                  : 'bg-surface/80 text-content-secondary hover:bg-surface-hover hover:text-content-primary border border-surface-border/60'
              )}
            >
              {opt.label}
            </button>
          ))}
        </div>

        {/* 排序 */}
        <div className="flex items-center gap-2 text-sm text-content-muted ml-auto">
          <ArrowDownWideNarrow className="h-4 w-4" />
          <select
            value={sortField}
            onChange={(e) => setSortField(e.target.value as SortField)}
            className="select text-sm py-1.5 font-medium"
          >
            {sortOptions.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
          <button
            onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
            className="p-1.5 rounded-lg hover:bg-surface/60 text-content-muted hover:text-content-primary transition-colors"
          >
            {sortOrder === 'asc' ? (
              <ArrowUp className="h-4 w-4" />
            ) : (
              <ArrowDown className="h-4 w-4" />
            )}
          </button>
        </div>

        <span className="text-xs text-content-muted font-medium">
          {t('common.total')} {filteredAndSorted.length} {t('common.items')}
        </span>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* 左侧：赛道列表 */}
        <div className="lg:col-span-2">
          {/* 赛道列表 */}
          <div className="min-h-[400px]">
            <AnimatePresence mode="wait">
              <motion.div
                key={`${filterType}-${sortField}-${sortOrder}`}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.15 }}
                className="space-y-2"
              >
                {filteredAndSorted.map((category, index) => (
                  <CategoryRow
                    key={category.id}
                    category={category}
                    isSelected={selectedCategory?.id === category.id}
                    onClick={() => setSelectedCategory(category)}
                    index={index}
                  />
                ))}
                {filteredAndSorted.length === 0 && (
                  <div className="text-center py-12 text-content-muted">
                    {t('categories.noCategories')}
                  </div>
                )}
              </motion.div>
            </AnimatePresence>
          </div>
        </div>

        {/* 右侧：详情面板 */}
        <div className="lg:sticky lg:top-24 lg:self-start space-y-4">
          <AnimatePresence mode="wait">
            {selectedCategory ? (
              <motion.div
                key={selectedCategory.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.2 }}
              >
                <CategoryDetailPanel category={selectedCategory} />
              </motion.div>
            ) : (
              <Card className="text-center py-12 text-content-muted">
                {t('categories.selectCategory')}
              </Card>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  )
}

interface CategoryRowProps {
  category: CategoryAnalysis
  isSelected: boolean
  onClick: () => void
  index: number
}

function CategoryRow({ category, isSelected, onClick, index }: CategoryRowProps) {
  const { t } = useLocale()
  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.2, delay: index * 0.02 }}
      onClick={onClick}
      className={cn(
        'flex items-center gap-4 p-4 rounded-xl cursor-pointer transition-all duration-200',
        'bg-surface/70 backdrop-blur-sm border border-surface-border/50',
        isSelected
          ? 'border-brand-500/50 ring-2 ring-brand-500/20 bg-brand-50/50 dark:bg-brand-950/20'
          : 'hover:border-surface-border hover:shadow-sm hover:bg-surface/90'
      )}
    >
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-3 mb-1">
          <span className={cn(
            'text-sm font-bold tracking-tight',
            isSelected ? 'text-brand-600 dark:text-brand-400' : 'text-content-primary'
          )}>
            {category.category}
          </span>
          <MarketTypeBadge type={category.market_type} size="sm" />
        </div>
        <p className="text-xs text-content-tertiary line-clamp-1 font-medium">
          {category.market_type_reason}
        </p>
      </div>

      <div className="flex items-center gap-6 flex-shrink-0">
        <div className="text-right">
          <div className="font-mono text-sm font-bold text-content-primary tabular-nums">
            {category.total_projects}
          </div>
          <div className="text-[11px] text-content-muted font-medium">{t('categories.units.products')}</div>
        </div>
        <div className="text-right">
          <div className="font-mono text-sm font-bold text-content-primary tabular-nums">
            {formatCurrency(category.median_revenue)}
          </div>
          <div className="text-[11px] text-content-muted font-medium">{t('categories.units.median')}</div>
        </div>
        <div className="text-right w-24">
          <div className="font-mono text-sm font-bold text-brand-600 dark:text-brand-400 tabular-nums">
            {formatCurrency(category.total_revenue)}
          </div>
          <div className="text-[11px] text-content-muted font-medium">{t('categories.metrics.totalRevenue')}</div>
        </div>
      </div>
    </motion.div>
  )
}

interface CategoryDetailPanelProps {
  category: CategoryAnalysis
}

function CategoryDetailPanel({ category }: CategoryDetailPanelProps) {
  const { t } = useLocale()
  return (
    <div className="space-y-4">
      {/* 基本信息 */}
      <Card>
        <div className="flex items-start justify-between mb-4">
          <div>
            <h2 className="text-xl font-display font-bold text-content-primary tracking-tight">
              {category.category}
            </h2>
            <MarketTypeBadge type={category.market_type} size="md" className="mt-2" />
          </div>
        </div>
        <p className="text-sm text-content-secondary leading-relaxed mb-4 font-medium">
          {category.market_type_reason}
        </p>

        {/* 雷达图 */}
        <MarketRadarChart
          metrics={{
            total_projects: category.total_projects,
            median_revenue: category.median_revenue,
            top10_revenue_share: category.top10_revenue_share,
            gini_coefficient: category.gini_coefficient,
          }}
          className="h-48"
        />
      </Card>

      {/* 详细指标 */}
      <Card>
        <CardHeader title={t('categories.detailMetrics')} />
        <div className="space-y-3">
          <MetricRow label={t('categories.metrics.totalProjects')} value={formatNumber(category.total_projects)} />
          <MetricRow label={t('categories.metrics.totalRevenue')} value={formatCurrency(category.total_revenue)} />
          <MetricRow label={t('categories.metrics.avgRevenue')} value={formatCurrency(category.avg_revenue)} />
          <MetricRow label={t('categories.metrics.medianRevenue')} value={formatCurrency(category.median_revenue)} highlight />
          <MetricRow label={t('categories.metrics.revenuePerProject')} value={formatCurrency(category.revenue_per_project)} />
          <MetricRow label={t('categories.metrics.top10Share')} value={formatPercent(category.top10_revenue_share)} />
          <MetricRow label={t('categories.metrics.top50Share')} value={formatPercent(category.top50_revenue_share)} />
          <MetricRow label={t('categories.metrics.revenueStdDev')} value={formatCurrency(category.revenue_std_dev)} />
          <MetricRow label={t('categories.metrics.giniCoefficient')} value={category.gini_coefficient.toFixed(4)} />
        </div>
      </Card>
    </div>
  )
}

function MetricRow({ label, value, highlight }: { label: string; value: string; highlight?: boolean }) {
  return (
    <div className="flex items-center justify-between py-1.5">
      <span className="text-sm text-content-tertiary font-medium">{label}</span>
      <span className={cn(
        'font-mono text-sm tabular-nums',
        highlight ? 'text-brand-600 dark:text-brand-400 font-bold' : 'text-content-primary font-semibold'
      )}>
        {value}
      </span>
    </div>
  )
}

function CategoriesPageSkeleton() {
  return (
    <div className="space-y-6">
      {/* 头部骨架 */}
      <div>
        <div className="h-8 w-48 bg-surface-border rounded animate-pulse mb-2" />
        <div className="h-4 w-64 bg-surface-border rounded animate-pulse" />
      </div>

      {/* 筛选栏骨架 */}
      <div className="flex gap-2">
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="h-8 w-16 bg-surface-border rounded-full animate-pulse" />
        ))}
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-2">
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="flex items-center gap-4 p-4 rounded-xl bg-surface border border-surface-border/50">
              <div className="flex-1">
                <div className="h-4 w-32 bg-surface-border rounded animate-pulse mb-2" />
                <div className="h-3 w-48 bg-surface-border rounded animate-pulse" />
              </div>
              <div className="h-4 w-16 bg-surface-border rounded animate-pulse" />
              <div className="h-4 w-16 bg-surface-border rounded animate-pulse" />
              <div className="h-4 w-20 bg-surface-border rounded animate-pulse" />
            </div>
          ))}
        </div>
        <div className="card animate-pulse h-96" />
      </div>
    </div>
  )
}
