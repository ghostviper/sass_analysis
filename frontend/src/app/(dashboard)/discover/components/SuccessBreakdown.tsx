'use client'

import { useLocale } from '@/contexts/LocaleContext'
import { Card } from '@/components/ui/Card'
import { Target, ArrowRight, Clock, Lightbulb, MessageCircle, TrendingUp } from 'lucide-react'
import Link from 'next/link'

// 模拟数据 - 爆款解剖
const mockBreakdowns = [
  {
    id: 1,
    title: '这个 $20k MRR 产品，第一版其实很烂',
    subtitle: 'Plausible Analytics 的成长故事',
    product: {
      name: 'Plausible Analytics',
      logo: '📊',
      mrr: '$20k+',
      founder: 'Uku Täht',
    },
    timeline: [
      { date: '2019.04', event: '第一版上线，功能简陋' },
      { date: '2019.08', event: '开源策略，获得关注' },
      { date: '2020.03', event: '隐私合规成为卖点' },
      { date: '2021.01', event: 'MRR 突破 $10k' },
    ],
    keyInsights: [
      '隐私合规是差异化的关键',
      '开源带来信任和传播',
      '简单比功能多更重要',
    ],
    gradient: 'from-emerald-500/10 to-teal-500/5',
    accentColor: 'emerald',
  },
  {
    id: 2,
    title: '这个 SaaS 的成功，80% 不在技术',
    subtitle: 'Carrd 的极简主义哲学',
    product: {
      name: 'Carrd',
      logo: '🎴',
      mrr: '$100k+',
      founder: 'AJ',
    },
    timeline: [
      { date: '2016.08', event: '一个人开发上线' },
      { date: '2017.02', event: '免费版获得大量用户' },
      { date: '2018.06', event: 'Pro 版本推出' },
      { date: '2020.12', event: 'MRR 突破 $100k' },
    ],
    keyInsights: [
      '极简设计降低用户门槛',
      '免费版是最好的营销',
      '一个人也能做大产品',
    ],
    gradient: 'from-violet-500/10 to-purple-500/5',
    accentColor: 'violet',
  },
]

export function SuccessBreakdown() {
  const { t } = useLocale()

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
            <p className="text-xs text-content-muted">{t('discover.breakdown.subtitle')}</p>
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
        {mockBreakdowns.map((breakdown) => (
          <Card
            key={breakdown.id}
            hover
            className={`group bg-gradient-to-br ${breakdown.gradient}`}
          >
            {/* 产品信息 */}
            <div className="flex items-center gap-3 mb-4 pb-4 border-b border-surface-border/50">
              <div className="w-12 h-12 rounded-xl bg-surface flex items-center justify-center text-2xl shadow-sm">
                {breakdown.product.logo}
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-bold text-content-primary">
                    {breakdown.product.name}
                  </span>
                  <span className={`text-xs font-mono font-medium px-2 py-0.5 rounded-md
                    ${breakdown.accentColor === 'emerald' ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400' : ''}
                    ${breakdown.accentColor === 'violet' ? 'bg-violet-500/10 text-violet-600 dark:text-violet-400' : ''}
                  `}>
                    {breakdown.product.mrr}
                  </span>
                </div>
                <span className="text-xs text-content-muted">by {breakdown.product.founder}</span>
              </div>
            </div>

            {/* 标题 */}
            <h3 className="text-base font-bold text-content-primary mb-1 group-hover:text-brand-600 dark:group-hover:text-brand-400 transition-colors">
              {breakdown.title}
            </h3>
            <p className="text-xs text-content-tertiary mb-4">{breakdown.subtitle}</p>

            {/* 时间线 */}
            <div className="mb-4">
              <div className="flex items-center gap-1.5 text-xs font-medium text-content-secondary mb-2">
                <Clock className="h-3.5 w-3.5" />
                {t('discover.breakdown.timeline')}
              </div>
              <div className="space-y-2">
                {breakdown.timeline.slice(0, 3).map((item, idx) => (
                  <div key={idx} className="flex items-start gap-2 text-xs">
                    <span className="font-mono text-content-muted w-16 flex-shrink-0">{item.date}</span>
                    <span className="text-content-secondary">{item.event}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* 核心洞察 */}
            <div className="mb-4">
              <div className="flex items-center gap-1.5 text-xs font-medium text-content-secondary mb-2">
                <Lightbulb className="h-3.5 w-3.5" />
                {t('discover.breakdown.keyInsights')}
              </div>
              <div className="flex flex-wrap gap-2">
                {breakdown.keyInsights.map((insight, idx) => (
                  <span
                    key={idx}
                    className={`text-xs px-2 py-1 rounded-md
                      ${breakdown.accentColor === 'emerald' ? 'bg-emerald-500/10 text-emerald-700 dark:text-emerald-300' : ''}
                      ${breakdown.accentColor === 'violet' ? 'bg-violet-500/10 text-violet-700 dark:text-violet-300' : ''}
                    `}
                  >
                    {insight}
                  </span>
                ))}
              </div>
            </div>

            {/* CTA */}
            <div className="flex gap-2">
              <Link
                href={`/discover/breakdowns/${breakdown.id}`}
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
