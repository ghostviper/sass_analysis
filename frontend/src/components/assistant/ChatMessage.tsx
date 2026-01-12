'use client'

import { useState } from 'react'
import { cn } from '@/lib/utils'
import { useLocale } from '@/contexts/LocaleContext'
import {
  Bot,
  User,
  Loader2,
  Check,
  ChevronDown,
  ChevronUp,
  Copy,
  ThumbsUp,
  ThumbsDown,
  RotateCcw,
  Share2,
  Clock,
  Coins,
} from 'lucide-react'
import { Streamdown } from 'streamdown'

export type MessageRole = 'user' | 'assistant'

// 工具调用状态
interface ToolStatus {
  name: string
  toolId?: string  // Unique ID for matching tool_start with tool_end
  status: 'running' | 'completed'
  input?: Record<string, unknown>
  result?: string
  displayText?: string  // 用户友好的显示文本
}

// 消息统计
interface MessageMetrics {
  duration?: number  // 耗时（秒）
  tokens?: number    // token 数
  cost?: number      // 费用
}

// 内容块类型
interface ContentBlock {
  type: 'thinking' | 'text' | 'tool_use' | 'tool_result'
  content: string
  isStreaming?: boolean
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
  // 内容块数组 - 用于区分 thinking、text、tool 等不同类型的内容
  contentBlocks?: ContentBlock[]
}

interface ChatMessageProps {
  message: Message
  onRetry?: () => void
  onCopy?: (content: string) => void
  onFeedback?: (type: 'like' | 'dislike') => void
}

// 思考块图标
const ThinkingIcon = () => (
  <svg className="thinking-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10"/>
    <path d="M12 16v-4"/>
    <path d="M12 8h.01"/>
  </svg>
)

// 思考块组件
function ThinkingBlock({
  content,
  isStreaming,
  t,
}: {
  content: string
  isStreaming?: boolean
  t: (key: string) => string
}) {
  const [isExpanded, setIsExpanded] = useState(false)

  return (
    <div data-chat-block="thinking" className={isStreaming ? 'streaming' : ''}>
      <div
        className="thinking-header"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <ThinkingIcon />
        <span>{t('assistant.thinking.title')}</span>
        {isStreaming && (
          <Loader2 className="h-3 w-3 animate-spin" />
        )}
        <span className="thinking-badge">
          {isExpanded ? t('assistant.thinking.collapse') : t('assistant.thinking.expand')}
        </span>
        {isExpanded ? (
          <ChevronUp className="h-3 w-3 opacity-60" />
        ) : (
          <ChevronDown className="h-3 w-3 opacity-60" />
        )}
      </div>
      {isExpanded && (
        <div className="thinking-content">
          <Streamdown isAnimating={isStreaming}>
            {content}
          </Streamdown>
        </div>
      )}
    </div>
  )
}

export function ChatMessage({ message, onRetry, onCopy, onFeedback }: ChatMessageProps) {
  const { t } = useLocale()
  const [copied, setCopied] = useState(false)
  const [feedback, setFeedback] = useState<'like' | 'dislike' | null>(null)
  const [toolsExpanded, setToolsExpanded] = useState(false)
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
        <div className="flex flex-col items-end gap-1.5 flex-1 min-w-0">
          <div className="max-w-full rounded-2xl rounded-tr-md px-5 py-3.5 bg-gradient-to-r from-brand-500 to-brand-600 text-white shadow-md shadow-brand-500/20">
            <div className="text-[0.9375rem] leading-[1.7] whitespace-pre-wrap font-normal break-words">
              {message.content}
            </div>
          </div>
          <span className="text-[11px] text-content-muted/50 mr-1 font-medium">
            {formatTime(message.timestamp)}
          </span>
        </div>
        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-brand-500 to-brand-600 flex items-center justify-center flex-shrink-0 shadow-sm">
          <User className="h-4 w-4 text-white" />
        </div>
      </div>
    )
  }

  // AI 消息 - 无气泡，宽松布局
  const hasActiveTools = message.toolStatus && message.toolStatus.length > 0
  const runningTool = message.toolStatus?.find(t => t.status === 'running')
  const completedToolsCount = message.toolStatus?.filter(t => t.status === 'completed').length || 0
  const isComplete = !message.isStreaming && message.content
  const totalTools = message.toolStatus?.length || 0
  const allToolsCompleted = totalTools > 0 && completedToolsCount === totalTools

  // 工具状态栏 - 只在完成后显示
  const renderToolStatusBar = () => {
    // 只有完成后才显示状态栏
    if (!hasActiveTools || message.isStreaming) return null

    return (
      <div className="mt-4 flex justify-center">
        <div className="inline-flex flex-col items-center">
          {/* 摘要行 */}
          <button
            type="button"
            onClick={() => setToolsExpanded(!toolsExpanded)}
            className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs text-content-muted hover:text-content-secondary bg-surface/50 hover:bg-surface/80 transition-all cursor-pointer"
          >
            <Check className="h-3 w-3 text-emerald-500" />
            <span className="font-medium">
              {completedToolsCount} {t('assistant.tools.stepsCompleted') || '个步骤完成'}
            </span>
            <ChevronDown className={cn(
              'h-3 w-3 transition-transform',
              toolsExpanded && 'rotate-180'
            )} />
          </button>

          {/* 展开的详情 */}
          {toolsExpanded && (
            <div className="mt-2 flex flex-wrap justify-center gap-1.5">
              {message.toolStatus?.map((tool, idx) => {
                const displayLabel = tool.displayText || tool.name

                return (
                  <div 
                    key={`${tool.name}-${idx}`} 
                    className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] bg-emerald-500/10 text-emerald-600 dark:text-emerald-400"
                  >
                    <Check className="h-2.5 w-2.5" />
                    <span className="font-medium truncate max-w-[180px]">{displayLabel}</span>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      </div>
    )
  }

  return (
    <div className="flex gap-3 group">
      <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-brand-500/20 via-accent-secondary/20 to-brand-600/20 flex items-center justify-center flex-shrink-0 ring-1 ring-brand-500/10">
        <Bot className="h-4 w-4 text-brand-500" />
      </div>
      <div className="flex-1 min-w-0 pt-1">
        {/* 消息内容 - 使用 contentBlocks 渲染不同类型的内容 */}
        {(() => {
          // 提取 thinking 和 text 内容块
          const thinkingBlock = message.contentBlocks?.find(b => b.type === 'thinking')
          const textBlock = message.contentBlocks?.find(b => b.type === 'text')
          const hasThinking = thinkingBlock && thinkingBlock.content
          const hasText = textBlock && textBlock.content

          return (
            <>
              {/* 思考块 */}
              {hasThinking && (
                <ThinkingBlock
                  content={thinkingBlock.content}
                  isStreaming={thinkingBlock.isStreaming}
                  t={t}
                />
              )}

              {/* 文本内容 */}
              {hasText ? (
                <div data-chat-block="text">
                  <Streamdown isAnimating={message.isStreaming}>
                    {textBlock.content}
                  </Streamdown>
                </div>
              ) : message.content ? (
                // 有 content 但没有 textBlock（兼容旧格式）
                <div data-chat-block="text">
                  <Streamdown isAnimating={message.isStreaming}>
                    {message.content}
                  </Streamdown>
                </div>
              ) : null}

              {/* 
                加载状态显示逻辑：
                1. 有思考内容正在输出时 -> 不显示额外的加载状态（思考块已有转圈）
                2. 有工具正在执行时 -> 不显示（输入框 placeholder 会显示）
                3. 正在流式传输但没有任何内容时 -> 显示"正在思考"
              */}
              {message.isStreaming && !hasText && !message.content && !hasThinking && !runningTool && (
                <div className="flex items-center gap-2.5 text-content-muted py-2">
                  <Loader2 className="h-4 w-4 animate-spin text-brand-500" />
                  <span className="text-sm font-medium">{t('assistant.thinkingStatus')}</span>
                </div>
              )}

              {/* 工具状态栏 - 放在文本内容下方居中 */}
              {renderToolStatusBar()}
            </>
          )
        })()}

        {/* 底部信息栏 - 操作按钮和统计信息在一行 */}
        {isComplete && (
          <div className="flex items-center justify-between mt-4 pt-3 border-t border-surface-border/30">
            {/* 左侧：操作按钮 */}
            <div className="flex items-center gap-0.5">
              <button
                onClick={handleCopy}
                className={cn(
                  'p-2 rounded-lg transition-all duration-150 hover:bg-surface/80',
                  copied ? 'text-emerald-500' : 'text-content-secondary hover:text-content-primary'
                )}
                title={t('assistant.actions.copy')}
              >
                {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
              </button>
              <button
                onClick={() => handleFeedback('like')}
                className={cn(
                  'p-2 rounded-lg transition-all duration-150 hover:bg-surface/80',
                  feedback === 'like' ? 'text-emerald-500' : 'text-content-secondary hover:text-content-primary'
                )}
                title={t('assistant.actions.helpful')}
              >
                <ThumbsUp className="h-4 w-4" />
              </button>
              <button
                onClick={() => handleFeedback('dislike')}
                className={cn(
                  'p-2 rounded-lg transition-all duration-150 hover:bg-surface/80',
                  feedback === 'dislike' ? 'text-rose-500' : 'text-content-secondary hover:text-content-primary'
                )}
                title={t('assistant.actions.notHelpful')}
              >
                <ThumbsDown className="h-4 w-4" />
              </button>
              <button
                onClick={onRetry}
                className="p-2 rounded-lg transition-all duration-150 hover:bg-surface/80 text-content-secondary hover:text-content-primary"
                title={t('assistant.actions.retry')}
              >
                <RotateCcw className="h-4 w-4" />
              </button>
              <button
                onClick={() => {
                  // TODO: 实现分享功能
                }}
                className="p-2 rounded-lg transition-all duration-150 hover:bg-surface/80 text-content-secondary hover:text-content-primary"
                title={t('assistant.actions.share')}
              >
                <Share2 className="h-4 w-4" />
              </button>
            </div>

            {/* 右侧：统计信息 */}
            <div className="flex items-center gap-3 text-xs text-content-tertiary">
              {message.metrics?.duration && (
                <span className="flex items-center gap-1.5">
                  <Clock className="h-3.5 w-3.5" />
                  <span className="font-medium">{message.metrics.duration.toFixed(1)}s</span>
                </span>
              )}
              {message.metrics?.tokens && (
                <span className="flex items-center gap-1.5">
                  <Coins className="h-3.5 w-3.5" />
                  <span className="font-medium">{message.metrics.tokens.toLocaleString()}</span>
                </span>
              )}
              {message.metrics?.cost !== undefined && message.metrics.cost > 0 && (
                <span className="font-semibold text-amber-600 dark:text-amber-400">
                  ${message.metrics.cost.toFixed(4)}
                </span>
              )}
              <span className="text-content-muted">{formatTime(message.timestamp)}</span>
            </div>
          </div>
        )}
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
