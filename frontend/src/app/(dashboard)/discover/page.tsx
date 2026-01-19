'use client'

import { useLocale } from '@/contexts/LocaleContext'
import { TodayCuration } from './components/TodayCuration'
import { TopicCollections } from './components/TopicCollections'
import { SuccessBreakdown } from './components/SuccessBreakdown'
import { CreatorUniverse } from './components/CreatorUniverse'
import { ForYouSection } from './components/ForYouSection'
import { Sparkles, Compass } from 'lucide-react'

export default function DiscoverPage() {
  const { t } = useLocale()

  return (
    <div className="space-y-8">
      {/* 欢迎横幅 */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-brand-500/10 via-brand-400/5 to-accent-secondary/10 border border-brand-500/20 p-6 md:p-8">
        <div className="absolute top-0 right-0 w-64 h-64 bg-brand-500/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2" />
        <div className="absolute bottom-0 left-0 w-48 h-48 bg-accent-secondary/10 rounded-full blur-3xl translate-y-1/2 -translate-x-1/2" />
        <div className="relative">
          <div className="flex items-center gap-4 mb-4">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-brand-500 via-brand-600 to-accent-secondary flex items-center justify-center shadow-lg shadow-brand-500/20">
              <Compass className="h-7 w-7 text-white" />
            </div>
            <div>
              <h1 className="text-2xl md:text-3xl font-display font-bold tracking-tight bg-gradient-to-r from-content-primary via-content-primary to-brand-600 dark:to-brand-400 bg-clip-text text-transparent">
                {t('discover.title')}
              </h1>
              <p className="text-sm text-content-secondary mt-1 font-medium">
                {t('discover.subtitle')}
              </p>
            </div>
          </div>
          <div className="flex flex-wrap gap-4 mt-5">
            <div className="flex items-center gap-2.5 text-sm text-content-secondary font-medium">
              <div className="w-8 h-8 rounded-lg bg-brand-500/10 flex items-center justify-center">
                <Sparkles className="h-4 w-4 text-brand-500" />
              </div>
              <span>AI 每日策展，发现隐藏机会</span>
            </div>
          </div>
        </div>
      </div>

      {/* 今日 AI 策展 */}
      <div id="curations">
        <TodayCuration />
      </div>

      {/* 主题合集 */}
      <TopicCollections />

      {/* 爆款解剖 */}
      <SuccessBreakdown />

      {/* 创作者宇宙 */}
      <CreatorUniverse />

      {/* 为你推荐 */}
      <ForYouSection />
    </div>
  )
}
