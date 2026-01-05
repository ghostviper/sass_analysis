'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { Card, CardHeader } from '@/components/ui/Card'
import { Badge, MarketTypeBadge, ComplexityBadge } from '@/components/ui/Badge'
import { ProductLogo } from '@/components/ui/ProductLogo'
import { ScoreBar, ScoreCard, OverallScore } from '@/components/charts/ScoreBar'
import { AnalysisRadarChart } from '@/components/charts/RadarChart'
import { ProductDetailSkeleton } from '@/components/ui/Loading'
import {
  getStartupBySlug,
  getComprehensiveAnalysis,
  getLandingAnalysis,
  getProductSelection,
  getCategoryByName,
} from '@/lib/api'
import { formatCurrency, formatDate, cn } from '@/lib/utils'
import {
  ArrowLeft,
  ExternalLink,
  Check,
  X,
  Lightbulb,
  AlertTriangle,
  CheckCircle,
  Zap,
  TrendingUp,
  Code,
  DollarSign,
  Users,
  Calendar,
  Globe,
  Target,
  BarChart3,
  Sparkles,
  Shield,
  Layers,
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

  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [product, setProduct] = useState<Startup | null>(null)
  const [comprehensive, setComprehensive] = useState<ComprehensiveAnalysis | null>(null)
  const [landing, setLanding] = useState<LandingPageAnalysis | null>(null)
  const [selection, setSelection] = useState<ProductSelectionAnalysis | null>(null)
  const [category, setCategory] = useState<CategoryAnalysis | null>(null)

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true)
        setError(null)

        const productData = await getStartupBySlug(slug)
        setProduct(productData)

        const [compData, landingData, selectionData] = await Promise.allSettled([
          getComprehensiveAnalysis(slug),
          getLandingAnalysis(slug),
          getProductSelection(slug),
        ])

        if (compData.status === 'fulfilled') setComprehensive(compData.value)
        if (landingData.status === 'fulfilled') setLanding(landingData.value)
        if (selectionData.status === 'fulfilled') setSelection(selectionData.value)

        if (productData.category) {
          try {
            const catData = await getCategoryByName(productData.category)
            setCategory(catData)
          } catch (e) {
            // 分类可能不存在
          }
        }
      } catch (err) {
        console.error('Failed to fetch product:', err)
        setError('产品数据加载失败')
      } finally {
        setLoading(false)
      }
    }

    if (slug) {
      fetchData()
    }
  }, [slug])

  if (loading) {
    return <ProductDetailSkeleton />
  }

  if (error || !product) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Card className="text-center max-w-md">
          <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-surface-hover flex items-center justify-center">
            <AlertTriangle className="h-8 w-8 text-content-muted" />
          </div>
          <h2 className="text-xl font-display font-bold text-content-primary mb-2">
            {error || '产品未找到'}
          </h2>
          <p className="text-sm text-content-secondary mb-6">请检查链接是否正确或返回产品列表</p>
          <Link href="/products" className="btn btn-primary">
            返回产品列表
          </Link>
        </Card>
      </div>
    )
  }

  const summary = comprehensive?.analysis_summary

  return (
    <div className="space-y-8">
      {/* 返回导航 */}
      <Link
        href="/products"
        className="inline-flex items-center gap-2 text-sm font-medium text-content-muted hover:text-brand-500 transition-colors group"
      >
        <ArrowLeft className="h-4 w-4 transition-transform group-hover:-translate-x-1" />
        返回产品列表
      </Link>

      {/* 产品头部 */}
      <ProductHeader product={product} category={category} />

      {/* 综合评分 */}
      {comprehensive && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.1 }}
          className="grid md:grid-cols-3 gap-6"
        >
          <Card className="md:col-span-1 flex flex-col items-center justify-center py-8 bg-gradient-to-br from-brand-500/5 via-transparent to-accent-secondary/5">
            <OverallScore
              score={comprehensive.overall_recommendation}
              label="综合推荐"
              subtitle="基于多维度分析"
              size="lg"
            />
          </Card>

          <Card className="md:col-span-2">
            <CardHeader title="分析雷达图" subtitle="六维评分可视化" />
            <AnalysisRadarChart
              scores={{
                maturity_score: comprehensive.maturity_score,
                positioning_clarity: comprehensive.positioning_clarity,
                pain_point_sharpness: comprehensive.pain_point_sharpness,
                pricing_clarity: comprehensive.pricing_clarity,
                conversion_friendliness: comprehensive.conversion_friendliness,
                individual_replicability: comprehensive.individual_replicability,
              }}
              className="h-64"
            />
          </Card>
        </motion.div>
      )}

      {/* 评分详情 */}
      {comprehensive && (
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.2 }}
        >
          <SectionHeader icon={BarChart3} title="评分详情" />
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            <ScoreCard
              label="产品成熟度"
              score={comprehensive.maturity_score}
              description="产品完成度与功能完整性"
              icon={<TrendingUp className="h-4 w-4" />}
            />
            <ScoreCard
              label="定位清晰度"
              score={comprehensive.positioning_clarity}
              description="目标用户与价值主张清晰度"
              icon={<Target className="h-4 w-4" />}
            />
            <ScoreCard
              label="痛点锋利度"
              score={comprehensive.pain_point_sharpness}
              description="解决的问题是否足够痛"
              icon={<Zap className="h-4 w-4" />}
            />
            <ScoreCard
              label="定价清晰度"
              score={comprehensive.pricing_clarity}
              description="价格体系是否清晰合理"
              icon={<DollarSign className="h-4 w-4" />}
            />
            <ScoreCard
              label="转化友好度"
              score={comprehensive.conversion_friendliness}
              description="用户转化路径是否顺畅"
              icon={<Users className="h-4 w-4" />}
            />
            <ScoreCard
              label="可复制性"
              score={comprehensive.individual_replicability}
              description="独立开发者复制难度"
              icon={<Code className="h-4 w-4" />}
            />
          </div>
        </motion.section>
      )}

      {/* 选品分析 */}
      {selection && (
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.3 }}
        >
          <SectionHeader icon={Target} title="选品分析" />
          <div className="grid md:grid-cols-2 gap-6">
            <SelectionAnalysisCard selection={selection} />
            <ComboMatchCard selection={selection} />
          </div>
        </motion.section>
      )}

      {/* 综合建议 */}
      {summary && (
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.4 }}
        >
          <SectionHeader icon={Lightbulb} title="综合建议" />
          <div className="grid md:grid-cols-3 gap-4">
            <InsightCard
              title="优势"
              items={summary.strengths}
              icon={CheckCircle}
              variant="success"
            />
            <InsightCard
              title="风险"
              items={summary.risks}
              icon={AlertTriangle}
              variant="warning"
            />
            <InsightCard
              title="建议"
              items={summary.recommendations}
              icon={Sparkles}
              variant="info"
            />
          </div>
        </motion.section>
      )}

      {/* Landing Page 分析详情 */}
      {landing && (
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.5 }}
        >
          <SectionHeader icon={Globe} title="Landing Page 分析" />
          <LandingAnalysisSection landing={landing} />
        </motion.section>
      )}

      {/* 数据完整度 */}
      {summary && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.6 }}
        >
          <Card>
            <CardHeader
              title="数据来源"
              subtitle={`数据完整度 ${summary.data_completeness.toFixed(0)}%`}
              action={
                <div className="flex items-center gap-2">
                  <div className="h-2 w-24 bg-surface-border rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-brand-500 to-accent-secondary rounded-full transition-all duration-500"
                      style={{ width: `${summary.data_completeness}%` }}
                    />
                  </div>
                  <span className="text-sm font-mono font-semibold text-brand-500">
                    {summary.data_completeness.toFixed(0)}%
                  </span>
                </div>
              }
            />
            <div className="flex flex-wrap gap-3">
              <DataSourceBadge
                label="选品分析"
                available={summary.data_sources.has_selection_analysis}
              />
              <DataSourceBadge
                label="Landing分析"
                available={summary.data_sources.has_landing_analysis}
              />
              <DataSourceBadge
                label="赛道分析"
                available={summary.data_sources.has_category_analysis}
              />
              <DataSourceBadge
                label="收入数据"
                available={summary.data_sources.has_revenue_data}
              />
              <DataSourceBadge
                label="粉丝数据"
                available={summary.data_sources.has_follower_data}
              />
            </div>
          </Card>
        </motion.div>
      )}
    </div>
  )
}

// 区块标题组件
function SectionHeader({ icon: Icon, title }: { icon: React.ComponentType<{ className?: string }>; title: string }) {
  return (
    <div className="flex items-center gap-3 mb-5">
      <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-brand-500/15 to-accent-secondary/15 flex items-center justify-center ring-1 ring-brand-500/10">
        <Icon className="h-4.5 w-4.5 text-brand-500" />
      </div>
      <h2 className="text-lg font-display font-bold text-content-primary tracking-tight">
        {title}
      </h2>
    </div>
  )
}

// 产品头部组件
function ProductHeader({ product, category }: { product: Startup; category: CategoryAnalysis | null }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Card className="relative overflow-hidden">
        {/* 背景装饰 */}
        <div className="absolute top-0 right-0 w-80 h-80 bg-gradient-to-bl from-brand-500/5 via-transparent to-transparent rounded-full blur-3xl -translate-y-1/2 translate-x-1/3 pointer-events-none" />
        <div className="absolute bottom-0 left-0 w-60 h-60 bg-gradient-to-tr from-accent-secondary/5 via-transparent to-transparent rounded-full blur-3xl translate-y-1/2 -translate-x-1/3 pointer-events-none" />

        <div className="relative flex flex-col md:flex-row md:items-start gap-6">
          {/* 产品 Logo */}
          <div className="flex-shrink-0">
            <ProductLogo
              name={product.name}
              logoUrl={product.logo_url}
              size="lg"
            />
          </div>

          {/* 产品信息 */}
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h1 className="text-2xl font-display font-bold text-content-primary tracking-tight">
                  {product.name}
                </h1>
                <div className="flex items-center gap-3 mt-2.5">
                  {product.category && (
                    <span className="text-sm font-medium text-content-tertiary">{product.category}</span>
                  )}
                  {category && (
                    <MarketTypeBadge type={category.market_type} />
                  )}
                </div>
              </div>

              {product.website_url && (
                <a
                  href={product.website_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className={cn(
                    'inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold transition-all duration-200',
                    'bg-brand-500 text-white hover:bg-brand-600',
                    'shadow-sm hover:shadow-md hover:shadow-brand-500/20'
                  )}
                >
                  <ExternalLink className="h-4 w-4" />
                  访问网站
                </a>
              )}
            </div>

            <p className="text-sm text-content-secondary mt-4 leading-relaxed max-w-2xl">
              {product.description || '暂无描述'}
            </p>

            {/* 关键指标 */}
            <div className="flex flex-wrap gap-8 mt-6 pt-5 border-t border-surface-border/50">
              <MetricItem
                icon={DollarSign}
                label="月收入"
                value={formatCurrency(product.revenue_30d)}
                highlight
              />
              {product.twitter_followers && (
                <MetricItem
                  icon={Users}
                  label="关注者"
                  value={product.twitter_followers.toLocaleString()}
                />
              )}
              {product.founded_date && (
                <MetricItem
                  icon={Calendar}
                  label="成立时间"
                  value={formatDate(product.founded_date)}
                />
              )}
            </div>
          </div>
        </div>
      </Card>
    </motion.div>
  )
}

// 指标项组件
function MetricItem({
  icon: Icon,
  label,
  value,
  highlight = false,
}: {
  icon: React.ComponentType<{ className?: string }>
  label: string
  value: string
  highlight?: boolean
}) {
  return (
    <div className="flex items-center gap-3">
      <div className={cn(
        'w-10 h-10 rounded-xl flex items-center justify-center',
        highlight
          ? 'bg-gradient-to-br from-brand-500/15 to-accent-secondary/15 ring-1 ring-brand-500/10'
          : 'bg-surface-hover'
      )}>
        <Icon className={cn('h-4.5 w-4.5', highlight ? 'text-brand-500' : 'text-content-muted')} />
      </div>
      <div>
        <div className={cn(
          'text-xl font-mono font-bold tabular-nums tracking-tight',
          highlight ? 'text-brand-600 dark:text-brand-400' : 'text-content-primary'
        )}>
          {value}
        </div>
        <div className="text-xs text-content-muted font-medium">{label}</div>
      </div>
    </div>
  )
}

// 选品分析卡片
function SelectionAnalysisCard({ selection }: { selection: ProductSelectionAnalysis }) {
  const features = [
    { label: '产品驱动型', value: selection.is_product_driven, icon: Zap },
    { label: '小而美', value: selection.is_small_and_beautiful, icon: Sparkles },
    { label: '依赖LLM', value: selection.uses_llm_api, icon: Code },
    { label: '需要合规', value: selection.requires_compliance, icon: Shield },
  ]

  return (
    <Card>
      <CardHeader title="产品特征" subtitle="选品维度分析" />

      <div className="space-y-4">
        {/* 核心指标 */}
        <div className="grid grid-cols-2 gap-4">
          <div className="p-3 rounded-xl bg-gradient-to-br from-brand-500/5 to-transparent border border-surface-border/50">
            <div className="text-xs text-content-muted font-medium mb-1">IP依赖度</div>
            <div className="flex items-baseline gap-1">
              <span className="text-xl font-mono font-bold text-content-primary tabular-nums">
                {selection.ip_dependency_score.toFixed(1)}
              </span>
              <span className="text-sm text-content-muted">/10</span>
            </div>
          </div>
          <div className="p-3 rounded-xl bg-gradient-to-br from-accent-secondary/5 to-transparent border border-surface-border/50">
            <div className="text-xs text-content-muted font-medium mb-1">描述字数</div>
            <div className="text-xl font-mono font-bold text-content-primary tabular-nums">
              {selection.description_word_count}
            </div>
          </div>
        </div>

        <ScoreBar
          label="个人开发适合度"
          score={selection.individual_dev_suitability}
          delay={100}
        />

        <div className="flex items-center justify-between py-2">
          <span className="text-sm text-content-secondary font-medium">技术复杂度</span>
          <ComplexityBadge level={selection.tech_complexity_level} />
        </div>

        <div className="grid grid-cols-2 gap-2 pt-4 border-t border-surface-border/50">
          {features.map((f) => {
            const IconComponent = f.icon
            return (
              <div
                key={f.label}
                className={cn(
                  'flex items-center gap-2.5 p-2.5 rounded-xl transition-all duration-200',
                  f.value
                    ? 'bg-accent-success/8 border border-accent-success/20'
                    : 'bg-surface-hover/50 border border-transparent'
                )}
              >
                <div className={cn(
                  'w-7 h-7 rounded-lg flex items-center justify-center',
                  f.value ? 'bg-accent-success/15' : 'bg-surface-border/50'
                )}>
                  {f.value ? (
                    <Check className="h-3.5 w-3.5 text-accent-success" />
                  ) : (
                    <IconComponent className="h-3.5 w-3.5 text-content-muted" />
                  )}
                </div>
                <span className={cn(
                  'text-sm font-medium',
                  f.value ? 'text-content-primary' : 'text-content-muted'
                )}>
                  {f.label}
                </span>
              </div>
            )
          })}
        </div>
      </div>
    </Card>
  )
}

// 组合匹配卡片
function ComboMatchCard({ selection }: { selection: ProductSelectionAnalysis }) {
  const combos = [
    {
      name: '组合1',
      match: selection.combo1_match,
      desc: '低粉丝 + 高收入 + 技术简单 + 年轻产品',
      detail: '适合快速验证的产品机会',
      color: 'from-cyan-500/10 to-cyan-500/5',
    },
    {
      name: '组合2',
      match: selection.combo2_match,
      desc: '简短描述 + 中等收入 + 低复杂度',
      detail: '功能聚焦的小工具类产品',
      color: 'from-violet-500/10 to-violet-500/5',
    },
    {
      name: '组合3',
      match: selection.combo3_match,
      desc: '简单产品 + 有收入验证 + 低复杂度',
      detail: '已验证需求的简单产品',
      color: 'from-amber-500/10 to-amber-500/5',
    },
  ]

  const matchCount = combos.filter(c => c.match).length

  return (
    <Card>
      <CardHeader
        title="组合匹配"
        subtitle={`${matchCount}/3 组合命中`}
        action={
          matchCount >= 2 ? (
            <Badge variant="success">
              <Zap className="h-3 w-3" />
              高度推荐
            </Badge>
          ) : matchCount >= 1 ? (
            <Badge variant="warning">值得关注</Badge>
          ) : null
        }
      />

      <div className="space-y-3">
        {combos.map((combo, index) => (
          <div
            key={combo.name}
            className={cn(
              'p-4 rounded-xl border transition-all duration-200',
              combo.match
                ? 'bg-gradient-to-r from-accent-success/8 to-transparent border-accent-success/25'
                : 'bg-surface-hover/30 border-surface-border/50'
            )}
          >
            <div className="flex items-center gap-3">
              <div className={cn(
                'w-9 h-9 rounded-xl flex items-center justify-center font-display font-bold text-sm',
                combo.match
                  ? 'bg-accent-success/15 text-accent-success'
                  : `bg-gradient-to-br ${combo.color} text-content-muted`
              )}>
                {combo.match ? (
                  <Check className="h-4.5 w-4.5" />
                ) : (
                  index + 1
                )}
              </div>
              <div className="flex-1 min-w-0">
                <div className={cn(
                  'text-sm font-semibold tracking-tight',
                  combo.match ? 'text-content-primary' : 'text-content-muted'
                )}>
                  {combo.name}
                  <span className="font-normal text-content-tertiary ml-2">{combo.detail}</span>
                </div>
                <div className="text-xs text-content-muted mt-0.5 truncate">{combo.desc}</div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </Card>
  )
}

// 洞察卡片
function InsightCard({
  title,
  items,
  icon: Icon,
  variant,
}: {
  title: string
  items: string[]
  icon: React.ComponentType<{ className?: string }>
  variant: 'success' | 'warning' | 'info'
}) {
  const variantConfig = {
    success: {
      border: 'border-l-accent-success',
      bg: 'bg-accent-success/8',
      iconBg: 'bg-accent-success/15',
      iconColor: 'text-accent-success',
      dotColor: 'bg-accent-success',
    },
    warning: {
      border: 'border-l-accent-warning',
      bg: 'bg-accent-warning/8',
      iconBg: 'bg-accent-warning/15',
      iconColor: 'text-accent-warning',
      dotColor: 'bg-accent-warning',
    },
    info: {
      border: 'border-l-brand-500',
      bg: 'bg-brand-500/8',
      iconBg: 'bg-brand-500/15',
      iconColor: 'text-brand-500',
      dotColor: 'bg-brand-500',
    },
  }

  const config = variantConfig[variant]

  return (
    <Card className={cn('border-l-4', config.border)}>
      <div className="flex items-center gap-3 mb-4">
        <div className={cn('w-9 h-9 rounded-xl flex items-center justify-center', config.iconBg)}>
          <Icon className={cn('h-4.5 w-4.5', config.iconColor)} />
        </div>
        <h3 className="font-display font-semibold text-content-primary tracking-tight">{title}</h3>
      </div>

      {items.length > 0 ? (
        <ul className="space-y-2.5">
          {items.map((item, i) => (
            <li key={i} className="flex items-start gap-2.5 text-sm text-content-secondary leading-relaxed">
              <span className={cn('mt-2 w-1.5 h-1.5 rounded-full flex-shrink-0', config.dotColor)} />
              {item}
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-sm text-content-muted">暂无数据</p>
      )}
    </Card>
  )
}

// Landing Page 分析区块 - 增强版
function LandingAnalysisSection({ landing }: { landing: LandingPageAnalysis }) {
  return (
    <div className="space-y-5">
      {/* 第一行：评分 + 标题信息 */}
      <div className="grid md:grid-cols-2 gap-5">
        <Card>
          <CardHeader title="页面评分" subtitle="AI 分析结果" />
          <div className="space-y-3">
            {landing.product_maturity_score !== null && (
              <ScoreBar label="产品成熟度" score={landing.product_maturity_score} delay={0} />
            )}
            {landing.positioning_clarity_score !== null && (
              <ScoreBar label="定位清晰度" score={landing.positioning_clarity_score} delay={50} />
            )}
            {landing.pain_point_sharpness !== null && (
              <ScoreBar label="痛点锋利度" score={landing.pain_point_sharpness} delay={100} />
            )}
            {landing.pricing_clarity_score !== null && (
              <ScoreBar label="定价清晰度" score={landing.pricing_clarity_score} delay={150} />
            )}
            {landing.conversion_friendliness_score !== null && (
              <ScoreBar label="转化友好度" score={landing.conversion_friendliness_score} delay={200} />
            )}
            {landing.individual_replicability_score !== null && (
              <ScoreBar label="可复制性" score={landing.individual_replicability_score} delay={250} />
            )}
          </div>
        </Card>

        <Card>
          <CardHeader title="页面标题" subtitle="主要文案提取" />
          <div className="space-y-4">
            {landing.headline_text && (
              <div className="p-3 rounded-xl bg-gradient-to-r from-brand-500/5 to-transparent border border-surface-border/50">
                <div className="text-xs text-content-muted font-medium mb-1.5">主标题</div>
                <div className="text-base font-semibold text-content-primary leading-relaxed">{landing.headline_text}</div>
              </div>
            )}
            {landing.tagline_text && (
              <div className="p-3 rounded-xl bg-surface-hover/50 border border-surface-border/30">
                <div className="text-xs text-content-muted font-medium mb-1.5">副标题/标语</div>
                <div className="text-sm text-content-secondary leading-relaxed">{landing.tagline_text}</div>
              </div>
            )}
            {!landing.headline_text && !landing.tagline_text && (
              <div className="text-content-muted text-sm py-4 text-center">暂无标题信息</div>
            )}
          </div>
        </Card>
      </div>

      {/* 第二行：目标用户 + 使用场景 */}
      <div className="grid md:grid-cols-2 gap-5">
        <Card>
          <CardHeader title="目标用户" subtitle="用户群体分析" />
          <div className="space-y-4">
            {landing.target_audience && landing.target_audience.length > 0 && (
              <div>
                <div className="text-xs text-content-muted font-medium mb-2">用户群体</div>
                <div className="flex flex-wrap gap-2">
                  {landing.target_audience.map((item, i) => (
                    <Badge key={i} variant="info" size="sm">{item}</Badge>
                  ))}
                </div>
              </div>
            )}
            {landing.target_roles && landing.target_roles.length > 0 && (
              <div>
                <div className="text-xs text-content-muted font-medium mb-2">目标角色</div>
                <div className="flex flex-wrap gap-2">
                  {landing.target_roles.map((item, i) => (
                    <Badge key={i} variant="muted" size="sm">{item}</Badge>
                  ))}
                </div>
              </div>
            )}
            {(!landing.target_audience || landing.target_audience.length === 0) &&
             (!landing.target_roles || landing.target_roles.length === 0) && (
              <div className="text-content-muted text-sm py-4 text-center">暂无用户分析数据</div>
            )}
          </div>
        </Card>

        <Card>
          <CardHeader title="使用场景" subtitle="产品应用场景" />
          {landing.use_cases && landing.use_cases.length > 0 ? (
            <ul className="space-y-2.5">
              {landing.use_cases.map((item, i) => (
                <li key={i} className="flex items-start gap-2.5 text-sm text-content-secondary leading-relaxed">
                  <span className="mt-2 w-1.5 h-1.5 rounded-full bg-brand-500 flex-shrink-0" />
                  {item}
                </li>
              ))}
            </ul>
          ) : (
            <div className="text-content-muted text-sm py-4 text-center">暂无使用场景数据</div>
          )}
        </Card>
      </div>

      {/* 第三行：核心功能 + 价值主张 */}
      <div className="grid md:grid-cols-2 gap-5">
        <Card>
          <CardHeader
            title="核心功能"
            subtitle={landing.feature_count ? `共 ${landing.feature_count} 个功能` : undefined}
          />
          {landing.core_features && landing.core_features.length > 0 ? (
            <ul className="space-y-2.5">
              {landing.core_features.map((item, i) => (
                <li key={i} className="flex items-start gap-2.5 text-sm text-content-secondary leading-relaxed">
                  <div className="mt-0.5 w-5 h-5 rounded-md bg-accent-success/10 flex items-center justify-center flex-shrink-0">
                    <Check className="h-3 w-3 text-accent-success" />
                  </div>
                  {item}
                </li>
              ))}
            </ul>
          ) : (
            <div className="text-content-muted text-sm py-4 text-center">暂无功能列表</div>
          )}
        </Card>

        <Card>
          <CardHeader title="价值主张" subtitle="产品核心价值" />
          {landing.value_propositions && landing.value_propositions.length > 0 ? (
            <ul className="space-y-2.5">
              {landing.value_propositions.map((item, i) => (
                <li key={i} className="flex items-start gap-2.5 text-sm text-content-secondary leading-relaxed">
                  <div className="mt-0.5 w-5 h-5 rounded-md bg-accent-warning/10 flex items-center justify-center flex-shrink-0">
                    <Sparkles className="h-3 w-3 text-accent-warning" />
                  </div>
                  {item}
                </li>
              ))}
            </ul>
          ) : (
            <div className="text-content-muted text-sm py-4 text-center">暂无价值主张数据</div>
          )}
        </Card>
      </div>

      {/* 第四行：痛点分析 + 潜在护城河 */}
      <div className="grid md:grid-cols-2 gap-5">
        <Card>
          <CardHeader title="痛点分析" subtitle="解决的用户痛点" />
          <div className="space-y-4">
            {landing.pain_points && landing.pain_points.length > 0 ? (
              <ul className="space-y-2.5">
                {landing.pain_points.map((item, i) => (
                  <li key={i} className="flex items-start gap-2.5 text-sm text-content-secondary leading-relaxed">
                    <div className="mt-0.5 w-5 h-5 rounded-md bg-rose-500/10 flex items-center justify-center flex-shrink-0">
                      <AlertTriangle className="h-3 w-3 text-rose-500" />
                    </div>
                    {item}
                  </li>
                ))}
              </ul>
            ) : (
              <div className="text-content-muted text-sm py-4 text-center">暂无痛点数据</div>
            )}

            {/* 痛点表达技巧 */}
            <div className="flex gap-2 pt-3 border-t border-surface-border/50">
              <div className={cn(
                'flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium transition-colors',
                landing.uses_before_after
                  ? 'bg-accent-success/10 text-accent-success border border-accent-success/20'
                  : 'bg-surface-hover/50 text-content-muted border border-transparent'
              )}>
                {landing.uses_before_after ? <Check className="h-3 w-3" /> : <X className="h-3 w-3" />}
                新旧对比
              </div>
              <div className={cn(
                'flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium transition-colors',
                landing.uses_emotional_words
                  ? 'bg-accent-success/10 text-accent-success border border-accent-success/20'
                  : 'bg-surface-hover/50 text-content-muted border border-transparent'
              )}>
                {landing.uses_emotional_words ? <Check className="h-3 w-3" /> : <X className="h-3 w-3" />}
                情绪化表达
              </div>
            </div>
          </div>
        </Card>

        <Card>
          <CardHeader title="潜在护城河" subtitle="竞争优势分析" />
          {landing.potential_moats && landing.potential_moats.length > 0 ? (
            <ul className="space-y-2.5">
              {landing.potential_moats.map((item, i) => (
                <li key={i} className="flex items-start gap-2.5 text-sm text-content-secondary leading-relaxed">
                  <div className="mt-0.5 w-5 h-5 rounded-md bg-violet-500/10 flex items-center justify-center flex-shrink-0">
                    <Shield className="h-3 w-3 text-violet-500" />
                  </div>
                  {item}
                </li>
              ))}
            </ul>
          ) : (
            <div className="text-content-muted text-sm py-4 text-center">暂无护城河分析</div>
          )}
        </Card>
      </div>

      {/* 第五行：定价信息 + 转化分析 */}
      <div className="grid md:grid-cols-2 gap-5">
        <Card>
          <CardHeader title="定价信息" subtitle="价格策略分析" />
          <div className="space-y-4">
            <div className="flex flex-wrap items-center gap-3">
              {landing.pricing_model && (
                <div className="flex items-center gap-2">
                  <span className="text-xs text-content-muted font-medium">定价模式</span>
                  <Badge variant="info">{landing.pricing_model}</Badge>
                </div>
              )}
              {landing.has_free_tier && (
                <Badge variant="success" size="sm">免费版</Badge>
              )}
              {landing.has_trial && (
                <Badge variant="success" size="sm">试用期</Badge>
              )}
            </div>

            {landing.pricing_tiers && landing.pricing_tiers.length > 0 && (
              <div>
                <div className="text-xs text-content-muted font-medium mb-2">定价层级</div>
                <div className="space-y-2">
                  {landing.pricing_tiers.map((tier: any, i: number) => (
                    <div key={i} className="p-3 rounded-xl bg-surface-hover/50 border border-surface-border/30 text-sm flex items-center justify-between">
                      <span className="font-medium text-content-primary">{tier.name || `方案${i+1}`}</span>
                      {tier.price && <span className="font-mono font-semibold text-brand-500">{tier.price}</span>}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </Card>

        <Card>
          <CardHeader title="转化分析" subtitle="用户转化路径" />
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div className="p-3 rounded-xl bg-gradient-to-br from-brand-500/5 to-transparent border border-surface-border/50">
                <div className="text-2xl font-mono font-bold text-content-primary tabular-nums">{landing.cta_count || 0}</div>
                <div className="text-xs text-content-muted font-medium">CTA按钮数</div>
              </div>
              <div className="p-3 rounded-xl bg-gradient-to-br from-accent-secondary/5 to-transparent border border-surface-border/50">
                <div className="text-2xl font-mono font-bold text-content-primary tabular-nums">{landing.conversion_funnel_steps || 0}</div>
                <div className="text-xs text-content-muted font-medium">转化步骤</div>
              </div>
            </div>

            {landing.cta_texts && landing.cta_texts.length > 0 && (
              <div>
                <div className="text-xs text-content-muted font-medium mb-2">CTA 文案</div>
                <div className="flex flex-wrap gap-2">
                  {landing.cta_texts.map((text, i) => (
                    <Badge key={i} variant="muted" size="sm">{text}</Badge>
                  ))}
                </div>
              </div>
            )}

            <div className={cn(
              'flex items-center gap-2.5 p-3 rounded-xl text-sm font-medium transition-colors',
              landing.has_instant_value_demo
                ? 'bg-accent-success/8 text-accent-success border border-accent-success/20'
                : 'bg-surface-hover/50 text-content-muted border border-transparent'
            )}>
              <div className={cn(
                'w-6 h-6 rounded-lg flex items-center justify-center',
                landing.has_instant_value_demo ? 'bg-accent-success/15' : 'bg-surface-border/50'
              )}>
                {landing.has_instant_value_demo ? <Check className="h-3.5 w-3.5" /> : <X className="h-3.5 w-3.5" />}
              </div>
              {landing.has_instant_value_demo ? '有即时价值体验' : '无即时价值体验'}
            </div>
          </div>
        </Card>
      </div>
    </div>
  )
}

// 数据来源徽章
function DataSourceBadge({ label, available }: { label: string; available: boolean }) {
  return (
    <span className={cn(
      'inline-flex items-center gap-2 px-3 py-2 rounded-xl text-sm font-medium transition-all duration-200',
      available
        ? 'bg-accent-success/8 text-accent-success border border-accent-success/20'
        : 'bg-surface-hover/50 text-content-muted border border-transparent'
    )}>
      <div className={cn(
        'w-5 h-5 rounded-md flex items-center justify-center',
        available ? 'bg-accent-success/15' : 'bg-surface-border/50'
      )}>
        {available ? <Check className="h-3 w-3" /> : <X className="h-3 w-3" />}
      </div>
      {label}
    </span>
  )
}
