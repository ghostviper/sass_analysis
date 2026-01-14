'use client'

import { useLocale } from '@/contexts/LocaleContext'
import { Card } from '@/components/ui/Card'
import { Sparkles, ArrowRight, MessageCircle, TrendingUp, Zap } from 'lucide-react'
import Link from 'next/link'

// 模拟数据 - 今日策展
const mockCurations = [
  {
    id: 1,
    title: '3 个独立开发者，靠一个很无聊的需求赚到了钱',
    description: '这些产品解决的问题看起来毫无新意，但每个月都在稳定赚钱。他们的共同点是什么？',
    tag: '被低估的赚钱机器',
    tagColor: 'amber',
    products: [
      { name: 'PDF Tool Pro', mrr: '$8.2k', logo: '📄' },
      { name: 'Invoice Simple', mrr: '$12.5k', logo: '🧾' },
      { name: 'Screenshot API', mrr: '$6.8k', logo: '📸' },
    ],
    insight: '无聊的需求 = 稳定的需求',
  },
  {
    id: 2,
    title: '这些 SaaS 没有官网设计感，但 MRR 都超过 $10k',
    description: '设计不是成功的必要条件。这些产品证明了：解决真实问题比好看更重要。',
    tag: '产品 > 设计',
    tagColor: 'emerald',
    products: [
      { name: 'DataBackup.io', mrr: '$15.3k', logo: '💾' },
      { name: 'FormBuilder', mrr: '$11.2k', logo: '📝' },
      { name: 'CronJob Monitor', mrr: '$9.7k', logo: '⏰' },
    ],
    insight: '功能价值 > 视觉价值',
  },
]

export function TodayCuration() {
  const { t } = useLocale()

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
          href="/discover/curations"
          className="text-sm text-brand-500 hover:text-brand-600 font-medium flex items-center gap-1 transition-colors"
        >
          {t('discover.todayCuration.viewAll')}
          <ArrowRight className="h-4 w-4" />
        </Link>
      </div>

      <div className="grid md:grid-cols-2 gap-5">
        {mockCurations.map((curation) => (
          <Card
            key={curation.id}
            hover
            className="group relative overflow-hidden"
          >
            {/* 背景装饰 */}
            <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-bl from-violet-500/5 to-transparent rounded-full -translate-y-1/2 translate-x-1/2" />
            
            <div className="relative">
              {/* 标签 */}
              <div className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium mb-3
                ${curation.tagColor === 'amber' ? 'bg-amber-500/10 text-amber-600 dark:text-amber-400' : ''}
                ${curation.tagColor === 'emerald' ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400' : ''}
              `}>
                <Zap className="h-3 w-3" />
                {curation.tag}
              </div>

              {/* 标题 */}
              <h3 className="text-base font-bold text-content-primary mb-2 group-hover:text-brand-600 dark:group-hover:text-brand-400 transition-colors line-clamp-2">
                {curation.title}
              </h3>

              {/* 描述 */}
              <p className="text-sm text-content-tertiary mb-4 line-clamp-2">
                {curation.description}
              </p>

              {/* 产品列表 */}
              <div className="space-y-2 mb-4">
                {curation.products.map((product, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between p-2.5 rounded-lg bg-surface/50 border border-surface-border/50"
                  >
                    <div className="flex items-center gap-2.5">
                      <span className="text-lg">{product.logo}</span>
                      <span className="text-sm font-medium text-content-primary">{product.name}</span>
                    </div>
                    <span className="text-sm font-mono text-emerald-600 dark:text-emerald-400 font-medium">
                      {product.mrr}
                    </span>
                  </div>
                ))}
              </div>

              {/* 洞察 */}
              <div className="flex items-center gap-2 p-3 rounded-lg bg-violet-500/5 border border-violet-500/10 mb-4">
                <TrendingUp className="h-4 w-4 text-violet-500 flex-shrink-0" />
                <span className="text-sm text-violet-600 dark:text-violet-400 font-medium">
                  {curation.insight}
                </span>
              </div>

              {/* CTA */}
              <Link
                href="/assistant"
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
