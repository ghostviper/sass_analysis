'use client'

import { useState } from 'react'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import {
  faMagnifyingGlass,
  faChartLine,
  faRocket,
  faLightbulb,
  faChevronDown,
} from '@fortawesome/free-solid-svg-icons'
import { cn } from '@/lib/utils'

interface SuggestedPromptsProps {
  onSelect: (prompt: string) => void
}

const suggestions = [
  {
    icon: faMagnifyingGlass,
    shortText: '高收入产品',
    color: 'from-blue-500 to-cyan-500',
    prompts: [
      '分析月收入超过 $5000 的产品有什么共同特点？',
      '技术复杂度低但收入不错的产品有哪些？',
      '有哪些小而美的产品案例值得学习？',
      '如何评估一个产品的可复制性？',
    ],
  },
  {
    icon: faChartLine,
    shortText: '热门赛道',
    color: 'from-purple-500 to-pink-500',
    prompts: [
      '当前最值得关注的 SaaS 赛道有哪些？',
      '哪些领域竞争相对较小但有潜力？',
      'AI 工具赛道还有哪些机会？',
      '2024 年独立开发者应该关注什么趋势？',
    ],
  },
  {
    icon: faRocket,
    shortText: '适合独立开发',
    color: 'from-amber-500 to-orange-500',
    prompts: [
      '独立开发者适合做什么类型的产品？',
      '我是前端开发，适合做什么 SaaS？',
      '如何从个人痛点出发找到产品方向？',
      '副业做 SaaS 需要注意什么？',
    ],
  },
  {
    icon: faLightbulb,
    shortText: '低门槛高收益',
    color: 'from-emerald-500 to-teal-500',
    prompts: [
      '技术简单但收入不错的产品有什么特点？',
      '有哪些一个人就能做的 SaaS 产品？',
      '不需要复杂后端的产品有哪些？',
      '快速验证产品想法的最佳方式？',
    ],
  },
]

export function SuggestedPrompts({ onSelect }: SuggestedPromptsProps) {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null)

  const handleClick = (index: number) => {
    setExpandedIndex(expandedIndex === index ? null : index)
  }

  const handlePromptSelect = (prompt: string) => {
    onSelect(prompt)
    setExpandedIndex(null)
  }

  return (
    <div className="w-full min-h-[180px]">
      {/* 标签按钮 */}
      <div className="flex flex-wrap justify-center gap-2">
        {suggestions.map((suggestion, index) => (
          <button
            key={index}
            onClick={() => handleClick(index)}
            className={cn(
              'group inline-flex items-center gap-2 px-3.5 py-2 rounded-full border transition-all text-sm',
              expandedIndex === index
                ? 'bg-accent-primary/10 border-accent-primary/30 text-accent-primary'
                : 'bg-surface/60 border-surface-border/50 text-content-secondary hover:bg-surface hover:border-accent-primary/30 hover:text-content-primary'
            )}
          >
            <FontAwesomeIcon
              icon={suggestion.icon}
              className={cn(
                'h-3.5 w-3.5 transition-colors',
                expandedIndex === index ? 'text-accent-primary' : 'text-content-muted group-hover:text-accent-primary'
              )}
            />
            <span>{suggestion.shortText}</span>
            <FontAwesomeIcon
              icon={faChevronDown}
              className={cn(
                'h-2.5 w-2.5 transition-transform duration-200',
                expandedIndex === index ? 'rotate-180 text-accent-primary' : 'text-content-muted'
              )}
            />
          </button>
        ))}
      </div>

      {/* 展开的问题面板 - 固定高度区域 */}
      <div className="mt-4 min-h-[120px]">
        <div
          className={cn(
            'transition-all duration-200 ease-out',
            expandedIndex !== null ? 'opacity-100 translate-y-0' : 'opacity-0 -translate-y-2 pointer-events-none'
          )}
        >
          {expandedIndex !== null && (
            <div className="p-4 bg-background-secondary border border-surface-border rounded-xl shadow-lg">
              <div className="flex items-center gap-2 mb-3">
                <div className={cn(
                  'w-6 h-6 rounded-lg flex items-center justify-center',
                  `bg-gradient-to-br ${suggestions[expandedIndex].color}`
                )}>
                  <FontAwesomeIcon
                    icon={suggestions[expandedIndex].icon}
                    className="h-3 w-3 text-white"
                  />
                </div>
                <span className="text-sm font-medium text-content-primary">
                  {suggestions[expandedIndex].shortText} - 常见问题
                </span>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                {suggestions[expandedIndex].prompts.map((prompt, idx) => (
                  <button
                    key={idx}
                    onClick={() => handlePromptSelect(prompt)}
                    className="text-left text-sm text-content-secondary hover:text-accent-primary px-3 py-2.5 rounded-lg bg-surface/60 hover:bg-surface border border-transparent hover:border-accent-primary/20 transition-all"
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
