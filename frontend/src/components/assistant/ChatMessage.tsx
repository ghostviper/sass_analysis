'use client'

import { useState } from 'react'
import { cn } from '@/lib/utils'
import { useLocale } from '@/contexts/LocaleContext'
import {
  Bot,
  User,
  Loader2,
  Check,
  Database,
  TrendingUp,
  Trophy,
  Layers,
  ChevronDown,
  ChevronUp,
  Copy,
  ThumbsUp,
  ThumbsDown,
  RotateCcw,
  Share2,
  Clock,
  Coins,
  Globe,
} from 'lucide-react'
import { LucideIcon } from 'lucide-react'
import { Streamdown } from 'streamdown'

export type MessageRole = 'user' | 'assistant'

// 内容块类型 - 对应 Claude Agent SDK 的 content blocks
type ContentBlockType = 'thinking' | 'text' | 'tool_use' | 'tool_result'

interface ContentBlock {
  type: ContentBlockType
  content: string
  // For tool blocks
  toolName?: string
  toolInput?: Record<string, unknown>
  toolResult?: string
  toolStatus?: 'running' | 'completed'
  // For thinking blocks
  isStreaming?: boolean
}

// 工具调用状态
interface ToolStatus {
  name: string
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

// 工具名称映射
const toolNameMap: Record<string, { label: string; icon: LucideIcon }> = {
  query_startups: { label: '查询产品数据', icon: Database },
  get_category_analysis: { label: '分析市场类目', icon: Layers },
  get_trend_report: { label: '生成趋势报告', icon: TrendingUp },
  get_leaderboard: { label: '获取排行榜', icon: Trophy },
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
  const previewLength = 150
  const hasMore = content.length > previewLength

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

// 内容块分隔符
function BlockSeparator({ label }: { label?: string }) {
  return (
    <div data-chat-block="separator">
      {label && <span className="separator-label">{label}</span>}
    </div>
  )
}

export function ChatMessage({ message, onRetry, onCopy, onFeedback }: ChatMessageProps) {
  const { t } = useLocale()
  const [copied, setCopied] = useState(false)
  const [feedback, setFeedback] = useState<'like' | 'dislike' | null>(null)
  const [toolsExpanded, setToolsExpanded] = useState(false)
  const [expandedTools, setExpandedTools] = useState<Record<string, boolean>>({})
  const isUser = message.role === 'user'

  // 工具名称映射 - 优先使用后端提供的 displayText
  const getToolLabel = (tool: ToolStatus): string => {
    if (tool.displayText) return tool.displayText
    const toolInfo = toolNameMap[tool.name]
    return toolInfo?.label || tool.name
  }

  // 工具名称映射
  const toolNameMap: Record<string, { label: string; icon: LucideIcon }> = {
    query_startups: { label: t('assistant.tools.queryProducts'), icon: Database },
    get_category_analysis: { label: t('assistant.tools.analyzeCategory'), icon: Layers },
    get_trend_report: { label: t('assistant.tools.generateTrend'), icon: TrendingUp },
    get_leaderboard: { label: t('assistant.tools.getLeaderboard'), icon: Trophy },
    find_excellent_developers: { label: t('assistant.tools.findDevelopers') || '查找优秀开发者', icon: User },
    web_search: { label: t('assistant.tools.webSearch') || '搜索网络信息', icon: Globe },
  }

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
        <div className="flex flex-col items-end gap-1.5">
          <div className="max-w-[85%] md:max-w-[75%] rounded-2xl rounded-tr-md px-5 py-3.5 bg-gradient-to-r from-brand-500 to-brand-600 text-white shadow-md shadow-brand-500/20">
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
  const latestTool = message.toolStatus && message.toolStatus.length > 0
    ? message.toolStatus[message.toolStatus.length - 1]
    : undefined

  // 工具调用时间线
  const renderToolTimeline = () => {
    if (!message.toolStatus || message.toolStatus.length === 0) return null

    return (
      <div className="mb-4 rounded-xl border border-surface-border/50 bg-surface/30 backdrop-blur-sm p-4 shadow-sm">
        <div className="text-xs font-semibold text-content-secondary mb-4 tracking-wide">{t('assistant.tools.analysisSteps')}</div>
        <div className="space-y-4">
          {message.toolStatus.map((tool, idx) => {
            const toolInfo = toolNameMap[tool.name] || { label: tool.name, icon: Database }
            const ToolIcon = toolInfo.icon
            const isRunningTool = tool.status === 'running'
            const isDoneTool = tool.status === 'completed'
            const toolKey = `${tool.name}-${idx}`
            const isExpanded = expandedTools[toolKey]
            const isLastItem = idx === message.toolStatus!.length - 1
            // 使用 displayText 或回退到 toolInfo.label
            const displayLabel = tool.displayText || toolInfo.label

            return (
              <div key={`${tool.name}-${idx}`} className="relative flex gap-3">
                {/* 左侧时间线 */}
                <div className="flex flex-col items-center">
                  <div className={cn(
                    'w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0',
                    isDoneTool ? 'bg-emerald-500/10' : isRunningTool ? 'bg-amber-500/10' : 'bg-surface/60'
                  )}>
                    <ToolIcon className={cn(
                      'h-4 w-4',
                      isDoneTool ? 'text-emerald-500' : isRunningTool ? 'text-amber-500' : 'text-content-muted'
                    )} />
                  </div>
                  {!isLastItem && (
                    <div className="w-px flex-1 bg-surface-border/60 my-1" />
                  )}
                </div>

                {/* 右侧内容 */}
                <div className="flex-1 min-w-0 pb-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-sm font-semibold text-content-primary">{displayLabel}</span>
                    <span className="inline-flex items-center justify-center px-1.5 py-0.5 text-[10px] font-semibold rounded bg-surface/60 text-content-muted border border-surface-border/60">
                      {idx + 1}/{message.toolStatus!.length}
                    </span>
                    {isRunningTool && (
                      <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-amber-500">
                        <Loader2 className="h-3 w-3 animate-spin" />
                        {t('assistant.tools.inProgress')}
                      </span>
                    )}
                    {isDoneTool && (
                      <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-500">
                        <Check className="h-3 w-3" />
                        {t('assistant.tools.completed')}
                      </span>
                    )}
                  </div>
                  {tool.result ? (
                    <div className="mt-2 rounded-lg bg-surface/40 border border-surface-border/40 p-3 text-xs text-content-secondary whitespace-pre-wrap leading-relaxed">
                      {isExpanded || tool.result.length <= 200 ? tool.result : `${tool.result.slice(0, 200)}…`}
                      {tool.result.length > 200 && (
                        <button
                          type="button"
                          className="mt-2 block text-[11px] font-semibold text-brand-500 hover:text-brand-600 transition-colors"
                          onClick={() => setExpandedTools(prev => ({ ...prev, [toolKey]: !isExpanded }))}
                        >
                          {isExpanded ? t('assistant.tools.collapse') : t('assistant.tools.expand')}
                        </button>
                      )}
                    </div>
                  ) : (
                    <div className="mt-1 text-xs text-content-muted/70 font-medium">
                      {isRunningTool ? t('assistant.tools.executing') : t('assistant.tools.waitingResult')}
                    </div>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      </div>
    )
  }

  const renderToolSummary = () => {
    if (!latestTool) return null
    const toolInfo = toolNameMap[latestTool.name] || { label: latestTool.name, icon: Database }
    const ToolIcon = toolInfo.icon
    const isRunningTool = latestTool.status === 'running'
    const isDoneTool = latestTool.status === 'completed'
    const totalTools = message.toolStatus?.length || 0
    const completedCount = message.toolStatus?.filter(t => t.status === 'completed').length || 0
    // 使用 displayText 或回退到 toolInfo.label
    const displayLabel = latestTool.displayText || toolInfo.label

    return (
      <button
        type="button"
        onClick={() => setToolsExpanded(!toolsExpanded)}
        className="mb-3 w-full rounded-xl border border-surface-border/50 bg-surface/30 backdrop-blur-sm px-4 py-3 text-left hover:border-brand-500/30 hover:bg-surface/40 transition-all shadow-sm"
      >
        <div className="flex items-center gap-3">
          <div className={cn(
            'flex h-9 w-9 items-center justify-center rounded-lg flex-shrink-0',
            isDoneTool ? 'bg-emerald-500/10' : isRunningTool ? 'bg-amber-500/10' : 'bg-brand-500/10'
          )}>
            <ToolIcon className={cn(
              'h-4 w-4',
              isDoneTool ? 'text-emerald-500' : isRunningTool ? 'text-amber-500' : 'text-brand-500'
            )} />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-sm font-semibold text-content-primary">{displayLabel}</span>
              <span className="text-[10px] font-semibold text-content-muted bg-surface/60 px-1.5 py-0.5 rounded border border-surface-border/60">
                {completedCount}/{totalTools}
              </span>
              {isRunningTool && (
                <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-amber-500">
                  <Loader2 className="h-3 w-3 animate-spin" />
                  {t('assistant.tools.inProgress')}
                </span>
              )}
              {isDoneTool && completedCount === totalTools && (
                <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-500">
                  <Check className="h-3 w-3" />
                  {t('assistant.tools.allCompleted')}
                </span>
              )}
            </div>
            <div className="text-xs text-content-muted/70 mt-1 truncate font-medium">
              {latestTool.result ? latestTool.result : (isRunningTool ? t('assistant.tools.executing') : t('assistant.tools.waitingResult'))}
            </div>
          </div>
          <div className="flex-shrink-0 p-1">
            {toolsExpanded ? (
              <ChevronUp className="h-4 w-4 text-content-muted/60" />
            ) : (
              <ChevronDown className="h-4 w-4 text-content-muted/60" />
            )}
          </div>
        </div>
      </button>
    )
  }

  return (
    <div className="flex gap-3 group">
      <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-brand-500/20 via-accent-secondary/20 to-brand-600/20 flex items-center justify-center flex-shrink-0 ring-1 ring-brand-500/10">
        <Bot className="h-4 w-4 text-brand-500" />
      </div>
      <div className="flex-1 min-w-0 pt-1">
        {/* 工具调用摘要 / 时间线 */}
        {hasActiveTools && (
          <>
            {renderToolSummary()}
            {toolsExpanded && renderToolTimeline()}
          </>
        )}

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

              {/* 思考和回复之间的分隔符 */}
              {hasThinking && hasText && (
                <BlockSeparator label={t('assistant.reply')} />
              )}

              {/* 文本内容 */}
              {hasText ? (
                <div data-chat-block="text">
                  <Streamdown isAnimating={message.isStreaming}>
                    {textBlock.content}
                  </Streamdown>
                </div>
              ) : message.isStreaming && !message.content && runningTool ? (
                <div className="flex items-center gap-2.5 text-content-muted">
                  <Loader2 className="h-4 w-4 animate-spin text-brand-500" />
                  <span className="text-sm font-medium">{t('assistant.queryingData')}</span>
                </div>
              ) : message.isStreaming && !message.content ? (
                <div className="flex items-center gap-2.5 text-content-muted">
                  <Loader2 className="h-4 w-4 animate-spin text-brand-500" />
                  <span className="text-sm font-medium">{t('assistant.thinkingStatus')}</span>
                </div>
              ) : message.content ? (
                <div data-chat-block="text">
                  <Streamdown isAnimating={message.isStreaming}>
                    {message.content}
                  </Streamdown>
                </div>
              ) : null}
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
