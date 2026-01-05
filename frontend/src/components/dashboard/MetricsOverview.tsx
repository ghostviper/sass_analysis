'use client'

import {
  Package,
  PieChart,
  Waves,
  Lightbulb,
  DollarSign,
  TrendingUp,
} from 'lucide-react'
import { StatCard, CardPattern } from '@/components/ui/Card'
import { formatCurrency, formatNumber } from '@/lib/utils'

interface MetricsOverviewProps {
  stats: {
    total_products: number
    products_with_revenue: number
    total_categories: number
    blue_ocean_categories: number
    opportunity_products: number
    avg_revenue: number
  }
}

export function MetricsOverview({ stats }: MetricsOverviewProps) {
  const metrics: Array<{
    title: string
    value: string
    subtitle: string
    icon: React.ReactNode
    pattern: CardPattern
  }> = [
    {
      title: '产品总数',
      value: formatNumber(stats.total_products),
      subtitle: `${stats.products_with_revenue} 个有收入`,
      icon: <Package className="h-5 w-5" />,
      pattern: 'circles',
    },
    {
      title: '分析赛道',
      value: formatNumber(stats.total_categories),
      subtitle: `${stats.blue_ocean_categories} 个蓝海`,
      icon: <PieChart className="h-5 w-5" />,
      pattern: 'stars',
    },
    {
      title: '蓝海赛道',
      value: formatNumber(stats.blue_ocean_categories),
      subtitle: '低竞争高收益',
      icon: <Waves className="h-5 w-5" />,
      pattern: 'leaves',
    },
    {
      title: '机会产品',
      value: formatNumber(stats.opportunity_products),
      subtitle: '符合筛选条件',
      icon: <Lightbulb className="h-5 w-5" />,
      pattern: 'light',
    },
    {
      title: '平均收入',
      value: formatCurrency(stats.avg_revenue),
      subtitle: '月收入/产品',
      icon: <DollarSign className="h-5 w-5" />,
      pattern: 'grass',
    },
    {
      title: '数据完整度',
      value: `${Math.round((stats.products_with_revenue / stats.total_products) * 100)}%`,
      subtitle: '有收入数据',
      icon: <TrendingUp className="h-5 w-5" />,
      pattern: 'ribbons',
    },
  ]

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
      {metrics.map((metric, index) => (
        <StatCard
          key={metric.title}
          title={metric.title}
          value={metric.value}
          subtitle={metric.subtitle}
          icon={metric.icon}
          pattern={metric.pattern}
          className="animate-fade-in"
          style={{ animationDelay: `${index * 50}ms` }}
        />
      ))}
    </div>
  )
}

// 骨架屏版本
export function MetricsOverviewSkeleton() {
  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
      {Array.from({ length: 6 }).map((_, i) => (
        <div key={i} className="card animate-pulse">
          <div className="flex items-center justify-between mb-2">
            <div className="h-4 w-16 bg-surface-border rounded" />
            <div className="h-10 w-10 bg-surface-border rounded-lg" />
          </div>
          <div className="h-8 w-20 bg-surface-border rounded mb-2" />
          <div className="h-3 w-24 bg-surface-border rounded" />
        </div>
      ))}
    </div>
  )
}
