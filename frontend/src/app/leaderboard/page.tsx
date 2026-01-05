'use client'

import { useEffect, useState, useCallback, useMemo } from 'react'
import Image from 'next/image'
import { motion, AnimatePresence } from 'framer-motion'
import { Card } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import {
  getFounderLeaderboard,
  getLeaderboardStats,
  type FounderLeaderboardItem,
  type LeaderboardSortField,
  type LeaderboardStats,
} from '@/lib/api'
import { formatCurrency, cn } from '@/lib/utils'
import { useLocale } from '@/contexts/LocaleContext'
import {
  Trophy,
  Share2,
  Check,
  ChevronLeft,
  ChevronRight,
  Package,
  Users,
  ArrowDownWideNarrow,
  Medal,
  TrendingUp,
  Twitter,
  Linkedin,
} from 'lucide-react'

type RankingDimension = {
  key: LeaderboardSortField
  label: string
  getValue: (f: FounderLeaderboardItem) => number
  format: (value: number, t: (key: string) => string) => string
}

export default function LeaderboardPage() {
  const { t, locale } = useLocale()
  const [founders, setFounders] = useState<FounderLeaderboardItem[]>([])
  const [stats, setStats] = useState<LeaderboardStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [sortBy, setSortBy] = useState<LeaderboardSortField>('total_revenue')
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const [totalPages, setTotalPages] = useState(0)
  const [copied, setCopied] = useState(false)
  const pageSize = 20

  // 动态生成排名维度配置，支持国际化
  const RANKING_DIMENSIONS: RankingDimension[] = useMemo(() => [
    {
      key: 'total_revenue',
      label: t('leaderboard.dimensions.total_revenue'),
      getValue: (f) => f.total_revenue,
      format: (v) => formatCurrency(v),
    },
    {
      key: 'product_count',
      label: t('leaderboard.dimensions.product_count'),
      getValue: (f) => f.product_count,
      format: (v, t) => locale === 'zh-CN' ? `${v} 个` : `${v}`,
    },
    {
      key: 'avg_revenue',
      label: t('leaderboard.dimensions.avg_revenue'),
      getValue: (f) => f.avg_revenue,
      format: (v) => formatCurrency(v),
    },
    {
      key: 'max_growth',
      label: t('leaderboard.dimensions.max_growth'),
      getValue: (f) => f.max_growth,
      format: (v) => `${v > 0 ? '+' : ''}${v.toFixed(1)}%`,
    },
    {
      key: 'followers',
      label: t('leaderboard.dimensions.followers'),
      getValue: (f) => f.followers,
      format: (v) => v >= 1000 ? `${(v / 1000).toFixed(1)}K` : v.toString(),
    },
  ], [t, locale])

  const currentDimension = RANKING_DIMENSIONS.find(d => d.key === sortBy)!

  const fetchData = useCallback(async () => {
    setLoading(true)
    try {
      const leaderboardData = await getFounderLeaderboard({
        sort_by: sortBy,
        sort_order: 'desc',
        limit: pageSize,
        page,
      })

      setFounders(leaderboardData.items)
      setTotal(leaderboardData.total)
      setTotalPages(leaderboardData.pages)
    } catch (err) {
      console.error('Failed to fetch leaderboard:', err)
    } finally {
      setLoading(false)
    }
  }, [sortBy, page])

  useEffect(() => {
    getLeaderboardStats()
      .then(setStats)
      .catch((err) => console.error('Failed to fetch stats:', err))
  }, [])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  useEffect(() => {
    setPage(1)
  }, [sortBy])

  const handleShare = async () => {
    const shareUrl = `${window.location.origin}/leaderboard?sort=${sortBy}`
    const shareText = `${t('leaderboard.shareTitle')} - ${currentDimension.label}\n${t('leaderboard.shareText')}`

    if (navigator.share) {
      try {
        await navigator.share({ title: t('leaderboard.shareTitle'), text: shareText, url: shareUrl })
      } catch {
        // User cancelled
      }
    } else {
      await navigator.clipboard.writeText(`${shareText}\n${shareUrl}`)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  return (
    <div className="space-y-6">
      {/* 页面头部 - 统计信息整合在标题区 */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-display font-bold text-content-primary flex items-center gap-3">
            <Trophy className="h-6 w-6 text-accent-warning" />
            {t('leaderboard.title')}
          </h1>
          {stats && (
            <p className="text-body mt-1">
              {locale === 'zh-CN' ? (
                <>
                  {t('common.total')} <span className="font-medium text-content-primary">{stats.total_founders}</span> 位开发者，
                  总月收入 <span className="font-mono font-medium text-content-primary">{formatCurrency(stats.total_revenue)}</span>
                </>
              ) : (
                <>
                  <span className="font-medium text-content-primary">{stats.total_founders}</span> founders,
                  total MRR <span className="font-mono font-medium text-content-primary">{formatCurrency(stats.total_revenue)}</span>
                </>
              )}
            </p>
          )}
        </div>
        <button
          onClick={handleShare}
          className="btn btn-secondary self-start sm:self-auto"
        >
          {copied ? <Check className="h-4 w-4 mr-2" /> : <Share2 className="h-4 w-4 mr-2" />}
          {copied ? t('common.copied') : t('leaderboard.shareList')}
        </button>
      </div>

      {/* 筛选栏 */}
      <div className="flex flex-wrap items-center gap-3">
        <div className="flex items-center gap-2 text-sm text-content-muted">
          <ArrowDownWideNarrow className="h-4 w-4" />
          <span>{t('leaderboard.sort')}</span>
        </div>
        <div className="flex flex-wrap gap-2">
          {RANKING_DIMENSIONS.map((dim) => (
            <button
              key={dim.key}
              onClick={() => setSortBy(dim.key)}
              className={cn(
                'px-3 py-1.5 rounded-full text-sm font-medium transition-all',
                sortBy === dim.key
                  ? 'bg-accent-primary text-white'
                  : 'bg-surface-border/50 text-content-secondary hover:bg-surface-border'
              )}
            >
              {dim.label}
            </button>
          ))}
        </div>
        <span className="text-caption ml-auto">
          {t('common.total')} {total} {locale === 'zh-CN' ? '位' : ''}
        </span>
      </div>

      {/* 排行榜列表 */}
      <div className="min-h-[400px]">
        <AnimatePresence mode="wait">
          {loading ? (
            <motion.div
              key="skeleton"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.15 }}
            >
              <LeaderboardSkeleton />
            </motion.div>
          ) : founders.length === 0 ? (
            <div className="text-center py-12 text-content-muted">
              {t('leaderboard.noData')}
            </div>
          ) : (
            <motion.div
              key={`${sortBy}-${page}`}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.15 }}
              className="space-y-2"
            >
              {founders.map((founder, index) => (
                <FounderRow
                  key={founder.username}
                  founder={founder}
                  index={index}
                  dimension={currentDimension}
                  sortBy={sortBy}
                  t={t}
                />
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* 分页 */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
            className="btn btn-secondary"
          >
            <ChevronLeft className="h-4 w-4" />
          </button>
          <span className="px-4 text-sm text-content-secondary">
            {page} / {totalPages}
          </span>
          <button
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
            className="btn btn-secondary"
          >
            <ChevronRight className="h-4 w-4" />
          </button>
        </div>
      )}
    </div>
  )
}

interface FounderRowProps {
  founder: FounderLeaderboardItem
  index: number
  dimension: RankingDimension
  sortBy: LeaderboardSortField
  t: (key: string) => string
}

function FounderRow({ founder, index, dimension, sortBy, t }: FounderRowProps) {
  const [imgError, setImgError] = useState(false)
  const avatarUrl = founder.avatar_url || `https://unavatar.io/x/${founder.username}`

  // 奖杯颜色配置
  const getRankStyle = (rank: number) => {
    if (rank === 1) return { bg: 'bg-gradient-to-br from-yellow-400 to-yellow-600', Icon: Trophy, color: 'text-yellow-400' }
    if (rank === 2) return { bg: 'bg-gradient-to-br from-gray-300 to-gray-500', Icon: Medal, color: 'text-gray-400' }
    if (rank === 3) return { bg: 'bg-gradient-to-br from-amber-600 to-amber-800', Icon: Medal, color: 'text-amber-600' }
    return null
  }

  // 获取社交平台图标
  const getSocialIcon = (platform: string) => {
    const p = platform?.toLowerCase() || ''
    if (p.includes('linkedin')) {
      return { Icon: Linkedin, color: 'hover:text-[#0A66C2]' }
    }
    // 默认为 X/Twitter
    return { Icon: Twitter, color: 'hover:text-content-primary' }
  }

  const rankStyle = getRankStyle(founder.rank)
  const isTop3 = founder.rank <= 3
  const socialIcon = getSocialIcon(founder.social_platform)

  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.2, delay: index * 0.02 }}
    >
      <div
        className={cn(
          'flex items-center gap-4 p-4 rounded-xl transition-all',
          'bg-surface border border-surface-border/50',
          'hover:border-surface-border hover:shadow-sm',
          isTop3 && 'border-accent-warning/20'
        )}
      >
        {/* 排名 */}
        <div className="w-10 flex justify-center flex-shrink-0">
          {rankStyle ? (
            <rankStyle.Icon className={cn('h-6 w-6', rankStyle.color)} />
          ) : (
            <span className="text-lg font-mono font-bold text-content-muted">
              {founder.rank}
            </span>
          )}
        </div>

        {/* 头像 - 可点击 */}
        <a
          href={founder.social_url || `https://x.com/${founder.username}`}
          target="_blank"
          rel="noopener noreferrer"
          className="w-11 h-11 rounded-full overflow-hidden flex-shrink-0 border-2 border-surface-border hover:border-accent-primary transition-colors"
        >
          {!imgError ? (
            <Image
              src={avatarUrl}
              alt={founder.name || founder.username}
              width={44}
              height={44}
              className="w-full h-full object-cover"
              onError={() => setImgError(true)}
              unoptimized
            />
          ) : (
            <div className="w-full h-full bg-gradient-to-br from-accent-primary/20 to-accent-secondary/20 flex items-center justify-center">
              <span className="text-sm font-bold text-accent-primary">
                {(founder.name || founder.username).charAt(0).toUpperCase()}
              </span>
            </div>
          )}
        </a>

        {/* 信息 */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-0.5">
            {/* 名字 - 可点击 */}
            <a
              href={founder.social_url || `https://x.com/${founder.username}`}
              target="_blank"
              rel="noopener noreferrer"
              className={cn(
                'font-medium truncate hover:text-accent-primary transition-colors',
                isTop3 ? 'text-content-primary' : 'text-content-primary'
              )}
            >
              {founder.name || founder.username}
            </a>
            {/* 社交平台图标 - 可点击 */}
            <a
              href={founder.social_url || `https://x.com/${founder.username}`}
              target="_blank"
              rel="noopener noreferrer"
              className={cn(
                'text-content-muted transition-colors flex-shrink-0',
                socialIcon.color
              )}
            >
              <socialIcon.Icon className="h-3.5 w-3.5" />
            </a>
          </div>
          <div className="flex items-center gap-3 text-caption">
            <span>@{founder.username}</span>
            <span className="flex items-center gap-1">
              <Package className="h-3 w-3" />
              {founder.product_count}
            </span>
            {founder.followers > 0 && (
              <span className="flex items-center gap-1">
                <Users className="h-3 w-3" />
                {founder.followers >= 1000 ? `${(founder.followers / 1000).toFixed(1)}K` : founder.followers}
              </span>
            )}
            {founder.max_growth > 0 && sortBy !== 'max_growth' && (
              <span className="text-accent-success flex items-center gap-1">
                <TrendingUp className="h-3 w-3" />
                +{founder.max_growth.toFixed(1)}%
              </span>
            )}
          </div>
        </div>

        {/* 核心指标 */}
        <div className="text-right flex-shrink-0">
          <div className={cn(
            'font-mono font-bold tabular-nums text-lg',
            isTop3 ? 'text-accent-warning' : 'text-content-primary'
          )}>
            {dimension.format(dimension.getValue(founder), t)}
          </div>
          <div className="text-caption">{dimension.label}</div>
        </div>
      </div>
    </motion.div>
  )
}

function LeaderboardSkeleton() {
  return (
    <div className="space-y-2">
      {Array.from({ length: 10 }).map((_, i) => (
        <div key={i} className="flex items-center gap-4 p-4 rounded-xl bg-surface border border-surface-border/50">
          <div className="w-10 flex justify-center">
            <div className="w-6 h-6 bg-surface-border rounded animate-pulse" />
          </div>
          <div className="w-11 h-11 bg-surface-border rounded-full animate-pulse" />
          <div className="flex-1">
            <div className="h-4 w-32 bg-surface-border rounded animate-pulse mb-2" />
            <div className="h-3 w-48 bg-surface-border rounded animate-pulse" />
          </div>
          <div className="text-right">
            <div className="h-6 w-20 bg-surface-border rounded animate-pulse mb-1" />
            <div className="h-3 w-12 bg-surface-border rounded animate-pulse ml-auto" />
          </div>
        </div>
      ))}
    </div>
  )
}
