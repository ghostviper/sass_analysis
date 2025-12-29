'use client'

import { cn } from '@/lib/utils'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faRobot, faUser, faSpinner, faCheck, faDatabase, faChartLine, faTrophy, faLayerGroup } from '@fortawesome/free-solid-svg-icons'
import { IconDefinition } from '@fortawesome/fontawesome-svg-core'

export type MessageRole = 'user' | 'assistant'

// 工具调用状态
interface ToolStatus {
  name: string
  status: 'running' | 'completed'
  input?: Record<string, unknown>
  result?: string
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
}

interface ChatMessageProps {
  message: Message
}

// 工具名称映射
const toolNameMap: Record<string, { label: string; icon: IconDefinition }> = {
  query_startups: { label: '查询产品数据', icon: faDatabase },
  get_category_analysis: { label: '分析市场类目', icon: faLayerGroup },
  get_trend_report: { label: '生成趋势报告', icon: faChartLine },
  get_leaderboard: { label: '获取排行榜', icon: faTrophy },
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user'

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
  const hasRunningTools = message.toolStatus?.some(t => t.status === 'running')

  return (
    <div className="flex gap-3">
      <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent-primary/20 to-accent-secondary/20 flex items-center justify-center flex-shrink-0">
        <FontAwesomeIcon icon={faRobot} className="h-4 w-4 text-accent-primary" />
      </div>
      <div className="flex-1 min-w-0 pt-1">
        {/* 工具调用状态 */}
        {hasActiveTools && (
          <div className="mb-3 space-y-2">
            {message.toolStatus!.map((tool, index) => {
              const toolInfo = toolNameMap[tool.name] || { label: tool.name, icon: faDatabase }
              return (
                <div
                  key={`${tool.name}-${index}`}
                  className={cn(
                    'inline-flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-medium transition-all',
                    tool.status === 'running'
                      ? 'bg-accent-warning/10 text-accent-warning border border-accent-warning/20'
                      : 'bg-accent-success/10 text-accent-success border border-accent-success/20'
                  )}
                >
                  <FontAwesomeIcon
                    icon={tool.status === 'running' ? faSpinner : toolInfo.icon}
                    className={cn('h-3 w-3', tool.status === 'running' && 'animate-spin')}
                  />
                  <span>{toolInfo.label}</span>
                  {tool.status === 'completed' && (
                    <FontAwesomeIcon icon={faCheck} className="h-3 w-3" />
                  )}
                </div>
              )
            })}
          </div>
        )}

        {/* 消息内容 */}
        {message.isStreaming && !message.content && hasRunningTools ? (
          <div className="flex items-center gap-2 text-content-muted">
            <FontAwesomeIcon icon={faSpinner} className="h-4 w-4 animate-spin" />
            <span className="text-sm">正在查询数据...</span>
          </div>
        ) : message.isStreaming && !message.content ? (
          <div className="flex items-center gap-2 text-content-muted">
            <FontAwesomeIcon icon={faSpinner} className="h-4 w-4 animate-spin" />
            <span className="text-sm">正在思考...</span>
          </div>
        ) : (
          <div className="prose-chat">
            <MarkdownRenderer content={message.content} />
          </div>
        )}
        <div className="text-xs mt-3 text-content-muted">
          {formatTime(message.timestamp)}
        </div>
      </div>
    </div>
  )
}

// Markdown 渲染器
function MarkdownRenderer({ content }: { content: string }) {
  const processContent = (text: string) => {
    // 处理代码块
    text = text.replace(/```(\w*)\n([\s\S]*?)```/g, (_, lang, code) => {
      return `<pre class="bg-surface/50 rounded-lg p-4 overflow-x-auto my-3 border border-surface-border/30"><code class="text-sm text-content-primary">${escapeHtml(code.trim())}</code></pre>`
    })

    // 处理行内代码
    text = text.replace(/`([^`]+)`/g, '<code class="bg-surface/50 px-1.5 py-0.5 rounded text-sm text-accent-primary">$1</code>')

    // 处理粗体
    text = text.replace(/\*\*([^*]+)\*\*/g, '<strong class="font-semibold text-content-primary">$1</strong>')

    // 处理标题
    text = text.replace(/^### (.+)$/gm, '<h4 class="text-sm font-semibold text-content-primary mt-4 mb-2 first:mt-0">$1</h4>')
    text = text.replace(/^## (.+)$/gm, '<h3 class="text-base font-semibold text-content-primary mt-5 mb-3 first:mt-0">$1</h3>')

    // 处理列表
    text = text.replace(/^(\d+)\. (.+)$/gm, '<li class="ml-5 list-decimal text-content-secondary text-sm leading-relaxed py-0.5">$2</li>')
    text = text.replace(/^- (.+)$/gm, '<li class="ml-5 list-disc text-content-secondary text-sm leading-relaxed py-0.5">$1</li>')

    // 处理表格
    const tableRegex = /\|(.+)\|/g
    let hasTable = false
    text = text.replace(tableRegex, (match) => {
      const cells = match.split('|').filter(c => c.trim())
      if (cells.every(c => c.trim().match(/^[-:]+$/))) {
        return ''
      }
      if (!hasTable) {
        hasTable = true
        return `<div class="overflow-x-auto my-3"><table class="w-full text-sm border-collapse"><tr class="bg-surface/30">${cells.map(c => `<th class="border border-surface-border/50 px-3 py-2 text-left font-medium text-content-primary">${c.trim()}</th>`).join('')}</tr>`
      }
      return `<tr>${cells.map(c => `<td class="border border-surface-border/50 px-3 py-2 text-content-secondary">${c.trim()}</td>`).join('')}</tr>`
    })
    if (hasTable) {
      text = text.replace(/<\/tr>(?![\s\S]*<tr)/, '</tr></table></div>')
    }

    // 处理引用
    text = text.replace(/^> (.+)$/gm, '<blockquote class="border-l-3 border-accent-primary/40 pl-4 my-3 text-content-muted italic">$1</blockquote>')

    // 处理段落和换行
    text = text.replace(/\n\n/g, '</p><p class="text-sm text-content-secondary leading-relaxed my-2">')
    text = text.replace(/\n/g, '<br/>')

    return `<p class="text-sm text-content-secondary leading-relaxed">${text}</p>`
  }

  const escapeHtml = (text: string) => {
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;')
  }

  return (
    <div
      className="text-content-secondary"
      dangerouslySetInnerHTML={{ __html: processContent(content) }}
    />
  )
}

function formatTime(date: Date): string {
  return date.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
  })
}
