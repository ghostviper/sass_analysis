'use client'

import { useLocale } from '@/contexts/LocaleContext'
import { Card } from '@/components/ui/Card'
import { Target, ArrowRight, Clock, Lightbulb, MessageCircle, TrendingUp, Package } from 'lucide-react'
import Link from 'next/link'
import { useState, useEffect } from 'react'
import type { SuccessStory } from '@/types/discover'
import { getStories } from '@/lib/api/discover'

// Mock data for fallback
const mockStories: SuccessStory[] = [
  {
    id: 1,
    title: '这个 $20k MRR 产品，第一版其实很烂',
    title_zh: '这个 $20k MRR 产品，第一版其实很烂',
    title_en: 'This $20k MRR product started really rough',
    subtitle: 'Plausible Analytics 的成长故事',
    subtitle_zh: 'Plausible Analytics 的成长故事',
    subtitle_en: 'The growth story of Plausible Analytics',
    product: {
      name: 'Plausible Analytics',
      logo: '📊',
      mrr: '$20k+',
      founder: 'Uku Täht',
    },
    timeline: [
      { date: '2019.04', event: '第一版上线，功能简陋', event_zh: '第一版上线，功能简陋', event_en: 'First version launched, basic features' },
      { date: '2019.08', event: '开源策略，获得关注', event_zh: '开源策略，获得关注', event_en: 'Open source strategy gained attention' },
      { date: '2020.03', event: '隐私合规成为卖点', event_zh: '隐私合规成为卖点', event_en: 'Privacy compliance became selling point' },
      { date: '2021.01', event: 'MRR 突破 $10k', event_zh: 'MRR 突破 $10k', event_en: 'MRR exceeded $10k' },
    ],
    key_insights: [
      { text: '隐私合规是差异化的关键', text_zh: '隐私合规是差异化的关键', text_en: 'Privacy compliance is key to differentiation' },
      { text: '开源带来信任和传播', text_zh: '开源带来信任和传播', text_en: 'Open source brings trust and virality' },
      { text: '简单比功能多更重要', text_zh: '简单比功能多更重要', text_en: 'Simplicity matters more than features' },
    ],
    gradient: 'from-emerald-500/10 to-teal-500/5',
    accent_color: 'emerald',
  },
  {
    id: 2,
    title: '这个 SaaS 的成功，80% 不在技术',
    title_zh: '这个 SaaS 的成功，80% 不在技术',
    title_en: '80% of this SaaS success is not about tech',
    subtitle: 'Carrd 的极简主义哲学',
    subtitle_zh: 'Carrd 的极简主义哲学',
    subtitle_en: "Carrd's minimalist philosophy",
    product: {
      name: 'Carrd',
      logo: '🎴',
      mrr: '$100k+',
      founder: 'AJ',
    },
    timeline: [
      { date: '2016.08', event: '一个人开发上线', event_zh: '一个人开发上线', event_en: 'Solo developer launched' },
      { date: '2017.02', event: '免费版获得大量用户', event_zh: '免费版获得大量用户', event_en: 'Free tier gained massive users' },
      { date: '2018.06', event: 'Pro 版本推出', event_zh: 'Pro 版本推出', event_en: 'Pro version launched' },
      { date: '2020.12', event: 'MRR 突破 $100k', event_zh: 'MRR 突破 $100k', event_en: 'MRR exceeded $100k' },
    ],
    key_insights: [
      { text: '极简设计降低用户门槛', text_zh: '极简设计降低用户门槛', text_en: 'Minimalist design lowers user barrier' },
      { text: '免费版是最好的营销', text_zh: '免费版是最好的营销', text_en: 'Free tier is the best marketing' },
      { text: '一个人也能做大产品', text_zh: '一个人也能做大产品', text_en: 'One person can build big products' },
    ],
    gradient: 'from-violet-500/10 to-purple-500/5',
    accent_color: 'violet',
  },
]

export function SuccessBreakdown() {
  const { t, locale } = useLocale()
  const [stories, setStories] = useState<SuccessStory[]>([])
  const [loading, setLoading] = useState(true)

  const isEn = locale === 'en'

  useEffect(() => {
    async function fetchStories() {
      try {
        setLoading(true)
        const data = await getStories({ limit: 2 })
        if (data.stories.length > 0) {
          setStories(data.stories)
        } else {
          setStories(mockStories)
        }
      } catch (err) {
        console.error('Failed to fetch stories:', err)
        setStories(mockStories)
      } finally {
        setLoading(false)
      }
    }
    fetchStories()
  }, [])

  const getTitle = (s: SuccessStory) => isEn ? s.title_en : s.title_zh
  const getSubtitle = (s: SuccessStory) => isEn ? s.subtitle_en : s.subtitle_zh
  const getEvent = (e: { event_zh: string; event_en: string }) => isEn ? e.event_en : e.event_zh
  const getInsight = (i: { text_zh: string; text_en: string }) => isEn ? i.text_en : i.text_zh

  if (loading) {
    return (
      <section>
        <div className="flex items-center justify-between mb-5">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-rose-500 to-orange-500 flex items-center justify-center shadow-lg shadow-rose-500/20">
              <Target className="h-5 w-5 text-white" />
            </div>
            <div>
              <h2 className="text-lg font-display font-bold text-content-primary tracking-tight">
                {t('discover.breakdown.title')}
              </h2>
              <p className="text-xs text-slate-600 dark:text-slate-400">{t('discover.breakdown.subtitle')}</p>
            </div>
          </div>
        </div>
        <div className="grid lg:grid-cols-2 gap-5">
          <Card className="animate-pulse">
            <div className="h-48 bg-surface-hover rounded-lg" />
          </Card>
          <Card className="animate-pulse">
            <div className="h-48 bg-surface-hover rounded-lg" />
          </Card>
        </div>
      </section>
    )
  }

  return (
    <section>
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-rose-500 to-orange-500 flex items-center justify-center shadow-lg shadow-rose-500/20">
            <Target className="h-5 w-5 text-white" />
          </div>
          <div>
            <h2 className="text-lg font-display font-bold text-content-primary tracking-tight">
              {t('discover.breakdown.title')}
            </h2>
            <p className="text-xs text-slate-600 dark:text-slate-400">{t('discover.breakdown.subtitle')}</p>
          </div>
        </div>
        <Link
          href="/discover/breakdowns"
          className="text-sm text-brand-500 hover:text-brand-600 font-medium flex items-center gap-1 transition-colors"
        >
          {t('discover.todayCuration.viewAll')}
          <ArrowRight className="h-4 w-4" />
        </Link>
      </div>

      <div className="grid lg:grid-cols-2 gap-5">
        {stories.map((story) => (
          <Card key={story.id} hover className={`group bg-gradient-to-br ${story.gradient}`}>
            <div className="flex items-center gap-3 mb-4 pb-4 border-b border-surface-border/50">
              <div className="w-12 h-12 rounded-xl bg-surface border border-surface-border flex items-center justify-center shadow-sm">
                <Package className="h-6 w-6 text-brand-600 dark:text-brand-400" />
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-bold text-content-primary">
                    {story.product.name}
                  </span>
                  <span className={`text-xs font-mono font-medium px-2 py-0.5 rounded-md
                    ${story.accent_color === 'emerald' ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400' : ''}
                    ${story.accent_color === 'violet' ? 'bg-violet-500/10 text-violet-600 dark:text-violet-400' : ''}
                  `}>
                    {story.product.mrr}
                  </span>
                </div>
                <span className="text-xs text-content-muted">by {story.product.founder}</span>
              </div>
            </div>

            <h3 className="text-base font-bold text-content-primary mb-1 group-hover:text-brand-600 dark:group-hover:text-brand-400 transition-colors">
              {getTitle(story)}
            </h3>
            <p className="text-xs text-content-tertiary mb-4">{getSubtitle(story)}</p>

            <div className="mb-4">
              <div className="flex items-center gap-1.5 text-xs font-medium text-content-secondary mb-2">
                <Clock className="h-3.5 w-3.5" />
                {t('discover.breakdown.timeline')}
              </div>
              <div className="space-y-2">
                {story.timeline.slice(0, 3).map((item, idx) => (
                  <div key={idx} className="flex items-start gap-2 text-xs">
                    <span className="font-mono text-content-muted w-16 flex-shrink-0">{item.date}</span>
                    <span className="text-content-secondary">{getEvent(item)}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="mb-4">
              <div className="flex items-center gap-1.5 text-xs font-medium text-content-secondary mb-2">
                <Lightbulb className="h-3.5 w-3.5" />
                {t('discover.breakdown.keyInsights')}
              </div>
              <div className="flex flex-wrap gap-2">
                {story.key_insights.map((insight, idx) => (
                  <span
                    key={idx}
                    className={`text-xs px-2 py-1 rounded-md
                      ${story.accent_color === 'emerald' ? 'bg-emerald-500/10 text-emerald-700 dark:text-emerald-300' : ''}
                      ${story.accent_color === 'violet' ? 'bg-violet-500/10 text-violet-700 dark:text-violet-300' : ''}
                    `}
                  >
                    {getInsight(insight)}
                  </span>
                ))}
              </div>
            </div>

            <div className="flex gap-2">
              <Link
                href={`/discover/breakdowns/${story.id}`}
                className="flex-1 flex items-center justify-center gap-2 py-2 rounded-lg bg-surface border border-surface-border text-sm font-medium text-content-secondary hover:text-content-primary hover:border-brand-500/30 transition-colors"
              >
                <TrendingUp className="h-4 w-4" />
                {t('discover.breakdown.readMore')}
              </Link>
              <Link
                href="/assistant"
                className="flex-1 flex items-center justify-center gap-2 py-2 rounded-lg bg-brand-500/10 text-brand-600 dark:text-brand-400 text-sm font-medium hover:bg-brand-500/20 transition-colors"
              >
                <MessageCircle className="h-4 w-4" />
                {t('discover.cta.askAI')}
              </Link>
            </div>
          </Card>
        ))}
      </div>
    </section>
  )
}
