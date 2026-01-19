'use client'

import { useLocale } from '@/contexts/LocaleContext'
import { Card } from '@/components/ui/Card'
import { Users, ArrowRight, ExternalLink, Package, Loader2 } from 'lucide-react'
import Link from 'next/link'
import { useState, useEffect } from 'react'
import type { Creator } from '@/types/discover'
import { getCreators } from '@/lib/api/discover'

export function CreatorUniverse() {
  const { t, locale } = useLocale()
  const [creators, setCreators] = useState<Creator[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const isEn = locale === 'en'

  useEffect(() => {
    async function fetchCreators() {
      try {
        setLoading(true)
        const data = await getCreators({ limit: 4, useFeatured: true })
        setCreators(data.creators)
      } catch (err) {
        setError(isEn ? 'Failed to load' : '加载失败')
        console.error('Failed to fetch creators:', err)
      } finally {
        setLoading(false)
      }
    }
    fetchCreators()
  }, [isEn])

  const getBio = (c: Creator) => isEn ? (c.bio_en || c.bio) : (c.bio_zh || c.bio)
  const getTag = (c: Creator) => isEn ? (c.tag_en || c.tag) : (c.tag_zh || c.tag)

  if (loading) {
    return (
      <section>
        <div className="flex items-center justify-center py-16">
          <Loader2 className="h-6 w-6 animate-spin text-content-muted" />
        </div>
      </section>
    )
  }

  if (error || creators.length === 0) {
    return null
  }

  return (
    <section>
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-500 flex items-center justify-center shadow-lg shadow-cyan-500/20">
            <Users className="h-5 w-5 text-white" />
          </div>
          <div>
            <h2 className="text-lg font-display font-bold text-content-primary tracking-tight">
              {t('discover.creatorUniverse.title')}
            </h2>
            <p className="text-xs text-content-muted">{t('discover.creatorUniverse.subtitle')}</p>
          </div>
        </div>
        <Link
          href="/leaderboard"
          className="text-sm text-brand-500 hover:text-brand-600 font-medium flex items-center gap-1 transition-colors"
        >
          {t('discover.todayCuration.viewAll')}
          <ArrowRight className="h-4 w-4" />
        </Link>
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {creators.map((creator) => (
          <Card key={creator.id} hover className="group">
            <div className="flex items-start gap-3 mb-3">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-surface to-background-tertiary flex items-center justify-center text-2xl shadow-sm border border-surface-border/50">
                {creator.avatar}
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="text-sm font-bold text-content-primary truncate group-hover:text-brand-600 dark:group-hover:text-brand-400 transition-colors">
                  {creator.name}
                </h3>
                <p className="text-xs text-content-muted truncate">{creator.handle}</p>
              </div>
            </div>

            {getTag(creator) && (
              <div className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-medium mb-2
                ${creator.tag_color === 'amber' ? 'bg-amber-500/10 text-amber-600 dark:text-amber-400' : ''}
                ${creator.tag_color === 'blue' ? 'bg-blue-500/10 text-blue-600 dark:text-blue-400' : ''}
                ${creator.tag_color === 'violet' ? 'bg-violet-500/10 text-violet-600 dark:text-violet-400' : ''}
                ${creator.tag_color === 'emerald' ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400' : ''}
              `}>
                {getTag(creator)}
              </div>
            )}

            {getBio(creator) && (
              <p className="text-xs text-content-tertiary mb-3 line-clamp-2">
                {getBio(creator)}
              </p>
            )}

            <div className="space-y-1.5 mb-3">
              {creator.products.slice(0, 2).map((product, idx) => (
                <div key={idx} className="flex items-center justify-between text-xs">
                  <span className="text-content-secondary truncate">{product.name}</span>
                  <span className="font-mono text-emerald-600 dark:text-emerald-400 font-medium">
                    {product.mrr}
                  </span>
                </div>
              ))}
              {creator.product_count > 2 && (
                <span className="text-[10px] text-content-muted">
                  +{creator.product_count - 2} more
                </span>
              )}
            </div>

            <div className="flex items-center justify-between pt-3 border-t border-surface-border/50">
              <div className="flex items-center gap-1 text-xs">
                <Package className="h-3 w-3 text-content-muted" />
                <span className="text-content-secondary">{creator.product_count}</span>
                <span className="text-content-muted">{t('discover.creatorUniverse.products')}</span>
              </div>
              <div className="text-xs font-mono font-medium text-brand-600 dark:text-brand-400">
                {creator.total_mrr}
              </div>
            </div>

            <Link
              href={`/leaderboard?creator=${creator.id}`}
              className="flex items-center justify-center gap-1.5 w-full mt-3 py-2 rounded-lg bg-surface border border-surface-border text-xs font-medium text-content-secondary hover:text-content-primary hover:border-brand-500/30 transition-colors"
            >
              {t('discover.creatorUniverse.viewProfile')}
              <ExternalLink className="h-3 w-3" />
            </Link>
          </Card>
        ))}
      </div>
    </section>
  )
}
