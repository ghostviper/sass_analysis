'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'
import { Card } from '@/components/ui/Card'
import { Badge, MarketTypeBadge } from '@/components/ui/Badge'
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
import {
  ArrowLeft,
  ExternalLink,
  AlertTriangle,
  Check,
  AlertCircle,
  Info,
} from 'lucide-react'
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
      <div className="flex items-center justify-center min-h-[400px] animate-fade-in">
        <Card className="text-center max-w-md p-8">
          <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-accent-warning/10 flex items-center justify-center">
            <AlertTriangle className="h-8 w-8 text-accent-warning" />
          </div>
          <h3 className="text-lg font-semibold text-content-primary mb-2">
            {isZh ? '未找到产品' : 'Product Not Found'}
          </h3>
          <p className="text-content-secondary mb-6">
            {error || (isZh ? '该产品可能已被移除或链接无效' : 'This product may have been removed or the link is invalid')}
          </p>
          <Link href="/products" className="btn btn-primary">
            <ArrowLeft className="h-4 w-4" />
            {isZh ? '返回产品列表' : 'Back to Products'}
          </Link>
        </Card>
      </div>
    )
  }

  // 计算数据完整度
  const dataCompleteness = {
    hasLanding: !!landing,
    hasSelection: !!selection,
    hasComprehensive: !!comprehensive,
    hasCategory: !!category,
  }
  const completenessScore = Object.values(dataCompleteness).filter(Boolean).length / 4

  return (
    <div className="space-y-6 pb-12 animate-fade-in">
      {/* 面包屑导航 */}
      <nav className="flex items-center gap-2 text-sm">
        <Link
          href="/products"
          className="inline-flex items-center gap-1.5 text-content-muted hover:text-content-primary transition-colors group"
        >
          <ArrowLeft className="h-4 w-4 transition-transform group-hover:-translate-x-0.5" />
          {isZh ? '产品列表' : 'Products'}
        </Link>
        <span className="text-content-muted/50">/</span>
        <span className="text-content-secondary font-medium truncate max-w-[200px]">{product.name}</span>
      </nav>

      {/* 产品头部 */}
      <ProductHeader product={product} category={category} isZh={isZh} />

      {/* 数据完整度提示 */}
      {completenessScore < 1 && (
        <Card className="bg-amber-500/5 border-amber-500/20">
          <div className="flex items-start gap-3">
            <Info className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h4 className="text-sm font-medium text-amber-900 dark:text-amber-200 mb-1">
                {isZh ? '数据完整度' : 'Data Completeness'}: {Math.round(completenessScore * 100)}%
              </h4>
              <p className="text-xs text-amber-800 dark:text-amber-300">
                {isZh
                  ? '部分分析数据尚未生成，展示的信息可能不完整。'
                  : 'Some analysis data is not yet available. The information shown may be incomplete.'}
              </p>
            </div>
          </div>
        </Card>
      )}

      {/* 主体内容 */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* 左侧主内容区 (2列) */}
        <div className="lg:col-span-2 space-y-6">
          {/* 产品定位与价值 */}
          {landing && <ProductPositioning landing={landing} isZh={isZh} />}

          {/* 商业模式分析 */}
          {(landing || selection) && <BusinessModelSection landing={landing} selection={selection} isZh={isZh} />}

          {/* 产品功能与特性 */}
          {landing && <ProductFeaturesSection landing={landing} isZh={isZh} />}

          {/* 学习参考建议 */}
          {(comprehensive || insights) && (
            <LearningReferenceSection
              comprehensive={comprehensive}
              insights={insights}
              selection={selection}
              isZh={isZh}
            />
          )}
        </div>

        {/* 右侧边栏 (1列) */}
        <div className="lg:col-span-1 space-y-6">
          {/* 综合评分 */}
          {comprehensive && <ScorePanel comprehensive={comprehensive} isZh={isZh} />}

          {/* 技术实现分析 */}
          {selection && <TechnicalAnalysisPanel selection={selection} isZh={isZh} />}

          {/* 市场与竞争 */}
          {category && <MarketAnalysisPanel category={category} product={product} isZh={isZh} />}
        </div>
      </div>
    </div>
  )
}

// ============ 产品头部 ============
function ProductHeader({ product, category, isZh }: {
  product: Startup
  category: CategoryAnalysis | null
  isZh: boolean
}) {
  return (
    <Card padding="none" className="overflow-hidden">
      <div className="p-8">
        <div className="flex gap-6">
          {/* Logo */}
          <div className="flex-shrink-0">
            <div className="w-24 h-24 rounded-xl overflow-hidden bg-surface-hover border border-surface-border flex items-center justify-center">
              {product.logo_url ? (
                <img src={product.logo_url} alt={product.name} className="w-full h-full object-cover" />
              ) : (
                <span className="text-4xl font-semibold text-content-tertiary">
                  {product.name.charAt(0).toUpperCase()}
                </span>
              )}
            </div>
          </div>

          {/* 主要信息 */}
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between gap-4 mb-4">
              <div className="min-w-0 flex-1">
                <h1 className="text-3xl font-semibold text-content-primary tracking-tight mb-3">
                  {product.name}
                </h1>
                <div className="flex flex-wrap items-center gap-2">
                  {product.category && (
                    <Badge variant="default" size="md">
                      {product.category}
                    </Badge>
                  )}
                  {category && <MarketTypeBadge type={category.market_type} size="md" />}
                  {product.is_verified && (
                    <Badge variant="success" size="md">
                      {isZh ? '已验证' : 'Verified'}
                    </Badge>
                  )}
                  {product.country_code && (
                    <Badge variant="muted" size="md">
                      {product.country_code}
                    </Badge>
                  )}
                </div>
              </div>
              {product.website_url && (
                <a
                  href={product.website_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn btn-primary flex-shrink-0"
                >
                  <ExternalLink className="h-4 w-4" />
                  {isZh ? '访问官网' : 'Visit Site'}
                </a>
              )}
            </div>
            {product.description && (
              <p className="text-sm text-content-secondary leading-relaxed">
                {product.description}
              </p>
            )}
          </div>
        </div>
      </div>

      {/* 关键指标 */}
      <div className="border-t border-surface-border px-8 py-5">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          <MetricItem
            label={isZh ? '月收入' : 'Monthly Revenue'}
            value={formatCurrency(product.revenue_30d)}
            valueClass="text-content-primary"
          />
          <MetricItem
            label={isZh ? '增长率' : 'Growth Rate'}
            value={product.growth_rate ? `${product.growth_rate > 0 ? '+' : ''}${product.growth_rate.toFixed(0)}%` : '-'}
            valueClass={cn(
              product.growth_rate && product.growth_rate > 0 ? 'text-accent-success' :
              product.growth_rate && product.growth_rate < 0 ? 'text-accent-error' : 'text-content-muted'
            )}
          />
          <MetricItem
            label={isZh ? '粉丝数' : 'Followers'}
            value={product.twitter_followers ? `${(product.twitter_followers / 1000).toFixed(1)}K` : '-'}
            valueClass="text-content-primary"
          />
          <MetricItem
            label={isZh ? '成立时间' : 'Founded'}
            value={product.founded_date ? formatDate(product.founded_date) : '-'}
            valueClass="text-content-primary"
          />
        </div>
      </div>
    </Card>
  )
}

function MetricItem({ label, value, valueClass }: {
  label: string
  value: string
  valueClass?: string
}) {
  return (
    <div>
      <div className="text-xs font-medium text-content-muted mb-1.5">{label}</div>
      <div className={cn('text-xl font-semibold font-mono tracking-tight', valueClass)}>
        {value}
      </div>
    </div>
  )
}

// ============ 产品定位与价值 ============
function ProductPositioning({ landing, isZh }: {
  landing: LandingPageAnalysis
  isZh: boolean
}) {
  const hasContent = landing.headline_text || landing.value_propositions?.length ||
    landing.target_audience?.length || landing.use_cases?.length

  if (!hasContent) return null

  return (
    <Card>
      <h2 className="text-lg font-semibold text-content-primary mb-6">
        {isZh ? '产品定位与价值' : 'Product Positioning & Value'}
      </h2>

      {/* 核心定位 */}
      {landing.headline_text && (
        <div className="mb-6 p-5 rounded-lg bg-surface-hover border border-surface-border">
          <p className="text-base text-content-primary leading-relaxed font-medium">
            "{landing.headline_text}"
          </p>
          {landing.tagline_text && (
            <p className="text-sm text-content-secondary mt-2">
              {landing.tagline_text}
            </p>
          )}
        </div>
      )}

      {/* 价值主张 */}
      {landing.value_propositions && landing.value_propositions.length > 0 && (
        <div className="mb-6">
          <h3 className="text-sm font-medium text-content-primary mb-3">
            {isZh ? '核心价值' : 'Value Propositions'}
          </h3>
          <div className="space-y-2">
            {landing.value_propositions.map((prop, i) => (
              <div key={i} className="flex items-start gap-3 p-3 rounded-lg bg-surface-hover">
                <Check className="w-4 h-4 text-accent-success flex-shrink-0 mt-0.5" />
                <span className="text-sm text-content-secondary">{prop}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 目标用户和使用场景 */}
      <div className="grid md:grid-cols-2 gap-6">
        {landing.target_audience && landing.target_audience.length > 0 && (
          <div>
            <h3 className="text-sm font-medium text-content-primary mb-3">
              {isZh ? '目标用户' : 'Target Audience'}
            </h3>
            <div className="flex flex-wrap gap-2">
              {landing.target_audience.map((item, i) => (
                <Badge key={i} variant="default" size="md">
                  {item}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {landing.use_cases && landing.use_cases.length > 0 && (
          <div>
            <h3 className="text-sm font-medium text-content-primary mb-3">
              {isZh ? '使用场景' : 'Use Cases'}
            </h3>
            <ul className="space-y-2">
              {landing.use_cases.slice(0, 4).map((item, i) => (
                <li key={i} className="text-sm text-content-secondary flex items-start gap-2">
                  <span className="w-1 h-1 rounded-full bg-content-tertiary mt-2 flex-shrink-0" />
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </Card>
  )
}

// ============ 商业模式分析 ============
function BusinessModelSection({ landing, selection, isZh }: {
  landing: LandingPageAnalysis | null
  selection: ProductSelectionAnalysis | null
  isZh: boolean
}) {
  const pricingModel = landing?.pricing_model || selection?.pricing_model
  const targetCustomer = selection?.target_customer
  const marketScope = selection?.market_scope
  const hasFree = landing?.has_free_tier
  const hasTrial = landing?.has_trial
  const pricingTiers = landing?.pricing_tiers

  const hasContent = pricingModel || targetCustomer || marketScope || hasFree || hasTrial || pricingTiers

  if (!hasContent) return null

  const customerLabels: Record<string, string> = {
    b2c: isZh ? 'B2C - 个人消费者' : 'B2C - Consumers',
    b2b_smb: isZh ? 'B2B - 中小企业' : 'B2B - SMB',
    b2b_enterprise: isZh ? 'B2B - 大型企业' : 'B2B - Enterprise',
    b2d: isZh ? 'B2D - 开发者' : 'B2D - Developers',
  }

  const scopeLabels: Record<string, string> = {
    horizontal: isZh ? '横向市场 - 通用型产品' : 'Horizontal - General Purpose',
    vertical: isZh ? '垂直市场 - 行业专用' : 'Vertical - Industry Specific',
  }

  return (
    <Card>
      <h2 className="text-lg font-semibold text-content-primary mb-6">
        {isZh ? '商业模式分析' : 'Business Model Analysis'}
      </h2>

      <div className="grid md:grid-cols-2 gap-6">
        {/* 左列 */}
        <div className="space-y-3">
          {pricingModel && (
            <InfoRow
              label={isZh ? '定价模式' : 'Pricing Model'}
              value={pricingModel}
            />
          )}
          {targetCustomer && (
            <InfoRow
              label={isZh ? '目标客户' : 'Target Customer'}
              value={customerLabels[targetCustomer] || targetCustomer}
            />
          )}
          {marketScope && (
            <InfoRow
              label={isZh ? '市场范围' : 'Market Scope'}
              value={scopeLabels[marketScope] || marketScope}
            />
          )}
        </div>

        {/* 右列 */}
        <div className="space-y-3">
          {(hasFree || hasTrial) && (
            <div className="p-4 rounded-lg bg-surface-hover border border-surface-border">
              <div className="text-sm font-medium text-content-primary mb-3">
                {isZh ? '试用选项' : 'Trial Options'}
              </div>
              <div className="flex flex-wrap gap-2">
                {hasFree && (
                  <Badge variant="success" size="md">
                    {isZh ? '免费版' : 'Free Tier'}
                  </Badge>
                )}
                {hasTrial && (
                  <Badge variant="info" size="md">
                    {isZh ? '试用期' : 'Trial Period'}
                  </Badge>
                )}
              </div>
            </div>
          )}

          {pricingTiers && pricingTiers.length > 0 && (
            <div className="p-4 rounded-lg bg-surface-hover border border-surface-border">
              <div className="text-sm font-medium text-content-primary mb-1">
                {isZh ? '定价层级' : 'Pricing Tiers'}
              </div>
              <div className="text-sm text-content-secondary">
                {pricingTiers.length} {isZh ? '个套餐' : 'plans available'}
              </div>
            </div>
          )}
        </div>
      </div>
    </Card>
  )
}

function InfoRow({ label, value }: {
  label: string
  value: string
}) {
  return (
    <div className="flex items-center justify-between p-4 rounded-lg bg-surface-hover border border-surface-border">
      <span className="text-sm text-content-secondary">{label}</span>
      <span className="text-sm font-medium text-content-primary">{value}</span>
    </div>
  )
}

// 继续下一部分...

// ============ 产品功能与特性 ============
function ProductFeaturesSection({ landing, isZh }: {
  landing: LandingPageAnalysis
  isZh: boolean
}) {
  const hasFeatures = landing.core_features && landing.core_features.length > 0
  const hasPainPoints = landing.pain_points && landing.pain_points.length > 0
  const hasMoats = landing.potential_moats && landing.potential_moats.length > 0

  if (!hasFeatures && !hasPainPoints && !hasMoats) return null

  return (
    <Card>
      <h2 className="text-lg font-semibold text-content-primary mb-6">
        {isZh ? '产品功能与特性' : 'Product Features & Characteristics'}
      </h2>

      <div className="space-y-6">
        {/* 核心功能 */}
        {hasFeatures && (
          <div>
            <h3 className="text-sm font-medium text-content-primary mb-3">
              {isZh ? '核心功能' : 'Core Features'}
              <span className="text-xs text-content-muted ml-2">({landing.feature_count})</span>
            </h3>
            <div className="grid md:grid-cols-2 gap-2">
              {landing.core_features.slice(0, 8).map((feature, i) => (
                <div key={i} className="flex items-center gap-2 p-3 rounded-lg bg-surface-hover border border-surface-border">
                  <div className="w-1 h-1 rounded-full bg-accent-primary flex-shrink-0" />
                  <span className="text-sm text-content-secondary">{feature}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 解决的痛点 */}
        {hasPainPoints && (
          <div>
            <h3 className="text-sm font-medium text-content-primary mb-3">
              {isZh ? '解决的痛点' : 'Pain Points Addressed'}
            </h3>
            <div className="space-y-2">
              {landing.pain_points.slice(0, 4).map((pain, i) => (
                <div key={i} className="flex items-start gap-3 p-3 rounded-lg bg-surface-hover border border-surface-border">
                  <AlertCircle className="w-4 h-4 text-accent-warning flex-shrink-0 mt-0.5" />
                  <span className="text-sm text-content-secondary">{pain}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 竞争优势 */}
        {hasMoats && (
          <div>
            <h3 className="text-sm font-medium text-content-primary mb-3">
              {isZh ? '竞争优势' : 'Competitive Advantages'}
            </h3>
            <div className="grid md:grid-cols-2 gap-2">
              {landing.potential_moats.slice(0, 4).map((moat, i) => (
                <div key={i} className="flex items-start gap-2 p-3 rounded-lg bg-surface-hover border border-surface-border">
                  <Check className="w-4 h-4 text-accent-success flex-shrink-0 mt-0.5" />
                  <span className="text-sm text-content-secondary">{moat}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </Card>
  )
}

// ============ 学习参考建议 ============
function LearningReferenceSection({ comprehensive, insights, selection, isZh }: {
  comprehensive: ComprehensiveAnalysis | null
  insights: ProductInsightsResponse | null
  selection: ProductSelectionAnalysis | null
  isZh: boolean
}) {
  const positiveInsights = insights?.insights.filter(i => i.type === 'positive') || []
  const warningInsights = insights?.insights.filter(i => i.type === 'warning') || []
  const strengths = comprehensive?.analysis_summary?.strengths || []
  const risks = comprehensive?.analysis_summary?.risks || []
  const recommendations = comprehensive?.analysis_summary?.recommendations || []

  const allStrengths = [...positiveInsights.map(i => i.description), ...strengths]
  const allRisks = [...new Set([...warningInsights.map(i => i.description), ...risks])]

  const hasContent = allStrengths.length > 0 || allRisks.length > 0 || recommendations.length > 0

  if (!hasContent) return null

  return (
    <Card>
      <h2 className="text-lg font-semibold text-content-primary mb-6">
        {isZh ? '学习参考建议' : 'Learning Reference & Insights'}
      </h2>

      <div className="space-y-6">
        {/* 可复制性评估 */}
        {selection && (
          <div className="p-5 rounded-lg bg-surface-hover border border-surface-border">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-medium text-content-primary">
                {isZh ? '独立开发适合度' : 'Indie Dev Suitability'}
              </h3>
              <div className="flex items-baseline gap-1">
                <div className="text-2xl font-semibold font-mono text-accent-primary">
                  {selection.individual_dev_suitability.toFixed(1)}
                </div>
                <span className="text-xs text-content-muted">/10</span>
              </div>
            </div>
            <div className="flex flex-wrap gap-2">
              {selection.is_product_driven && (
                <Badge variant="success" size="sm">
                  {isZh ? '产品驱动' : 'Product-led'}
                </Badge>
              )}
              {selection.is_small_and_beautiful && (
                <Badge variant="info" size="sm">
                  {isZh ? '小而美' : 'Focused'}
                </Badge>
              )}
              {selection.combo1_match && (
                <Badge variant="success" size="sm">
                  {isZh ? '组合1匹配' : 'Pattern 1'}
                </Badge>
              )}
              {selection.combo3_match && (
                <Badge variant="success" size="sm">
                  {isZh ? '组合3匹配' : 'Pattern 3'}
                </Badge>
              )}
            </div>
          </div>
        )}

        {/* 成功要素 */}
        {allStrengths.length > 0 && (
          <div>
            <h3 className="text-sm font-medium text-accent-success mb-3">
              {isZh ? '成功要素' : 'Success Factors'}
            </h3>
            <ul className="space-y-2">
              {allStrengths.slice(0, 5).map((item, i) => (
                <li key={i} className="text-sm text-content-secondary flex items-start gap-3 p-3 rounded-lg bg-surface-hover border border-surface-border">
                  <Check className="w-4 h-4 text-accent-success flex-shrink-0 mt-0.5" />
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* 风险提示 */}
        {allRisks.length > 0 && (
          <div>
            <h3 className="text-sm font-medium text-accent-warning mb-3">
              {isZh ? '风险提示' : 'Risk Factors'}
            </h3>
            <ul className="space-y-2">
              {allRisks.slice(0, 4).map((item, i) => (
                <li key={i} className="text-sm text-content-secondary flex items-start gap-3 p-3 rounded-lg bg-surface-hover border border-surface-border">
                  <AlertCircle className="w-4 h-4 text-accent-warning flex-shrink-0 mt-0.5" />
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* 实施建议 */}
        {recommendations.length > 0 && (
          <div>
            <h3 className="text-sm font-medium text-content-primary mb-3">
              {isZh ? '实施建议' : 'Implementation Tips'}
            </h3>
            <ul className="space-y-2">
              {recommendations.slice(0, 4).map((item, i) => (
                <li key={i} className="text-sm text-content-secondary flex items-start gap-3 p-3 rounded-lg bg-surface-hover border border-surface-border">
                  <span className="w-1 h-1 rounded-full bg-accent-info mt-2 flex-shrink-0" />
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </Card>
  )
}

// ============ 综合评分面板 ============
function ScorePanel({ comprehensive, isZh }: {
  comprehensive: ComprehensiveAnalysis
  isZh: boolean
}) {
  const score = comprehensive.overall_recommendation

  const dimensions = [
    { label: isZh ? '成熟度' : 'Maturity', value: comprehensive.maturity_score, key: 'maturity_score' },
    { label: isZh ? '定位' : 'Positioning', value: comprehensive.positioning_clarity, key: 'positioning_clarity' },
    { label: isZh ? '痛点' : 'Problem', value: comprehensive.pain_point_sharpness, key: 'pain_point_sharpness' },
    { label: isZh ? '定价' : 'Pricing', value: comprehensive.pricing_clarity, key: 'pricing_clarity' },
    { label: isZh ? '转化' : 'Conversion', value: comprehensive.conversion_friendliness, key: 'conversion_friendliness' },
    { label: isZh ? '可复制' : 'Replicability', value: comprehensive.individual_replicability, key: 'individual_replicability' },
  ]

  const getScoreColor = (s: number) => {
    if (s >= 7) return 'text-accent-success'
    if (s >= 5) return 'text-accent-warning'
    return 'text-content-muted'
  }

  const getScoreLabel = (s: number) => {
    if (s >= 8) return isZh ? '强烈推荐' : 'Highly Recommended'
    if (s >= 7) return isZh ? '值得研究' : 'Worth Studying'
    if (s >= 5) return isZh ? '可以参考' : 'Good Reference'
    return isZh ? '参考有限' : 'Limited Value'
  }

  return (
    <Card>
      <h2 className="text-lg font-semibold text-content-primary mb-6">
        {isZh ? '综合评分' : 'Overall Score'}
      </h2>

      {/* 总分 */}
      <div className="text-center py-6 mb-6 rounded-lg bg-surface-hover border border-surface-border">
        <div className={cn('text-5xl font-semibold font-mono mb-2', getScoreColor(score))}>
          {score.toFixed(1)}
        </div>
        <div className="text-sm text-content-muted">
          {getScoreLabel(score)}
        </div>
      </div>

      {/* 雷达图 */}
      <div className="mb-6">
        <AnalysisRadarChart
          scores={{
            maturity_score: comprehensive.maturity_score,
            positioning_clarity: comprehensive.positioning_clarity,
            pain_point_sharpness: comprehensive.pain_point_sharpness,
            pricing_clarity: comprehensive.pricing_clarity,
            conversion_friendliness: comprehensive.conversion_friendliness,
            individual_replicability: comprehensive.individual_replicability,
          }}
          className="h-48"
        />
      </div>

      {/* 各项分数 */}
      <div className="space-y-4">
        {dimensions.map((dim) => (
          <div key={dim.key}>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-content-secondary">{dim.label}</span>
              <span className={cn(
                'font-mono text-base font-semibold',
                getScoreColor(dim.value)
              )}>
                {dim.value.toFixed(1)}
              </span>
            </div>
            <div className="w-full h-2 bg-surface-hover rounded-full overflow-hidden">
              <div
                className={cn(
                  'h-full rounded-full transition-all duration-500',
                  dim.value >= 7 ? 'bg-accent-success' :
                  dim.value >= 5 ? 'bg-accent-warning' :
                  'bg-content-muted'
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

// ============ 技术实现分析面板 ============
function TechnicalAnalysisPanel({ selection, isZh }: {
  selection: ProductSelectionAnalysis
  isZh: boolean
}) {
  const complexityLabels: Record<string, { label: string; color: string }> = {
    low: { label: isZh ? '低' : 'Low', color: 'text-accent-success' },
    medium: { label: isZh ? '中' : 'Medium', color: 'text-accent-warning' },
    high: { label: isZh ? '高' : 'High', color: 'text-accent-error' },
  }

  const aiLabels: Record<string, string> = {
    none: isZh ? '不依赖' : 'None',
    light: isZh ? '轻度依赖' : 'Light',
    heavy: isZh ? '重度依赖' : 'Heavy',
  }

  const costLabels: Record<string, { label: string; color: string }> = {
    low: { label: isZh ? '低成本' : 'Low', color: 'text-accent-success' },
    medium: { label: isZh ? '中等成本' : 'Medium', color: 'text-accent-warning' },
    high: { label: isZh ? '高成本' : 'High', color: 'text-accent-error' },
  }

  return (
    <Card>
      <h2 className="text-lg font-semibold text-content-primary mb-6">
        {isZh ? '技术实现分析' : 'Technical Analysis'}
      </h2>

      <div className="space-y-4">
        {/* 技术复杂度 */}
        <div className="p-4 rounded-lg bg-surface-hover border border-surface-border">
          <div className="flex items-center justify-between">
            <span className="text-sm text-content-secondary">
              {isZh ? '技术复杂度' : 'Tech Complexity'}
            </span>
            <span className={cn('text-sm font-semibold', complexityLabels[selection.tech_complexity_level]?.color)}>
              {complexityLabels[selection.tech_complexity_level]?.label}
            </span>
          </div>
        </div>

        {/* AI 依赖 */}
        {selection.ai_dependency_level && (
          <div className="p-4 rounded-lg bg-surface-hover border border-surface-border">
            <div className="flex items-center justify-between">
              <span className="text-sm text-content-secondary">
                {isZh ? 'AI 依赖' : 'AI Dependency'}
              </span>
              <span className="text-sm font-medium text-content-primary">
                {aiLabels[selection.ai_dependency_level]}
              </span>
            </div>
          </div>
        )}

        {/* 启动成本 */}
        {selection.startup_cost_level && (
          <div className="p-4 rounded-lg bg-surface-hover border border-surface-border">
            <div className="flex items-center justify-between">
              <span className="text-sm text-content-secondary">
                {isZh ? '启动成本' : 'Startup Cost'}
              </span>
              <span className={cn('text-sm font-semibold', costLabels[selection.startup_cost_level]?.color)}>
                {costLabels[selection.startup_cost_level]?.label}
              </span>
            </div>
          </div>
        )}

        {/* 技术特征标签 */}
        <div>
          <div className="text-sm font-medium text-content-primary mb-3">
            {isZh ? '技术特征' : 'Tech Features'}
          </div>
          <div className="flex flex-wrap gap-2">
            {selection.uses_llm_api && (
              <Badge variant="info" size="sm">
                LLM API
              </Badge>
            )}
            {selection.has_realtime_feature && (
              <Badge variant="warning" size="sm">
                {isZh ? '实时功能' : 'Realtime'}
              </Badge>
            )}
            {selection.is_data_intensive && (
              <Badge variant="info" size="sm">
                {isZh ? '数据密集' : 'Data-intensive'}
              </Badge>
            )}
            {selection.has_compliance_requirement && (
              <Badge variant="danger" size="sm">
                {isZh ? '需合规' : 'Compliance'}
              </Badge>
            )}
          </div>
        </div>

        {/* IP 依赖度 */}
        <div className="pt-4 border-t border-surface-border">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-content-secondary">{isZh ? 'IP 依赖度' : 'IP Dependency'}</span>
            <span className="text-sm font-mono font-semibold text-content-primary">
              {selection.ip_dependency_score.toFixed(1)}/10
            </span>
          </div>
          <div className="w-full h-2 bg-surface-hover rounded-full overflow-hidden">
            <div
              className={cn(
                'h-full rounded-full',
                selection.ip_dependency_score <= 3 ? 'bg-accent-success' :
                selection.ip_dependency_score <= 6 ? 'bg-accent-warning' :
                'bg-accent-error'
              )}
              style={{ width: `${selection.ip_dependency_score * 10}%` }}
            />
          </div>
          <p className="text-xs text-content-muted mt-2">
            {isZh ? '越低越好，表示产品驱动而非个人IP驱动' : 'Lower is better - product-driven vs IP-driven'}
          </p>
        </div>
      </div>
    </Card>
  )
}

// ============ 市场与竞争分析面板 ============
function MarketAnalysisPanel({ category, product, isZh }: {
  category: CategoryAnalysis
  product: Startup
  isZh: boolean
}) {
  return (
    <Card>
      <h2 className="text-lg font-semibold text-content-primary mb-6">
        {isZh ? '市场与竞争' : 'Market & Competition'}
      </h2>

      <div className="space-y-4">
        {/* 赛道信息 */}
        <div className="p-4 rounded-lg bg-surface-hover border border-surface-border">
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm font-medium text-content-primary">{category.category}</span>
            <MarketTypeBadge type={category.market_type} size="sm" />
          </div>
          <p className="text-xs text-content-secondary leading-relaxed">
            {category.market_type_reason}
          </p>
        </div>

        {/* 市场指标 */}
        <div className="space-y-3">
          <div className="flex items-center justify-between p-3 rounded-lg bg-surface-hover border border-surface-border">
            <span className="text-sm text-content-secondary">{isZh ? '同类产品' : 'Similar Products'}</span>
            <span className="text-sm font-semibold text-content-primary">{category.total_projects}</span>
          </div>
          <div className="flex items-center justify-between p-3 rounded-lg bg-surface-hover border border-surface-border">
            <span className="text-sm text-content-secondary">{isZh ? '赛道总收入' : 'Category Revenue'}</span>
            <span className="text-sm font-semibold text-accent-primary">{formatCurrency(category.total_revenue)}</span>
          </div>
          <div className="flex items-center justify-between p-3 rounded-lg bg-surface-hover border border-surface-border">
            <span className="text-sm text-content-secondary">{isZh ? '平均收入' : 'Avg Revenue'}</span>
            <span className="text-sm font-semibold text-content-primary">{formatCurrency(category.avg_revenue)}</span>
          </div>
          <div className="flex items-center justify-between p-3 rounded-lg bg-surface-hover border border-surface-border">
            <span className="text-sm text-content-secondary">{isZh ? '中位数收入' : 'Median Revenue'}</span>
            <span className="text-sm font-semibold text-content-primary">{formatCurrency(category.median_revenue)}</span>
          </div>
        </div>

        {/* 竞争态势 */}
        <div className="pt-4 border-t border-surface-border">
          <div className="text-sm font-medium text-content-primary mb-3">
            {isZh ? '竞争态势' : 'Competition'}
          </div>
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="text-content-secondary">{isZh ? 'TOP10 收入占比' : 'TOP10 Share'}</span>
              <span className="font-mono font-semibold text-content-primary">{category.top10_revenue_share.toFixed(1)}%</span>
            </div>
            <div className="w-full h-2 bg-surface-hover rounded-full overflow-hidden">
              <div
                className="h-full bg-accent-primary rounded-full"
                style={{ width: `${category.top10_revenue_share}%` }}
              />
            </div>
            <p className="text-xs text-content-muted mt-2">
              {category.top10_revenue_share > 70
                ? (isZh ? '市场集中度高，头部效应明显' : 'High concentration, strong leader effect')
                : category.top10_revenue_share > 40
                ? (isZh ? '市场集中度中等' : 'Moderate concentration')
                : (isZh ? '市场分散，机会较多' : 'Fragmented market, more opportunities')}
            </p>
          </div>
        </div>
      </div>
    </Card>
  )
}
