'use client'

import { useLocale } from '@/contexts/LocaleContext'
import { Card } from '@/components/ui/Card'
import { Sparkles, ArrowRight, MessageCircle, TrendingUp, Zap, Loader2 } from 'lucide-react'
import Link from 'next/link'
import { useState, useEffect } from 'react'
import type { Curation } from '@/types/discover'
import { getCurations } from '@/lib/api/discover'

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
  const [useMock, setUseMock] = useState(false)

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
          setUseMock(true)
        }
      } catch (err) {
        console.error('Failed to fetch curations:', err)
        setCurations(mockCurations)
        setUseMock(true)
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

  if (loading) {
    return (
      <section>
        <div className="flex items-center justify-center py-16">
          <Loader2 className="h-6 w-6 animate-spin text-content-muted" />
        </div>
      </section>
    )
  }

  return (
    <section>
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center shadow-lg shadow-violet-500/20">
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
          href="/discover#curations"
          className="text-sm text-brand-500 hover:text-brand-600 font-medium flex items-center gap-1 transition-colors"
        >
          {t('discover.todayCuration.viewAll')}
          <ArrowRight className="h-4 w-4" />
        </Link>
      </div>

      <div className="grid md:grid-cols-2 gap-5">
        {curations.map((curation) => (
          <Card key={curation.id} hover className="group relative overflow-hidden">
            <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-bl from-violet-500/5 to-transparent rounded-full -translate-y-1/2 translate-x-1/2" />
            
            <div className="relative">
              <div className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium mb-3
                ${curation.tag_color === 'amber' ? 'bg-amber-500/10 text-amber-600 dark:text-amber-400' : ''}
                ${curation.tag_color === 'emerald' ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400' : ''}
                ${curation.tag_color === 'violet' ? 'bg-violet-500/10 text-violet-600 dark:text-violet-400' : ''}
              `}>
                <Zap className="h-3 w-3" />
                {getTag(curation)}
              </div>

              <h3 className="text-base font-bold text-content-primary mb-2 group-hover:text-brand-600 dark:group-hover:text-brand-400 transition-colors line-clamp-2">
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
                    className="flex items-center justify-between p-2.5 rounded-lg bg-surface/50 border border-surface-border/50 hover:bg-surface hover:border-brand-500/30 transition-all group"
                  >
                    <div className="flex items-center gap-2.5">
                      {product.logo && product.logo.startsWith('http') ? (
                        <img src={product.logo} alt={product.name} className="w-6 h-6 rounded object-cover" />
                      ) : (
                        <div className="w-6 h-6 rounded bg-gradient-to-br from-brand-500/20 to-violet-500/20 flex items-center justify-center group-hover:from-brand-500/30 group-hover:to-violet-500/30 transition-colors">
                          <span className="text-xs font-bold text-brand-600 dark:text-brand-400">
                            {product.name?.charAt(0)?.toUpperCase() || 'P'}
                          </span>
                        </div>
                      )}
                      <span className="text-sm font-medium text-content-primary group-hover:text-brand-600 dark:group-hover:text-brand-400 transition-colors">{product.name}</span>
                    </div>
                    <span className="text-sm font-mono text-emerald-600 dark:text-emerald-400 font-medium">
                      {product.mrr}
                    </span>
                  </Link>
                ))}
              </div>

              <div className="flex items-center gap-2 p-3 rounded-lg bg-violet-500/5 border border-violet-500/10 mb-4">
                <TrendingUp className="h-4 w-4 text-violet-500 flex-shrink-0" />
                <span className="text-sm text-violet-600 dark:text-violet-400 font-medium">
                  {getInsight(curation)}
                </span>
              </div>

              <Link
                href={`/assistant?products=${curation.products.map(p => p.name).join(',')}`}
                className="flex items-center justify-center gap-2 w-full py-2.5 rounded-xl bg-brand-500/10 text-brand-600 dark:text-brand-400 text-sm font-medium hover:bg-brand-500/20 transition-colors"
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
