'use client'

import { useState } from 'react'
import Image from 'next/image'
import { cn } from '@/lib/utils'

interface ProductLogoProps {
  name: string
  logoUrl?: string | null
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl'
  className?: string
}

const sizeMap = {
  xs: { container: 'w-8 h-8', text: 'text-sm', radius: 'rounded-lg' },
  sm: { container: 'w-10 h-10', text: 'text-base', radius: 'rounded-lg' },
  md: { container: 'w-12 h-12', text: 'text-lg', radius: 'rounded-xl' },
  lg: { container: 'w-16 h-16', text: 'text-2xl', radius: 'rounded-2xl' },
  xl: { container: 'w-20 h-20', text: 'text-3xl', radius: 'rounded-2xl' },
}

// 根据名称生成一致的渐变颜色
function getGradientColors(name: string): string {
  const gradients = [
    'from-blue-500/20 to-cyan-500/20',
    'from-purple-500/20 to-pink-500/20',
    'from-amber-500/20 to-orange-500/20',
    'from-emerald-500/20 to-teal-500/20',
    'from-rose-500/20 to-red-500/20',
    'from-indigo-500/20 to-violet-500/20',
    'from-lime-500/20 to-green-500/20',
    'from-fuchsia-500/20 to-purple-500/20',
  ]

  // 使用名称的哈希值来选择颜色
  let hash = 0
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash)
  }

  return gradients[Math.abs(hash) % gradients.length]
}

// 获取首字母
function getInitials(name: string): string {
  if (!name) return '?'

  // 如果是英文，取首字母
  const words = name.trim().split(/\s+/)
  if (words.length >= 2) {
    return (words[0][0] + words[1][0]).toUpperCase()
  }

  // 单个单词，取第一个字符
  return name.charAt(0).toUpperCase()
}

export function ProductLogo({ name, logoUrl, size = 'md', className }: ProductLogoProps) {
  const [imageError, setImageError] = useState(false)
  const sizeConfig = sizeMap[size]

  const showFallback = !logoUrl || imageError

  if (showFallback) {
    const gradientColors = getGradientColors(name)
    const initials = getInitials(name)

    return (
      <div
        className={cn(
          sizeConfig.container,
          sizeConfig.radius,
          'bg-gradient-to-br flex items-center justify-center flex-shrink-0',
          'border border-surface-border/30',
          gradientColors,
          className
        )}
      >
        <span className={cn(
          sizeConfig.text,
          'font-display font-bold text-content-primary/80'
        )}>
          {initials}
        </span>
      </div>
    )
  }

  return (
    <div
      className={cn(
        sizeConfig.container,
        sizeConfig.radius,
        'relative overflow-hidden flex-shrink-0',
        'bg-surface border border-surface-border/30',
        className
      )}
    >
      <Image
        src={logoUrl}
        alt={`${name} logo`}
        fill
        sizes={sizeConfig.container.split(' ')[0].replace('w-', '') + 'px'}
        className="object-contain p-1"
        onError={() => setImageError(true)}
        unoptimized
      />
    </div>
  )
}

export default ProductLogo
