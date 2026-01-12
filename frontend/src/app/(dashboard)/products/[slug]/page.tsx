'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { Card } from '@/components/ui/Card'
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
import {
  ArrowLeft,
  ExternalLink,
  Check,
  TrendingUp,
  Users,
  Calendar,
  DollarSign,
  Target,
  Zap,
  Shield,
  Code,
  Sparkles
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
      <div className="flex items-center justify-center min-h-[400px]">
        <Card className="text-center max-w-md p-8">
          <h3 className="text-lg font-semibold text-content-primary mb-2">
            {isZh ? '未找到产品' : 'Product Not Found'}
          </h3>
          <p className="text-content-secondary text-sm mb-6">
            {error || (isZh ? '该产品可能已被移除' : 'This product may have been removed')}
          </p>
          <Link href="/products" className="btn btn-primary">
            <ArrowLeft className="h-4 w-4" />
            {isZh ? '返回' : 'Back'}
          </Link>
        </Card>
      </div>
    )
  }

  const hasAnalysis = landing || comprehensive || selection

  return (
    <div className="space-y-6 pb-12">
      {/* 返回 */}
      <Link href="/products" className="inline-flex items-center gap-1.5 text-sm text-content-muted hover:text-content-primary transition-colors">
        <ArrowLeft className="h-4 w-4" />
        {isZh ? '返回列表' : 'Back'}
      </Link>

      {/* ========== 主卡片：产品概览 ========== */}
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.2 }}
      >
        <Card padding="none" className="overflow-hidden">
          {/* 头部区域 */}
          <div className="relative">
            {/* 背景装饰 */}
            <div className="absolute inset-0 bg-gradient-to-br from-brand-500/5 via-transparent to-transparent pointer-events-none" />

            <div className="relative p-8">
              <div className="flex items-start gap-6">
                {/* Logo */}
                <div className="flex-shrink-0">
                  <ProductLogo name={product.name} logoUrl={product.logo_url} size="lg" className="ring-2 ring-surface-border/50 ring-offset-4 ring-offset-surface-base" />
                </div>

                {/* 主要信息 */}
                <div className="flex-1 min-w-0">
                  {/* 标题行 */}
                  <div className="flex items-start justify-between gap-4 mb-3">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-3 flex-wrap mb-2">
                        <h1 className="text-3xl font-display font-bold text-content-primary tracking-tight">
                          {product.name}
                        </h1>
                        <div className="flex items-center gap-1.5 flex-wrap">
                          {product.is_verified && (
                            <Badge variant="success" size="sm" className="shadow-sm">
                              <Check className="w-3 h-3 mr-1" />
                              {isZh ? '已验证' : 'Verified'}
                            </Badge>
                          )}
                          {category && <MarketTypeBadge type={category.market_type} size="sm" className="shadow-sm" />}
                        </div>
                      </div>

                      {/* 分类和国家 */}
                      <div className="flex items-center gap-2 text-sm text-content-muted">
                        {product.category && (
                          <>
                            <span className="font-medium">{product.category}</span>
                            {product.country_code && <span className="text-content-tertiary">•</span>}
                          </>
                        )}
                        {product.country_code && (
                          <span className="inline-flex items-center gap-1">
                            <span className="text-content-tertiary">{product.country_code}</span>
                            {product.country && <span className="text-content-tertiary">({product.country})</span>}
                          </span>
                        )}
                      </div>
                    </div>

                    {/* 访问按钮 */}
                    {product.website_url && (
                      <a
                        href={product.website_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex-shrink-0 inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-brand-500 text-white text-sm font-medium hover:bg-brand-600 transition-all shadow-sm hover:shadow-md"
                      >
                        <ExternalLink className="w-4 h-4" />
                        {isZh ? '访问官网' : 'Visit Website'}
                      </a>
                    )}
                  </div>

                  {/* 描述文本 */}
                  <div className="space-y-2 mt-4">
                    {landing?.headline_text && (
                      <p className="text-base text-content-primary leading-relaxed font-medium">
                        {landing.headline_text}
                      </p>
                    )}
                    {product.description && (
                      <p className="text-sm text-content-secondary leading-relaxed">
                        {product.description}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* 核心指标区域 */}
          <div className="border-t border-surface-border/50 bg-gradient-to-b from-surface-subtle/50 to-surface-subtle/30">
            <div className="px-8 py-6">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
                {/* 月收入 */}
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-xs font-medium text-content-muted uppercase tracking-wider">
                    <div className="p-1.5 rounded-md bg-brand-500/10">
                      <DollarSign className="w-3.5 h-3.5 text-brand-500" />
                    </div>
                    {isZh ? '月收入' : 'Monthly Revenue'}
                  </div>
                  <div className="text-2xl font-bold font-mono tabular-nums text-content-primary">
                    {formatCurrency(product.revenue_30d)}
                  </div>
                </div>

                {/* 增长率 */}
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-xs font-medium text-content-muted uppercase tracking-wider">
                    <div className={cn(
                      "p-1.5 rounded-md",
                      product.growth_rate && product.growth_rate > 0 ? 'bg-accent-success/10' :
                      product.growth_rate && product.growth_rate < 0 ? 'bg-accent-error/10' : 'bg-surface-border/50'
                    )}>
                      <TrendingUp className={cn(
                        "w-3.5 h-3.5",
                        product.growth_rate && product.growth_rate > 0 ? 'text-accent-success' :
                        product.growth_rate && product.growth_rate < 0 ? 'text-accent-error' : 'text-content-muted'
                      )} />
                    </div>
                    {isZh ? '增长率' : 'Growth Rate'}
                  </div>
                  <div className={cn(
                    "text-2xl font-bold font-mono tabular-nums",
                    product.growth_rate && product.growth_rate > 0 ? 'text-accent-success' :
                    product.growth_rate && product.growth_rate < 0 ? 'text-accent-error' : 'text-content-secondary'
                  )}>
                    {product.growth_rate ? `${product.growth_rate > 0 ? '+' : ''}${product.growth_rate.toFixed(1)}%` : '-'}
                  </div>
                </div>

                {/* 关注者 */}
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-xs font-medium text-content-muted uppercase tracking-wider">
                    <div className="p-1.5 rounded-md bg-surface-border/50">
                      <Users className="w-3.5 h-3.5 text-content-muted" />
                    </div>
                    {isZh ? '关注者' : 'Followers'}
                  </div>
                  <div className="text-2xl font-bold font-mono tabular-nums text-content-secondary">
                    {product.founder_followers ? product.founder_followers.toLocaleString() : '-'}
                  </div>
                </div>

                {/* 成立时间 */}
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-xs font-medium text-content-muted uppercase tracking-wider">
                    <div className="p-1.5 rounded-md bg-surface-border/50">
                      <Calendar className="w-3.5 h-3.5 text-content-muted" />
                    </div>
                    {isZh ? '成立时间' : 'Founded'}
                  </div>
                  <div className="text-2xl font-bold font-mono tabular-nums text-content-secondary">
                    {product.founded_date ? formatDate(product.founded_date) : '-'}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </Card>
      </motion.div>

      {/* ========== 分析区域 ========== */}
      {hasAnalysis && (
        <div className="grid lg:grid-cols-3 gap-6">
          {/* 左侧：产品详情 */}
          <div className="lg:col-span-2 space-y-6">
            {/* 产品定位 */}
            {(landing?.target_audience?.length || landing?.target_roles?.length || landing?.core_features?.length || landing?.use_cases?.length) && (
              <Card padding="none">
                <div className="p-6">
                  <h2 className="text-lg font-semibold text-content-primary mb-4 flex items-center gap-2">
                    <Target className="w-5 h-5 text-brand-500" />
                    {isZh ? '产品定位' : 'Product Positioning'}
                  </h2>
                  <div className="space-y-5">
                    {/* 目标用户 & 角色 */}
                    {(landing?.target_audience?.length || landing?.target_roles?.length) && (
                      <div className="grid md:grid-cols-2 gap-4">
                        {landing?.target_audience && landing.target_audience.length > 0 && (
                          <div>
                            <h3 className="text-xs font-medium text-content-muted uppercase tracking-wide mb-2">{isZh ? '目标用户' : 'Target Audience'}</h3>
                            <div className="flex flex-wrap gap-1.5">
                              {landing.target_audience.map((item, i) => (
                                <Badge key={i} variant="default" size="sm">{item}</Badge>
                              ))}
                            </div>
                          </div>
                        )}
                        {landing?.target_roles && landing.target_roles.length > 0 && (
                          <div>
                            <h3 className="text-xs font-medium text-content-muted uppercase tracking-wide mb-2">{isZh ? '目标角色' : 'Target Roles'}</h3>
                            <div className="flex flex-wrap gap-1.5">
                              {landing.target_roles.map((item, i) => (
                                <Badge key={i} variant="muted" size="sm">{item}</Badge>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                    {/* 使用场景 */}
                    {landing?.use_cases && landing.use_cases.length > 0 && (
                      <div>
                        <h3 className="text-xs font-medium text-content-muted uppercase tracking-wide mb-2">{isZh ? '使用场景' : 'Use Cases'}</h3>
                        <div className="grid md:grid-cols-2 gap-x-4 gap-y-1.5">
                          {landing.use_cases.slice(0, 6).map((item, i) => (
                            <div key={i} className="text-sm text-content-secondary flex items-start gap-2">
                              <span className="text-brand-500 mt-1">•</span>
                              <span>{item}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                    {/* 核心功能 */}
                    {landing?.core_features && landing.core_features.length > 0 && (
                      <div>
                        <h3 className="text-xs font-medium text-content-muted uppercase tracking-wide mb-2">
                          {isZh ? '核心功能' : 'Core Features'}
                          {landing.feature_count > 0 && <span className="text-content-tertiary ml-1">({landing.feature_count})</span>}
                        </h3>
                        <div className="grid md:grid-cols-2 gap-x-4 gap-y-1.5">
                          {landing.core_features.slice(0, 8).map((feature, i) => (
                            <div key={i} className="text-sm text-content-secondary flex items-start gap-2">
                              <Check className="w-3.5 h-3.5 text-accent-success flex-shrink-0 mt-0.5" />
                              <span>{feature}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                    {/* 价值主张 */}
                    {landing?.value_propositions && landing.value_propositions.length > 0 && (
                      <div>
                        <h3 className="text-xs font-medium text-content-muted uppercase tracking-wide mb-2">{isZh ? '价值主张' : 'Value Propositions'}</h3>
                        <div className="flex flex-wrap gap-2">
                          {landing.value_propositions.map((prop, i) => (
                            <span key={i} className="px-3 py-1.5 text-sm bg-brand-500/10 text-brand-600 dark:text-brand-400 rounded-lg">
                              {prop}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </Card>
            )}

            {/* 竞争分析 */}
            {(landing?.pain_points?.length || landing?.potential_moats?.length) && (
              <Card padding="none">
                <div className="p-6">
                  <h2 className="text-lg font-semibold text-content-primary mb-4 flex items-center gap-2">
                    <Shield className="w-5 h-5 text-brand-500" />
                    {isZh ? '竞争分析' : 'Competitive Analysis'}
                  </h2>
                  <div className="grid md:grid-cols-2 gap-6">
                    {landing?.pain_points && landing.pain_points.length > 0 && (
                      <div>
                        <h3 className="text-xs font-medium text-content-muted uppercase tracking-wide mb-3">{isZh ? '解决的痛点' : 'Pain Points'}</h3>
                        <ul className="space-y-2">
                          {landing.pain_points.slice(0, 4).map((item, i) => (
                            <li key={i} className="text-sm text-content-secondary flex items-start gap-2">
                              <span className="text-accent-error mt-1">•</span>
                              <span>{item}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {landing?.potential_moats && landing.potential_moats.length > 0 && (
                      <div>
                        <h3 className="text-xs font-medium text-content-muted uppercase tracking-wide mb-3">{isZh ? '竞争壁垒' : 'Competitive Moats'}</h3>
                        <ul className="space-y-2">
                          {landing.potential_moats.slice(0, 4).map((item, i) => (
                            <li key={i} className="text-sm text-content-secondary flex items-start gap-2">
                              <Check className="w-3.5 h-3.5 text-accent-success flex-shrink-0 mt-0.5" />
                              <span>{item}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              </Card>
            )}

            {/* 转化策略 */}
            {landing && (landing.cta_texts?.length || landing.has_instant_value_demo || landing.uses_before_after || landing.uses_emotional_words || landing.pricing_model) && (
              <Card padding="none">
                <div className="p-6">
                  <h2 className="text-lg font-semibold text-content-primary mb-4 flex items-center gap-2">
                    <Zap className="w-5 h-5 text-brand-500" />
                    {isZh ? '转化策略' : 'Conversion Strategy'}
                  </h2>
                  <div className="space-y-4">
                    {/* 定价信息 */}
                    {landing.pricing_model && (
                      <div>
                        <h3 className="text-xs font-medium text-content-muted uppercase tracking-wide mb-2">{isZh ? '定价模式' : 'Pricing Model'}</h3>
                        <div className="flex items-center gap-2 flex-wrap">
                          <Badge variant="default" size="sm">{landing.pricing_model}</Badge>
                          {landing.has_free_tier && <Badge variant="success" size="sm">{isZh ? '免费版' : 'Free Tier'}</Badge>}
                          {landing.has_trial && <Badge variant="info" size="sm">{isZh ? '试用期' : 'Trial'}</Badge>}
                          {landing.pricing_clarity_score && (
                            <span className="text-xs text-content-tertiary">
                              {isZh ? '清晰度' : 'Clarity'}: {landing.pricing_clarity_score.toFixed(1)}/10
                            </span>
                          )}
                        </div>
                      </div>
                    )}
                    {/* CTA 文案 */}
                    {landing.cta_texts && landing.cta_texts.length > 0 && (
                      <div>
                        <h3 className="text-xs font-medium text-content-muted uppercase tracking-wide mb-2">
                          {isZh ? '行动号召' : 'Call to Action'}
                          {landing.cta_count > 0 && <span className="text-content-tertiary ml-1">({landing.cta_count})</span>}
                        </h3>
                        <div className="flex flex-wrap gap-2">
                          {landing.cta_texts.slice(0, 6).map((cta, i) => (
                            <span key={i} className="px-3 py-1.5 text-sm bg-brand-500/10 text-brand-600 dark:text-brand-400 rounded-lg">
                              {cta}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                    {/* 营销技巧标签 */}
                    {(landing.has_instant_value_demo || landing.uses_before_after || landing.uses_emotional_words || landing.conversion_funnel_steps > 0) && (
                      <div>
                        <h3 className="text-xs font-medium text-content-muted uppercase tracking-wide mb-2">{isZh ? '营销技巧' : 'Marketing Tactics'}</h3>
                        <div className="flex flex-wrap gap-2">
                          {landing.has_instant_value_demo && (
                            <Badge variant="success" size="sm">{isZh ? '即时价值演示' : 'Instant Demo'}</Badge>
                          )}
                          {landing.uses_before_after && (
                            <Badge variant="info" size="sm">{isZh ? '前后对比' : 'Before/After'}</Badge>
                          )}
                          {landing.uses_emotional_words && (
                            <Badge variant="warning" size="sm">{isZh ? '情感营销' : 'Emotional Copy'}</Badge>
                          )}
                          {landing.conversion_funnel_steps > 0 && (
                            <Badge variant="muted" size="sm">{landing.conversion_funnel_steps} {isZh ? '步转化' : 'Steps'}</Badge>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </Card>
            )}

            {/* 行业关键词 */}
            {landing?.industry_keywords && Object.keys(landing.industry_keywords).length > 0 && (
              <Card padding="none">
                <div className="p-6">
                  <h2 className="text-lg font-semibold text-content-primary mb-4 flex items-center gap-2">
                    <Code className="w-5 h-5 text-brand-500" />
                    {isZh ? '关键词' : 'Keywords'}
                  </h2>
                  <div className="flex flex-wrap gap-2">
                    {Object.entries(landing.industry_keywords)
                      .sort(([,a], [,b]) => b - a)
                      .slice(0, 15)
                      .map(([keyword, count], i) => (
                        <span
                          key={i}
                          className="px-2.5 py-1 text-sm text-content-secondary bg-surface-hover rounded-md"
                        >
                          {keyword}
                          {count > 1 && <span className="text-content-muted ml-1">×{count}</span>}
                        </span>
                      ))}
                  </div>
                </div>
              </Card>
            )}

            {/* 市场信息与产品洞察 */}
            {(category || (insights && insights.summary_points && insights.summary_points.length > 0)) && (
              <Card padding="none">
                <div className="p-6">
                  <h2 className="text-lg font-semibold text-content-primary mb-4 flex items-center gap-2">
                    <TrendingUp className="w-5 h-5 text-brand-500" />
                    {isZh ? '市场与洞察' : 'Market & Insights'}
                  </h2>
                  <div className="space-y-5">
                    {/* 市场信息 */}
                    {category && (
                      <div>
                        <div className="flex items-center justify-between mb-3">
                          <h3 className="text-sm font-medium text-content-primary">{category.category}</h3>
                          <MarketTypeBadge type={category.market_type} size="sm" />
                        </div>
                        <div className="grid grid-cols-2 gap-3 text-sm">
                          <div className="flex items-center justify-between">
                            <span className="text-content-muted">{isZh ? '同类产品' : 'Products'}</span>
                            <span className="text-content-secondary font-medium">{category.total_projects}</span>
                          </div>
                          <div className="flex items-center justify-between">
                            <span className="text-content-muted">{isZh ? 'TOP10占比' : 'TOP10 Share'}</span>
                            <span className="text-content-secondary font-medium">{category.top10_revenue_share.toFixed(0)}%</span>
                          </div>
                          <div className="flex items-center justify-between">
                            <span className="text-content-muted">{isZh ? '赛道收入' : 'Category Revenue'}</span>
                            <span className="text-content-secondary font-medium">{formatCurrency(category.total_revenue)}</span>
                          </div>
                          <div className="flex items-center justify-between">
                            <span className="text-content-muted">{isZh ? '平均收入' : 'Avg Revenue'}</span>
                            <span className="text-content-secondary font-medium">{formatCurrency(category.avg_revenue)}</span>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* 产品洞察 */}
                    {insights && insights.summary_points && insights.summary_points.length > 0 && (
                      <div>
                        {category && <div className="border-t border-surface-border/50 -mx-6 mb-4"></div>}
                        <h3 className="text-sm font-medium text-content-primary mb-3">{isZh ? '产品洞察' : 'Product Insights'}</h3>
                        <div className="space-y-2.5">
                          {insights.summary_points.map((point, i) => (
                            <div key={i} className="flex items-start gap-2">
                              <div className={cn(
                                "w-1.5 h-1.5 rounded-full mt-2 flex-shrink-0",
                                point.type === 'strength' ? 'bg-accent-success' :
                                point.type === 'weakness' ? 'bg-accent-error' :
                                point.type === 'opportunity' ? 'bg-brand-500' :
                                'bg-content-muted'
                              )} />
                              <p className="text-sm text-content-secondary leading-relaxed">{point.text}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </Card>
            )}
          </div>

          {/* 右侧：评分与指标 */}
          <div className="lg:col-span-1 space-y-6">
            {/* 综合评分卡片 */}
            {comprehensive && (
              <Card padding="none">
                <div className="p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h2 className="text-base font-semibold text-content-primary flex items-center gap-2">
                      <Sparkles className="w-5 h-5 text-brand-500" />
                      {isZh ? '综合分析' : 'Comprehensive Analysis'}
                    </h2>
                    <div className="text-right">
                      <div className="text-3xl font-bold font-mono text-brand-500">
                        {comprehensive.overall_recommendation.toFixed(1)}
                      </div>
                      <div className="text-xs text-content-tertiary mt-0.5">
                        {comprehensive.overall_recommendation >= 8 ? (isZh ? '强烈推荐' : 'Highly Recommended') :
                         comprehensive.overall_recommendation >= 6 ? (isZh ? '值得研究' : 'Worth Studying') :
                         (isZh ? '可以参考' : 'Reference')}
                      </div>
                    </div>
                  </div>
                  <AnalysisRadarChart
                    scores={{
                      maturity_score: comprehensive.maturity_score,
                      positioning_clarity: comprehensive.positioning_clarity,
                      pain_point_sharpness: comprehensive.pain_point_sharpness,
                      pricing_clarity: comprehensive.pricing_clarity,
                      conversion_friendliness: comprehensive.conversion_friendliness,
                      individual_replicability: comprehensive.individual_replicability,
                    }}
                    className="h-64 mt-4"
                  />
                </div>
              </Card>
            )}

            {/* Landing Page 评分 */}
            {landing && (landing.positioning_clarity_score || landing.pain_point_sharpness || landing.pricing_clarity_score || landing.conversion_friendliness_score) && (
              <Card padding="none">
                <div className="p-6">
                  <h3 className="text-base font-semibold text-content-primary mb-4">{isZh ? '落地页评分' : 'Landing Page Scores'}</h3>
                  <div className="space-y-3">
                    {landing.positioning_clarity_score && (
                      <ScoreBar label={isZh ? '定位清晰度' : 'Positioning'} value={landing.positioning_clarity_score} />
                    )}
                    {landing.pain_point_sharpness && (
                      <ScoreBar label={isZh ? '痛点精准度' : 'Pain Point'} value={landing.pain_point_sharpness} />
                    )}
                    {landing.pricing_clarity_score && (
                      <ScoreBar label={isZh ? '定价清晰度' : 'Pricing'} value={landing.pricing_clarity_score} />
                    )}
                    {landing.conversion_friendliness_score && (
                      <ScoreBar label={isZh ? '转化友好度' : 'Conversion'} value={landing.conversion_friendliness_score} />
                    )}
                    {landing.product_maturity_score && (
                      <ScoreBar label={isZh ? '产品成熟度' : 'Maturity'} value={landing.product_maturity_score} />
                    )}
                  </div>
                </div>
              </Card>
            )}

            {/* 开发适合度 + 技术指标 */}
            {selection && (
              <Card padding="none">
                <div className="p-6">
                  <h3 className="text-base font-semibold text-content-primary mb-4">{isZh ? '开发适合度' : 'Development Fit'}</h3>
                  <div className="flex justify-between items-center mb-3">
                    <span className="text-sm text-content-secondary">{isZh ? '独立开发适合度' : 'Indie Dev Suitability'}</span>
                    <span className="text-2xl font-bold font-mono text-brand-500">{selection.individual_dev_suitability.toFixed(1)}</span>
                  </div>
                  <div className="h-2 bg-surface-border/50 rounded-full overflow-hidden mb-5">
                    <div className="h-full bg-brand-500 rounded-full transition-all" style={{ width: `${selection.individual_dev_suitability * 10}%` }} />
                  </div>
                  <div className="space-y-2.5 text-sm">
                    <Row label={isZh ? '技术复杂度' : 'Tech Complexity'} value={selection.tech_complexity_level} />
                    {selection.feature_complexity && <Row label={isZh ? '功能复杂度' : 'Feature Complexity'} value={selection.feature_complexity} />}
                    {selection.startup_cost_level && <Row label={isZh ? '启动成本' : 'Startup Cost'} value={selection.startup_cost_level} />}
                    {selection.ai_dependency_level && <Row label={isZh ? 'AI依赖' : 'AI Dependency'} value={selection.ai_dependency_level} />}
                    {selection.target_customer && <Row label={isZh ? '客户类型' : 'Target Customer'} value={selection.target_customer.replace('_', ' ')} />}
                    {selection.market_scope && <Row label={isZh ? '市场范围' : 'Market Scope'} value={selection.market_scope} />}
                    {selection.product_stage && <Row label={isZh ? '产品阶段' : 'Product Stage'} value={selection.product_stage} />}
                  </div>
                  <div className="flex flex-wrap gap-1.5 mt-4">
                    {selection.is_product_driven && <Badge variant="success" size="sm">{isZh ? '产品驱动' : 'Product-led'}</Badge>}
                    {selection.is_small_and_beautiful && <Badge variant="info" size="sm">{isZh ? '小而美' : 'Focused'}</Badge>}
                    {selection.uses_llm_api && <Badge variant="muted" size="sm">LLM</Badge>}
                    {selection.has_realtime_feature && <Badge variant="warning" size="sm">{isZh ? '实时功能' : 'Realtime'}</Badge>}
                    {selection.is_data_intensive && <Badge variant="warning" size="sm">{isZh ? '数据密集' : 'Data Intensive'}</Badge>}
                    {selection.has_compliance_requirement && <Badge variant="error" size="sm">{isZh ? '合规要求' : 'Compliance'}</Badge>}
                  </div>
                </div>
              </Card>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

// Helper Components
function MetricItem({ icon, label, value, valueClassName }: {
  icon: React.ReactNode
  label: string
  value: string
  valueClassName?: string
}) {
  return (
    <div>
      <div className="flex items-center gap-1.5 text-[11px] uppercase tracking-wider text-content-muted font-medium mb-1.5">
        {icon}
        {label}
      </div>
      <div className={cn("text-xl font-bold font-mono tabular-nums", valueClassName)}>
        {value}
      </div>
    </div>
  )
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-content-muted">{label}</span>
      <span className="text-content-secondary capitalize">{value}</span>
    </div>
  )
}

function ScoreBar({ label, value }: { label: string; value: number }) {
  const percentage = (value / 10) * 100
  const color = value >= 7 ? 'bg-accent-success' : value >= 5 ? 'bg-brand-500' : 'bg-accent-warning'

  return (
    <div>
      <div className="flex items-center justify-between mb-1.5">
        <span className="text-xs text-content-secondary">{label}</span>
        <span className="text-xs font-mono font-semibold text-content-primary">{value.toFixed(1)}</span>
      </div>
      <div className="h-1.5 bg-surface-border/50 rounded-full overflow-hidden">
        <div
          className={cn("h-full rounded-full transition-all", color)}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  )
}
