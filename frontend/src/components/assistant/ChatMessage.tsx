'use client'

import { useState } from 'react'
import { cn } from '@/lib/utils'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import {
  faRobot,
  faUser,
  faSpinner,
  faCheck,
  faDatabase,
  faChartLine,
  faTrophy,
  faLayerGroup,
} from '@fortawesome/free-solid-svg-icons'
import { IconDefinition } from '@fortawesome/fontawesome-svg-core'
import { Streamdown } from 'streamdown'

export type MessageRole = 'user' | 'assistant'

// 工具调用状态
interface ToolStatus {
  name: string
  status: 'running' | 'completed'
  input?: Record<string, unknown>
  result?: string
}

// 消息统计
interface MessageMetrics {
  duration?: number  // 耗时（秒）
  tokens?: number    // token 数
  cost?: number      // 费用
}

interface Message {
  id: string
  role: MessageRole
  content: string
  timestamp: Date
  context?: {
    type: 'product' | 'category' | 'url' | 'general'
    value?: string
  }
  isStreaming?: boolean
  toolStatus?: ToolStatus[]
  metrics?: MessageMetrics
}

interface ChatMessageProps {
  message: Message
  onRetry?: () => void
  onCopy?: (content: string) => void
  onFeedback?: (type: 'like' | 'dislike') => void
}

// 工具名称映射
const toolNameMap: Record<string, { label: string; icon: IconDefinition }> = {
  query_startups: { label: '查询产品数据', icon: faDatabase },
  get_category_analysis: { label: '分析市场类目', icon: faLayerGroup },
  get_trend_report: { label: '生成趋势报告', icon: faChartLine },
  get_leaderboard: { label: '获取排行榜', icon: faTrophy },
}

// Streamdown 自定义组件样式
const streamdownComponents = {
  h1: ({ children }: { children: React.ReactNode }) => (
    <h1 className="text-lg font-semibold text-content-primary mt-5 mb-3 first:mt-0">{children}</h1>
  ),
  h2: ({ children }: { children: React.ReactNode }) => (
    <h2 className="text-base font-semibold text-content-primary mt-5 mb-3 first:mt-0">{children}</h2>
  ),
  h3: ({ children }: { children: React.ReactNode }) => (
    <h3 className="text-sm font-semibold text-content-primary mt-4 mb-2 first:mt-0">{children}</h3>
  ),
  h4: ({ children }: { children: React.ReactNode }) => (
    <h4 className="text-sm font-medium text-content-primary mt-3 mb-2 first:mt-0">{children}</h4>
  ),
  p: ({ children }: { children: React.ReactNode }) => (
    <p className="text-sm text-content-secondary leading-relaxed my-2">{children}</p>
  ),
  ul: ({ children }: { children: React.ReactNode }) => (
    <ul className="list-disc ml-5 my-2 space-y-1">{children}</ul>
  ),
  ol: ({ children }: { children: React.ReactNode }) => (
    <ol className="list-decimal ml-5 my-2 space-y-1">{children}</ol>
  ),
  li: ({ children }: { children: React.ReactNode }) => (
    <li className="text-sm text-content-secondary leading-relaxed">{children}</li>
  ),
  blockquote: ({ children }: { children: React.ReactNode }) => (
    <blockquote className="border-l-3 border-accent-primary/40 pl-4 my-3 text-content-muted italic">
      {children}
    </blockquote>
  ),
  code: ({ children }: { children: React.ReactNode }) => (
    <code className="bg-surface/50 px-1.5 py-0.5 rounded text-sm text-accent-primary font-mono">
      {children}
    </code>
  ),
  pre: ({ children }: { children: React.ReactNode }) => (
    <pre className="bg-surface/50 rounded-lg p-4 overflow-x-auto my-3 border border-surface-border/30 text-sm">
      {children}
    </pre>
  ),
  a: ({ href, children }: { href?: string; children: React.ReactNode }) => (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="text-accent-primary hover:text-accent-primary/80 underline underline-offset-2"
    >
      {children}
    </a>
  ),
  strong: ({ children }: { children: React.ReactNode }) => (
    <strong className="font-semibold text-content-primary">{children}</strong>
  ),
  em: ({ children }: { children: React.ReactNode }) => (
    <em className="italic text-content-secondary">{children}</em>
  ),
  table: ({ children }: { children: React.ReactNode }) => (
    <div className="overflow-x-auto my-3">
      <table className="w-full text-sm border-collapse">{children}</table>
    </div>
  ),
  thead: ({ children }: { children: React.ReactNode }) => (
    <thead className="bg-surface/30">{children}</thead>
  ),
  th: ({ children }: { children: React.ReactNode }) => (
    <th className="border border-surface-border/50 px-3 py-2 text-left font-medium text-content-primary">
      {children}
    </th>
  ),
  td: ({ children }: { children: React.ReactNode }) => (
    <td className="border border-surface-border/50 px-3 py-2 text-content-secondary">{children}</td>
  ),
  hr: () => <hr className="my-4 border-surface-border/50" />,
}

// 现代风格 SVG 图标组件
const Icons = {
  copy: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
      <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
    </svg>
  ),
  check: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="20 6 9 17 4 12"/>
    </svg>
  ),
  thumbUp: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M7 22V11M2 13V20C2 21.1 2.9 22 4 22H17.4C18.6 22 19.6 21.2 19.9 20L21.7 12C22.1 10.5 21 9 19.4 9H14V4C14 2.9 13.1 2 12 2C11.5 2 11.1 2.3 10.9 2.7L7 11"/>
    </svg>
  ),
  thumbDown: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M17 2V13M22 11V4C22 2.9 21.1 2 20 2H6.6C5.4 2 4.4 2.8 4.1 4L2.3 12C1.9 13.5 3 15 4.6 15H10V20C10 21.1 10.9 22 12 22C12.5 22 12.9 21.7 13.1 21.3L17 13"/>
    </svg>
  ),
  refresh: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/>
      <path d="M21 3v5h-5"/>
      <path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/>
      <path d="M3 21v-5h5"/>
    </svg>
  ),
  share: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"/>
      <polyline points="16 6 12 2 8 6"/>
      <line x1="12" y1="2" x2="12" y2="15"/>
    </svg>
  ),
  more: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="1"/>
      <circle cx="19" cy="12" r="1"/>
      <circle cx="5" cy="12" r="1"/>
    </svg>
  ),
  clock: (
    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10"/>
      <polyline points="12 6 12 12 16 14"/>
    </svg>
  ),
  coins: (
    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="8" cy="8" r="6"/>
      <path d="M18.09 10.37A6 6 0 1 1 10.34 18"/>
      <path d="M7 6h1v4"/>
      <path d="M16.71 13.88l.7.71-2.82 2.82"/>
    </svg>
  ),
}

// 操作按钮组件
function ActionButton({
  icon,
  label,
  onClick,
  active,
  activeClass,
}: {
  icon: React.ReactNode
  label: string
  onClick?: () => void
  active?: boolean
  activeClass?: string
}) {
  return (
    <button
      onClick={onClick}
      className={cn(
        'p-1.5 rounded-md transition-all duration-150',
        'hover:bg-surface-hover/80',
        active
          ? activeClass || 'text-accent-primary'
          : 'text-content-muted/60 hover:text-content-secondary'
      )}
      title={label}
    >
      {icon}
    </button>
  )
}

export function ChatMessage({ message, onRetry, onCopy, onFeedback }: ChatMessageProps) {
  const [copied, setCopied] = useState(false)
  const [feedback, setFeedback] = useState<'like' | 'dislike' | null>(null)
  const isUser = message.role === 'user'

  // 复制内容
  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(message.content)
      setCopied(true)
      onCopy?.(message.content)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error('Failed to copy:', err)
    }
  }

  // 反馈
  const handleFeedback = (type: 'like' | 'dislike') => {
    setFeedback(feedback === type ? null : type)
    onFeedback?.(type)
  }

  if (isUser) {
    // 用户消息 - 使用气泡样式，靠右
    return (
      <div className="flex justify-end gap-3">
        <div className="max-w-[75%] rounded-2xl rounded-tr-md px-4 py-3 bg-accent-primary text-white">
          <div className="text-sm leading-relaxed whitespace-pre-wrap">
            {message.content}
          </div>
          <div className="text-xs mt-2 text-white/60 text-right">
            {formatTime(message.timestamp)}
          </div>
        </div>
        <div className="w-8 h-8 rounded-lg bg-accent-primary flex items-center justify-center flex-shrink-0">
          <FontAwesomeIcon icon={faUser} className="h-4 w-4 text-white" />
        </div>
      </div>
    )
  }

  // AI 消息 - 无气泡，宽松布局
  const hasActiveTools = message.toolStatus && message.toolStatus.length > 0
  const runningTool = message.toolStatus?.find(t => t.status === 'running')
  const completedToolsCount = message.toolStatus?.filter(t => t.status === 'completed').length || 0
  const isComplete = !message.isStreaming && message.content

  // 获取当前显示的工具状态
  // 只在流式传输过程中显示，消息完成后不显示
  const getCurrentToolDisplay = () => {
    // 消息已完成，不显示工具状态
    if (isComplete) {
      return null
    }

    // 有正在运行的工具
    if (runningTool) {
      const toolInfo = toolNameMap[runningTool.name] || { label: runningTool.name, icon: faDatabase }
      return (
        <div className="inline-flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-medium bg-accent-warning/10 text-accent-warning border border-accent-warning/20 animate-pulse">
          <FontAwesomeIcon icon={faSpinner} className="h-3 w-3 animate-spin" />
          <span>{toolInfo.label}</span>
        </div>
      )
    }

    // 工具已完成但还没有内容（等待 AI 生成回复）
    if (completedToolsCount > 0 && !message.content && message.isStreaming) {
      return (
        <div className="inline-flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-medium bg-accent-success/10 text-accent-success border border-accent-success/20">
          <FontAwesomeIcon icon={faCheck} className="h-3 w-3" />
          <span>已完成 {completedToolsCount} 项查询</span>
        </div>
      )
    }

    return null
  }

  const toolDisplay = getCurrentToolDisplay()

  return (
    <div className="flex gap-3 group">
      <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent-primary/20 to-accent-secondary/20 flex items-center justify-center flex-shrink-0">
        <FontAwesomeIcon icon={faRobot} className="h-4 w-4 text-accent-primary" />
      </div>
      <div className="flex-1 min-w-0 pt-1">
        {/* 工具调用状态 - 只在进行中显示 */}
        {toolDisplay && (
          <div className="mb-3">
            {toolDisplay}
          </div>
        )}

        {/* 消息内容 - 使用 Streamdown 渲染 */}
        {message.isStreaming && !message.content && runningTool ? (
          <div className="flex items-center gap-2 text-content-muted">
            <FontAwesomeIcon icon={faSpinner} className="h-4 w-4 animate-spin" />
            <span className="text-sm">正在查询数据...</span>
          </div>
        ) : message.isStreaming && !message.content ? (
          <div className="flex items-center gap-2 text-content-muted">
            <FontAwesomeIcon icon={faSpinner} className="h-4 w-4 animate-spin" />
            <span className="text-sm">正在思考...</span>
          </div>
        ) : message.content ? (
          <div className="prose-chat text-content-secondary">
            <Streamdown
              isAnimating={message.isStreaming}
              components={streamdownComponents}
            >
              {message.content}
            </Streamdown>
          </div>
        ) : null}

        {/* 底部信息栏 */}
        <div className="flex items-center gap-4 mt-3">
          {/* 左侧：操作按钮 - 完成后显示 */}
          {isComplete && (
            <div className="flex items-center gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
              <ActionButton
                icon={copied ? Icons.check : Icons.copy}
                label="复制"
                onClick={handleCopy}
                active={copied}
                activeClass="text-accent-success"
              />
              <ActionButton
                icon={Icons.thumbUp}
                label="有帮助"
                onClick={() => handleFeedback('like')}
                active={feedback === 'like'}
                activeClass="text-accent-success"
              />
              <ActionButton
                icon={Icons.thumbDown}
                label="没帮助"
                onClick={() => handleFeedback('dislike')}
                active={feedback === 'dislike'}
                activeClass="text-accent-error"
              />
              <ActionButton
                icon={Icons.refresh}
                label="重试"
                onClick={onRetry}
              />
              <ActionButton
                icon={Icons.share}
                label="分享"
                onClick={() => {
                  // TODO: 实现分享功能
                }}
              />
            </div>
          )}

          {/* 右侧：时间和统计 */}
          <div className="flex items-center gap-3 text-xs text-content-muted/60 ml-auto">
            {message.metrics?.duration && (
              <span className="flex items-center gap-1">
                {Icons.clock}
                {message.metrics.duration.toFixed(1)}s
              </span>
            )}
            {message.metrics?.tokens && (
              <span className="flex items-center gap-1">
                {Icons.coins}
                {message.metrics.tokens.toLocaleString()}
              </span>
            )}
            {message.metrics?.cost !== undefined && message.metrics.cost > 0 && (
              <span className="text-accent-warning/80">
                ${message.metrics.cost.toFixed(4)}
              </span>
            )}
            <span>{formatTime(message.timestamp)}</span>
          </div>
        </div>
      </div>
    </div>
  )
}

function formatTime(date: Date): string {
  return date.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
  })
}
