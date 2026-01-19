'use client'

import { useLocale } from '@/contexts/LocaleContext'
import { Card } from '@/components/ui/Card'
import { ArrowRight, MessageCircle, TrendingUp, Zap, Sparkles } from 'lucide-react'
import Link from 'next/link'
import { useState, useEffect } from 'react'
import type { Curation } from '@/types/discover'
import { getCurations } from '@/lib/api/discover'
import { CurationCardSkeleton } from '@/components/ui/Loading'

// Mock data for fallback
const mockCurations: Curation[] = [
  {
    id: 1,
    title: '3 个独立开发者，靠一个很无聊的需求赚到了钱',
    title_zh: '3 个独立开发者，靠一个很无聊的需求赚到了钱',
    title_en: '3 indie devs making money from boring problems',
    description: '这些产品解决的问题看起来毫无新意，但每个月都在稳定赚钱。',
    description_zh: '这些产品解决的问题看起来毫无新意，但每个月都在稳定赚钱。',
    description_en: 'These products solve boring problems but make steady money.',
    tag: '被低估的赚钱机器',
    tag_zh: '被低估的赚钱机器',
    tag_en: 'Underrated Money Makers',
    tag_color: 'amber',
    insight: '无聊的需求 = 稳定的需求',
    insight_zh: '无聊的需求 = 稳定的需求',
    insight_en: 'Boring needs = Stable needs',
    curation_type: 'contrast',
    curation_date: new Date().toISOString().split('T')[0],
    products: [
      { name: 'PDF Tool Pro', mrr: '$8.2k', logo: '📄' },
      { name: 'Invoice Simple', mrr: '$12.5k', logo: '🧾' },
      { name: 'Screenshot API', mrr: '$6.8k', logo: '📸' },
    ],
  },
  {
    id: 2,
    title: '这些 SaaS 没有官网设计感，但 MRR 都超过 $10k',
    title_zh: '这些 SaaS 没有官网设计感，但 MRR 都超过 $10k',
    title_en: 'These SaaS have ugly websites but $10k+ MRR',
    description: '设计不是成功的必要条件。这些产品证明了：解决真实问题比好看更重要。',
    description_zh: '设计不是成功的必要条件。这些产品证明了：解决真实问题比好看更重要。',
    description_en: 'Design is not required for success. Solving real problems matters more.',
    tag: '产品 > 设计',
    tag_zh: '产品 > 设计',
    tag_en: 'Product > Design',
    tag_color: 'emerald',
    insight: '功能价值 > 视觉价值',
    insight_zh: '功能价值 > 视觉价值',
    insight_en: 'Functional value > Visual value',
    curation_type: 'cognitive',
    curation_date: new Date().toISOString().split('T')[0],
    products: [
      { name: 'DataBackup.io', mrr: '$15.3k', logo: '💾' },
      { name: 'FormBuilder', mrr: '$11.2k', logo: '📝' },
      { name: 'CronJob Monitor', mrr: '$9.7k', logo: '⏰' },
    ],
  },
]

export function TodayCuration() {
  const { t, locale } = useLocale()
  const [curations, setCurations] = useState<Curation[]>([])
  const [loading, setLoading] = useState(true)

  const isEn = locale === 'en'

  useEffect(() => {
    async function fetchCurations() {
      try {
        setLoading(true)
        const data = await getCurations({ limit: 2, days: 7 })
        if (data.curations.length > 0) {
          setCurations(data.curations)
        } else {
          setCurations(mockCurations)
        }
      } catch (err) {
        console.error('Failed to fetch curations:', err)
        setCurations(mockCurations)
      } finally {
        setLoading(false)
      }
    }
    fetchCurations()
  }, [])

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

  if (loading) {
    return (
      <section>
        <div className="flex items-center justify-between mb-5">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-brand-500 to-violet-500 flex items-center justify-center shadow-lg shadow-brand-500/20">
              <Sparkles className="h-5 w-5 text-white" />
            </div>
            <div>
              <h2 className="text-lg font-display font-bold text-content-primary tracking-tight">
                {t('discover.todayCuration.title')}
              </h2>
              <p className="text-xs text-content-muted">{t('discover.todayCuration.subtitle')}</p>
            </div>
          </div>
          <Link
            href="/discover/curations"
            className="text-sm text-brand-500 hover:text-brand-600 font-medium flex items-center gap-1 transition-colors cursor-pointer"
          >
            {t('discover.todayCuration.viewAll')}
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
        <div className="grid md:grid-cols-2 gap-5">
          <CurationCardSkeleton />
          <CurationCardSkeleton />
        </div>
      </section>
    )
  }

  return (
    <section>
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-brand-500 to-violet-500 flex items-center justify-center shadow-lg shadow-brand-500/20">
            <Sparkles className="h-5 w-5 text-white" />
          </div>
          <div>
            <h2 className="text-lg font-display font-bold text-content-primary tracking-tight">
              {t('discover.todayCuration.title')}
            </h2>
            <p className="text-xs text-content-muted">{t('discover.todayCuration.subtitle')}</p>
          </div>
        </div>
        <Link
          href="/discover/curations"
          className="text-sm text-brand-500 hover:text-brand-600 font-medium flex items-center gap-1 transition-colors cursor-pointer"
        >
          {t('discover.todayCuration.viewAll')}
          <ArrowRight className="h-4 w-4" />
        </Link>
      </div>

      <div className="grid md:grid-cols-2 gap-5">
        {curations.map((curation) => (
          <Card key={curation.id} hover className="group relative overflow-hidden cursor-pointer">
            <div className="relative">
              <div className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium mb-3
                ${tagColorClasses[curation.tag_color] || tagColorClasses.amber}
              `}>
                <Zap className="h-3 w-3" />
                {getTag(curation)}
              </div>

              <h3 className="text-base font-bold text-content-primary mb-2 group-hover:text-brand-600 dark:group-hover:text-brand-400 transition-colors duration-200 line-clamp-2">
                {getTitle(curation)}
              </h3>

              <p className="text-sm text-content-tertiary mb-4 line-clamp-2">
                {getDesc(curation)}
              </p>

              <div className="space-y-2 mb-4">
                {curation.products.map((product, idx) => (
                  <Link
                    key={idx}
                    href={product.slug ? `/products/${product.slug}` : '#'}
                    className="flex items-center justify-between p-2.5 rounded-lg bg-surface/50 border border-surface-border/50 hover:bg-surface active:bg-surface-hover hover:border-brand-500/30 active:border-brand-500/50 transition-colors duration-200 group/product cursor-pointer"
                  >
                    <div className="flex items-center gap-2.5 min-w-0">
                      {product.logo && product.logo.startsWith('http') ? (
                        <img src={product.logo} alt={`${product.name} logo`} className="w-6 h-6 rounded object-cover" />
                      ) : (
                        <div className="w-6 h-6 rounded bg-brand-500/10 border border-brand-500/20 flex items-center justify-center group-hover/product:bg-brand-500/20 transition-colors">
                          <span className="text-xs font-bold text-brand-600 dark:text-brand-400">
                            {product.name?.charAt(0)?.toUpperCase() || 'P'}
                          </span>
                        </div>
                      )}
                      <div className="min-w-0">
                        <span className="text-sm font-medium text-content-primary group-hover/product:text-brand-600 dark:group-hover/product:text-brand-400 transition-colors block truncate">{product.name}</span>
                        {getProductHighlight(product) && (
                          <span className="text-xs text-content-muted block truncate">
                            {getProductHighlight(product)}
                          </span>
                        )}
                      </div>
                    </div>
                    <span className="text-sm font-mono text-emerald-600 dark:text-emerald-400 font-medium">
                      {product.mrr}
                    </span>
                  </Link>
                ))}
              </div>

              <div className="flex items-center gap-2 p-3 rounded-lg bg-brand-500/5 border border-brand-500/10 mb-4">
                <TrendingUp className="h-4 w-4 text-brand-500 flex-shrink-0" />
                <span className="text-sm text-brand-600 dark:text-brand-400 font-medium">
                  {getInsight(curation)}
                </span>
              </div>

              <Link
                href={`/assistant?message=${encodeURIComponent(buildChatMessage(curation))}`}
                className="flex items-center justify-center gap-2 w-full py-2.5 rounded-xl bg-gradient-to-r from-amber-500/10 to-orange-500/10 text-amber-600 dark:text-amber-400 text-sm font-medium hover:from-amber-500/20 hover:to-orange-500/20 active:from-amber-500/30 active:to-orange-500/30 transition-all duration-200 cursor-pointer"
              >
                <MessageCircle className="h-4 w-4" />
                {t('discover.cta.canICopy')}
              </Link>
            </div>
          </Card>
        ))}
      </div>
    </section>
  )
}
