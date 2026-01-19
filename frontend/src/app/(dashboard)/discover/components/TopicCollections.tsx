'use client'

import { useLocale } from '@/contexts/LocaleContext'
import { Card } from '@/components/ui/Card'
import { 
  ChevronLeft, 
  ChevronRight, 
  ArrowRight,
  TrendingUp,
  Code2,
  Zap,
  Target,
  AlertTriangle,
  Gem,
  Search,
  Sparkles,
  Shield,
  PenTool,
  Focus,
  Layers
} from 'lucide-react'
import Link from 'next/link'
import { useRef, useState, useEffect } from 'react'
import type { TopicSummary } from '@/types/discover'
import { getTopics, formatRevenue } from '@/lib/api/discover'
import { TopicCardSkeleton } from '@/components/ui/Loading'

// 临时：角色到图标的映射，后续会从 API 的 icon 字段获取
const ROLE_ICONS: Record<string, React.ReactNode> = {
  'cautious_indie_dev': <Code2 className="h-4 w-4" />,
  'quick_starter': <Zap className="h-4 w-4" />,
  'opportunity_hunter': <Target className="h-4 w-4" />,
  'anti_bubble': <AlertTriangle className="h-4 w-4" />,
  'product_driven_fan': <Gem className="h-4 w-4" />,
  'niche_hunter': <Search className="h-4 w-4" />,
  'ux_differentiator': <Sparkles className="h-4 w-4" />,
  'low_risk_starter': <Shield className="h-4 w-4" />,
  'content_to_product': <PenTool className="h-4 w-4" />,
  'scenario_focused': <Focus className="h-4 w-4" />,
}

export function TopicCollections() {
  const { t, locale } = useLocale()
  const scrollRef = useRef<HTMLDivElement>(null)
  const [topics, setTopics] = useState<TopicSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [canScrollLeft, setCanScrollLeft] = useState(false)
  const [canScrollRight, setCanScrollRight] = useState(true)

  // 根据 locale 获取对应语言的文本
  const isEn = locale === 'en'
  const getTitle = (topic: TopicSummary) => isEn ? (topic.title_en || topic.title) : (topic.title_zh || topic.title)
  const getDescription = (topic: TopicSummary) => isEn ? (topic.description_en || topic.description) : (topic.description_zh || topic.description)

  useEffect(() => {
    async function fetchTopics() {
      try {
        setLoading(true)
        const data = await getTopics()
        setTopics(data.topics)
      } catch (err) {
        setError(isEn ? 'Failed to load' : '加载失败')
        console.error('Failed to fetch topics:', err)
      } finally {
        setLoading(false)
      }
    }
    fetchTopics()
  }, [isEn])

  const checkScrollButtons = () => {
    if (scrollRef.current) {
      const { scrollLeft, scrollWidth, clientWidth } = scrollRef.current
      setCanScrollLeft(scrollLeft > 0)
      setCanScrollRight(scrollLeft < scrollWidth - clientWidth - 10)
    }
  }

  useEffect(() => {
    const el = scrollRef.current
    if (el) {
      el.addEventListener('scroll', checkScrollButtons)
      checkScrollButtons()
      return () => el.removeEventListener('scroll', checkScrollButtons)
    }
  }, [topics])

  const scroll = (direction: 'left' | 'right') => {
    if (scrollRef.current) {
      const scrollAmount = 340
      scrollRef.current.scrollBy({
        left: direction === 'left' ? -scrollAmount : scrollAmount,
        behavior: 'smooth',
      })
    }
  }

  if (loading) {
    return (
      <section className="py-2">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center shadow-lg shadow-emerald-500/20">
              <Layers className="h-5 w-5 text-white" />
            </div>
            <div>
              <h2 className="text-base font-semibold text-content-primary">
                {t('discover.topics.title')}
              </h2>
              <p className="text-xs text-slate-600 dark:text-slate-400 mt-0.5">
                {t('discover.topics.subtitle')}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-1.5">
            <button
              disabled
              className="w-8 h-8 rounded-lg bg-surface border border-surface-border flex items-center justify-center text-content-muted opacity-30 cursor-not-allowed"
            >
              <ChevronLeft className="h-4 w-4" />
            </button>
            <button
              disabled
              className="w-8 h-8 rounded-lg bg-surface border border-surface-border flex items-center justify-center text-content-muted opacity-30 cursor-not-allowed"
            >
              <ChevronRight className="h-4 w-4" />
            </button>
          </div>
        </div>
        <div className="flex gap-4 overflow-x-auto scrollbar-hide pb-2">
          <TopicCardSkeleton />
          <TopicCardSkeleton />
          <TopicCardSkeleton />
        </div>
      </section>
    )
  }

  if (error) {
    return (
      <section className="py-2">
        <div className="text-center py-16 text-content-muted text-sm">{error}</div>
      </section>
    )
  }

  return (
    <section className="py-2">
      {/* 标题区 */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center shadow-lg shadow-emerald-500/20">
            <Layers className="h-5 w-5 text-white" />
          </div>
          <div>
            <h2 className="text-base font-semibold text-content-primary">
              {t('discover.topics.title')}
            </h2>
            <p className="text-xs text-content-muted mt-0.5">
              {t('discover.topics.subtitle')}
            </p>
          </div>
        </div>
        
        <div className="flex items-center gap-1.5">
          <button
            onClick={() => scroll('left')}
            disabled={!canScrollLeft}
            aria-label={isEn ? 'Scroll left' : '向左滚动'}
            className="min-w-[44px] min-h-[44px] w-11 h-11 rounded-lg bg-surface border border-surface-border flex items-center justify-center text-content-muted hover:text-content-primary hover:bg-surface-hover active:bg-surface-hover active:scale-95 disabled:opacity-30 disabled:cursor-not-allowed transition-all duration-200 cursor-pointer"
          >
            <ChevronLeft className="h-5 w-5" />
          </button>
          <button
            onClick={() => scroll('right')}
            disabled={!canScrollRight}
            aria-label={isEn ? 'Scroll right' : '向右滚动'}
            className="min-w-[44px] min-h-[44px] w-11 h-11 rounded-lg bg-surface border border-surface-border flex items-center justify-center text-content-muted hover:text-content-primary hover:bg-surface-hover active:bg-surface-hover active:scale-95 disabled:opacity-30 disabled:cursor-not-allowed transition-all duration-200 cursor-pointer"
          >
            <ChevronRight className="h-5 w-5" />
          </button>
        </div>
      </div>

      {/* 卡片滚动区 */}
      <div className="relative">
        {/* 左侧渐变提示 */}
        {canScrollLeft && (
          <div className="absolute left-0 top-0 bottom-0 w-12 bg-gradient-to-r from-background to-transparent z-10 pointer-events-none" />
        )}
        
        <div
          ref={scrollRef}
          className="flex gap-4 overflow-x-auto scrollbar-hide pb-2 -mx-1 px-1 snap-x snap-mandatory"
        >
        {topics.map((topic, index) => {
          const icon = ROLE_ICONS[topic.curator_role] || <Layers className="h-4 w-4" />
          const title = getTitle(topic)
          const description = getDescription(topic)
          
          return (
            <Link
              key={topic.id}
              href={`/discover/topics/${topic.id}`}
              className="flex-shrink-0 w-80 snap-start group cursor-pointer"
              style={{ animationDelay: `${Math.min(index * 50, 500)}ms` }}
            >
              <Card
                hover
                className="h-full border-surface-border/50 hover:border-brand-500/30 active:border-brand-500/50 transition-all duration-200"
              >
                {/* 图标 + 标题 */}
                <div className="flex items-start gap-3 mb-3">
                  <div className="w-9 h-9 rounded-xl bg-brand-500/10 border border-brand-500/20 text-brand-600 dark:text-brand-400 flex items-center justify-center flex-shrink-0 group-hover:bg-brand-500/20 transition-all duration-200">
                    {icon}
                  </div>
                  <h3 className="text-base font-bold text-content-primary leading-snug pt-1 group-hover:text-brand-600 dark:group-hover:text-brand-400 transition-colors duration-200">
                    {title}
                  </h3>
                </div>

                {/* 描述 */}
                <p className="text-xs text-content-tertiary mb-4 line-clamp-2 leading-relaxed">
                  {description}
                </p>

                {/* 代表产品 */}
                {topic.top_products.length > 0 && (
                  <div className="space-y-1.5 mb-4 py-3 border-y border-surface-border/30">
                    {topic.top_products.slice(0, 2).map((p, idx) => (
                      <div 
                        key={idx} 
                        className="flex items-center justify-between"
                      >
                        <span className="text-xs text-content-secondary truncate flex-1 mr-3">
                          {p.name}
                        </span>
                        <span className="flex items-center gap-1 text-xs tabular-nums font-medium text-emerald-600 dark:text-emerald-400">
                          <TrendingUp className="h-3 w-3 opacity-60" />
                          ${formatRevenue(p.revenue_30d)}
                        </span>
                      </div>
                    ))}
                  </div>
                )}

                {/* 底部 */}
                <div className="flex items-center justify-between">
                  <span className="text-xs text-content-muted">
                    {topic.product_count} {isEn ? 'products' : '个产品'}
                  </span>
                  <div className="flex items-center gap-1.5 text-xs text-content-muted group-hover:text-brand-500 transition-colors duration-200">
                    <span>{isEn ? 'Explore' : '探索'}</span>
                    <ArrowRight className="h-3.5 w-3.5 transition-transform duration-200 group-hover:translate-x-0.5" />
                  </div>
                </div>
              </Card>
            </Link>
          )
        })}
        </div>
        
        {/* 右侧渐变提示 */}
        {canScrollRight && (
          <div className="absolute right-0 top-0 bottom-0 w-12 bg-gradient-to-l from-background to-transparent z-10 pointer-events-none" />
        )}
      </div>
    </section>
  )
}
