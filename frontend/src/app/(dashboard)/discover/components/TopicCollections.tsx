'use client'

import { useLocale } from '@/contexts/LocaleContext'
import { Card } from '@/components/ui/Card'
import { Layers, ArrowRight, ChevronLeft, ChevronRight } from 'lucide-react'
import Link from 'next/link'
import { useRef } from 'react'

// 模拟数据 - 主题合集
const mockTopics = [
  {
    id: 1,
    title: '被低估的赚钱机器',
    description: '这些产品看起来平平无奇，但每月稳定盈利',
    emoji: '💰',
    gradient: 'from-amber-500 to-orange-500',
    bgGradient: 'from-amber-500/10 to-orange-500/5',
    productCount: 12,
    creatorCount: 8,
  },
  {
    id: 2,
    title: '一个人也能维护的 SaaS',
    description: '技术复杂度低，适合独立开发者',
    emoji: '🧑‍💻',
    gradient: 'from-blue-500 to-cyan-500',
    bgGradient: 'from-blue-500/10 to-cyan-500/5',
    productCount: 18,
    creatorCount: 15,
  },
  {
    id: 3,
    title: '没有融资，但活得很好',
    description: '自力更生的盈利产品',
    emoji: '🌱',
    gradient: 'from-emerald-500 to-green-500',
    bgGradient: 'from-emerald-500/10 to-green-500/5',
    productCount: 24,
    creatorCount: 20,
  },
  {
    id: 4,
    title: '被大厂忽视的角落需求',
    description: '小众但真实的市场机会',
    emoji: '🔍',
    gradient: 'from-violet-500 to-purple-500',
    bgGradient: 'from-violet-500/10 to-purple-500/5',
    productCount: 15,
    creatorCount: 12,
  },
  {
    id: 5,
    title: '不是 AI，但活得很好',
    description: '传统需求的现代解决方案',
    emoji: '⚡',
    gradient: 'from-rose-500 to-pink-500',
    bgGradient: 'from-rose-500/10 to-pink-500/5',
    productCount: 21,
    creatorCount: 16,
  },
  {
    id: 6,
    title: '靠教程起家，靠 SaaS 变现',
    description: '内容创作者的产品化之路',
    emoji: '📚',
    gradient: 'from-indigo-500 to-blue-500',
    bgGradient: 'from-indigo-500/10 to-blue-500/5',
    productCount: 9,
    creatorCount: 9,
  },
]

export function TopicCollections() {
  const { t } = useLocale()
  const scrollRef = useRef<HTMLDivElement>(null)

  const scroll = (direction: 'left' | 'right') => {
    if (scrollRef.current) {
      const scrollAmount = 320
      scrollRef.current.scrollBy({
        left: direction === 'left' ? -scrollAmount : scrollAmount,
        behavior: 'smooth',
      })
    }
  }

  return (
    <section>
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-brand-500 to-accent-secondary flex items-center justify-center shadow-lg shadow-brand-500/20">
            <Layers className="h-5 w-5 text-white" />
          </div>
          <div>
            <h2 className="text-lg font-display font-bold text-content-primary tracking-tight">
              {t('discover.topics.title')}
            </h2>
            <p className="text-xs text-content-muted">{t('discover.topics.subtitle')}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => scroll('left')}
            className="w-8 h-8 rounded-lg bg-surface border border-surface-border flex items-center justify-center text-content-muted hover:text-content-primary hover:border-brand-500/30 transition-colors"
          >
            <ChevronLeft className="h-4 w-4" />
          </button>
          <button
            onClick={() => scroll('right')}
            className="w-8 h-8 rounded-lg bg-surface border border-surface-border flex items-center justify-center text-content-muted hover:text-content-primary hover:border-brand-500/30 transition-colors"
          >
            <ChevronRight className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* 横向滚动容器 */}
      <div
        ref={scrollRef}
        className="flex gap-4 overflow-x-auto scrollbar-hide pb-2 -mx-1 px-1"
        style={{ scrollSnapType: 'x mandatory' }}
      >
        {mockTopics.map((topic) => (
          <Link
            key={topic.id}
            href={`/discover/topics/${topic.id}`}
            className="flex-shrink-0 w-72"
            style={{ scrollSnapAlign: 'start' }}
          >
            <Card
              hover
              className={`h-full bg-gradient-to-br ${topic.bgGradient} border-transparent hover:border-brand-500/30`}
            >
              <div className="flex items-start gap-3 mb-3">
                <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${topic.gradient} flex items-center justify-center text-2xl shadow-lg`}>
                  {topic.emoji}
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="text-sm font-bold text-content-primary line-clamp-2 mb-1">
                    {topic.title}
                  </h3>
                  <p className="text-xs text-content-tertiary line-clamp-2">
                    {topic.description}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-3 text-xs text-content-muted">
                <span className="flex items-center gap-1">
                  <span className="font-medium text-content-secondary">{topic.productCount}</span>
                  {t('discover.topics.products')}
                </span>
                <span className="w-1 h-1 rounded-full bg-content-muted/50" />
                <span className="flex items-center gap-1">
                  <span className="font-medium text-content-secondary">{topic.creatorCount}</span>
                  {t('discover.topics.creators')}
                </span>
              </div>

              <div className="flex items-center gap-1 mt-3 text-xs text-brand-500 font-medium">
                {t('discover.topics.viewMore')}
                <ArrowRight className="h-3 w-3" />
              </div>
            </Card>
          </Link>
        ))}
      </div>
    </section>
  )
}
