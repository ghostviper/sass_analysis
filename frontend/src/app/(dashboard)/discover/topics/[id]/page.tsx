'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import Link from 'next/link'
import Image from 'next/image'
import { useLocale } from '@/contexts/LocaleContext'
import { Card } from '@/components/ui/Card'
import { 
  ArrowLeft, 
  Loader2, 
  Sparkles,
  TrendingUp,
  ChevronLeft,
  ChevronRight,
  Package
} from 'lucide-react'
import type { TopicDetailResponse, ProductInTopic } from '@/types/discover'
import { getTopicDetail, formatRevenue } from '@/lib/api/discover'

// Curiosity-sparking CTA texts (bilingual)
const CTA_VARIANTS = {
  zh: [
    '这个方向适合我吗？',
    '帮我分析一下可行性',
    '我能做类似的吗？',
    '深入了解这个机会',
  ],
  en: [
    'Is this right for me?',
    'Analyze feasibility for me',
    'Can I build something similar?',
    'Explore this opportunity',
  ]
}

export default function TopicDetailPage() {
  const params = useParams()
  const router = useRouter()
  const { locale } = useLocale()
  const topicId = params.id as string
  const isEn = locale === 'en'
  
  const [data, setData] = useState<TopicDetailResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [page, setPage] = useState(1)

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true)
        const result = await getTopicDetail(topicId, { page, limit: 20, sort: 'revenue' })
        setData(result)
      } catch (err) {
        setError(isEn ? 'Failed to load' : '加载失败')
        console.error('Failed to fetch topic detail:', err)
      } finally {
        setLoading(false)
      }
    }
    if (topicId) {
      fetchData()
    }
  }, [topicId, page, isEn])

  // Get localized text
  const getTitle = () => {
    if (!data) return ''
    return isEn ? (data.topic.title_en || data.topic.title) : (data.topic.title_zh || data.topic.title)
  }
  const getDescription = () => {
    if (!data) return ''
    return isEn ? (data.topic.description_en || data.topic.description) : (data.topic.description_zh || data.topic.description)
  }

  if (loading && !data) {
    return (
      <div className="flex items-center justify-center py-24">
        <Loader2 className="h-8 w-8 animate-spin text-brand-500" />
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="text-center py-24">
        <p className="text-content-muted mb-4">{error || (isEn ? 'Topic not found' : '专题不存在')}</p>
        <button
          onClick={() => router.back()}
          className="text-brand-500 hover:underline"
        >
          {isEn ? 'Go back' : '返回'}
        </button>
      </div>
    )
  }

  const { topic, products, pagination } = data

  return (
    <div className="space-y-8">
      {/* Back button */}
      <Link
        href="/discover"
        className="inline-flex items-center gap-2 text-sm text-content-muted hover:text-content-primary transition-colors"
      >
        <ArrowLeft className="h-4 w-4" />
        {isEn ? 'Back to Discover' : '返回发现页'}
      </Link>

      {/* Topic Header - Clean, minimal design */}
      <div className="space-y-4">
        <h1 className="text-2xl md:text-3xl font-display font-bold text-content-primary">
          {getTitle()}
        </h1>
        <p className="text-content-secondary text-base leading-relaxed max-w-2xl">
          {getDescription()}
        </p>
        <div className="text-sm text-content-muted">
          {topic.product_count} {isEn ? 'products' : '个产品'}
        </div>
      </div>

      {/* Product Grid */}
      <div className="space-y-4">
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {products.map((product) => (
            <ProductCard 
              key={product.id} 
              product={product} 
              topicId={topicId}
              isEn={isEn}
            />
          ))}
        </div>

        {/* Pagination */}
        {pagination.total_pages > 1 && (
          <div className="flex items-center justify-center gap-3 pt-6">
            <button
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
              className="w-10 h-10 rounded-lg bg-surface border border-surface-border flex items-center justify-center disabled:opacity-30 disabled:cursor-not-allowed hover:border-brand-500/30 transition-colors"
            >
              <ChevronLeft className="h-5 w-5" />
            </button>
            <span className="text-sm text-content-muted tabular-nums min-w-[80px] text-center">
              {page} / {pagination.total_pages}
            </span>
            <button
              onClick={() => setPage(p => Math.min(pagination.total_pages, p + 1))}
              disabled={page === pagination.total_pages}
              className="w-10 h-10 rounded-lg bg-surface border border-surface-border flex items-center justify-center disabled:opacity-30 disabled:cursor-not-allowed hover:border-brand-500/30 transition-colors"
            >
              <ChevronRight className="h-5 w-5" />
            </button>
          </div>
        )}
      </div>
    </div>
  )
}


interface ProductCardProps {
  product: ProductInTopic
  topicId: string
  isEn: boolean
}

function ProductCard({ product, topicId, isEn }: ProductCardProps) {
  // Random CTA text for variety
  const ctaTexts = isEn ? CTA_VARIANTS.en : CTA_VARIANTS.zh
  const ctaText = ctaTexts[product.id % ctaTexts.length]
  
  // Build chat URL with pre-filled message
  const chatMessage = isEn 
    ? `I'm interested in "${product.name}". Can you analyze if I could build something similar?`
    : `我对「${product.name}」很感兴趣，帮我分析一下我能不能做类似的产品？`
  const chatUrl = `/assistant?message=${encodeURIComponent(chatMessage)}`

  return (
    <Link href={`/products/${product.slug}`} className="block group">
      <Card hover className="h-full">
        {/* Header: Logo + Name + Revenue */}
        <div className="flex items-start gap-3 mb-3">
          {/* Logo */}
          <div className="w-12 h-12 rounded-xl bg-surface-hover border border-surface-border flex items-center justify-center flex-shrink-0 overflow-hidden">
            {product.logo_url ? (
              <Image
                src={product.logo_url}
                alt={product.name}
                width={48}
                height={48}
                className="w-full h-full object-cover"
                unoptimized
              />
            ) : (
              <Package className="h-6 w-6 text-content-muted" />
            )}
          </div>
          
          {/* Name + Category */}
          <div className="flex-1 min-w-0">
            <h3 className="font-semibold text-content-primary group-hover:text-brand-500 transition-colors truncate">
              {product.name}
            </h3>
            {product.category && (
              <span className="text-xs text-content-muted">{product.category}</span>
            )}
          </div>
          
          {/* Revenue */}
          {product.revenue_30d && (
            <div className="flex items-center gap-1 text-emerald-600 dark:text-emerald-400 flex-shrink-0">
              <TrendingUp className="h-3.5 w-3.5" />
              <span className="text-sm font-semibold tabular-nums">
                ${formatRevenue(product.revenue_30d)}
              </span>
            </div>
          )}
        </div>

        {/* Tags */}
        {product.key_tags.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mb-4">
            {product.key_tags.slice(0, 3).map((tag, idx) => (
              <span
                key={idx}
                className="px-2 py-0.5 rounded-md bg-surface-hover text-xs text-content-secondary"
              >
                {tag.value}
              </span>
            ))}
          </div>
        )}

        {/* CTA Link - Opens chat in new tab */}
        <a
          href={chatUrl}
          target="_blank"
          rel="noopener noreferrer"
          onClick={(e) => e.stopPropagation()}
          className="flex items-center gap-1.5 text-sm text-brand-500 hover:text-brand-600 transition-colors"
        >
          <Sparkles className="h-3.5 w-3.5" />
          <span>{ctaText}</span>
        </a>
      </Card>
    </Link>
  )
}
