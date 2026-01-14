'use client'

import { useLocale } from '@/contexts/LocaleContext'
import { Card } from '@/components/ui/Card'
import { Users, ArrowRight, ExternalLink, Package } from 'lucide-react'
import Link from 'next/link'

// 模拟数据 - 创作者宇宙
const mockCreators = [
  {
    id: 1,
    name: 'Pieter Levels',
    handle: '@levelsio',
    avatar: '🚀',
    bio: '不爱写推特，但很会赚钱的人',
    tag: '连续创业者',
    tagColor: 'amber',
    products: [
      { name: 'Nomad List', mrr: '$45k' },
      { name: 'Remote OK', mrr: '$35k' },
      { name: 'Photo AI', mrr: '$80k' },
    ],
    totalMRR: '$160k+',
    followers: '450k',
  },
  {
    id: 2,
    name: 'Tony Dinh',
    handle: '@tdinh_me',
    avatar: '⚡',
    bio: '产品比人火的创作者',
    tag: '效率工具专家',
    tagColor: 'blue',
    products: [
      { name: 'TypingMind', mrr: '$50k' },
      { name: 'DevUtils', mrr: '$8k' },
      { name: 'Xnapper', mrr: '$5k' },
    ],
    totalMRR: '$63k+',
    followers: '85k',
  },
  {
    id: 3,
    name: 'Marc Lou',
    handle: '@marc_louvion',
    avatar: '🎯',
    bio: '靠教程起家，靠 SaaS 变现',
    tag: '内容创作者',
    tagColor: 'violet',
    products: [
      { name: 'ShipFast', mrr: '$40k' },
      { name: 'ByeDispute', mrr: '$5k' },
    ],
    totalMRR: '$45k+',
    followers: '120k',
  },
  {
    id: 4,
    name: 'Damon Chen',
    handle: '@damengchen',
    avatar: '🌟',
    bio: '一年只发布 2 个产品的人',
    tag: '精品路线',
    tagColor: 'emerald',
    products: [
      { name: 'Testimonial.to', mrr: '$25k' },
      { name: 'Gumroad Clone', mrr: '$3k' },
    ],
    totalMRR: '$28k+',
    followers: '45k',
  },
]

export function CreatorUniverse() {
  const { t } = useLocale()

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
        {mockCreators.map((creator) => (
          <Card
            key={creator.id}
            hover
            className="group"
          >
            {/* 头像和基本信息 */}
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

            {/* 标签 */}
            <div className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-medium mb-2
              ${creator.tagColor === 'amber' ? 'bg-amber-500/10 text-amber-600 dark:text-amber-400' : ''}
              ${creator.tagColor === 'blue' ? 'bg-blue-500/10 text-blue-600 dark:text-blue-400' : ''}
              ${creator.tagColor === 'violet' ? 'bg-violet-500/10 text-violet-600 dark:text-violet-400' : ''}
              ${creator.tagColor === 'emerald' ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400' : ''}
            `}>
              {creator.tag}
            </div>

            {/* Bio */}
            <p className="text-xs text-content-tertiary mb-3 line-clamp-2">
              {creator.bio}
            </p>

            {/* 产品列表 */}
            <div className="space-y-1.5 mb-3">
              {creator.products.slice(0, 2).map((product, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between text-xs"
                >
                  <span className="text-content-secondary truncate">{product.name}</span>
                  <span className="font-mono text-emerald-600 dark:text-emerald-400 font-medium">
                    {product.mrr}
                  </span>
                </div>
              ))}
              {creator.products.length > 2 && (
                <span className="text-[10px] text-content-muted">
                  +{creator.products.length - 2} more
                </span>
              )}
            </div>

            {/* 统计 */}
            <div className="flex items-center justify-between pt-3 border-t border-surface-border/50">
              <div className="flex items-center gap-1 text-xs">
                <Package className="h-3 w-3 text-content-muted" />
                <span className="text-content-secondary">{creator.products.length}</span>
                <span className="text-content-muted">{t('discover.creatorUniverse.products')}</span>
              </div>
              <div className="text-xs font-mono font-medium text-brand-600 dark:text-brand-400">
                {creator.totalMRR}
              </div>
            </div>

            {/* 查看主页 */}
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
