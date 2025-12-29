'use client'

import Link from 'next/link'
import { Card, CardHeader } from '@/components/ui/Card'
import { MarketTypeBadge } from '@/components/ui/Badge'
import { formatCurrency, formatNumber } from '@/lib/utils'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faArrowRight } from '@fortawesome/free-solid-svg-icons'
import type { CategoryAnalysis, MarketType } from '@/types'

interface CategoryOverviewProps {
  categories: CategoryAnalysis[]
  title?: string
  subtitle?: string
  limit?: number
}

export function CategoryOverview({
  categories,
  title = '赛道分析',
  subtitle = '市场机会洞察',
  limit = 8,
}: CategoryOverviewProps) {
  // 按市场类型排序：蓝海 > 新兴 > 适中 > 其他
  const typeOrder: Record<MarketType, number> = {
    blue_ocean: 0,
    emerging: 1,
    moderate: 2,
    concentrated: 3,
    red_ocean: 4,
    weak_demand: 5,
  }

  const sortedCategories = [...categories]
    .sort((a, b) => {
      const orderDiff = typeOrder[a.market_type] - typeOrder[b.market_type]
      if (orderDiff !== 0) return orderDiff
      return b.median_revenue - a.median_revenue
    })
    .slice(0, limit)

  return (
    <Card>
      <CardHeader
        title={title}
        subtitle={subtitle}
        action={
          <Link
            href="/categories"
            className="flex items-center gap-1 text-sm text-accent-primary hover:underline"
          >
            查看全部
            <FontAwesomeIcon icon={faArrowRight} className="h-3 w-3" />
          </Link>
        }
      />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {sortedCategories.map((category, index) => (
          <CategoryCard
            key={category.id}
            category={category}
            index={index}
          />
        ))}

        {sortedCategories.length === 0 && (
          <div className="col-span-2 text-center py-8 text-content-muted">
            暂无赛道分析数据
          </div>
        )}
      </div>
    </Card>
  )
}

interface CategoryCardProps {
  category: CategoryAnalysis
  index: number
}

function CategoryCard({ category, index }: CategoryCardProps) {
  return (
    <Link
      href={`/categories?name=${encodeURIComponent(category.category)}`}
      className="flex items-center justify-between p-4 rounded-lg border border-surface-border/50 bg-background-secondary/30 hover:bg-surface/50 hover:border-accent-primary/30 transition-all group animate-fade-in"
      style={{ animationDelay: `${index * 50}ms` }}
    >
      <div className="min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <span className="font-medium text-content-primary group-hover:text-accent-primary transition-colors truncate">
            {category.category}
          </span>
          <MarketTypeBadge type={category.market_type} size="sm" />
        </div>
        <div className="flex items-center gap-4 text-sm text-content-muted">
          <span>{category.total_projects} 个产品</span>
          <span>中位数 {formatCurrency(category.median_revenue)}</span>
        </div>
      </div>

      <div className="text-right flex-shrink-0">
        <div className="font-mono text-lg font-medium text-content-primary">
          {formatCurrency(category.total_revenue)}
        </div>
        <div className="text-xs text-content-muted">总收入</div>
      </div>
    </Link>
  )
}

// 市场类型分布统计
interface MarketTypeDistributionProps {
  categories: CategoryAnalysis[]
}

export function MarketTypeDistribution({ categories }: MarketTypeDistributionProps) {
  const distribution = categories.reduce((acc, cat) => {
    acc[cat.market_type] = (acc[cat.market_type] || 0) + 1
    return acc
  }, {} as Record<MarketType, number>)

  const types: MarketType[] = ['blue_ocean', 'emerging', 'moderate', 'concentrated', 'red_ocean', 'weak_demand']

  return (
    <Card>
      <CardHeader title="市场分布" subtitle="按类型统计" />

      <div className="space-y-3">
        {types.map((type) => {
          const count = distribution[type] || 0
          const percentage = categories.length > 0 ? (count / categories.length) * 100 : 0

          return (
            <div key={type} className="flex items-center gap-3">
              <MarketTypeBadge type={type} size="sm" className="w-24 justify-center" />
              <div className="flex-1">
                <div className="h-2 rounded-full bg-background-tertiary overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${getMarketTypeBarColor(type)}`}
                    style={{ width: `${percentage}%` }}
                  />
                </div>
              </div>
              <span className="text-sm font-mono text-content-secondary w-12 text-right">
                {count}
              </span>
            </div>
          )
        })}
      </div>
    </Card>
  )
}

function getMarketTypeBarColor(type: MarketType): string {
  const colors: Record<MarketType, string> = {
    blue_ocean: 'bg-market-blue-ocean',
    emerging: 'bg-market-emerging',
    moderate: 'bg-market-moderate',
    concentrated: 'bg-market-concentrated',
    red_ocean: 'bg-market-red-ocean',
    weak_demand: 'bg-market-weak-demand',
  }
  return colors[type]
}

// 骨架屏
export function CategoryOverviewSkeleton() {
  return (
    <Card>
      <div className="flex items-center justify-between mb-4">
        <div>
          <div className="h-5 w-24 bg-surface-border rounded mb-1" />
          <div className="h-4 w-32 bg-surface-border rounded" />
        </div>
        <div className="h-4 w-16 bg-surface-border rounded" />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="flex items-center justify-between p-4 rounded-lg border border-surface-border/50 animate-pulse">
            <div>
              <div className="h-4 w-24 bg-surface-border rounded mb-2" />
              <div className="h-3 w-32 bg-surface-border rounded" />
            </div>
            <div className="text-right">
              <div className="h-5 w-16 bg-surface-border rounded mb-1" />
              <div className="h-3 w-10 bg-surface-border rounded" />
            </div>
          </div>
        ))}
      </div>
    </Card>
  )
}
