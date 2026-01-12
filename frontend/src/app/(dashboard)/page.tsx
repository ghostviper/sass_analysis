'use client'

import { useEffect, useState } from 'react'
import { MetricsOverview, MetricsOverviewSkeleton } from '@/components/dashboard/MetricsOverview'
import { OpportunityRanking, OpportunityRankingSkeleton } from '@/components/dashboard/OpportunityRanking'
import { CategoryOverview, CategoryOverviewSkeleton, MarketTypeDistribution } from '@/components/dashboard/CategoryOverview'
import { LeaderboardSwitcher } from '@/components/dashboard/LeaderboardSwitcher'
import { DataDisclaimer } from '@/components/ui/DataDisclaimer'
import { Card, CardHeader } from '@/components/ui/Card'
import { useLocale } from '@/contexts/LocaleContext'
import {
  getDashboardStats,
  getOpportunityProducts,
  getCategoryAnalysis,
} from '@/lib/api'
import type { OpportunityProduct, CategoryAnalysis } from '@/types'
import { Rocket, Lightbulb, TrendingUp } from 'lucide-react'

export default function DashboardPage() {
  const { t } = useLocale()
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
        setError(t('dashboard.errorMessage'))
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [t])

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Card className="text-center max-w-md">
          <div className="text-accent-danger text-4xl mb-4">⚠️</div>
          <h2 className="text-xl font-semibold text-content-primary mb-2">{t('common.error')}</h2>
          <p className="text-content-muted mb-4">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="btn btn-primary"
          >
            {t('common.retry')}
          </button>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* 欢迎横幅 */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-brand-500/10 via-brand-400/5 to-accent-secondary/10 border border-brand-500/20 p-6 md:p-8">
        <div className="absolute top-0 right-0 w-64 h-64 bg-brand-500/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2" />
        <div className="absolute bottom-0 left-0 w-48 h-48 bg-accent-secondary/10 rounded-full blur-3xl translate-y-1/2 -translate-x-1/2" />
        <div className="relative">
          <div className="flex items-center gap-4 mb-4">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-brand-500 via-brand-600 to-accent-secondary flex items-center justify-center shadow-lg shadow-brand-500/20">
              <Rocket className="h-7 w-7 text-white" />
            </div>
            <div>
              <h1 className="text-2xl md:text-3xl font-display font-bold tracking-tight bg-gradient-to-r from-content-primary via-content-primary to-brand-600 dark:to-brand-400 bg-clip-text text-transparent">
                {t('dashboard.welcome.title')}
              </h1>
              <p className="text-sm text-content-secondary mt-1 font-medium">
                {t('dashboard.welcome.subtitle')}
              </p>
            </div>
          </div>
          <div className="flex flex-wrap gap-4 mt-5">
            <div className="flex items-center gap-2.5 text-sm text-content-secondary font-medium">
              <div className="w-8 h-8 rounded-lg bg-amber-500/10 flex items-center justify-center">
                <Lightbulb className="h-4 w-4 text-amber-500" />
              </div>
              <span>{t('dashboard.welcome.filterTip')}</span>
            </div>
            <div className="flex items-center gap-2.5 text-sm text-content-secondary font-medium">
              <div className="w-8 h-8 rounded-lg bg-emerald-500/10 flex items-center justify-center">
                <TrendingUp className="h-4 w-4 text-emerald-500" />
              </div>
              <span>{t('dashboard.welcome.analysisTip')}</span>
            </div>
          </div>
        </div>
      </div>

      {/* 关键指标 */}
      <section>
        <h2 className="text-lg font-display font-bold text-content-primary mb-4 tracking-tight">
          {t('dashboard.keyMetrics')}
        </h2>
        {loading ? (
          <MetricsOverviewSkeleton />
        ) : (
          stats && <MetricsOverview stats={stats} />
        )}
      </section>

      {/* 主要内容区 */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* 多视角榜单 - 占 2 列 */}
        <div className="lg:col-span-2">
          <LeaderboardSwitcher limit={5} />
        </div>

        {/* 市场分布 */}
        <div className="lg:sticky lg:top-20 lg:self-start space-y-4">
          {loading ? (
            <Card className="animate-pulse">
              <div className="h-64 bg-surface-border rounded" />
            </Card>
          ) : (
            <MarketTypeDistribution categories={categories} />
          )}
          {/* 数据说明 - 紧凑版 */}
          <DataDisclaimer variant="compact" />
        </div>
      </div>

      {/* 机会榜单 */}
      <section>
        {loading ? (
          <OpportunityRankingSkeleton />
        ) : (
          <OpportunityRanking
            products={opportunities}
            title={`🔥 ${t('dashboard.opportunityRanking')}`}
            subtitle={t('dashboard.opportunitySubtitle')}
            limit={5}
          />
        )}
      </section>

      {/* 赛道分析 */}
      <section>
        {loading ? (
          <CategoryOverviewSkeleton />
        ) : (
          <CategoryOverview
            categories={categories}
            title={`📊 ${t('dashboard.categoryAnalysis')}`}
            subtitle={t('dashboard.categorySubtitle')}
            limit={8}
          />
        )}
      </section>

      {/* 快速入口 */}
      <section>
        <h2 className="text-lg font-display font-bold text-content-primary mb-4 tracking-tight">
          {t('dashboard.quickAccess')}
        </h2>
        <div className="grid md:grid-cols-3 gap-4">
          <QuickAccessCard
            href="/categories"
            icon="📈"
            title={t('dashboard.quickAccessCards.categories.title')}
            description={t('dashboard.quickAccessCards.categories.desc')}
            color="from-market-blue-ocean/20 to-market-blue-ocean/5"
          />
          <QuickAccessCard
            href="/products?filter=opportunities"
            icon="💡"
            title={t('dashboard.quickAccessCards.opportunities.title')}
            description={t('dashboard.quickAccessCards.opportunities.desc')}
            color="from-accent-warning/20 to-accent-warning/5"
          />
          <QuickAccessCard
            href="/products"
            icon="📦"
            title={t('dashboard.quickAccessCards.products.title')}
            description={t('dashboard.quickAccessCards.products.desc')}
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
      className={`block p-6 rounded-2xl bg-gradient-to-br ${color} border border-surface-border/50 hover:border-brand-500/30 hover:shadow-md transition-all duration-200 group`}
    >
      <div className="text-3xl mb-3">{icon}</div>
      <h3 className="text-base font-bold text-content-primary group-hover:text-brand-600 dark:group-hover:text-brand-400 transition-colors tracking-tight">
        {title}
      </h3>
      <p className="text-sm text-content-tertiary mt-1.5 font-medium">{description}</p>
    </a>
  )
}
