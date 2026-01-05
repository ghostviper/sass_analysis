'use client'

import { useState } from 'react'
import { Search, TrendingUp, Compass } from 'lucide-react'
import { cn } from '@/lib/utils'

interface SuggestedPromptsProps {
  onSelect: (prompt: string) => void
}

const categories = [
  {
    id: 'product',
    icon: Search,
    label: '产品分析',
    description: '深度分析产品数据、收入、竞争力等',
    prompts: [
      '分析月收入超过 $5000 的产品有什么共同特点？',
      '技术复杂度低但收入不错的产品有哪些？',
      '有哪些小而美的产品案例值得学习？',
      '如何评估一个产品的可复制性？',
    ],
  },
  {
    id: 'trend',
    icon: TrendingUp,
    label: '行业趋势',
    description: '洞察赛道机会、市场动态与趋势',
    prompts: [
      '当前最值得关注的 SaaS 赛道有哪些？',
      '哪些领域竞争相对较小但有潜力？',
      'AI 工具赛道还有哪些机会？',
      '2024 年独立开发者应该关注什么趋势？',
    ],
  },
  {
    id: 'career',
    icon: Compass,
    label: '方向探索',
    description: '根据你的背景推荐适合的方向',
    prompts: [
      '独立开发者适合做什么类型的产品？',
      '我是前端开发，适合做什么 SaaS？',
      '如何从个人痛点出发找到产品方向？',
      '副业做 SaaS 需要注意什么？',
    ],
  },
]

export function SuggestedPrompts({ onSelect }: SuggestedPromptsProps) {
  const [expandedId, setExpandedId] = useState<string | null>(null)

  const handleClick = (id: string) => {
    setExpandedId(expandedId === id ? null : id)
  }

  const handlePromptSelect = (prompt: string) => {
    onSelect(prompt)
    setExpandedId(null)
  }

  const expandedCategory = categories.find(c => c.id === expandedId)

  return (
    <div className="w-full">
      {/* 分类标签按钮 - 胶囊式设计 */}
      <div className="flex flex-wrap justify-center gap-5">
        {categories.map((category) => {
          const isExpanded = expandedId === category.id
          const Icon = category.icon
          return (
            <button
              key={category.id}
              onClick={() => handleClick(category.id)}
              className={cn(
                'group inline-flex items-center gap-2.5 px-5 py-2.5 rounded-full transition-all duration-300 text-sm border cursor-pointer',
                isExpanded
                  ? 'bg-accent-primary/10 text-accent-primary border-accent-primary/30 shadow-md scale-[1.02]'
                  : 'bg-surface border-surface-border text-content-secondary hover:border-accent-primary/40 hover:bg-accent-primary/5 hover:text-accent-primary hover:shadow-md'
              )}
            >
              <Icon
                className={cn(
                  'h-3.5 w-3.5 transition-all duration-300',
                  isExpanded ? 'text-accent-primary' : 'text-content-muted group-hover:text-accent-primary'
                )}
              />
              <span className="font-medium">{category.label}</span>
            </button>
          )
        })}
      </div>

      {/* 展开的问题面板 - 与页面输入框风格一致 */}
      <div className="relative mt-5 h-0">
        <div
          className={cn(
            'absolute left-0 right-0 top-0 z-10',
            'transition-all duration-300 ease-out origin-top',
            expandedId !== null
              ? 'opacity-100 scale-100 translate-y-0 pointer-events-auto'
              : 'opacity-0 scale-95 -translate-y-3 pointer-events-none'
          )}
        >
          {expandedCategory && (
            <div className="bg-surface/50 rounded-2xl border border-surface-border shadow-sm">
              {/* 内容区域 */}
              <div className="p-4">
                {/* 标题区 - 简洁风格 */}
                <div className="flex items-center gap-2.5 mb-3 pb-3 border-b border-surface-border/50">
                  <div className="w-7 h-7 rounded-lg bg-background-tertiary flex items-center justify-center">
                    <expandedCategory.icon className="h-3.5 w-3.5 text-content-secondary" />
                  </div>
                  <div>
                    <h3 className="text-sm font-medium text-content-primary">
                      {expandedCategory.label}
                    </h3>
                    <p className="text-xs text-content-muted">
                      {expandedCategory.description}
                    </p>
                  </div>
                </div>

                {/* 问题列表 - 简洁卡片风格 */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  {expandedCategory.prompts.map((prompt, idx) => (
                    <button
                      key={idx}
                      onClick={() => handlePromptSelect(prompt)}
                      className={cn(
                        'text-left text-sm px-3.5 py-2.5 rounded-xl transition-all duration-200',
                        'bg-background-tertiary/50 hover:bg-background-tertiary',
                        'text-content-secondary hover:text-content-primary'
                      )}
                    >
                      {prompt}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
