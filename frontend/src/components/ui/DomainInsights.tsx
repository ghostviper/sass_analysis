'use client'

import { CheckCircle, AlertTriangle, Info, Shield, Lightbulb } from 'lucide-react'
import { useLocale } from '@/contexts/LocaleContext'
import { cn } from '@/lib/utils'
import type { DomainInsight, SummaryPoint, RiskAssessment } from '@/types'

interface DomainInsightsProps {
  insights: DomainInsight[]
  summaryPoints?: SummaryPoint[]
  riskAssessment?: RiskAssessment
  className?: string
}

export function DomainInsights({
  insights,
  summaryPoints,
  riskAssessment,
  className = '',
}: DomainInsightsProps) {
  const { locale } = useLocale()
  const isZh = locale === 'zh-CN'

  const getInsightIcon = (type: string) => {
    switch (type) {
      case 'positive':
        return <CheckCircle className="w-4 h-4 text-emerald-500" />
      case 'warning':
        return <AlertTriangle className="w-4 h-4 text-amber-500" />
      case 'info':
      default:
        return <Info className="w-4 h-4 text-brand-500" />
    }
  }

  const getInsightBgColor = (type: string) => {
    switch (type) {
      case 'positive':
        return 'bg-emerald-500/5 border-emerald-500/20 dark:bg-emerald-500/10'
      case 'warning':
        return 'bg-amber-500/5 border-amber-500/20 dark:bg-amber-500/10'
      case 'info':
      default:
        return 'bg-brand-500/5 border-brand-500/20 dark:bg-brand-500/10'
    }
  }

  return (
    <div className={cn('space-y-5', className)}>
      {/* 风险评估卡片 */}
      {riskAssessment && (
        <div className="rounded-2xl border border-surface-border/50 bg-surface/80 backdrop-blur-sm p-5">
          <div className="flex items-center gap-2 mb-4">
            <Shield className="w-5 h-5 text-content-muted" />
            <h3 className="text-sm font-semibold text-content-primary">
              {isZh ? '风险评估' : 'Risk Assessment'}
            </h3>
          </div>

          <div className="flex items-center gap-5 mb-5">
            {/* 风险分数 */}
            <div className="flex-shrink-0">
              <div
                className={cn(
                  'w-16 h-16 rounded-2xl flex items-center justify-center text-xl font-bold shadow-sm',
                  riskAssessment.risk_level === 'low'
                    ? 'bg-emerald-500/15 text-emerald-600 dark:text-emerald-400'
                    : riskAssessment.risk_level === 'medium'
                    ? 'bg-amber-500/15 text-amber-600 dark:text-amber-400'
                    : 'bg-red-500/15 text-red-600 dark:text-red-400'
                )}
              >
                {riskAssessment.risk_score.toFixed(1)}
              </div>
            </div>

            {/* 风险标签和统计 */}
            <div className="flex-1">
              <div
                className={cn(
                  'inline-block px-2.5 py-1 rounded-lg text-xs font-semibold mb-2',
                  riskAssessment.risk_level === 'low'
                    ? 'bg-emerald-500/15 text-emerald-600 dark:text-emerald-400'
                    : riskAssessment.risk_level === 'medium'
                    ? 'bg-amber-500/15 text-amber-600 dark:text-amber-400'
                    : 'bg-red-500/15 text-red-600 dark:text-red-400'
                )}
              >
                {riskAssessment.risk_label}
              </div>
              <div className="flex items-center gap-4 text-xs text-content-muted">
                <span className="flex items-center gap-1.5">
                  <CheckCircle className="w-3.5 h-3.5 text-emerald-500" />
                  {riskAssessment.positive_count} {isZh ? '优势' : 'advantages'}
                </span>
                <span className="flex items-center gap-1.5">
                  <AlertTriangle className="w-3.5 h-3.5 text-amber-500" />
                  {riskAssessment.warning_count} {isZh ? '风险' : 'risks'}
                </span>
              </div>
            </div>
          </div>

          {/* 关键优势和风险 */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {riskAssessment.key_advantages.length > 0 && (
              <div className="p-3 rounded-xl bg-emerald-500/5 dark:bg-emerald-500/10">
                <h4 className="text-xs font-semibold text-emerald-600 dark:text-emerald-400 mb-2">
                  {isZh ? '关键优势' : 'Key Advantages'}
                </h4>
                <ul className="space-y-1.5">
                  {riskAssessment.key_advantages.map((item, index) => (
                    <li key={index} className="flex items-start gap-2 text-xs text-content-secondary">
                      <CheckCircle className="w-3.5 h-3.5 text-emerald-500 flex-shrink-0 mt-0.5" />
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {riskAssessment.key_risks.length > 0 && (
              <div className="p-3 rounded-xl bg-amber-500/5 dark:bg-amber-500/10">
                <h4 className="text-xs font-semibold text-amber-600 dark:text-amber-400 mb-2">
                  {isZh ? '关键风险' : 'Key Risks'}
                </h4>
                <ul className="space-y-1.5">
                  {riskAssessment.key_risks.map((item, index) => (
                    <li key={index} className="flex items-start gap-2 text-xs text-content-secondary">
                      <AlertTriangle className="w-3.5 h-3.5 text-amber-500 flex-shrink-0 mt-0.5" />
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}

      {/* 摘要要点 */}
      {summaryPoints && summaryPoints.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {summaryPoints.map((point, index) => (
            <span
              key={index}
              className={cn(
                'inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium',
                point.type === 'positive'
                  ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400'
                  : point.type === 'warning'
                  ? 'bg-amber-500/10 text-amber-600 dark:text-amber-400'
                  : 'bg-brand-500/10 text-brand-600 dark:text-brand-400'
              )}
            >
              {getInsightIcon(point.type)}
              {point.text}
            </span>
          ))}
        </div>
      )}

      {/* 详细洞察列表 */}
      {insights.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <Lightbulb className="w-4 h-4 text-content-muted" />
            <h3 className="text-sm font-semibold text-content-primary">
              {isZh ? '确定性洞察' : 'Domain Insights'}
            </h3>
          </div>
          <div className="space-y-2">
            {insights.map((insight, index) => (
              <div
                key={index}
                className={cn(
                  'rounded-xl border p-4 transition-all duration-200 hover:shadow-sm',
                  getInsightBgColor(insight.type)
                )}
              >
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 mt-0.5">
                    {getInsightIcon(insight.type)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <h4 className="text-sm font-medium text-content-primary">
                        {insight.title}
                      </h4>
                      {insight.confidence === 'high' && (
                        <span className="px-1.5 py-0.5 text-[10px] font-medium bg-surface-hover text-content-muted rounded">
                          {isZh ? '高置信度' : 'High Confidence'}
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-content-secondary leading-relaxed mb-1.5">
                      {insight.description}
                    </p>
                    <span className="text-[10px] text-content-muted">
                      {isZh ? '来源' : 'Source'}: {insight.source}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

// 紧凑版洞察展示
export function CompactInsights({
  insights,
  maxItems = 3,
  className = '',
}: {
  insights: DomainInsight[]
  maxItems?: number
  className?: string
}) {
  const { locale } = useLocale()
  const isZh = locale === 'zh-CN'

  const displayInsights = insights.slice(0, maxItems)
  const remainingCount = insights.length - maxItems

  const getIcon = (type: string) => {
    switch (type) {
      case 'positive':
        return <CheckCircle className="w-3.5 h-3.5 text-emerald-500" />
      case 'warning':
        return <AlertTriangle className="w-3.5 h-3.5 text-amber-500" />
      default:
        return <Info className="w-3.5 h-3.5 text-brand-500" />
    }
  }

  return (
    <div className={cn('space-y-1.5', className)}>
      {displayInsights.map((insight, index) => (
        <div key={index} className="flex items-center gap-2 text-xs">
          {getIcon(insight.type)}
          <span className="text-content-secondary truncate">{insight.title}</span>
        </div>
      ))}
      {remainingCount > 0 && (
        <span className="text-xs text-content-muted font-medium">
          +{remainingCount} {isZh ? '更多洞察' : 'more insights'}
        </span>
      )}
    </div>
  )
}

export default DomainInsights
