'use client'

import { useEffect, useState } from 'react'
import { MetricsOverview, MetricsOverviewSkeleton } from '@/components/dashboard/MetricsOverview'
import { OpportunityRanking, OpportunityRankingSkeleton } from '@/components/dashboard/OpportunityRanking'
import { CategoryOverview, CategoryOverviewSkeleton, MarketTypeDistribution } from '@/components/dashboard/CategoryOverview'
import { Card, CardHeader } from '@/components/ui/Card'
import {
  getDashboardStats,
  getOpportunityProducts,
  getCategoryAnalysis,
} from '@/lib/api'
import type { OpportunityProduct, CategoryAnalysis } from '@/types'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faLightbulb, faChartLine, faRocket } from '@fortawesome/free-solid-svg-icons'

export default function DashboardPage() {
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState<any>(null)
  const [opportunities, setOpportunities] = useState<OpportunityProduct[]>([])
  const [categories, setCategories] = useState<CategoryAnalysis[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true)
        const [statsData, opportunitiesData, categoriesData] = await Promise.all([
          getDashboardStats(),
          getOpportunityProducts({ limit: 10 }),
          getCategoryAnalysis(),
        ])

        setStats(statsData)
        setOpportunities(opportunitiesData)
        setCategories(categoriesData)
      } catch (err) {
        console.error('Failed to fetch dashboard data:', err)
        setError('数据加载失败，请确保后端服务已启动')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Card className="text-center max-w-md">
          <div className="text-accent-danger text-4xl mb-4">⚠️</div>
          <h2 className="text-xl font-semibold text-content-primary mb-2">加载失败</h2>
          <p className="text-content-muted mb-4">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="btn btn-primary"
          >
            重新加载
          </button>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* 欢迎横幅 */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-accent-primary/20 via-accent-secondary/10 to-market-blue-ocean/20 border border-accent-primary/20 p-6 md:p-8">
        <div className="absolute top-0 right-0 w-64 h-64 bg-accent-primary/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2" />
        <div className="relative">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-12 h-12 rounded-xl bg-accent-primary/20 flex items-center justify-center">
              <FontAwesomeIcon icon={faRocket} className="h-6 w-6 text-accent-primary" />
            </div>
            <div>
              <h1 className="text-display">
                发现下一个产品机会
              </h1>
              <p className="text-body-sm mt-1">
                基于数据驱动的 SaaS 产品分析，为独立开发者提供洞察
              </p>
            </div>
          </div>
          <div className="flex flex-wrap gap-4 mt-4">
            <div className="flex items-center gap-2 text-caption">
              <FontAwesomeIcon icon={faLightbulb} className="text-accent-warning" />
              <span>筛选低竞争高收益产品</span>
            </div>
            <div className="flex items-center gap-2 text-caption">
              <FontAwesomeIcon icon={faChartLine} className="text-accent-success" />
              <span>分析市场类型与机会</span>
            </div>
          </div>
        </div>
      </div>

      {/* 关键指标 */}
      <section>
        <h2 className="text-heading mb-4">
          关键指标
        </h2>
        {loading ? (
          <MetricsOverviewSkeleton />
        ) : (
          stats && <MetricsOverview stats={stats} />
        )}
      </section>

      {/* 主要内容区 */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* 机会榜单 - 占 2 列 */}
        <div className="lg:col-span-2">
          {loading ? (
            <OpportunityRankingSkeleton />
          ) : (
            <OpportunityRanking
              products={opportunities}
              title="🔥 机会榜单 TOP 5"
              subtitle="符合筛选条件的优质产品"
              limit={5}
            />
          )}
        </div>

        {/* 市场分布 */}
        <div className="lg:sticky lg:top-20 lg:self-start">
          {loading ? (
            <Card className="animate-pulse">
              <div className="h-64 bg-surface-border rounded" />
            </Card>
          ) : (
            <MarketTypeDistribution categories={categories} />
          )}
        </div>
      </div>

      {/* 赛道分析 */}
      <section>
        {loading ? (
          <CategoryOverviewSkeleton />
        ) : (
          <CategoryOverview
            categories={categories}
            title="📊 赛道分析"
            subtitle="发现蓝海与新兴市场"
            limit={8}
          />
        )}
      </section>

      {/* 快速入口 */}
      <section>
        <h2 className="text-heading mb-4">
          快速入口
        </h2>
        <div className="grid md:grid-cols-3 gap-4">
          <QuickAccessCard
            href="/categories"
            icon="📈"
            title="赛道分析"
            description="查看所有赛道的市场类型和机会评估"
            color="from-market-blue-ocean/20 to-market-blue-ocean/5"
          />
          <QuickAccessCard
            href="/products?filter=opportunities"
            icon="💡"
            title="机会产品"
            description="筛选符合条件的可复制产品"
            color="from-accent-warning/20 to-accent-warning/5"
          />
          <QuickAccessCard
            href="/products"
            icon="📦"
            title="产品库"
            description="浏览所有已分析的 SaaS 产品"
            color="from-accent-secondary/20 to-accent-secondary/5"
          />
        </div>
      </section>
    </div>
  )
}

interface QuickAccessCardProps {
  href: string
  icon: string
  title: string
  description: string
  color: string
}

function QuickAccessCard({ href, icon, title, description, color }: QuickAccessCardProps) {
  return (
    <a
      href={href}
      className={`block p-6 rounded-xl bg-gradient-to-br ${color} border border-surface-border/50 hover:border-accent-primary/30 transition-all group`}
    >
      <div className="text-3xl mb-3">{icon}</div>
      <h3 className="text-heading-sm group-hover:text-accent-primary transition-colors">
        {title}
      </h3>
      <p className="text-caption mt-1.5">{description}</p>
    </a>
  )
}
