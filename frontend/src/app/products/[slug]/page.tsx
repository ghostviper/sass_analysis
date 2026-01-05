'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'
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
  Twitter,
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

        // 先获取产品基础信息
        const productData = await getStartupBySlug(slug)
        setProduct(productData)

        // 并行获取其他分析数据
        const [compData, landingData, selectionData] = await Promise.allSettled([
          getComprehensiveAnalysis(slug),
          getLandingAnalysis(slug),
          getProductSelection(slug),
        ])

        if (compData.status === 'fulfilled') setComprehensive(compData.value)
        if (landingData.status === 'fulfilled') setLanding(landingData.value)
        if (selectionData.status === 'fulfilled') setSelection(selectionData.value)

        // 获取分类信息
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
          <div className="text-4xl mb-4">😕</div>
          <h2 className="text-xl font-semibold text-content-primary mb-2">
            {error || '产品未找到'}
          </h2>
          <Link href="/products" className="btn btn-primary mt-4">
            返回产品列表
          </Link>
        </Card>
      </div>
    )
  }

  const summary = comprehensive?.analysis_summary

  return (
    <div className="space-y-6">
      {/* 返回导航 */}
      <Link
        href="/products"
        className="inline-flex items-center gap-2 text-content-muted hover:text-content-primary transition-colors"
      >
        <ArrowLeft className="h-4 w-4" />
        返回产品列表
      </Link>

      {/* 产品头部 */}
      <ProductHeader product={product} category={category} />

      {/* 综合评分 */}
      {comprehensive && (
        <div className="grid md:grid-cols-3 gap-6">
          <Card className="md:col-span-1 flex flex-col items-center justify-center py-8">
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
        </div>
      )}

      {/* 评分详情 */}
      {comprehensive && (
        <section>
          <h2 className="text-lg font-display font-semibold text-content-primary mb-4">
            📊 评分详情
          </h2>
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
              icon={<Users className="h-4 w-4" />}
            />
            <ScoreCard
              label="痛点锋利度"
              score={comprehensive.pain_point_sharpness}
              description="解决的问题是否足够痛"
              icon={<Lightbulb className="h-4 w-4" />}
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
              icon={<CheckCircle className="h-4 w-4" />}
            />
            <ScoreCard
              label="可复制性"
              score={comprehensive.individual_replicability}
              description="独立开发者复制难度"
              icon={<Code className="h-4 w-4" />}
            />
          </div>
        </section>
      )}

      {/* 选品分析 */}
      {selection && (
        <section>
          <h2 className="text-lg font-display font-semibold text-content-primary mb-4">
            🎯 选品分析
          </h2>
          <div className="grid md:grid-cols-2 gap-6">
            <SelectionAnalysisCard selection={selection} />
            <ComboMatchCard selection={selection} />
          </div>
        </section>
      )}

      {/* 综合建议 */}
      {summary && (
        <section>
          <h2 className="text-lg font-display font-semibold text-content-primary mb-4">
            💡 综合建议
          </h2>
          <div className="grid md:grid-cols-3 gap-4">
            <InsightCard
              title="优势"
              items={summary.strengths}
              icon={CheckCircle}
              color="text-accent-success"
              bgColor="bg-accent-success/10"
            />
            <InsightCard
              title="风险"
              items={summary.risks}
              icon={AlertTriangle}
              color="text-accent-warning"
              bgColor="bg-accent-warning/10"
            />
            <InsightCard
              title="建议"
              items={summary.recommendations}
              icon={Lightbulb}
              color="text-accent-primary"
              bgColor="bg-accent-primary/10"
            />
          </div>
        </section>
      )}

      {/* Landing Page 分析详情 */}
      {landing && (
        <section>
          <h2 className="text-lg font-display font-semibold text-content-primary mb-4">
            🌐 Landing Page 分析
          </h2>
          <LandingAnalysisSection landing={landing} />
        </section>
      )}

      {/* 数据完整度 */}
      {summary && (
        <Card>
          <CardHeader
            title="数据来源"
            subtitle={`数据完整度 ${summary.data_completeness.toFixed(0)}%`}
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
      )}
    </div>
  )
}

// 产品头部组件
function ProductHeader({ product, category }: { product: Startup; category: CategoryAnalysis | null }) {
  return (
    <Card>
      <div className="flex flex-col md:flex-row md:items-start gap-6">
        {/* 产品 Logo */}
        <ProductLogo
          name={product.name}
          logoUrl={product.logo_url}
          size="lg"
        />

        {/* 产品信息 */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h1 className="text-2xl font-display font-bold text-content-primary">
                {product.name}
              </h1>
              <div className="flex items-center gap-3 mt-2">
                {product.category && (
                  <span className="text-content-muted">{product.category}</span>
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
                className="btn btn-secondary flex-shrink-0"
              >
                <ExternalLink className="h-4 w-4" />
                访问网站
              </a>
            )}
          </div>

          <p className="text-content-secondary mt-4">
            {product.description || '暂无描述'}
          </p>

          {/* 关键指标 */}
          <div className="flex flex-wrap gap-6 mt-6 pt-4 border-t border-surface-border/50">
            <div>
              <div className="text-2xl font-mono font-bold text-content-primary">
                {formatCurrency(product.revenue_30d)}
              </div>
              <div className="text-sm text-content-muted flex items-center gap-1">
                <DollarSign className="h-3 w-3" />
                月收入
              </div>
            </div>

            {product.twitter_followers && (
              <div>
                <div className="text-2xl font-mono font-bold text-content-primary">
                  {product.twitter_followers.toLocaleString()}
                </div>
                <div className="text-sm text-content-muted flex items-center gap-1">
                  <Twitter className="h-3 w-3" />
                  关注者
                </div>
              </div>
            )}

            {product.founded_date && (
              <div>
                <div className="text-2xl font-mono font-bold text-content-primary">
                  {formatDate(product.founded_date)}
                </div>
                <div className="text-sm text-content-muted flex items-center gap-1">
                  <Calendar className="h-3 w-3" />
                  成立时间
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </Card>
  )
}

// 选品分析卡片
function SelectionAnalysisCard({ selection }: { selection: ProductSelectionAnalysis }) {
  const features = [
    { label: '产品驱动型', value: selection.is_product_driven, desc: '产品本身吸引用户' },
    { label: '小而美', value: selection.is_small_and_beautiful, desc: '功能聚焦不臃肿' },
    { label: '依赖LLM', value: selection.uses_llm_api, desc: '使用大语言模型API' },
    { label: '需要合规', value: selection.requires_compliance, desc: '涉及法规合规要求' },
  ]

  return (
    <Card>
      <CardHeader title="产品特征" subtitle="选品维度分析" />

      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <span className="text-content-secondary">IP依赖度</span>
          <span className="font-mono text-content-primary">
            {selection.ip_dependency_score.toFixed(1)}/10
          </span>
        </div>

        <ScoreBar
          label="个人开发适合度"
          score={selection.individual_dev_suitability}
          delay={100}
        />

        <div className="flex items-center justify-between">
          <span className="text-content-secondary">描述字数</span>
          <span className="font-mono text-content-primary">
            {selection.description_word_count}
          </span>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-content-secondary">技术复杂度</span>
          <ComplexityBadge level={selection.tech_complexity_level} />
        </div>

        <div className="grid grid-cols-2 gap-3 pt-4 border-t border-surface-border/50">
          {features.map((f) => (
            <div
              key={f.label}
              className={cn(
                'flex items-center gap-2 p-2 rounded-lg',
                f.value ? 'bg-accent-success/10' : 'bg-background-tertiary'
              )}
            >
              {f.value ? (
                <Check className={cn('h-3.5 w-3.5', 'text-accent-success')} />
              ) : (
                <X className={cn('h-3.5 w-3.5', 'text-content-muted')} />
              )}
              <span className={cn('text-sm', f.value ? 'text-content-primary' : 'text-content-muted')}>
                {f.label}
              </span>
            </div>
          ))}
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
    },
    {
      name: '组合2',
      match: selection.combo2_match,
      desc: '简短描述 + 中等收入 + 低复杂度',
      detail: '功能聚焦的小工具类产品',
    },
    {
      name: '组合3',
      match: selection.combo3_match,
      desc: '简单产品 + 有收入验证 + 低复杂度',
      detail: '已验证需求的简单产品',
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
        {combos.map((combo) => (
          <div
            key={combo.name}
            className={cn(
              'p-4 rounded-lg border transition-all',
              combo.match
                ? 'bg-accent-success/5 border-accent-success/30'
                : 'bg-background-tertiary border-surface-border/50'
            )}
          >
            <div className="flex items-center gap-3 mb-2">
              <div className={cn(
                'w-8 h-8 rounded-lg flex items-center justify-center',
                combo.match ? 'bg-accent-success/20' : 'bg-surface'
              )}>
                {combo.match ? (
                  <Check className={cn('h-4 w-4', 'text-accent-success')} />
                ) : (
                  <X className={cn('h-4 w-4', 'text-content-muted')} />
                )}
              </div>
              <div>
                <div className={cn(
                  'font-medium',
                  combo.match ? 'text-content-primary' : 'text-content-muted'
                )}>
                  {combo.name}
                </div>
                <div className="text-xs text-content-muted">{combo.desc}</div>
              </div>
            </div>
            <p className={cn(
              'text-sm ml-11',
              combo.match ? 'text-content-secondary' : 'text-content-muted'
            )}>
              {combo.detail}
            </p>
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
  color,
  bgColor,
}: {
  title: string
  items: string[]
  icon: React.ComponentType<{ className?: string }>
  color: string
  bgColor: string
}) {
  return (
    <Card className={cn('border-l-4', color.replace('text-', 'border-'))}>
      <div className="flex items-center gap-2 mb-4">
        <div className={cn('w-8 h-8 rounded-lg flex items-center justify-center', bgColor)}>
          <Icon className={cn('h-4 w-4', color)} />
        </div>
        <h3 className="font-medium text-content-primary">{title}</h3>
      </div>

      {items.length > 0 ? (
        <ul className="space-y-2">
          {items.map((item, i) => (
            <li key={i} className="flex items-start gap-2 text-sm text-content-secondary">
              <span className={cn('mt-1.5 w-1.5 h-1.5 rounded-full flex-shrink-0', bgColor.replace('/10', ''))} />
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
    <div className="space-y-6">
      {/* 第一行：评分 + 标题信息 */}
      <div className="grid md:grid-cols-2 gap-6">
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
              <div>
                <div className="text-xs text-content-muted mb-1">主标题</div>
                <div className="text-lg font-medium text-content-primary">{landing.headline_text}</div>
              </div>
            )}
            {landing.tagline_text && (
              <div>
                <div className="text-xs text-content-muted mb-1">副标题/标语</div>
                <div className="text-content-secondary">{landing.tagline_text}</div>
              </div>
            )}
            {!landing.headline_text && !landing.tagline_text && (
              <div className="text-content-muted text-sm">暂无标题信息</div>
            )}
          </div>
        </Card>
      </div>

      {/* 第二行：目标用户 + 使用场景 */}
      <div className="grid md:grid-cols-2 gap-6">
        <Card>
          <CardHeader title="目标用户" subtitle="用户群体分析" />
          <div className="space-y-4">
            {landing.target_audience && landing.target_audience.length > 0 && (
              <div>
                <div className="text-xs text-content-muted mb-2">用户群体</div>
                <div className="flex flex-wrap gap-2">
                  {landing.target_audience.map((item, i) => (
                    <Badge key={i} variant="info" size="sm">{item}</Badge>
                  ))}
                </div>
              </div>
            )}
            {landing.target_roles && landing.target_roles.length > 0 && (
              <div>
                <div className="text-xs text-content-muted mb-2">目标角色</div>
                <div className="flex flex-wrap gap-2">
                  {landing.target_roles.map((item, i) => (
                    <Badge key={i} variant="muted" size="sm">{item}</Badge>
                  ))}
                </div>
              </div>
            )}
            {(!landing.target_audience || landing.target_audience.length === 0) &&
             (!landing.target_roles || landing.target_roles.length === 0) && (
              <div className="text-content-muted text-sm">暂无用户分析数据</div>
            )}
          </div>
        </Card>

        <Card>
          <CardHeader title="使用场景" subtitle="产品应用场景" />
          {landing.use_cases && landing.use_cases.length > 0 ? (
            <ul className="space-y-2">
              {landing.use_cases.map((item, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-content-secondary">
                  <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-accent-primary flex-shrink-0" />
                  {item}
                </li>
              ))}
            </ul>
          ) : (
            <div className="text-content-muted text-sm">暂无使用场景数据</div>
          )}
        </Card>
      </div>

      {/* 第三行：核心功能 + 价值主张 */}
      <div className="grid md:grid-cols-2 gap-6">
        <Card>
          <CardHeader
            title="核心功能"
            subtitle={landing.feature_count ? `共 ${landing.feature_count} 个功能` : undefined}
          />
          {landing.core_features && landing.core_features.length > 0 ? (
            <ul className="space-y-2">
              {landing.core_features.map((item, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-content-secondary">
                  <Check className="mt-0.5 h-3 w-3 text-accent-success flex-shrink-0" />
                  {item}
                </li>
              ))}
            </ul>
          ) : (
            <div className="text-content-muted text-sm">暂无功能列表</div>
          )}
        </Card>

        <Card>
          <CardHeader title="价值主张" subtitle="产品核心价值" />
          {landing.value_propositions && landing.value_propositions.length > 0 ? (
            <ul className="space-y-2">
              {landing.value_propositions.map((item, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-content-secondary">
                  <Lightbulb className="mt-0.5 h-3 w-3 text-accent-warning flex-shrink-0" />
                  {item}
                </li>
              ))}
            </ul>
          ) : (
            <div className="text-content-muted text-sm">暂无价值主张数据</div>
          )}
        </Card>
      </div>

      {/* 第四行：痛点分析 + 潜在护城河 */}
      <div className="grid md:grid-cols-2 gap-6">
        <Card>
          <CardHeader title="痛点分析" subtitle="解决的用户痛点" />
          <div className="space-y-4">
            {landing.pain_points && landing.pain_points.length > 0 ? (
              <ul className="space-y-2">
                {landing.pain_points.map((item, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-content-secondary">
                    <AlertTriangle className="mt-0.5 h-3 w-3 text-accent-danger flex-shrink-0" />
                    {item}
                  </li>
                ))}
              </ul>
            ) : (
              <div className="text-content-muted text-sm">暂无痛点数据</div>
            )}

            {/* 痛点表达技巧 */}
            <div className="flex gap-3 pt-3 border-t border-surface-border/50">
              <div className={cn(
                'flex items-center gap-1.5 px-2 py-1 rounded text-xs',
                landing.uses_before_after ? 'bg-accent-success/10 text-accent-success' : 'bg-background-tertiary text-content-muted'
              )}>
                {landing.uses_before_after ? <Check className="h-3 w-3" /> : <X className="h-3 w-3" />}
                新旧对比
              </div>
              <div className={cn(
                'flex items-center gap-1.5 px-2 py-1 rounded text-xs',
                landing.uses_emotional_words ? 'bg-accent-success/10 text-accent-success' : 'bg-background-tertiary text-content-muted'
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
            <ul className="space-y-2">
              {landing.potential_moats.map((item, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-content-secondary">
                  <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-accent-secondary flex-shrink-0" />
                  {item}
                </li>
              ))}
            </ul>
          ) : (
            <div className="text-content-muted text-sm">暂无护城河分析</div>
          )}
        </Card>
      </div>

      {/* 第五行：定价信息 + 转化分析 */}
      <div className="grid md:grid-cols-2 gap-6">
        <Card>
          <CardHeader title="定价信息" subtitle="价格策略分析" />
          <div className="space-y-4">
            <div className="flex items-center gap-4">
              {landing.pricing_model && (
                <div>
                  <div className="text-xs text-content-muted mb-1">定价模式</div>
                  <Badge variant="info">{landing.pricing_model}</Badge>
                </div>
              )}
              <div className="flex gap-2">
                {landing.has_free_tier && (
                  <Badge variant="success" size="sm">免费版</Badge>
                )}
                {landing.has_trial && (
                  <Badge variant="success" size="sm">试用期</Badge>
                )}
              </div>
            </div>

            {landing.pricing_tiers && landing.pricing_tiers.length > 0 && (
              <div>
                <div className="text-xs text-content-muted mb-2">定价层级</div>
                <div className="space-y-2">
                  {landing.pricing_tiers.map((tier: any, i: number) => (
                    <div key={i} className="p-2 rounded bg-background-secondary/50 text-sm">
                      <span className="font-medium text-content-primary">{tier.name || `方案${i+1}`}</span>
                      {tier.price && <span className="ml-2 text-accent-primary">{tier.price}</span>}
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
            <div className="grid grid-cols-2 gap-4">
              <div className="p-3 rounded-lg bg-background-secondary/50">
                <div className="text-2xl font-bold text-content-primary">{landing.cta_count || 0}</div>
                <div className="text-xs text-content-muted">CTA按钮数</div>
              </div>
              <div className="p-3 rounded-lg bg-background-secondary/50">
                <div className="text-2xl font-bold text-content-primary">{landing.conversion_funnel_steps || 0}</div>
                <div className="text-xs text-content-muted">转化步骤</div>
              </div>
            </div>

            {landing.cta_texts && landing.cta_texts.length > 0 && (
              <div>
                <div className="text-xs text-content-muted mb-2">CTA 文案</div>
                <div className="flex flex-wrap gap-2">
                  {landing.cta_texts.map((text, i) => (
                    <Badge key={i} variant="muted" size="sm">{text}</Badge>
                  ))}
                </div>
              </div>
            )}

            <div className={cn(
              'flex items-center gap-2 p-2 rounded text-sm',
              landing.has_instant_value_demo ? 'bg-accent-success/10 text-accent-success' : 'bg-background-tertiary text-content-muted'
            )}>
              {landing.has_instant_value_demo ? <Check className="h-3.5 w-3.5" /> : <X className="h-3.5 w-3.5" />}
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
      'inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm',
      available
        ? 'bg-accent-success/10 text-accent-success'
        : 'bg-background-tertiary text-content-muted'
    )}>
      {available ? <Check className="h-3 w-3" /> : <X className="h-3 w-3" />}
      {label}
    </span>
  )
}
