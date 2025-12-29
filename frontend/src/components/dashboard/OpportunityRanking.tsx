'use client'

import Link from 'next/link'
import { Card, CardHeader } from '@/components/ui/Card'
import { Badge, ComplexityBadge } from '@/components/ui/Badge'
import { formatCurrency } from '@/lib/utils'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import {
  faArrowRight,
  faMedal,
  faCheck,
  faBolt,
} from '@fortawesome/free-solid-svg-icons'
import type { OpportunityProduct } from '@/types'

interface OpportunityRankingProps {
  products: OpportunityProduct[]
  title?: string
  subtitle?: string
  limit?: number
}

export function OpportunityRanking({
  products,
  title = '机会榜单',
  subtitle = 'TOP 产品推荐',
  limit = 10,
}: OpportunityRankingProps) {
  const displayProducts = products.slice(0, limit)

  return (
    <Card>
      <CardHeader
        title={title}
        subtitle={subtitle}
        action={
          <Link
            href="/products?filter=opportunities"
            className="flex items-center gap-1 text-sm text-accent-primary hover:underline"
          >
            查看全部
            <FontAwesomeIcon icon={faArrowRight} className="h-3 w-3" />
          </Link>
        }
      />

      <div className="space-y-2">
        {displayProducts.map((item, index) => (
          <OpportunityItem
            key={item.startup.id}
            product={item}
            rank={index + 1}
          />
        ))}

        {displayProducts.length === 0 && (
          <div className="text-center py-8 text-content-muted">
            暂无机会产品数据
          </div>
        )}
      </div>
    </Card>
  )
}

// 获取排名图标配置
function getRankDisplay(rank: number): { icon: React.ReactNode; className: string; ismedal: boolean } {
  switch (rank) {
    case 1:
      return {
        icon: <span className="text-2xl">🥇</span>,
        className: '',
        isMedal: true
      }
    case 2:
      return {
        icon: <span className="text-2xl">🥈</span>,
        className: '',
        isModal: true
      }
    case 3:
      return {
        icon: <span className="text-2xl">🥉</span>,
        className: '',
        isModal: true
      }
    default:
      return {
        icon: <span className="text-xs font-bold">{rank}</span>,
        className: 'w-8 h-8 rounded-full bg-surface border border-surface-border flex items-center justify-center text-content-muted',
        isModal: false
      }
  }
}

interface OpportunityItemProps {
  product: OpportunityProduct
  rank: number
}

function OpportunityItem({ product, rank }: OpportunityItemProps) {
  const { startup, analysis } = product
  const rankDisplay = getRankDisplay(rank)
  const isTopThree = rank <= 3

  // 计算匹配的组合数量
  const comboMatches = [
    analysis.combo1_match,
    analysis.combo2_match,
    analysis.combo3_match,
  ].filter(Boolean).length

  return (
    <Link
      href={`/products/${startup.slug}`}
      className="flex items-center gap-3 p-3 -mx-3 rounded-xl hover:bg-surface/50 transition-colors group"
    >
      {/* 排名 */}
      {isTopThree ? (
        <div className="w-8 h-8 flex items-center justify-center flex-shrink-0">
          {rankDisplay.icon}
        </div>
      ) : (
        <div className={rankDisplay.className}>
          {rankDisplay.icon}
        </div>
      )}

      {/* 产品信息 */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-content-primary group-hover:text-accent-primary transition-colors truncate">
            {startup.name}
          </span>
          {analysis.is_product_driven && (
            <Badge variant="success" size="sm">
              <FontAwesomeIcon icon={faBolt} className="h-2.5 w-2.5" />
              产品驱动
            </Badge>
          )}
        </div>
        <div className="flex items-center gap-3 mt-0.5 text-xs text-content-muted">
          <span>{startup.category || '未分类'}</span>
          {comboMatches > 0 && (
            <span className="flex items-center gap-1 text-accent-success">
              <FontAwesomeIcon icon={faCheck} className="h-2.5 w-2.5" />
              {comboMatches} 组合
            </span>
          )}
        </div>
      </div>

      {/* 右侧信息 */}
      <div className="flex items-center gap-3 flex-shrink-0">
        <ComplexityBadge level={analysis.tech_complexity_level} />
        <div className="text-right">
          <div className="font-mono text-sm font-medium text-content-primary tabular-nums">
            {formatCurrency(startup.revenue_30d)}
          </div>
          <div className="text-xs text-content-muted">月收入</div>
        </div>
      </div>
    </Link>
  )
}

// 精简版本（用于侧边栏等）
interface OpportunityRankingCompactProps {
  products: OpportunityProduct[]
  limit?: number
}

export function OpportunityRankingCompact({
  products,
  limit = 5,
}: OpportunityRankingCompactProps) {
  const displayProducts = products.slice(0, limit)

  return (
    <Card>
      <CardHeader
        title="机会产品"
        subtitle="快速发现"
        action={
          <Link
            href="/products?filter=opportunities"
            className="text-xs text-accent-primary hover:underline"
          >
            更多
          </Link>
        }
      />

      <div className="space-y-2">
        {displayProducts.map((item, index) => (
          <Link
            key={item.startup.id}
            href={`/products/${item.startup.slug}`}
            className="flex items-center justify-between p-2 -mx-2 rounded hover:bg-surface/50 transition-colors"
          >
            <div className="flex items-center gap-2 min-w-0">
              <span className="text-xs text-content-muted w-4">{index + 1}</span>
              <span className="text-sm text-content-primary truncate">
                {item.startup.name}
              </span>
            </div>
            <span className="text-xs font-mono text-content-secondary">
              {formatCurrency(item.startup.revenue_30d)}
            </span>
          </Link>
        ))}
      </div>
    </Card>
  )
}

// 骨架屏
export function OpportunityRankingSkeleton() {
  return (
    <Card>
      <div className="flex items-center justify-between mb-4">
        <div>
          <div className="h-5 w-24 bg-surface-border rounded mb-1" />
          <div className="h-4 w-32 bg-surface-border rounded" />
        </div>
        <div className="h-4 w-16 bg-surface-border rounded" />
      </div>

      <div className="space-y-2">
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="flex items-center gap-3 p-3 animate-pulse">
            <div className="w-8 h-8 bg-surface-border rounded-full" />
            <div className="flex-1">
              <div className="h-4 w-32 bg-surface-border rounded mb-1.5" />
              <div className="h-3 w-24 bg-surface-border rounded" />
            </div>
            <div className="h-6 w-14 bg-surface-border rounded-full" />
            <div className="text-right">
              <div className="h-4 w-14 bg-surface-border rounded mb-1" />
              <div className="h-3 w-10 bg-surface-border rounded" />
            </div>
          </div>
        ))}
      </div>
    </Card>
  )
}
