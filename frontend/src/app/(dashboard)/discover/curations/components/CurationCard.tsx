'use client'

import { useLocale } from '@/contexts/LocaleContext'
import { Card } from '@/components/ui/Card'
import { Zap, TrendingUp, MessageCircle, Calendar } from 'lucide-react'
import Link from 'next/link'
import type { Curation } from '@/types/discover'

interface CurationCardProps {
  curation: Curation
  index: number
}

export function CurationCard({ curation, index }: CurationCardProps) {
  const { locale } = useLocale()
  const isEn = locale === 'en'

  const getTitle = (c: Curation) => isEn ? c.title_en : c.title_zh
  const getDesc = (c: Curation) => isEn ? c.description_en : c.description_zh
  const getTag = (c: Curation) => isEn ? c.tag_en : c.tag_zh
  const getInsight = (c: Curation) => isEn ? c.insight_en : c.insight_zh
  const getProductHighlight = (product: Curation['products'][number]) => {
    if (isEn) {
      return product.highlight_en || product.highlight_zh || null
    }
    return product.highlight_zh || product.highlight_en || null
  }

  const tagColorClasses: Record<string, string> = {
    amber: 'bg-amber-500/10 text-amber-600 dark:text-amber-400',
    emerald: 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400',
    violet: 'bg-violet-500/10 text-violet-600 dark:text-violet-400',
    blue: 'bg-blue-500/10 text-blue-600 dark:text-blue-400',
    rose: 'bg-rose-500/10 text-rose-600 dark:text-rose-400',
    slate: 'bg-slate-500/10 text-slate-600 dark:text-slate-400',
    purple: 'bg-purple-500/10 text-purple-600 dark:text-purple-400',
    orange: 'bg-orange-500/10 text-orange-600 dark:text-orange-400',
    teal: 'bg-teal-500/10 text-teal-600 dark:text-teal-400',
    green: 'bg-green-500/10 text-green-600 dark:text-green-400',
    gray: 'bg-gray-500/10 text-gray-600 dark:text-gray-400',
    yellow: 'bg-yellow-500/10 text-yellow-600 dark:text-yellow-400',
    indigo: 'bg-indigo-500/10 text-indigo-600 dark:text-indigo-400',
    cyan: 'bg-cyan-500/10 text-cyan-600 dark:text-cyan-400',
  }

  const buildChatMessage = (c: Curation) => {
    const title = getTitle(c)
    const productNames = c.products.map(p => p.name).filter(Boolean)
    const productList = productNames.length
      ? productNames.join(isEn ? ', ' : '、')
      : (isEn ? 'these products' : '这些产品')
    return isEn
      ? `I'm interested in the curation "${title}". It includes ${productList}. Can you analyze whether I could build something similar?`
      : `我对「${title}」这组策展很感兴趣，包含${productList}。帮我分析一下我能不能做类似的产品？`
  }
  const chatUrl = `/assistant?message=${encodeURIComponent(buildChatMessage(curation))}`

  // 格式化日期
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    if (isEn) {
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
    }
    return date.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
  }

  return (
    <Card 
      hover 
      className="group relative overflow-hidden cursor-pointer"
      style={{ animationDelay: `${Math.min(index * 50, 500)}ms` }}
    >
      <div className="relative">
        {/* 标签和日期 */}
        <div className="flex items-center justify-between mb-3">
          <div className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium
            ${tagColorClasses[curation.tag_color] || tagColorClasses.amber}
          `}>
            <Zap className="h-3 w-3" />
            {getTag(curation)}
          </div>
          
          {curation.curation_date && (
            <div className="flex items-center gap-1.5 text-xs text-content-muted">
              <Calendar className="h-3 w-3" />
              <span>{formatDate(curation.curation_date)}</span>
            </div>
          )}
        </div>

        {/* 标题 */}
        <h3 className="text-base font-bold text-content-primary mb-2 group-hover:text-brand-600 dark:group-hover:text-brand-400 transition-colors duration-200 line-clamp-2 leading-snug">
          {getTitle(curation)}
        </h3>

        {/* 描述 */}
        <p className="text-sm text-content-tertiary mb-4 line-clamp-2 leading-relaxed">
          {getDesc(curation)}
        </p>

        {/* 产品列表 */}
        <div className="space-y-2 mb-4">
          {curation.products.map((product, idx) => (
            <Link
              key={idx}
              href={product.slug ? `/products/${product.slug}` : '#'}
              className="flex items-center justify-between p-2.5 rounded-lg bg-surface/50 border border-surface-border/50 hover:bg-surface active:bg-surface-hover hover:border-brand-500/30 active:border-brand-500/50 transition-colors duration-200 group/product cursor-pointer"
            >
              <div className="flex items-center gap-2.5 min-w-0">
                {product.logo && product.logo.startsWith('http') ? (
                  <img 
                    src={product.logo} 
                    alt={`${product.name} logo`}
                    className="w-6 h-6 rounded object-cover flex-shrink-0" 
                  />
                ) : (
                  <div className="w-6 h-6 rounded bg-brand-500/10 border border-brand-500/20 flex items-center justify-center group-hover/product:bg-brand-500/20 transition-colors flex-shrink-0">
                    <span className="text-xs font-bold text-brand-600 dark:text-brand-400">
                      {product.name?.charAt(0)?.toUpperCase() || 'P'}
                    </span>
                  </div>
                )}
                <div className="min-w-0">
                  <span className="text-sm font-medium text-content-primary group-hover/product:text-brand-600 dark:group-hover/product:text-brand-400 transition-colors block truncate">
                    {product.name}
                  </span>
                  {getProductHighlight(product) && (
                    <span className="text-xs text-content-muted block truncate">
                      {getProductHighlight(product)}
                    </span>
                  )}
                </div>
              </div>
              {product.mrr && (
                <span className="text-sm font-mono text-emerald-600 dark:text-emerald-400 font-medium flex-shrink-0 ml-2">
                  {product.mrr}
                </span>
              )}
            </Link>
          ))}
        </div>

        {/* 洞察 */}
        <div className="flex items-center gap-2 p-3 rounded-lg bg-brand-500/5 border border-brand-500/10 mb-4">
          <TrendingUp className="h-4 w-4 text-brand-500 flex-shrink-0" />
          <span className="text-sm text-brand-600 dark:text-brand-400 font-medium">
            {getInsight(curation)}
          </span>
        </div>

        {/* CTA 按钮 */}
        <Link
          href={chatUrl}
          className="flex items-center justify-center gap-2 w-full py-2.5 rounded-xl bg-gradient-to-r from-amber-500/10 to-orange-500/10 text-amber-600 dark:text-amber-400 text-sm font-medium hover:from-amber-500/20 hover:to-orange-500/20 active:from-amber-500/30 active:to-orange-500/30 transition-all duration-200 cursor-pointer"
        >
          <MessageCircle className="h-4 w-4" />
          {isEn ? 'Can I copy this?' : '我能做类似的吗？'}
        </Link>
      </div>
    </Card>
  )
}
