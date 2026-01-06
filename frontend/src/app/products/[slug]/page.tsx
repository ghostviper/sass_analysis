'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'
import { Card, CardHeader } from '@/components/ui/Card'
import { Badge, MarketTypeBadge } from '@/components/ui/Badge'
import { ProductLogo } from '@/components/ui/ProductLogo'
import { AnalysisRadarChart } from '@/components/charts/RadarChart'
import { ProductDetailSkeleton } from '@/components/ui/Loading'
import {
  getStartupBySlug,
  getComprehensiveAnalysis,
  getLandingAnalysis,
  getProductSelection,
  getCategoryByName,
  getProductInsights,
  type ProductInsightsResponse,
} from '@/lib/api'
import { formatCurrency, formatDate, cn } from '@/lib/utils'
import { useLocale } from '@/contexts/LocaleContext'
import { ArrowLeft, ExternalLink, AlertTriangle, Check } from 'lucide-react'
import type {
  Startup,
  ComprehensiveAnalysis,
  LandingPageAnalysis,
  ProductSelectionAnalysis,
  CategoryAnalysis,
} from '@/types'

export default function ProductDetailPage() {
  const params = useParams()
  const slug = params.slug as string
  const { locale } = useLocale()
  const isZh = locale === 'zh-CN'

  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [product, setProduct] = useState<Startup | null>(null)
  const [comprehensive, setComprehensive] = useState<ComprehensiveAnalysis | null>(null)
  const [landing, setLanding] = useState<LandingPageAnalysis | null>(null)
  const [selection, setSelection] = useState<ProductSelectionAnalysis | null>(null)
  const [category, setCategory] = useState<CategoryAnalysis | null>(null)
  const [insights, setInsights] = useState<ProductInsightsResponse | null>(null)

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true)
        setError(null)

        const productData = await getStartupBySlug(slug)
        setProduct(productData)

        const [compData, landingData, selectionData, insightsData] = await Promise.allSettled([
          getComprehensiveAnalysis(slug),
          getLandingAnalysis(slug),
          getProductSelection(slug),
          getProductInsights(slug),
        ])

        if (compData.status === 'fulfilled') setComprehensive(compData.value)
        if (landingData.status === 'fulfilled') setLanding(landingData.value)
        if (selectionData.status === 'fulfilled') setSelection(selectionData.value)
        if (insightsData.status === 'fulfilled') setInsights(insightsData.value)

        if (productData.category) {
          try {
            const catData = await getCategoryByName(productData.category)
            setCategory(catData)
          } catch (e) {}
        }
      } catch (err) {
        console.error('Failed to fetch product:', err)
        setError(isZh ? '加载失败' : 'Failed to load')
      } finally {
        setLoading(false)
      }
    }

    if (slug) fetchData()
  }, [slug, isZh])

  if (loading) return <ProductDetailSkeleton />

  if (error || !product) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Card className="text-center max-w-md">
          <AlertTriangle className="h-8 w-8 mx-auto mb-3 text-content-muted" />
          <p className="text-content-secondary mb-4">{error || (isZh ? '产品未找到' : 'Product not found')}</p>
          <Link href="/products" className="btn btn-primary">{isZh ? '返回' : 'Go Back'}</Link>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6 pb-12">
      <Link
        href="/products"
        className="inline-flex items-center gap-1.5 text-sm text-content-muted hover:text-content-primary transition-colors"
      >
        <ArrowLeft className="h-4 w-4" />
        {isZh ? '返回列表' : 'Back'}
      </Link>

      {/* 产品头部 */}
      <ProductHeader product={product} category={category} comprehensive={comprehensive} isZh={isZh} />

      {/* 主体两栏 */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* 左侧 - 核心信息 */}
        <div className="lg:col-span-2 space-y-6">
          {/* 产品介绍 */}
          {landing && <ProductIntro landing={landing} isZh={isZh} />}

          {/* 分析结论 */}
          <AnalysisSummary insights={insights} comprehensive={comprehensive} isZh={isZh} />
        </div>

        {/* 右侧 - 数据面板 */}
        <div className="space-y-6">
          {/* 评分 */}
          {comprehensive && <ScorePanel comprehensive={comprehensive} isZh={isZh} />}

          {/* 关键指标 */}
          <MetricsPanel selection={selection} landing={landing} category={category} isZh={isZh} />
        </div>
      </div>
    </div>
  )
}

// ============ 产品头部 ============
function ProductHeader({ product, category, comprehensive, isZh }: {
  product: Startup
  category: CategoryAnalysis | null
  comprehensive: ComprehensiveAnalysis | null
  isZh: boolean
}) {
  return (
    <Card padding="none" className="overflow-hidden">
      {/* 主体区域 */}
      <div className="p-6 md:p-8 lg:p-10">
        <div className="flex flex-col md:flex-row gap-6 md:gap-8">
          {/* Logo - 更大尺寸 */}
          <div className="flex-shrink-0">
            <div className="w-20 h-20 md:w-24 md:h-24 rounded-2xl overflow-hidden bg-surface-hover flex items-center justify-center">
              {product.logo_url ? (
                <img
                  src={product.logo_url}
                  alt={product.name}
                  className="w-full h-full object-cover"
                />
              ) : (
                <span className="text-3xl md:text-4xl font-bold text-content-muted">
                  {product.name.charAt(0).toUpperCase()}
                </span>
              )}
            </div>
          </div>

          {/* 主要信息 */}
          <div className="flex-1 min-w-0">
            {/* 标题行 */}
            <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
              <div>
                {/* 产品名称 - 大而醒目 */}
                <h1 className="text-3xl md:text-4xl font-bold text-content-primary tracking-tight">
                  {product.name}
                </h1>

                {/* 元信息 */}
                <div className="flex flex-wrap items-center gap-x-3 gap-y-1 mt-2 text-sm text-content-muted">
                  {product.category && (
                    <span className="font-medium">{product.category}</span>
                  )}
                  {category && (
                    <>
                      <span className="opacity-30">·</span>
                      <MarketTypeBadge type={category.market_type} />
                    </>
                  )}
                  {product.country_code && (
                    <>
                      <span className="opacity-30">·</span>
                      <span>{product.country_code}</span>
                    </>
                  )}
                </div>
              </div>

              {/* 访问按钮 */}
              {product.website_url && (
                <a
                  href={product.website_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn btn-primary flex-shrink-0 self-start"
                >
                  <ExternalLink className="h-4 w-4" />
                  {isZh ? '访问官网' : 'Visit Website'}
                </a>
              )}
            </div>

            {/* 产品描述 - 更大更显眼 */}
            {product.description && (
              <p className="text-base md:text-lg text-content-secondary mt-4 md:mt-5 leading-relaxed max-w-3xl">
                {product.description}
              </p>
            )}
          </div>
        </div>
      </div>

      {/* 数据指标区域 - 独立背景 */}
      <div className="bg-surface-hover/30 border-t border-surface-border/50">
        <div className="grid grid-cols-2 md:grid-cols-4">
          <DataCell
            label={isZh ? '月收入' : 'Monthly Revenue'}
            value={formatCurrency(product.revenue_30d)}
            highlight
          />
          <DataCell
            label={isZh ? '增长率' : 'Growth Rate'}
            value={product.growth_rate ? `${product.growth_rate > 0 ? '+' : ''}${product.growth_rate.toFixed(0)}%` : '-'}
            variant={product.growth_rate && product.growth_rate > 0 ? 'success' : product.growth_rate && product.growth_rate < 0 ? 'danger' : 'default'}
          />
          <DataCell
            label={isZh ? '粉丝数' : 'Followers'}
            value={product.twitter_followers ? `${(product.twitter_followers / 1000).toFixed(1)}K` : '-'}
          />
          <DataCell
            label={isZh ? '成立时间' : 'Founded'}
            value={product.founded_date ? formatDate(product.founded_date) : '-'}
          />
        </div>
      </div>
    </Card>
  )
}

function DataCell({ label, value, highlight, variant = 'default' }: {
  label: string
  value: string
  highlight?: boolean
  variant?: 'default' | 'success' | 'danger'
}) {
  return (
    <div className="text-center py-5 md:py-6 px-4 border-r border-surface-border/30 last:border-r-0 md:first:border-l-0">
      <div className={cn(
        'text-2xl md:text-3xl font-mono font-bold tracking-tight',
        highlight ? 'text-accent-primary' :
        variant === 'success' ? 'text-accent-success' :
        variant === 'danger' ? 'text-accent-danger' :
        'text-content-primary'
      )}>
        {value}
      </div>
      <div className="text-xs md:text-sm text-content-muted mt-1.5 font-medium">{label}</div>
    </div>
  )
}

// ============ 产品介绍 ============
function ProductIntro({ landing, isZh }: {
  landing: LandingPageAnalysis
  isZh: boolean
}) {
  const hasContent = landing.headline_text || landing.target_audience?.length ||
    landing.core_features?.length || landing.use_cases?.length

  if (!hasContent) return null

  return (
    <Card>
      <h2 className="text-lg font-semibold text-content-primary mb-5">
        {isZh ? '产品介绍' : 'About This Product'}
      </h2>

      {/* 核心定位 - 突出显示 */}
      {landing.headline_text && (
        <div className="mb-6 pb-6 border-b border-surface-border/50">
          <p className="text-lg md:text-xl text-content-primary leading-relaxed font-medium">
            {landing.headline_text}
          </p>
          {landing.tagline_text && (
            <p className="text-sm text-content-muted mt-2">{landing.tagline_text}</p>
          )}
        </div>
      )}

      {/* 信息网格 - 两列布局 */}
      <div className="grid md:grid-cols-2 gap-x-8 gap-y-6">
        {/* 左列 */}
        <div className="space-y-6">
          {/* 目标用户 */}
          {landing.target_audience && landing.target_audience.length > 0 && (
            <div>
              <h3 className="text-sm font-medium text-content-primary mb-3">{isZh ? '目标用户' : 'Target Users'}</h3>
              <div className="flex flex-wrap gap-2">
                {landing.target_audience.map((item, i) => (
                  <span key={i} className="px-3 py-1.5 rounded-full text-sm bg-surface-hover text-content-secondary">
                    {item}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* 使用场景 */}
          {landing.use_cases && landing.use_cases.length > 0 && (
            <div>
              <h3 className="text-sm font-medium text-content-primary mb-3">{isZh ? '使用场景' : 'Use Cases'}</h3>
              <ul className="space-y-2">
                {landing.use_cases.slice(0, 4).map((item, i) => (
                  <li key={i} className="text-sm text-content-secondary flex items-start gap-2">
                    <span className="text-content-muted mt-1.5">•</span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* 右列 */}
        <div className="space-y-6">
          {/* 核心功能 */}
          {landing.core_features && landing.core_features.length > 0 && (
            <div>
              <h3 className="text-sm font-medium text-content-primary mb-3">{isZh ? '核心功能' : 'Core Features'}</h3>
              <div className="flex flex-wrap gap-2">
                {landing.core_features.slice(0, 6).map((item, i) => (
                  <span key={i} className="px-3 py-1.5 rounded-full text-sm bg-surface-hover text-content-secondary">
                    {item}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* 产品优势 */}
          {landing.potential_moats && landing.potential_moats.length > 0 && (
            <div>
              <h3 className="text-sm font-medium text-content-primary mb-3">{isZh ? '产品优势' : 'Advantages'}</h3>
              <ul className="space-y-2">
                {landing.potential_moats.slice(0, 3).map((item, i) => (
                  <li key={i} className="text-sm text-content-secondary flex items-start gap-2">
                    <span className="text-content-muted mt-1.5">•</span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </Card>
  )
}

// ============ 分析结论 ============
function AnalysisSummary({ insights, comprehensive, isZh }: {
  insights: ProductInsightsResponse | null
  comprehensive: ComprehensiveAnalysis | null
  isZh: boolean
}) {
  const positiveInsights = insights?.insights.filter(i => i.type === 'positive') || []
  const warningInsights = insights?.insights.filter(i => i.type === 'warning') || []
  const strengths = comprehensive?.analysis_summary?.strengths || []
  const risks = comprehensive?.analysis_summary?.risks || []
  const keyRisks = insights?.risk_assessment?.key_risks || []
  const recommendations = comprehensive?.analysis_summary?.recommendations || []

  const allStrengths = [...positiveInsights.map(i => i.description), ...strengths]
  const allRisks = [...new Set([...warningInsights.map(i => i.description), ...keyRisks, ...risks])]

  if (allStrengths.length === 0 && allRisks.length === 0 && recommendations.length === 0) {
    return null
  }

  return (
    <Card>
      <h2 className="text-lg font-semibold text-content-primary mb-5">
        {isZh ? '分析结论' : 'Analysis'}
      </h2>

      <div className="space-y-6">
        {/* 亮点 - 绿色区块 */}
        {allStrengths.length > 0 && (
          <div className="rounded-lg bg-accent-success/5 p-4">
            <h3 className="text-sm font-medium text-accent-success mb-3">
              {isZh ? '做得好的地方' : 'What works well'}
            </h3>
            <ul className="space-y-2.5">
              {allStrengths.slice(0, 5).map((item, i) => (
                <li key={i} className="flex items-start gap-2.5 text-sm text-content-secondary">
                  <Check className="h-4 w-4 text-accent-success flex-shrink-0 mt-0.5" />
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* 风险和建议 - 两列布局 */}
        {(allRisks.length > 0 || recommendations.length > 0) && (
          <div className="grid md:grid-cols-2 gap-6">
            {/* 风险 */}
            {allRisks.length > 0 && (
              <div>
                <h3 className="text-sm font-medium text-content-primary mb-3">
                  {isZh ? '需要留意' : 'Things to watch'}
                </h3>
                <ul className="space-y-2.5">
                  {allRisks.slice(0, 4).map((item, i) => (
                    <li key={i} className="text-sm text-content-secondary flex items-start gap-2.5">
                      <span className="w-1.5 h-1.5 rounded-full bg-amber-500 mt-1.5 flex-shrink-0" />
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* 建议 */}
            {recommendations.length > 0 && (
              <div>
                <h3 className="text-sm font-medium text-content-primary mb-3">
                  {isZh ? '参考建议' : 'Suggestions'}
                </h3>
                <ul className="space-y-2.5">
                  {recommendations.slice(0, 4).map((item, i) => (
                    <li key={i} className="text-sm text-content-secondary flex items-start gap-2.5">
                      <span className="w-1.5 h-1.5 rounded-full bg-accent-primary mt-1.5 flex-shrink-0" />
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </Card>
  )
}

// ============ 评分面板 ============
function ScorePanel({ comprehensive, isZh }: {
  comprehensive: ComprehensiveAnalysis
  isZh: boolean
}) {
  const score = comprehensive.overall_recommendation

  const dimensions = [
    { label: isZh ? '成熟度' : 'Maturity', value: comprehensive.maturity_score },
    { label: isZh ? '定位' : 'Positioning', value: comprehensive.positioning_clarity },
    { label: isZh ? '需求' : 'Problem', value: comprehensive.pain_point_sharpness },
    { label: isZh ? '定价' : 'Pricing', value: comprehensive.pricing_clarity },
    { label: isZh ? '转化' : 'Conversion', value: comprehensive.conversion_friendliness },
    { label: isZh ? '可复制' : 'Replicability', value: comprehensive.individual_replicability },
  ]

  return (
    <Card>
      <h2 className="text-lg font-semibold text-content-primary mb-5">
        {isZh ? '综合评分' : 'Overall Score'}
      </h2>

      {/* 总分 - 更突出 */}
      <div className="text-center py-4 mb-5 rounded-xl bg-surface-hover">
        <div className={cn(
          'text-4xl font-mono font-bold',
          score >= 7 ? 'text-accent-success' : score >= 5 ? 'text-amber-500' : 'text-content-muted'
        )}>
          {score.toFixed(1)}
        </div>
        <div className="text-sm text-content-muted mt-1">
          {score >= 7 ? (isZh ? '值得研究' : 'Worth studying') :
           score >= 5 ? (isZh ? '可以参考' : 'Good reference') :
           (isZh ? '参考有限' : 'Limited value')}
        </div>
      </div>

      {/* 雷达图 */}
      <AnalysisRadarChart
        scores={{
          maturity_score: comprehensive.maturity_score,
          positioning_clarity: comprehensive.positioning_clarity,
          pain_point_sharpness: comprehensive.pain_point_sharpness,
          pricing_clarity: comprehensive.pricing_clarity,
          conversion_friendliness: comprehensive.conversion_friendliness,
          individual_replicability: comprehensive.individual_replicability,
        }}
        className="h-40 mb-5"
      />

      {/* 各项分数 - 带进度条 */}
      <div className="space-y-3">
        {dimensions.map((dim) => (
          <div key={dim.label}>
            <div className="flex items-center justify-between text-sm mb-1">
              <span className="text-content-muted">{dim.label}</span>
              <span className={cn(
                'font-mono font-medium',
                dim.value >= 7 ? 'text-accent-success' : dim.value >= 5 ? 'text-content-primary' : 'text-content-muted'
              )}>
                {dim.value.toFixed(1)}
              </span>
            </div>
            <div className="h-1.5 bg-surface-hover rounded-full overflow-hidden">
              <div
                className={cn(
                  'h-full rounded-full transition-all',
                  dim.value >= 7 ? 'bg-accent-success' : dim.value >= 5 ? 'bg-amber-500' : 'bg-content-muted/30'
                )}
                style={{ width: `${dim.value * 10}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </Card>
  )
}

// ============ 指标面板 ============
function MetricsPanel({ selection, landing, category, isZh }: {
  selection: ProductSelectionAnalysis | null
  landing: LandingPageAnalysis | null
  category: CategoryAnalysis | null
  isZh: boolean
}) {
  const pricingModel = landing?.pricing_model || selection?.pricing_model

  const customerLabels: Record<string, string> = {
    b2c: isZh ? '个人用户' : 'Consumers',
    b2b_smb: isZh ? '中小企业' : 'SMB',
    b2b_enterprise: isZh ? '大企业' : 'Enterprise',
    b2d: isZh ? '开发者' : 'Developers',
  }

  const complexityLabels: Record<string, string> = {
    low: isZh ? '简单' : 'Low',
    medium: isZh ? '中等' : 'Medium',
    high: isZh ? '复杂' : 'High',
  }

  const hasBusinessInfo = pricingModel || selection?.target_customer || landing?.has_free_tier || landing?.has_trial
  const hasDevInfo = selection
  const hasMarketInfo = category

  if (!hasBusinessInfo && !hasDevInfo && !hasMarketInfo) return null

  return (
    <Card>
      <h2 className="text-lg font-semibold text-content-primary mb-5">
        {isZh ? '关键信息' : 'Key Info'}
      </h2>

      <div className="space-y-5">
        {/* 商业模式 */}
        {hasBusinessInfo && (
          <div className="space-y-3">
            <h3 className="text-xs font-medium text-content-muted uppercase tracking-wider">
              {isZh ? '商业模式' : 'Business'}
            </h3>
            <div className="space-y-2.5">
              {pricingModel && (
                <InfoRow label={isZh ? '定价' : 'Pricing'} value={pricingModel} />
              )}
              {selection?.target_customer && (
                <InfoRow
                  label={isZh ? '客户' : 'Target'}
                  value={customerLabels[selection.target_customer] || selection.target_customer}
                />
              )}
              {(landing?.has_free_tier || landing?.has_trial) && (
                <div className="flex items-center justify-between text-sm">
                  <span className="text-content-muted">{isZh ? '试用' : 'Trial'}</span>
                  <div className="flex gap-1.5">
                    {landing.has_free_tier && <Badge variant="default" size="sm">{isZh ? '免费' : 'Free'}</Badge>}
                    {landing.has_trial && <Badge variant="default" size="sm">{isZh ? '试用' : 'Trial'}</Badge>}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* 开发参考 */}
        {hasDevInfo && (
          <div className="space-y-3 pt-4 border-t border-surface-border/50">
            <h3 className="text-xs font-medium text-content-muted uppercase tracking-wider">
              {isZh ? '开发参考' : 'Dev Reference'}
            </h3>
            <div className="space-y-2.5">
              <InfoRow
                label={isZh ? '技术难度' : 'Complexity'}
                value={complexityLabels[selection.tech_complexity_level] || selection.tech_complexity_level}
              />
              <div className="flex items-center justify-between text-sm">
                <span className="text-content-muted">{isZh ? '独立开发友好度' : 'Indie-friendly'}</span>
                <span className={cn(
                  'font-mono font-medium',
                  selection.individual_dev_suitability >= 7 ? 'text-accent-success' :
                  selection.individual_dev_suitability >= 5 ? 'text-content-primary' : 'text-content-muted'
                )}>
                  {selection.individual_dev_suitability.toFixed(1)}
                </span>
              </div>
            </div>
            {/* 特征标签 */}
            {(selection.is_product_driven || selection.is_small_and_beautiful || selection.uses_llm_api) && (
              <div className="flex flex-wrap gap-1.5 pt-1">
                {selection.is_product_driven && (
                  <Badge variant="default" size="sm">{isZh ? '产品驱动' : 'Product-led'}</Badge>
                )}
                {selection.is_small_and_beautiful && (
                  <Badge variant="default" size="sm">{isZh ? '小而美' : 'Focused'}</Badge>
                )}
                {selection.uses_llm_api && (
                  <Badge variant="default" size="sm">AI</Badge>
                )}
              </div>
            )}
          </div>
        )}

        {/* 市场信息 */}
        {hasMarketInfo && (
          <div className="space-y-3 pt-4 border-t border-surface-border/50">
            <h3 className="text-xs font-medium text-content-muted uppercase tracking-wider">
              {isZh ? '市场' : 'Market'}
            </h3>
            <div className="space-y-2.5">
              <InfoRow label={isZh ? '赛道' : 'Category'} value={category.category} />
              <div className="flex items-center justify-between text-sm">
                <span className="text-content-muted">{isZh ? '类型' : 'Type'}</span>
                <MarketTypeBadge type={category.market_type} />
              </div>
              <InfoRow label={isZh ? '同类产品' : 'Similar'} value={`${category.total_projects} ${isZh ? '个' : ''}`} />
              <InfoRow label={isZh ? '平均收入' : 'Avg MRR'} value={formatCurrency(category.avg_revenue)} />
            </div>
          </div>
        )}
      </div>
    </Card>
  )
}

function InfoRow({ label, value, className }: { label: string; value: string; className?: string }) {
  return (
    <div className={cn('flex items-center justify-between text-sm', className)}>
      <span className="text-content-muted">{label}</span>
      <span className="text-content-primary font-medium">{value}</span>
    </div>
  )
}
