'use client'

import { cn } from '@/lib/utils'
import { forwardRef } from 'react'

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'glass' | 'outline'
  hover?: boolean
  padding?: 'none' | 'sm' | 'md' | 'lg'
}

export const Card = forwardRef<HTMLDivElement, CardProps>(
  ({ className, variant = 'default', hover = false, padding = 'md', children, ...props }, ref) => {
    const variantStyles = {
      default: 'bg-surface/60 backdrop-blur-sm border border-surface-border',
      glass: 'bg-surface/40 backdrop-blur-md border border-white/5',
      outline: 'bg-transparent border border-surface-border',
    }

    const paddingStyles = {
      none: '',
      sm: 'p-4',
      md: 'p-6',
      lg: 'p-8',
    }

    return (
      <div
        ref={ref}
        className={cn(
          'rounded-xl shadow-card dark:shadow-card-dark transition-all duration-200',
          variantStyles[variant],
          paddingStyles[padding],
          hover && 'hover:shadow-card-hover dark:hover:shadow-card-dark-hover hover:border-accent-primary/30 hover:bg-surface/80 cursor-pointer',
          className
        )}
        {...props}
      >
        {children}
      </div>
    )
  }
)

Card.displayName = 'Card'

// 卡片标题
interface CardHeaderProps extends React.HTMLAttributes<HTMLDivElement> {
  title: string
  subtitle?: string
  action?: React.ReactNode
  icon?: React.ReactNode
}

export function CardHeader({ title, subtitle, action, icon, className, ...props }: CardHeaderProps) {
  return (
    <div className={cn('flex items-start justify-between mb-4', className)} {...props}>
      <div className="flex items-start gap-2.5">
        {icon && (
          <div className="flex-shrink-0 mt-0.5">
            {icon}
          </div>
        )}
        <div>
          <h3 className="text-heading">{title}</h3>
          {subtitle && (
            <p className="text-caption mt-1">{subtitle}</p>
          )}
        </div>
      </div>
      {action && <div>{action}</div>}
    </div>
  )
}

// 统计卡片
export type CardPattern = 'leaves' | 'stars' | 'light' | 'circles' | 'grass' | 'ribbons'

interface StatCardProps {
  title: string
  value: string | number
  subtitle?: string
  trend?: {
    value: number
    label?: string
  }
  icon?: React.ReactNode
  pattern?: CardPattern
  className?: string
  style?: React.CSSProperties
}

// 装饰图案组件 - 使用几何形状阴影
function PatternDecoration({ pattern }: { pattern: CardPattern }) {
  switch (pattern) {
    case 'circles':
      return (
        <>
          {/* 圆环组合 - 全卡片分布 */}
          {[
            { top: -30, right: -30, size: 80 },
            { top: -12, right: 40, size: 56 },
            { top: 24, right: -16, size: 64 },
            { top: 12, right: 88, size: 40 },
            { top: 56, right: 28, size: 48 },
            { top: 44, right: 120, size: 32 },
            { top: 80, right: 72, size: 36 },
            { top: 68, right: 160, size: 24 },
            { top: 96, right: 132, size: 28 },
          ].map((circle, i) => (
            <div
              key={i}
              className="absolute rounded-full"
              style={{
                top: circle.top,
                right: circle.right,
                width: circle.size,
                height: circle.size,
                border: `1px solid rgba(100, 116, 139, ${0.16 - i * 0.012})`,
              }}
            />
          ))}
          {/* 左侧延伸 */}
          {[
            { top: 20, left: 20, size: 28 },
            { top: 50, left: 60, size: 20 },
            { bottom: 16, left: 32, size: 24 },
          ].map((dot, i) => (
            <div
              key={`left-${i}`}
              className="absolute rounded-full"
              style={{
                ...dot,
                width: dot.size,
                height: dot.size,
                border: '1px solid rgba(100, 116, 139, 0.06)',
              }}
            />
          ))}
          {/* 底部点缀 */}
          {[
            { bottom: 8, right: 40, size: 22 },
            { bottom: 16, right: 90, size: 18 },
            { bottom: 6, right: 140, size: 16 },
            { bottom: 20, right: 190, size: 14 },
          ].map((dot, i) => (
            <div
              key={`dot-${i}`}
              className="absolute rounded-full"
              style={{
                bottom: dot.bottom,
                right: dot.right,
                width: dot.size,
                height: dot.size,
                border: '1px solid rgba(100, 116, 139, 0.05)',
              }}
            />
          ))}
        </>
      )
    case 'stars':
      return (
        <>
          {/* 菱形组合 - 全卡片分布 */}
          {[
            { top: -14, right: -14, size: 44, opacity: 0.16 },
            { top: 8, right: 44, size: 32, opacity: 0.14 },
            { top: 36, right: -6, size: 38, opacity: 0.13 },
            { top: 24, right: 88, size: 26, opacity: 0.12 },
            { top: 60, right: 36, size: 30, opacity: 0.11 },
            { top: 48, right: 128, size: 22, opacity: 0.1 },
            { top: 84, right: 80, size: 26, opacity: 0.09 },
            { top: 72, right: 168, size: 18, opacity: 0.08 },
            { top: 100, right: 124, size: 20, opacity: 0.07 },
          ].map((diamond, i) => (
            <div
              key={i}
              className="absolute"
              style={{
                top: diamond.top,
                right: diamond.right,
                width: diamond.size,
                height: diamond.size,
                border: `1px solid rgba(100, 116, 139, ${diamond.opacity})`,
                transform: 'rotate(45deg)',
              }}
            />
          ))}
          {/* 左侧延伸 */}
          {[
            { top: 28, left: 24, size: 16 },
            { top: 64, left: 56, size: 14 },
            { bottom: 20, left: 40, size: 12 },
          ].map((sq, i) => (
            <div
              key={`left-${i}`}
              className="absolute"
              style={{
                ...sq,
                width: sq.size,
                height: sq.size,
                border: '1px solid rgba(100, 116, 139, 0.05)',
                transform: 'rotate(45deg)',
              }}
            />
          ))}
          {/* 底部正方形点缀 */}
          {[
            { bottom: 10, right: 48, size: 16 },
            { bottom: 6, right: 100, size: 14 },
            { bottom: 14, right: 156, size: 12 },
          ].map((sq, i) => (
            <div
              key={`sq-${i}`}
              className="absolute"
              style={{
                bottom: sq.bottom,
                right: sq.right,
                width: sq.size,
                height: sq.size,
                border: '1px solid rgba(100, 116, 139, 0.05)',
                transform: 'rotate(45deg)',
              }}
            />
          ))}
        </>
      )
    case 'leaves':
      return (
        <>
          {/* 弧形叶片 - 全卡片层叠 */}
          {[
            { top: -24, right: -24, size: 72, clip: 'polygon(50% 0%, 100% 0%, 100% 50%)' },
            { top: -8, right: 48, size: 52, clip: 'polygon(50% 0%, 100% 0%, 100% 50%)' },
            { top: 32, right: -12, size: 56, clip: 'polygon(50% 0%, 100% 0%, 100% 50%)' },
            { top: 20, right: 96, size: 40, clip: 'polygon(50% 0%, 100% 0%, 100% 50%)' },
            { top: 64, right: 32, size: 48, clip: 'polygon(50% 0%, 100% 0%, 100% 50%)' },
            { top: 52, right: 136, size: 32, clip: 'polygon(50% 0%, 100% 0%, 100% 50%)' },
            { top: 92, right: 80, size: 36, clip: 'polygon(50% 0%, 100% 0%, 100% 50%)' },
            { top: 80, right: 176, size: 28, clip: 'polygon(50% 0%, 100% 0%, 100% 50%)' },
          ].map((leaf, i) => (
            <div
              key={i}
              className="absolute rounded-full"
              style={{
                top: leaf.top,
                right: leaf.right,
                width: leaf.size,
                height: leaf.size,
                border: `1px solid rgba(100, 116, 139, ${0.15 - i * 0.012})`,
                clipPath: leaf.clip,
              }}
            />
          ))}
          {/* 左侧延伸 */}
          {[
            { top: 36, left: 28, size: 24 },
            { top: 72, left: 64, size: 20 },
            { bottom: 24, left: 44, size: 18 },
          ].map((arc, i) => (
            <div
              key={`left-${i}`}
              className="absolute rounded-full"
              style={{
                ...arc,
                width: arc.size,
                height: arc.size,
                border: '1px solid rgba(100, 116, 139, 0.05)',
                clipPath: 'polygon(0% 50%, 0% 100%, 50% 100%)',
              }}
            />
          ))}
          {/* 底部小弧线 */}
          {[
            { bottom: 8, right: 56, size: 24 },
            { bottom: 14, right: 116, size: 20 },
            { bottom: 6, right: 172, size: 16 },
          ].map((arc, i) => (
            <div
              key={`arc-${i}`}
              className="absolute rounded-full"
              style={{
                bottom: arc.bottom,
                right: arc.right,
                width: arc.size,
                height: arc.size,
                border: '1px solid rgba(100, 116, 139, 0.05)',
                clipPath: 'polygon(50% 0%, 100% 0%, 100% 50%)',
              }}
            />
          ))}
        </>
      )
    case 'light':
      return (
        <>
          {/* 放射线条 - 更长更密覆盖全卡片 */}
          {[5, 14, 23, 32, 41, 50, 59, 68, 77, 86].map((angle, i) => (
            <div
              key={i}
              className="absolute top-0 right-0 origin-top-right"
              style={{
                width: `${200 - i * 12}px`,
                height: '1px',
                background: `rgba(100, 116, 139, ${0.15 - i * 0.012})`,
                transform: `rotate(${angle}deg)`,
              }}
            />
          ))}
          {/* 横向辅助线 - 覆盖更多区域 */}
          {[
            { top: 12, right: 0, width: 140 },
            { top: 28, right: 0, width: 110 },
            { top: 44, right: 0, width: 85 },
            { top: 60, right: 0, width: 65 },
            { top: 76, right: 0, width: 48 },
            { top: 92, right: 0, width: 32 },
          ].map((line, i) => (
            <div
              key={`h-${i}`}
              className="absolute"
              style={{
                top: line.top,
                right: line.right,
                width: line.width,
                height: '1px',
                background: `rgba(100, 116, 139, ${0.1 - i * 0.012})`,
              }}
            />
          ))}
          {/* 左侧辅助线 */}
          {[
            { top: 20, left: 0, width: 60 },
            { top: 48, left: 0, width: 40 },
            { top: 76, left: 0, width: 24 },
          ].map((line, i) => (
            <div
              key={`l-${i}`}
              className="absolute"
              style={{
                top: line.top,
                left: line.left,
                width: line.width,
                height: '1px',
                background: 'rgba(100, 116, 139, 0.05)',
              }}
            />
          ))}
        </>
      )
    case 'grass':
      return (
        <>
          {/* 竖向线条 - 覆盖整个底部 */}
          {[
            { right: 4, height: 56 },
            { right: 16, height: 76 },
            { right: 28, height: 52 },
            { right: 40, height: 68 },
            { right: 52, height: 44 },
            { right: 64, height: 60 },
            { right: 76, height: 40 },
            { right: 88, height: 54 },
            { right: 100, height: 36 },
            { right: 112, height: 48 },
            { right: 124, height: 32 },
            { right: 136, height: 42 },
            { right: 148, height: 28 },
            { right: 160, height: 38 },
            { right: 172, height: 24 },
          ].map((line, i) => (
            <div
              key={i}
              className="absolute bottom-0"
              style={{
                right: line.right,
                height: line.height,
                width: '1px',
                background: `rgba(100, 116, 139, ${0.15 - i * 0.007})`,
              }}
            />
          ))}
          {/* 左侧线条 */}
          {[
            { left: 12, height: 36 },
            { left: 28, height: 48 },
            { left: 44, height: 32 },
            { left: 60, height: 42 },
          ].map((line, i) => (
            <div
              key={`left-${i}`}
              className="absolute bottom-0"
              style={{
                left: line.left,
                height: line.height,
                width: '1px',
                background: 'rgba(100, 116, 139, 0.06)',
              }}
            />
          ))}
          {/* 顶部横向点缀 */}
          {[
            { top: 4, right: 8, width: 64 },
            { top: 16, right: 4, width: 48 },
            { top: 28, right: 12, width: 36 },
            { top: 40, right: 8, width: 24 },
          ].map((line, i) => (
            <div
              key={`h-${i}`}
              className="absolute"
              style={{
                top: line.top,
                right: line.right,
                width: line.width,
                height: '1px',
                background: `rgba(100, 116, 139, ${0.1 - i * 0.015})`,
              }}
            />
          ))}
        </>
      )
    case 'ribbons':
      return (
        <>
          {/* 同心弧线 - 更大范围 */}
          {[
            { size: 160, opacity: 0.15 },
            { size: 128, opacity: 0.13 },
            { size: 100, opacity: 0.11 },
            { size: 76, opacity: 0.09 },
            { size: 56, opacity: 0.07 },
            { size: 40, opacity: 0.05 },
            { size: 28, opacity: 0.04 },
          ].map((arc, i) => (
            <div
              key={i}
              className="absolute rounded-full"
              style={{
                top: -arc.size / 2,
                right: -arc.size / 2,
                width: arc.size,
                height: arc.size,
                border: `1px solid rgba(100, 116, 139, ${arc.opacity})`,
                clipPath: 'polygon(0 50%, 100% 50%, 100% 100%, 0 100%)',
              }}
            />
          ))}
          {/* 左下弧线 */}
          {[
            { size: 80, opacity: 0.06 },
            { size: 56, opacity: 0.05 },
            { size: 36, opacity: 0.04 },
          ].map((arc, i) => (
            <div
              key={`bl-${i}`}
              className="absolute rounded-full"
              style={{
                bottom: -arc.size / 2,
                left: -arc.size / 2,
                width: arc.size,
                height: arc.size,
                border: `1px solid rgba(100, 116, 139, ${arc.opacity})`,
                clipPath: 'polygon(50% 0%, 100% 0%, 100% 50%, 50% 50%)',
              }}
            />
          ))}
          {/* 辅助短弧 - 更分散 */}
          {[
            { bottom: 10, right: 40, size: 28 },
            { bottom: 20, right: 96, size: 24 },
            { bottom: 8, right: 148, size: 20 },
            { bottom: 24, right: 196, size: 16 },
          ].map((arc, i) => (
            <div
              key={`sub-${i}`}
              className="absolute rounded-full"
              style={{
                bottom: arc.bottom,
                right: arc.right,
                width: arc.size,
                height: arc.size,
                border: '1px solid rgba(100, 116, 139, 0.05)',
                clipPath: 'polygon(0 0%, 100% 0%, 100% 50%, 0 50%)',
              }}
            />
          ))}
        </>
      )
    default:
      return null
  }
}

export function StatCard({
  title,
  value,
  subtitle,
  trend,
  icon,
  pattern,
  className,
  style,
}: StatCardProps) {
  const trendColor = trend
    ? trend.value > 0
      ? 'text-accent-success'
      : trend.value < 0
        ? 'text-accent-danger'
        : 'text-content-muted'
    : ''

  return (
    <Card className={cn('relative overflow-hidden', className)} style={style}>
      {/* 装饰图案 */}
      {pattern && <PatternDecoration pattern={pattern} />}

      <div className="relative z-10">
        <div className="flex items-center justify-between mb-2">
          <span className="text-label">{title}</span>
          {icon && (
            <div className="w-10 h-10 rounded-lg bg-accent-primary/10 flex items-center justify-center text-accent-primary">
              {icon}
            </div>
          )}
        </div>

        <div className="stat-number text-content-primary">{value}</div>

        {(subtitle || trend) && (
          <div className="flex items-center gap-2 mt-2">
            {trend && (
              <span className={cn('text-sm font-medium tabular-nums', trendColor)}>
                {trend.value > 0 ? '+' : ''}{trend.value.toFixed(1)}%
                {trend.label && <span className="text-content-muted ml-1">{trend.label}</span>}
              </span>
            )}
            {subtitle && (
              <span className="text-caption">{subtitle}</span>
            )}
          </div>
        )}
      </div>
    </Card>
  )
}

// 列表项卡片
interface ListCardProps {
  items: Array<{
    id: string | number
    title: string
    subtitle?: string
    value?: string | number
    badge?: React.ReactNode
    onClick?: () => void
  }>
  emptyText?: string
  className?: string
}

export function ListCard({ items, emptyText = '暂无数据', className }: ListCardProps) {
  if (items.length === 0) {
    return (
      <Card className={className}>
        <div className="text-center py-8 text-content-muted">{emptyText}</div>
      </Card>
    )
  }

  return (
    <Card padding="none" className={className}>
      <div className="divide-y divide-surface-border/50">
        {items.map((item, index) => (
          <div
            key={item.id}
            className={cn(
              'flex items-center justify-between p-4 transition-colors',
              item.onClick && 'hover:bg-surface/50 cursor-pointer'
            )}
            onClick={item.onClick}
            style={{ animationDelay: `${index * 50}ms` }}
          >
            <div className="flex items-center gap-3 min-w-0">
              <span className="w-6 h-6 rounded-full bg-accent-primary/10 text-accent-primary text-xs font-medium flex items-center justify-center flex-shrink-0 tabular-nums">
                {index + 1}
              </span>
              <div className="min-w-0">
                <div className="text-sm font-medium text-content-primary truncate">{item.title}</div>
                {item.subtitle && (
                  <div className="text-caption truncate">{item.subtitle}</div>
                )}
              </div>
            </div>
            <div className="flex items-center gap-3 flex-shrink-0">
              {item.value && (
                <span className="font-mono text-sm text-content-secondary tabular-nums">{item.value}</span>
              )}
              {item.badge}
            </div>
          </div>
        ))}
      </div>
    </Card>
  )
}
