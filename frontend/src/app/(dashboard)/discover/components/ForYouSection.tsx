'use client'

import { useLocale } from '@/contexts/LocaleContext'
import { Card } from '@/components/ui/Card'
import { Sparkles, ArrowRight, MessageCircle, Heart, Zap, Loader2, User } from 'lucide-react'
import Link from 'next/link'
import { useState, useEffect } from 'react'
import type { Recommendation } from '@/types/discover'
import { getRecommendations } from '@/lib/api/discover'
import { useAuth } from '@/hooks/useAuth'

export function ForYouSection() {
  const { t, locale } = useLocale()
  const { user, isAuthenticated } = useAuth()
  const [recommendations, setRecommendations] = useState<Recommendation[]>([])
  const [loading, setLoading] = useState(true)

  const isEn = locale === 'en'

  useEffect(() => {
    async function fetchRecommendations() {
      try {
        setLoading(true)
        const data = await getRecommendations({ limit: 3, userId: user?.id })
        setRecommendations(data.recommendations)
      } catch (err) {
        console.error('Failed to fetch recommendations:', err)
      } finally {
        setLoading(false)
      }
    }
    fetchRecommendations()
  }, [user?.id])

  const getDirection = (r: Recommendation) => isEn ? r.direction_en : r.direction_zh
  const getDesc = (r: Recommendation) => isEn ? r.description_en : r.description_zh
  const getWhyForYou = (r: Recommendation) => isEn ? r.why_for_you_en : r.why_for_you_zh

  const getDifficultyLabel = (d: string) => {
    const map: Record<string, { zh: string; en: string }> = {
      low: { zh: '低', en: 'Low' },
      medium: { zh: '中等', en: 'Medium' },
      high: { zh: '高', en: 'High' },
    }
    return isEn ? map[d]?.en || d : map[d]?.zh || d
  }

  const getPotentialLabel = (p: string) => {
    const map: Record<string, { zh: string; en: string }> = {
      low: { zh: '低', en: 'Low' },
      medium: { zh: '中', en: 'Medium' },
      'medium-high': { zh: '中高', en: 'Medium-High' },
      high: { zh: '高', en: 'High' },
    }
    return isEn ? map[p]?.en || p : map[p]?.zh || p
  }


  if (loading) {
    return (
      <section>
        <div className="flex items-center justify-center py-16">
          <Loader2 className="h-6 w-6 animate-spin text-content-muted" />
        </div>
      </section>
    )
  }

  if (recommendations.length === 0) {
    return null
  }

  return (
    <section>
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-pink-500 to-rose-500 flex items-center justify-center shadow-lg shadow-pink-500/20">
            <Heart className="h-5 w-5 text-white" />
          </div>
          <div>
            <h2 className="text-lg font-display font-bold text-content-primary tracking-tight">
              {t('discover.forYou.title')}
            </h2>
            <p className="text-xs text-content-muted">{t('discover.forYou.subtitle')}</p>
          </div>
        </div>
      </div>

      <div className="grid md:grid-cols-3 gap-4">
        {recommendations.map((rec) => (
          <Card
            key={rec.id}
            hover
            className={`group bg-gradient-to-br ${rec.gradient}`}
          >
            <div className="flex items-start gap-2 mb-3">
              <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0
                ${rec.accent_color === 'blue' ? 'bg-blue-500/20 text-blue-500' : ''}
                ${rec.accent_color === 'violet' ? 'bg-violet-500/20 text-violet-500' : ''}
                ${rec.accent_color === 'rose' ? 'bg-rose-500/20 text-rose-500' : ''}
                ${rec.accent_color === 'amber' ? 'bg-amber-500/20 text-amber-500' : ''}
                ${rec.accent_color === 'emerald' ? 'bg-emerald-500/20 text-emerald-500' : ''}
              `}>
                <Zap className="h-4 w-4" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-content-primary group-hover:text-brand-600 dark:group-hover:text-brand-400 transition-colors">
                  {getDirection(rec)}
                </h3>
              </div>
            </div>

            <p className="text-xs text-content-tertiary mb-3 line-clamp-2">
              {getDesc(rec)}
            </p>

            {getWhyForYou(rec) && (
              <div className={`p-2.5 rounded-lg mb-3 text-xs
                ${rec.accent_color === 'blue' ? 'bg-blue-500/10 text-blue-700 dark:text-blue-300' : ''}
                ${rec.accent_color === 'violet' ? 'bg-violet-500/10 text-violet-700 dark:text-violet-300' : ''}
                ${rec.accent_color === 'rose' ? 'bg-rose-500/10 text-rose-700 dark:text-rose-300' : ''}
                ${rec.accent_color === 'amber' ? 'bg-amber-500/10 text-amber-700 dark:text-amber-300' : ''}
                ${rec.accent_color === 'emerald' ? 'bg-emerald-500/10 text-emerald-700 dark:text-emerald-300' : ''}
              `}>
                <div className="flex items-center gap-1.5 mb-1 font-medium">
                  <Sparkles className="h-3 w-3" />
                  {t('discover.forYou.whyForYou')}
                </div>
                <p className="text-content-secondary">{getWhyForYou(rec)}</p>
              </div>
            )}

            <div className="mb-3">
              <div className="text-[10px] text-content-muted mb-1.5">
                {isEn ? 'Reference directions' : '参考方向'}
              </div>
              <div className="flex flex-wrap gap-1.5">
                {rec.examples.map((example, idx) => (
                  <span
                    key={idx}
                    className="text-[10px] px-2 py-0.5 rounded bg-surface border border-surface-border/50 text-content-secondary"
                  >
                    {example}
                  </span>
                ))}
              </div>
            </div>

            <div className="flex items-center gap-4 mb-3 text-xs">
              <div>
                <span className="text-content-muted">{isEn ? 'Difficulty: ' : '难度：'}</span>
                <span className="text-content-secondary font-medium">{getDifficultyLabel(rec.difficulty)}</span>
              </div>
              <div>
                <span className="text-content-muted">{isEn ? 'Potential: ' : '潜力：'}</span>
                <span className={`font-medium
                  ${rec.potential === 'high' ? 'text-emerald-600 dark:text-emerald-400' : ''}
                  ${rec.potential === 'medium-high' ? 'text-amber-600 dark:text-amber-400' : ''}
                  ${rec.potential === 'medium' ? 'text-blue-600 dark:text-blue-400' : ''}
                `}>
                  {getPotentialLabel(rec.potential)}
                </span>
              </div>
            </div>

            <div className="flex gap-2">
              <Link
                href="/assistant"
                className="flex-1 flex items-center justify-center gap-1.5 py-2 rounded-lg bg-brand-500/10 text-brand-600 dark:text-brand-400 text-xs font-medium hover:bg-brand-500/20 transition-colors"
              >
                <MessageCircle className="h-3.5 w-3.5" />
                {t('discover.forYou.explore')}
              </Link>
              <Link
                href={`/products?direction=${rec.id}`}
                className="flex items-center justify-center gap-1 px-3 py-2 rounded-lg bg-surface border border-surface-border text-xs font-medium text-content-secondary hover:text-content-primary hover:border-brand-500/30 transition-colors"
              >
                {t('discover.cta.findSimilar')}
                <ArrowRight className="h-3 w-3" />
              </Link>
            </div>
          </Card>
        ))}
      </div>

      <div className="mt-6 space-y-4">
        {isAuthenticated ? (
          <div className="p-4 rounded-xl bg-surface border border-surface-border text-center">
            <p className="text-sm text-content-secondary mb-2">
              {isEn ? 'Want better recommendations? Update your preferences in Settings' : '想要更准的推荐？去设置里完善偏好'}
            </p>
            <Link
              href="/settings/preferences"
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-brand-500 text-white text-sm font-medium hover:bg-brand-600 transition-colors shadow-lg shadow-brand-500/20"
            >
              <User className="h-4 w-4" />
              {isEn ? 'Go to Preferences' : '前往偏好设置'}
            </Link>
          </div>
        ) : (
          <div className="p-4 rounded-xl bg-surface border border-surface-border text-center">
            <p className="text-sm text-content-secondary mb-2">
              {isEn ? 'Sign in to get recommendations tailored to you' : '登录后可以获得更精准的推荐'}
            </p>
            <Link
              href="/auth/sign-in?callbackUrl=/discover"
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-brand-500 text-white text-sm font-medium hover:bg-brand-600 transition-colors shadow-lg shadow-brand-500/20"
            >
              <User className="h-4 w-4" />
              {isEn ? 'Sign in to personalize' : '登录并个性化推荐'}
            </Link>
          </div>
        )}

        <div className="p-4 rounded-xl bg-gradient-to-r from-brand-500/5 via-violet-500/5 to-amber-500/5 border border-brand-500/10 text-center">
          <p className="text-sm text-content-secondary mb-2">
            {isEn ? 'Want deeper advice? Tell AI about your background' : '想要更深入的建议？告诉 AI 你的背景和目标'}
          </p>
          <Link
            href="/assistant"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-brand-500 text-white text-sm font-medium hover:bg-brand-600 transition-colors shadow-lg shadow-brand-500/20"
          >
            <MessageCircle className="h-4 w-4" />
            {isEn ? 'Start conversation' : '开始对话'}
          </Link>
        </div>
      </div>
    </section>
  )
}
