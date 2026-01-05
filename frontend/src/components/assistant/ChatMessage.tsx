'use client'

import { useState } from 'react'
import { cn } from '@/lib/utils'
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
}: {
  content: string
  isStreaming?: boolean
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
        <span>思考过程</span>
        {isStreaming && (
          <Loader2 className="h-3 w-3 animate-spin" />
        )}
        <span className="thinking-badge">
          {isExpanded ? '收起' : '展开'}
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
          : 'text-content-muted hover:text-content-primary'
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
  const [toolsExpanded, setToolsExpanded] = useState(false)
  const [expandedTools, setExpandedTools] = useState<Record<string, boolean>>({})
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
        <div className="flex flex-col items-end gap-1">
          <div className="max-w-[75%] rounded-2xl rounded-tr-md px-4 py-3 bg-accent-primary text-white">
            <div className="text-[0.9375rem] leading-[1.65] whitespace-pre-wrap">
              {message.content}
            </div>
          </div>
          <span className="text-[11px] text-content-muted/50 mr-1">
            {formatTime(message.timestamp)}
          </span>
        </div>
        <div className="w-8 h-8 rounded-lg bg-accent-primary flex items-center justify-center flex-shrink-0">
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
      <div className="mb-4 rounded-xl border border-surface-border/60 bg-surface/40 p-3 md:p-4 shadow-sm">
        <div className="text-xs font-semibold text-content-secondary mb-2">分析步骤</div>
        <div className="space-y-3">
          {message.toolStatus.map((tool, idx) => {
            const toolInfo = toolNameMap[tool.name] || { label: tool.name, icon: Database }
            const ToolIcon = toolInfo.icon
            const isRunningTool = tool.status === 'running'
            const isDoneTool = tool.status === 'completed'
            const toolKey = `${tool.name}-${idx}`
            const isExpanded = expandedTools[toolKey]
            const indicatorClass = isDoneTool
              ? 'bg-accent-success border-accent-success/60'
              : isRunningTool
                ? 'bg-accent-warning border-accent-warning/60 animate-pulse'
                : 'bg-surface-border'

            return (
              <div key={`${tool.name}-${idx}`} className="relative pl-7">
                <div className="absolute left-2 top-3 bottom-0 w-px bg-surface-border/70" aria-hidden />
                <div className={`absolute left-1 top-2 h-2.5 w-2.5 rounded-full border bg-surface ${indicatorClass}`} />
                <div className="flex items-start gap-2">
                  <div className={`mt-0.5 flex h-7 w-7 items-center justify-center rounded-lg bg-surface/60 text-accent-primary`}>
                    <ToolIcon className="h-3.5 w-3.5" />
                  </div>
                  <div className="flex-1 space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="inline-flex items-center justify-center px-2 py-0.5 text-[11px] rounded-full bg-surface/70 text-content-muted border border-surface-border/70">
                        步骤 {idx + 1}
                      </span>
                      <span className="text-sm font-medium text-content-primary">{toolInfo.label}</span>
                      {isRunningTool && (
                        <span className="inline-flex items-center gap-1 text-[11px] font-medium text-accent-warning">
                          <Loader2 className="h-3 w-3 animate-spin" />
                          进行中
                        </span>
                      )}
                      {isDoneTool && (
                        <span className="inline-flex items-center gap-1 text-[11px] font-medium text-accent-success">
                          <Check className="h-3 w-3" />
                          已完成
                        </span>
                      )}
                    </div>
                    {tool.result ? (
                      <div className="rounded-lg bg-surface/50 border border-surface-border/50 p-2 text-xs text-content-secondary whitespace-pre-wrap leading-relaxed">
                        {isExpanded || tool.result.length <= 300 ? tool.result : `${tool.result.slice(0, 300)}…`}
                        {tool.result.length > 300 && (
                          <button
                            type="button"
                            className="mt-1 block text-[11px] text-accent-primary hover:text-accent-primary/80"
                            onClick={() => setExpandedTools(prev => ({ ...prev, [toolKey]: !isExpanded }))}
                          >
                            {isExpanded ? '收起结果' : '展开全部'}
                          </button>
                        )}
                      </div>
                    ) : (
                      <div className="text-xs text-content-muted/80">
                        {isRunningTool ? '正在执行...' : '等待结果...'}
                      </div>
                    )}
                  </div>
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

    return (
      <button
        type="button"
        onClick={() => setToolsExpanded(!toolsExpanded)}
        className="mb-3 w-full rounded-lg border border-surface-border/60 bg-surface/40 px-3 py-2 text-left hover:border-accent-primary/40 transition-all shadow-sm"
      >
        <div className="flex items-center gap-2">
          <div className="flex h-7 w-7 items-center justify-center rounded-md bg-surface/70 text-accent-primary">
            <ToolIcon className="h-3.5 w-3.5" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium text-content-primary truncate">{toolInfo.label}</span>
              {isRunningTool && (
                <span className="inline-flex items-center gap-1 text-[11px] font-medium text-accent-warning">
                  <Loader2 className="h-3 w-3 animate-spin" />
                  进行中
                </span>
              )}
              {isDoneTool && (
                <span className="inline-flex items-center gap-1 text-[11px] font-medium text-accent-success">
                  <Check className="h-3 w-3" />
                  已完成
                </span>
              )}
            </div>
            <div className="text-xs text-content-muted/80 mt-0.5 truncate">
              {latestTool.result ? latestTool.result : (isRunningTool ? '正在执行...' : '等待结果...')}
            </div>
          </div>
          {toolsExpanded ? (
            <ChevronUp className="h-3.5 w-3.5 text-content-muted/70" />
          ) : (
            <ChevronDown className="h-3.5 w-3.5 text-content-muted/70" />
          )}
        </div>
      </button>
    )
  }

  return (
    <div className="flex gap-3 group">
      <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent-primary/20 to-accent-secondary/20 flex items-center justify-center flex-shrink-0">
        <Bot className="h-4 w-4 text-accent-primary" />
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
                />
              )}

              {/* 思考和回复之间的分隔符 */}
              {hasThinking && hasText && (
                <BlockSeparator label="回复" />
              )}

              {/* 文本内容 */}
              {hasText ? (
                <div data-chat-block="text">
                  <Streamdown isAnimating={message.isStreaming}>
                    {textBlock.content}
                  </Streamdown>
                </div>
              ) : message.isStreaming && !message.content && runningTool ? (
                <div className="flex items-center gap-2 text-content-muted">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span className="text-sm">正在查询数据...</span>
                </div>
              ) : message.isStreaming && !message.content ? (
                <div className="flex items-center gap-2 text-content-muted">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span className="text-sm">正在思考...</span>
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
