'use client'

import { useLocale } from '@/contexts/LocaleContext'
import { Sparkles, Calendar, TrendingUp } from 'lucide-react'
import { useState, useEffect } from 'react'
import type { Curation } from '@/types/discover'
import { getCurations } from '@/lib/api/discover'
import { CurationCard } from './components/CurationCard'
import { CurationFilters } from './components/CurationFilters'
import { CurationsPageSkeleton } from '@/components/ui/Loading'

export default function CurationsPage() {
  const { t, locale } = useLocale()
  const [curations, setCurations] = useState<Curation[]>([])
  const [loading, setLoading] = useState(true)
  const [filteredCurations, setFilteredCurations] = useState<Curation[]>([])
  const [selectedType, setSelectedType] = useState<string>('all')
  const [sortBy, setSortBy] = useState<'date' | 'products'>('date')

  const isEn = locale === 'en'

  useEffect(() => {
    async function fetchCurations() {
      try {
        setLoading(true)
        const data = await getCurations({ limit: 50, days: 90 })
        setCurations(data.curations)
        setFilteredCurations(data.curations)
      } catch (err) {
        console.error('Failed to fetch curations:', err)
      } finally {
        setLoading(false)
      }
    }
    fetchCurations()
  }, [])

  // 筛选和排序
  useEffect(() => {
    let filtered = [...curations]

    // 按类型筛选
    if (selectedType !== 'all') {
      filtered = filtered.filter(c => c.curation_type === selectedType)
    }

    // 排序
    if (sortBy === 'date') {
      filtered.sort((a, b) => {
        const dateA = new Date(a.curation_date).getTime()
        const dateB = new Date(b.curation_date).getTime()
        return dateB - dateA
      })
    } else {
      filtered.sort((a, b) => b.products.length - a.products.length)
    }

    setFilteredCurations(filtered)
  }, [curations, selectedType, sortBy])

  if (loading) {
    return <CurationsPageSkeleton />
  }

  return (
    <div className="space-y-6">
      {/* 欢迎横幅 */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-brand-500/10 via-brand-400/5 to-accent-secondary/10 border border-brand-500/20 p-6 md:p-8">
        <div className="absolute top-0 right-0 w-64 h-64 bg-brand-500/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2" />
        <div className="absolute bottom-0 left-0 w-48 h-48 bg-accent-secondary/10 rounded-full blur-3xl translate-y-1/2 -translate-x-1/2" />
        <div className="relative">
          <div className="flex items-center gap-4 mb-4">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-brand-500 via-brand-600 to-accent-secondary flex items-center justify-center shadow-lg shadow-brand-500/20">
              <Sparkles className="h-7 w-7 text-white" />
            </div>
            <div>
              <h1 className="text-2xl md:text-3xl font-display font-bold tracking-tight bg-gradient-to-r from-content-primary via-content-primary to-brand-600 dark:to-brand-400 bg-clip-text text-transparent">
                {isEn ? 'AI Curations' : '每日 AI 策展'}
              </h1>
              <p className="text-sm text-content-secondary mt-1 font-medium">
                {isEn ? 'Discover hidden opportunities through AI-curated insights' : 'AI 每日精选，发现隐藏的产品机会'}
              </p>
            </div>
          </div>
          <div className="flex flex-wrap gap-4 mt-5">
            <div className="flex items-center gap-2.5 text-sm text-content-secondary font-medium">
              <div className="w-8 h-8 rounded-lg bg-brand-500/10 flex items-center justify-center">
                <Calendar className="h-4 w-4 text-brand-500" />
              </div>
              <span>{isEn ? 'Updated daily with fresh insights' : '每日更新，持续发现新机会'}</span>
            </div>
          </div>
        </div>
      </div>

      {/* 筛选器 */}
      <CurationFilters
        selectedType={selectedType}
        onTypeChange={setSelectedType}
        sortBy={sortBy}
        onSortChange={setSortBy}
        totalCount={curations.length}
        filteredCount={filteredCurations.length}
      />

      {/* 策展列表 */}
      {filteredCurations.length === 0 ? (
        <div className="text-center py-20">
          <div className="p-4 rounded-2xl bg-gradient-to-br from-brand-500/20 to-accent-secondary/20 inline-flex items-center justify-center mx-auto mb-4">
            <Sparkles className="h-8 w-8 text-brand-500" />
          </div>
          <h3 className="text-lg font-semibold text-content-primary mb-2">
            {isEn ? 'No curations found' : '暂无策展内容'}
          </h3>
          <p className="text-sm text-content-muted">
            {isEn ? 'Try adjusting your filters or check back later' : '尝试调整筛选条件或稍后再来'}
          </p>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 gap-5">
          {filteredCurations.map((curation, index) => (
            <CurationCard
              key={curation.id}
              curation={curation}
              index={index}
            />
          ))}
        </div>
      )}

      {/* 统计信息 */}
      {filteredCurations.length > 0 && (
        <div className="flex items-center justify-center gap-2 text-sm text-content-muted py-4">
          <TrendingUp className="h-4 w-4" />
          <span>
            {isEn 
              ? `Showing ${filteredCurations.length} of ${curations.length} curations`
              : `显示 ${filteredCurations.length} / ${curations.length} 条策展`
            }
          </span>
        </div>
      )}
    </div>
  )
}
