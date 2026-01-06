'use client'

import { useState } from 'react'
import { Info, ChevronDown, ChevronUp, ExternalLink, Database } from 'lucide-react'
import { useLocale } from '@/contexts/LocaleContext'
import { cn } from '@/lib/utils'
import type { DataInfo } from '@/types'

interface DataDisclaimerProps {
  dataInfo?: DataInfo
  variant?: 'full' | 'compact' | 'inline'
  className?: string
}

export function DataDisclaimer({
  dataInfo,
  variant = 'full',
  className = '',
}: DataDisclaimerProps) {
  const { locale } = useLocale()
  const [isExpanded, setIsExpanded] = useState(false)

  const isZh = locale === 'zh-CN'

  // 默认数据信息
  const defaultInfo: DataInfo = {
    data_source: 'TrustMRR',
    data_source_url: 'https://trustmrr.com',
    total_products: 500,
    total_categories: 45,
    total_countries: 30,
    products_with_revenue: 450,
    analyzed_products: 400,
    last_crawl_time: null,
    last_analysis_time: null,
    coverage_note: '仅包含愿意公开收入数据的产品，非市场全貌',
    coverage_note_en: 'Only includes products willing to disclose revenue data, not a complete market picture',
    limitations: [
      '数据来源单一，仅来自TrustMRR平台',
      '样本量有限，部分赛道数据较少',
      '收入数据为自报告，可能存在偏差',
      '部分产品缺少粉丝数据，IP依赖度为估算值',
    ],
    limitations_en: [
      'Single data source from TrustMRR platform',
      'Limited sample size, some categories have sparse data',
      'Revenue data is self-reported, may have bias',
      'Some products lack follower data, IP dependency is estimated',
    ],
  }

  const info = dataInfo || defaultInfo

  // 内联版本 - 简短提示
  if (variant === 'inline') {
    return (
      <div className={cn('flex items-center gap-1.5 text-xs text-content-muted', className)}>
        <Info className="w-3 h-3" />
        <span>
          {isZh ? info.coverage_note : info.coverage_note_en}
        </span>
      </div>
    )
  }

  // 紧凑版本 - 可折叠
  if (variant === 'compact') {
    return (
      <div className={cn(
        'rounded-xl border border-surface-border/50 bg-surface/80 backdrop-blur-sm overflow-hidden',
        className
      )}>
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-surface-hover/50 transition-colors"
        >
          <div className="flex items-center gap-2">
            <Info className="w-4 h-4 text-brand-500" />
            <span className="text-sm font-medium text-content-primary">
              {isZh ? '数据说明' : 'Data Info'}
            </span>
          </div>
          {isExpanded ? (
            <ChevronUp className="w-4 h-4 text-content-muted" />
          ) : (
            <ChevronDown className="w-4 h-4 text-content-muted" />
          )}
        </button>

        {isExpanded && (
          <div className="px-4 pb-4 space-y-3 border-t border-surface-border/40">
            <p className="text-xs text-content-secondary pt-3">
              {isZh ? info.coverage_note : info.coverage_note_en}
            </p>
            <div className="flex items-center gap-4 text-xs text-content-muted">
              <span className="flex items-center gap-1">
                <Database className="w-3 h-3" />
                {isZh ? '产品数' : 'Products'}: {info.total_products}+
              </span>
              <span>{isZh ? '赛道数' : 'Categories'}: {info.total_categories}</span>
            </div>
          </div>
        )}
      </div>
    )
  }

  // 完整版本
  return (
    <div className={cn(
      'rounded-2xl border border-surface-border/50 bg-surface/80 backdrop-blur-sm p-5',
      className
    )}>
      {/* 标题 */}
      <div className="flex items-center gap-2 mb-4">
        <Info className="w-5 h-5 text-brand-500" />
        <h3 className="text-sm font-semibold text-content-primary">
          {isZh ? '数据说明' : 'Data Information'}
        </h3>
      </div>

      {/* 数据来源 */}
      <div className="mb-5">
        <div className="flex items-center gap-2 mb-1.5">
          <span className="text-xs text-content-muted">
            {isZh ? '数据来源' : 'Data Source'}:
          </span>
          <a
            href={info.data_source_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs text-brand-500 hover:text-brand-600 font-medium flex items-center gap-1 transition-colors"
          >
            {info.data_source}
            <ExternalLink className="w-3 h-3" />
          </a>
        </div>
        <p className="text-xs text-content-secondary leading-relaxed">
          {isZh ? info.coverage_note : info.coverage_note_en}
        </p>
      </div>

      {/* 统计数据 */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-5">
        <div className="bg-surface-hover/50 rounded-xl p-3 text-center">
          <div className="text-lg font-bold text-content-primary tabular-nums">
            {info.total_products}+
          </div>
          <div className="text-xs text-content-muted font-medium">
            {isZh ? '产品数' : 'Products'}
          </div>
        </div>
        <div className="bg-surface-hover/50 rounded-xl p-3 text-center">
          <div className="text-lg font-bold text-content-primary tabular-nums">
            {info.total_categories}
          </div>
          <div className="text-xs text-content-muted font-medium">
            {isZh ? '赛道数' : 'Categories'}
          </div>
        </div>
        <div className="bg-surface-hover/50 rounded-xl p-3 text-center">
          <div className="text-lg font-bold text-content-primary tabular-nums">
            {info.products_with_revenue}
          </div>
          <div className="text-xs text-content-muted font-medium">
            {isZh ? '有收入数据' : 'With Revenue'}
          </div>
        </div>
        <div className="bg-surface-hover/50 rounded-xl p-3 text-center">
          <div className="text-lg font-bold text-content-primary tabular-nums">
            {info.analyzed_products}
          </div>
          <div className="text-xs text-content-muted font-medium">
            {isZh ? '已分析' : 'Analyzed'}
          </div>
        </div>
      </div>

      {/* 局限性说明 */}
      <div className="p-3 rounded-xl bg-amber-500/5 dark:bg-amber-500/10 border border-amber-500/20">
        <h4 className="text-xs font-semibold text-amber-600 dark:text-amber-400 mb-2">
          {isZh ? '数据局限性' : 'Limitations'}
        </h4>
        <ul className="space-y-1.5">
          {(isZh ? info.limitations : info.limitations_en).map((item, index) => (
            <li key={index} className="flex items-start gap-2 text-xs text-content-secondary">
              <span className="text-amber-500 mt-0.5">•</span>
              <span>{item}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* 更新时间 */}
      {(info.last_crawl_time || info.last_analysis_time) && (
        <div className="mt-4 pt-4 border-t border-surface-border/40 flex items-center gap-4 text-xs text-content-muted">
          {info.last_crawl_time && (
            <span>
              {isZh ? '数据更新' : 'Data Updated'}: {new Date(info.last_crawl_time).toLocaleDateString()}
            </span>
          )}
          {info.last_analysis_time && (
            <span>
              {isZh ? '分析更新' : 'Analysis Updated'}: {new Date(info.last_analysis_time).toLocaleDateString()}
            </span>
          )}
        </div>
      )}
    </div>
  )
}

export default DataDisclaimer
