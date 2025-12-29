'use client'

import { useState, useRef, useEffect, useCallback } from 'react'
import { cn } from '@/lib/utils'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import {
  faPaperPlane,
  faSpinner,
  faChartLine,
  faCompass,
  faMagnifyingGlass,
  faLink,
  faDatabase,
  faGlobe,
  faXmark,
  faPlus,
  faChevronDown,
  faCheck,
  faSliders,
  faWandMagicSparkles,
  faClockRotateLeft,
  faTrash,
  faMessage,
} from '@fortawesome/free-solid-svg-icons'
import { ChatMessage, MessageRole } from '@/components/assistant/ChatMessage'
import { SuggestedPrompts } from '@/components/assistant/SuggestedPrompts'
import { getStartups } from '@/lib/api'
import type { Startup } from '@/types'

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

// 消息类型
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
  startTime?: number  // 开始时间戳，用于计算耗时
}

// SSE 事件类型
interface StreamEvent {
  type: 'text' | 'tool_start' | 'tool_end' | 'status' | 'done' | 'error'
  content?: string
  tool_name?: string
  tool_input?: Record<string, unknown>
  tool_result?: string
  cost?: number
}

// 会话类型
interface ChatSession {
  id: string
  title: string
  messages: Message[]
  mode: AnalysisMode
  context: {
    type: 'database' | 'url' | null
    value: string | null
  }
  createdAt: Date
  updatedAt: Date
}

// 分析模式
type AnalysisMode = 'product' | 'trend' | 'career' | null

const modeConfig = {
  product: {
    icon: faMagnifyingGlass,
    label: '产品分析',
    description: '深度分析产品数据、收入、竞争力等',
    placeholder: '描述你想分析的产品，或询问具体问题...',
    prompts: [
      '分析月收入超过 $5000 的产品有什么共同特点？',
      '技术复杂度低但收入不错的产品有哪些？',
      '有哪些小而美的产品案例值得学习？',
      '如何评估一个产品的可复制性？',
    ],
  },
  trend: {
    icon: faChartLine,
    label: '行业趋势',
    description: '洞察赛道机会、市场动态与趋势',
    placeholder: '询问行业趋势、市场机会...',
    prompts: [
      '当前最值得关注的 SaaS 赛道有哪些？',
      '哪些领域竞争相对较小但有潜力？',
      'AI 工具赛道还有哪些机会？',
      '2024 年独立开发者应该关注什么趋势？',
    ],
  },
  career: {
    icon: faCompass,
    label: '方向探索',
    description: '根据你的背景推荐适合的方向',
    placeholder: '描述你的背景和目标，我来帮你分析...',
    prompts: [
      '独立开发者适合做什么类型的产品？',
      '我是前端开发，适合做什么 SaaS？',
      '如何从个人痛点出发找到产品方向？',
      '副业做 SaaS 需要注意什么？',
    ],
  },
}

export default function AssistantPage() {
  // 会话管理
  const [sessions, setSessions] = useState<ChatSession[]>([])
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null)
  const [showHistory, setShowHistory] = useState(false)

  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [analysisMode, setAnalysisMode] = useState<AnalysisMode>(null)

  // 上下文相关
  const [showContextMenu, setShowContextMenu] = useState(false)
  const [contextType, setContextType] = useState<'database' | 'url' | null>(null)
  const [selectedProduct, setSelectedProduct] = useState<Startup | null>(null)
  const [urlInput, setUrlInput] = useState('')

  // 产品搜索
  const [products, setProducts] = useState<Startup[]>([])
  const [productSearch, setProductSearch] = useState('')
  const [isSearching, setIsSearching] = useState(false)

  // 模式选择菜单
  const [showModeMenu, setShowModeMenu] = useState(false)

  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)
  const contextMenuRef = useRef<HTMLDivElement>(null)
  const modeMenuRef = useRef<HTMLDivElement>(null)
  const historyMenuRef = useRef<HTMLDivElement>(null)

  // 获取当前会话
  const currentSession = sessions.find(s => s.id === currentSessionId)

  // 点击外部关闭菜单
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (contextMenuRef.current && !contextMenuRef.current.contains(e.target as Node)) {
        setShowContextMenu(false)
      }
      if (modeMenuRef.current && !modeMenuRef.current.contains(e.target as Node)) {
        setShowModeMenu(false)
      }
      if (historyMenuRef.current && !historyMenuRef.current.contains(e.target as Node)) {
        setShowHistory(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  // 搜索产品
  useEffect(() => {
    if (contextType !== 'database' || !showContextMenu) return

    const search = async () => {
      setIsSearching(true)
      try {
        const data = await getStartups({
          page: 1,
          page_size: 8,
          search: productSearch || undefined,
        })
        setProducts(data.items)
      } catch (error) {
        console.error('Failed to search products:', error)
      } finally {
        setIsSearching(false)
      }
    }

    const debounce = setTimeout(search, 300)
    return () => clearTimeout(debounce)
  }, [productSearch, contextType, showContextMenu])

  // 滚动到底部
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages, scrollToBottom])

  // 调用后端 SSE 流式 API
  const streamFromBackend = async (
    userMessage: string,
    aiMessageId: string,
    onText: (text: string) => void,
    onToolStart: (tool: ToolStatus) => void,
    onToolEnd: (toolName: string, result: string) => void,
    onError: (error: string) => void,
    onDone: (cost?: number) => void
  ): Promise<void> => {
    try {
      const response = await fetch('/api/chat/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMessage,
          mode: analysisMode,
          context: contextType ? {
            type: contextType,
            value: contextType === 'database' ? selectedProduct?.name : urlInput
          } : undefined
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const reader = response.body?.getReader()
      if (!reader) {
        throw new Error('No response body')
      }

      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6)
            if (data === '[DONE]') {
              return
            }

            try {
              const event: StreamEvent = JSON.parse(data)

              switch (event.type) {
                case 'text':
                  if (event.content) {
                    onText(event.content)
                  }
                  break
                case 'tool_start':
                  if (event.tool_name) {
                    onToolStart({
                      name: event.tool_name,
                      status: 'running',
                      input: event.tool_input
                    })
                  }
                  break
                case 'tool_end':
                  if (event.tool_name) {
                    onToolEnd(event.tool_name, event.tool_result || '')
                  }
                  break
                case 'error':
                  onError(event.content || '未知错误')
                  break
                case 'done':
                  // 传递成本信息
                  onDone(event.cost)
                  break
              }
            } catch {
              console.warn('Failed to parse SSE event:', data)
            }
          }
        }
      }
    } catch (error) {
      console.error('Stream error:', error)
      onError(error instanceof Error ? error.message : '连接失败')
    }
  }

  // 创建新会话
  const createNewSession = () => {
    setCurrentSessionId(null)
    setMessages([])
    setAnalysisMode(null)
    setContextType(null)
    setSelectedProduct(null)
    setUrlInput('')
    setShowHistory(false)
  }

  // 切换会话
  const switchSession = (sessionId: string) => {
    const session = sessions.find(s => s.id === sessionId)
    if (session) {
      setCurrentSessionId(sessionId)
      setMessages(session.messages)
      setAnalysisMode(session.mode)
      setContextType(session.context.type)
      // 恢复会话时，如果有产品名称，创建简化的产品对象用于显示
      if (session.context.type === 'database' && session.context.value) {
        setSelectedProduct({ name: session.context.value } as Startup)
      } else {
        setSelectedProduct(null)
      }
      setUrlInput(session.context.type === 'url' ? session.context.value || '' : '')
      setShowHistory(false)
    }
  }

  // 删除会话
  const deleteSession = (sessionId: string, e: React.MouseEvent) => {
    e.stopPropagation()
    setSessions(prev => prev.filter(s => s.id !== sessionId))
    if (currentSessionId === sessionId) {
      setCurrentSessionId(null)
      setMessages([])
    }
  }

  // 发送消息
  const sendMessage = async (messageText?: string) => {
    const text = messageText || input.trim()
    if (!text || isLoading) return

    // 如果没有当前会话，创建一个新的
    let sessionId = currentSessionId
    if (!sessionId) {
      const newSession: ChatSession = {
        id: Date.now().toString(),
        title: text.slice(0, 20) + (text.length > 20 ? '...' : ''),
        messages: [],
        mode: analysisMode,
        context: {
          type: contextType,
          value: contextType === 'database' ? selectedProduct?.name || null : urlInput || null
        },
        createdAt: new Date(),
        updatedAt: new Date(),
      }
      setSessions(prev => [newSession, ...prev])
      sessionId = newSession.id
      setCurrentSessionId(sessionId)
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: text,
      timestamp: new Date(),
      context: contextType ? {
        type: contextType === 'database' ? 'product' : 'url',
        value: contextType === 'database' ? selectedProduct?.name || undefined : urlInput || undefined
      } : undefined
    }

    const newMessages = [...messages, userMessage]
    setMessages(newMessages)
    setInput('')
    setIsLoading(true)

    // 更新会话标题（如果是第一条消息）
    if (messages.length === 0) {
      setSessions(prev => prev.map(s =>
        s.id === sessionId
          ? { ...s, title: text.slice(0, 20) + (text.length > 20 ? '...' : ''), updatedAt: new Date() }
          : s
      ))
    }

    const aiMessageId = (Date.now() + 1).toString()
    const startTime = Date.now()
    const messagesWithStreaming = [...newMessages, {
      id: aiMessageId,
      role: 'assistant' as MessageRole,
      content: '',
      timestamp: new Date(),
      isStreaming: true,
      toolStatus: [],
      startTime,
    }]
    setMessages(messagesWithStreaming)

    // 累积响应文本和成本
    let accumulatedText = ''
    let totalCost = 0

    try {
      await streamFromBackend(
        text,
        aiMessageId,
        // onText - 处理文本流
        (textChunk) => {
          accumulatedText += textChunk
          setMessages(prev => prev.map(msg =>
            msg.id === aiMessageId ? { ...msg, content: accumulatedText } : msg
          ))
        },
        // onToolStart - 工具开始调用
        (tool) => {
          setMessages(prev => prev.map(msg => {
            if (msg.id === aiMessageId) {
              const existingTools = msg.toolStatus || []
              return {
                ...msg,
                toolStatus: [...existingTools, tool]
              }
            }
            return msg
          }))
        },
        // onToolEnd - 工具调用完成
        (toolName, result) => {
          setMessages(prev => prev.map(msg => {
            if (msg.id === aiMessageId) {
              const updatedTools = (msg.toolStatus || []).map(t =>
                t.name === toolName ? { ...t, status: 'completed' as const, result } : t
              )
              return { ...msg, toolStatus: updatedTools }
            }
            return msg
          }))
        },
        // onError - 错误处理
        (errorMsg) => {
          setMessages(prev => prev.map(msg =>
            msg.id === aiMessageId
              ? { ...msg, content: `抱歉，发生了错误：${errorMsg}`, isStreaming: false }
              : msg
          ))
        },
        // onDone - 完成处理
        (cost) => {
          totalCost = cost || 0
        }
      )

      // 标记流式传输完成，计算耗时
      const duration = (Date.now() - startTime) / 1000
      setMessages(prev => {
        const finalMessages = prev.map(msg =>
          msg.id === aiMessageId
            ? {
                ...msg,
                isStreaming: false,
                metrics: {
                  duration,
                  cost: totalCost,
                }
              }
            : msg
        )
        // 保存到会话
        setSessions(prevSessions => prevSessions.map(s =>
          s.id === sessionId
            ? { ...s, messages: finalMessages, updatedAt: new Date() }
            : s
        ))
        return finalMessages
      })
    } catch {
      setMessages(prev => prev.map(msg =>
        msg.id === aiMessageId ? { ...msg, content: '抱歉，发生了错误。请稍后重试。', isStreaming: false } : msg
      ))
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const selectProduct = (product: Startup) => {
    setSelectedProduct(product)
    setShowContextMenu(false)
  }

  const confirmUrl = () => {
    if (urlInput.trim()) {
      setShowContextMenu(false)
    }
  }

  const handleSuggestedPrompt = (prompt: string) => {
    setInput(prompt)
    inputRef.current?.focus()
  }

  // 重试消息
  const handleRetry = (messageId: string) => {
    // 找到这条消息之前的用户消息
    const messageIndex = messages.findIndex(m => m.id === messageId)
    if (messageIndex <= 0) return

    const userMessage = messages[messageIndex - 1]
    if (userMessage.role !== 'user') return

    // 删除当前 AI 消息，重新发送
    setMessages(prev => prev.filter(m => m.id !== messageId))
    sendMessage(userMessage.content)
  }

  const hasMessages = messages.length > 0
  const currentMode = analysisMode ? modeConfig[analysisMode] : null
  const hasContext = (contextType === 'database' && selectedProduct) || (contextType === 'url' && urlInput)

  return (
    <div className="h-[calc(100vh-3.5rem)] flex relative bg-diagonal-grid bg-assistant-glow">
      {/* 主内容区 */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {!hasMessages ? (
          /* 欢迎页面 */
          <div className="flex-1 flex flex-col">
            {/* 顶部工具栏 */}
            <div className="flex items-center justify-between px-4 py-3">
              <div className="relative" ref={historyMenuRef}>
                <button
                  onClick={() => setShowHistory(!showHistory)}
                  className="flex items-center gap-2 px-3 py-2 rounded-xl text-sm text-content-secondary hover:bg-surface hover:text-content-primary transition-colors"
                >
                  <FontAwesomeIcon icon={faClockRotateLeft} className="h-3.5 w-3.5" />
                  历史对话
                  {sessions.length > 0 && (
                    <span className="px-1.5 py-0.5 bg-accent-primary/10 text-accent-primary text-xs rounded-full font-medium">
                      {sessions.length}
                    </span>
                  )}
                  <FontAwesomeIcon
                    icon={faChevronDown}
                    className={cn('h-2.5 w-2.5 opacity-60 transition-transform duration-200', showHistory && 'rotate-180')}
                  />
                </button>

                {/* 历史对话下拉弹层 */}
                {showHistory && (
                  <div className="absolute left-0 top-full mt-2 w-80 bg-background border border-surface-border rounded-xl shadow-xl z-20 overflow-hidden animate-in fade-in slide-in-from-top-2 duration-200">
                    <div className="p-3 border-b border-surface-border/50 flex items-center justify-between">
                      <span className="text-sm font-medium text-content-primary">历史对话</span>
                      <button
                        onClick={createNewSession}
                        className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-accent-primary text-white text-xs font-medium hover:bg-accent-primary/90 transition-colors"
                      >
                        <FontAwesomeIcon icon={faPlus} className="h-3 w-3" />
                        新对话
                      </button>
                    </div>
                    <div className="max-h-72 overflow-y-auto p-2">
                      {sessions.length > 0 ? (
                        <div className="space-y-1">
                          {sessions.map(session => (
                            <button
                              key={session.id}
                              onClick={() => switchSession(session.id)}
                              className={cn(
                                'w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-left text-sm transition-colors group',
                                currentSessionId === session.id
                                  ? 'bg-accent-primary/10 text-accent-primary'
                                  : 'hover:bg-surface text-content-secondary hover:text-content-primary'
                              )}
                            >
                              <FontAwesomeIcon icon={faMessage} className="h-3.5 w-3.5 flex-shrink-0 opacity-60" />
                              <span className="flex-1 truncate">{session.title}</span>
                              <button
                                onClick={(e) => deleteSession(session.id, e)}
                                className="opacity-0 group-hover:opacity-100 p-1.5 hover:text-red-500 transition-all rounded-lg hover:bg-surface-hover"
                              >
                                <FontAwesomeIcon icon={faTrash} className="h-3 w-3" />
                              </button>
                            </button>
                          ))}
                        </div>
                      ) : (
                        <div className="text-center py-6">
                          <FontAwesomeIcon icon={faMessage} className="h-8 w-8 text-content-muted/30 mb-2" />
                          <p className="text-xs text-content-muted">暂无历史对话</p>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* 欢迎内容 - 垂直居中 */}
            <div className="flex-1 flex flex-col items-center justify-center px-4 -mt-12">
              <div className="w-full max-w-3xl mx-auto flex flex-col items-center">
                {/* 标题区域 */}
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-accent-primary to-accent-secondary flex items-center justify-center shadow-lg">
                    <FontAwesomeIcon icon={faWandMagicSparkles} className="h-5 w-5 text-white" />
                  </div>
                  <div>
                    <h1 className="text-xl font-display font-semibold text-content-primary">
                      SaaS 分析助手
                    </h1>
                    <p className="text-sm text-content-muted">
                      产品洞察 · 趋势分析 · 机会发现
                    </p>
                  </div>
                </div>

                {/* 输入框 */}
                <div className="w-full mb-4">
                  <div className="relative bg-surface/50 rounded-2xl border border-surface-border focus-within:border-accent-primary/50 focus-within:ring-2 focus-within:ring-accent-primary/20 transition-all shadow-sm">
                    <div className="flex items-end gap-3 px-4 py-4">
                      <textarea
                        ref={inputRef}
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder={currentMode?.placeholder || '问我任何关于 SaaS 产品的问题...'}
                        className="flex-1 bg-transparent resize-none text-content-primary placeholder:text-content-muted focus:outline-none min-h-[72px] max-h-48 text-base leading-relaxed"
                        rows={3}
                        disabled={isLoading}
                      />
                      <button
                        onClick={() => sendMessage()}
                        disabled={!input.trim() || isLoading}
                        className={cn(
                          'flex-shrink-0 w-11 h-11 rounded-xl flex items-center justify-center transition-all mb-1',
                          input.trim() && !isLoading
                            ? 'bg-accent-primary text-white hover:bg-accent-primary/90 shadow-sm'
                            : 'bg-surface-hover text-content-muted cursor-not-allowed'
                        )}
                      >
                        {isLoading ? (
                          <FontAwesomeIcon icon={faSpinner} className="h-4 w-4 animate-spin" />
                        ) : (
                          <FontAwesomeIcon icon={faPaperPlane} className="h-4 w-4" />
                        )}
                      </button>
                    </div>

                    {/* 底部工具栏 */}
                    <div className="flex items-center gap-2 px-4 pb-3">
                      {/* 模式选择 */}
                      <div className="relative" ref={modeMenuRef}>
                        <button
                          onClick={() => {
                            setShowModeMenu(!showModeMenu)
                            setShowContextMenu(false)
                          }}
                          className={cn(
                            'inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all',
                            currentMode
                              ? 'bg-accent-primary/10 text-accent-primary'
                              : 'bg-surface hover:bg-surface-hover text-content-secondary'
                          )}
                        >
                          <FontAwesomeIcon icon={currentMode?.icon || faSliders} className="h-3 w-3" />
                          {currentMode?.label || '分析模式'}
                          <FontAwesomeIcon
                            icon={faChevronDown}
                            className={cn('h-2.5 w-2.5 opacity-60 transition-transform duration-200', showModeMenu && 'rotate-180')}
                          />
                        </button>

                        {showModeMenu && (
                          <div className="absolute left-0 top-full mt-2 w-80 bg-background border border-surface-border rounded-xl shadow-xl z-20 overflow-hidden">
                            <div className="p-2 space-y-1">
                              {(Object.entries(modeConfig) as [AnalysisMode, typeof modeConfig.product][]).map(([key, config]) => (
                                <button
                                  key={key}
                                  onClick={() => {
                                    setAnalysisMode(key as AnalysisMode)
                                    setShowModeMenu(false)
                                  }}
                                  className={cn(
                                    'w-full flex items-center gap-3 px-3 py-3 rounded-lg text-left transition-all group',
                                    analysisMode === key
                                      ? 'bg-accent-primary/10'
                                      : 'hover:bg-surface'
                                  )}
                                >
                                  <div className={cn(
                                    'w-9 h-9 rounded-lg flex items-center justify-center transition-colors',
                                    analysisMode === key ? 'bg-accent-primary/20' : 'bg-surface group-hover:bg-surface-hover'
                                  )}>
                                    <FontAwesomeIcon
                                      icon={config.icon}
                                      className={cn(
                                        'h-4 w-4 transition-colors',
                                        analysisMode === key ? 'text-accent-primary' : 'text-content-muted group-hover:text-content-secondary'
                                      )}
                                    />
                                  </div>
                                  <div className="flex-1 min-w-0">
                                    <div className={cn(
                                      'text-sm font-medium',
                                      analysisMode === key ? 'text-accent-primary' : 'text-content-primary'
                                    )}>{config.label}</div>
                                    <div className="text-xs text-content-muted mt-0.5">{config.description}</div>
                                  </div>
                                  {analysisMode === key && <FontAwesomeIcon icon={faCheck} className="h-3.5 w-3.5 text-accent-primary flex-shrink-0" />}
                                </button>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>

                      {/* 关联产品 */}
                      <div className="relative" ref={contextMenuRef}>
                        <button
                          onClick={() => {
                            setShowContextMenu(!showContextMenu)
                            setShowModeMenu(false)
                            if (!contextType) setContextType('database')
                          }}
                          className={cn(
                            'relative inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all',
                            hasContext
                              ? 'bg-accent-success/15 text-accent-success'
                              : 'bg-surface hover:bg-surface-hover text-content-secondary'
                          )}
                        >
                          <FontAwesomeIcon icon={faLink} className="h-3 w-3" />
                          {hasContext ? (contextType === 'database' ? selectedProduct?.name : '已添加链接') : '关联产品'}
                          {hasContext && (
                            <span
                              onClick={(e) => {
                                e.stopPropagation()
                                setSelectedProduct(null)
                                setUrlInput('')
                                setContextType(null)
                              }}
                              className="absolute -top-1.5 -right-1.5 w-4 h-4 flex items-center justify-center bg-content-muted hover:bg-content-secondary text-white rounded-full cursor-pointer transition-colors"
                              title="取消关联"
                            >
                              <FontAwesomeIcon icon={faXmark} className="h-2 w-2" />
                            </span>
                          )}
                        </button>

                        {showContextMenu && (
                          <div className="absolute left-0 top-full mt-2 w-72 bg-background border border-surface-border rounded-xl shadow-xl z-20 overflow-hidden">
                            <div className="flex gap-1 p-2 border-b border-surface-border/50">
                              <button
                                onClick={() => setContextType('database')}
                                className={cn(
                                  'flex-1 flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg text-xs font-medium transition-all',
                                  contextType === 'database' ? 'bg-accent-primary/10 text-accent-primary' : 'text-content-muted hover:bg-surface'
                                )}
                              >
                                <FontAwesomeIcon icon={faDatabase} className="h-3 w-3" />
                                已有产品
                              </button>
                              <button
                                onClick={() => setContextType('url')}
                                className={cn(
                                  'flex-1 flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg text-xs font-medium transition-all',
                                  contextType === 'url' ? 'bg-accent-primary/10 text-accent-primary' : 'text-content-muted hover:bg-surface'
                                )}
                              >
                                <FontAwesomeIcon icon={faGlobe} className="h-3 w-3" />
                                外部链接
                              </button>
                            </div>
                            <div className="p-2">
                              {contextType === 'database' && (
                                <div>
                                  <div className="relative mb-2">
                                    <FontAwesomeIcon
                                      icon={isSearching ? faSpinner : faMagnifyingGlass}
                                      className={cn('absolute left-2.5 top-1/2 -translate-y-1/2 h-3 w-3 text-content-muted', isSearching && 'animate-spin')}
                                    />
                                    <input
                                      type="text"
                                      value={productSearch}
                                      onChange={(e) => setProductSearch(e.target.value)}
                                      placeholder="搜索产品名称..."
                                      className="w-full pl-8 pr-3 py-2 bg-surface rounded-lg text-sm focus:outline-none focus:ring-1 focus:ring-accent-primary/30"
                                    />
                                  </div>
                                  <div className="max-h-48 overflow-y-auto space-y-0.5">
                                    {products.length > 0 ? products.map((product) => (
                                      <button
                                        key={product.id}
                                        onClick={() => selectProduct(product)}
                                        className={cn(
                                          'w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-left transition-all',
                                          selectedProduct?.id === product.id ? 'bg-accent-primary/10 text-accent-primary' : 'hover:bg-surface text-content-primary'
                                        )}
                                      >
                                        {/* 产品 Logo */}
                                        <div className="w-8 h-8 rounded-lg bg-surface flex items-center justify-center flex-shrink-0 overflow-hidden">
                                          {product.logo_url ? (
                                            <img
                                              src={product.logo_url}
                                              alt={product.name}
                                              className="w-full h-full object-cover"
                                              onError={(e) => {
                                                (e.target as HTMLImageElement).style.display = 'none';
                                                (e.target as HTMLImageElement).nextElementSibling?.classList.remove('hidden');
                                              }}
                                            />
                                          ) : null}
                                          <span className={cn(
                                            'text-xs font-medium text-content-muted',
                                            product.logo_url && 'hidden'
                                          )}>
                                            {product.name.slice(0, 2).toUpperCase()}
                                          </span>
                                        </div>
                                        <span className="flex-1 text-sm truncate">{product.name}</span>
                                        {selectedProduct?.id === product.id && <FontAwesomeIcon icon={faCheck} className="h-3 w-3" />}
                                      </button>
                                    )) : (
                                      <p className="text-xs text-content-muted text-center py-3">{isSearching ? '搜索中...' : '暂无产品'}</p>
                                    )}
                                  </div>
                                </div>
                              )}
                              {contextType === 'url' && (
                                <div>
                                  <p className="text-xs text-content-muted mb-2">输入产品官网或落地页</p>
                                  <div className="flex gap-2">
                                    <input
                                      type="url"
                                      value={urlInput}
                                      onChange={(e) => setUrlInput(e.target.value)}
                                      placeholder="https://..."
                                      className="flex-1 px-3 py-2 bg-surface rounded-lg text-sm focus:outline-none focus:ring-1 focus:ring-accent-primary/30"
                                    />
                                    <button
                                      onClick={confirmUrl}
                                      disabled={!urlInput.trim()}
                                      className={cn(
                                        'px-4 py-2 rounded-lg text-sm font-medium transition-all',
                                        urlInput.trim() ? 'bg-accent-primary text-white hover:bg-accent-primary/90' : 'bg-surface text-content-muted'
                                      )}
                                    >
                                      确定
                                    </button>
                                  </div>
                                </div>
                              )}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                  <p className="text-xs text-content-muted mt-2 text-center">按 Enter 发送 · Shift + Enter 换行</p>
                </div>

                {/* 快速提示 */}
                <div className="w-full">
                  <SuggestedPrompts onSelect={handleSuggestedPrompt} />
                </div>
              </div>
            </div>
          </div>
        ) : (
          /* 对话页面 */
          <div className="flex-1 flex flex-col min-h-0">
            {/* 顶部栏 */}
            <div className="flex items-center justify-between px-4 py-3">
              <div className="flex items-center gap-3">
                {/* 历史对话下拉 */}
                <div className="relative" ref={historyMenuRef}>
                  <button
                    onClick={() => setShowHistory(!showHistory)}
                    className="flex items-center gap-2 px-3 py-2 rounded-xl text-sm text-content-secondary hover:bg-surface hover:text-content-primary transition-colors"
                  >
                    <FontAwesomeIcon icon={faClockRotateLeft} className="h-3.5 w-3.5" />
                    <span className="hidden sm:inline">历史</span>
                    <FontAwesomeIcon
                      icon={faChevronDown}
                      className={cn('h-2.5 w-2.5 opacity-60 transition-transform duration-200', showHistory && 'rotate-180')}
                    />
                  </button>

                  {/* 历史对话下拉弹层 */}
                  {showHistory && (
                    <div className="absolute left-0 top-full mt-2 w-80 bg-background border border-surface-border rounded-xl shadow-xl z-20 overflow-hidden animate-in fade-in slide-in-from-top-2 duration-200">
                      <div className="p-3 border-b border-surface-border/50 flex items-center justify-between">
                        <span className="text-sm font-medium text-content-primary">历史对话</span>
                        <button
                          onClick={createNewSession}
                          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-accent-primary text-white text-xs font-medium hover:bg-accent-primary/90 transition-colors"
                        >
                          <FontAwesomeIcon icon={faPlus} className="h-3 w-3" />
                          新对话
                        </button>
                      </div>
                      <div className="max-h-72 overflow-y-auto p-2">
                        {sessions.length > 0 ? (
                          <div className="space-y-1">
                            {sessions.map(session => (
                              <button
                                key={session.id}
                                onClick={() => switchSession(session.id)}
                                className={cn(
                                  'w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-left text-sm transition-colors group',
                                  currentSessionId === session.id
                                    ? 'bg-accent-primary/10 text-accent-primary'
                                    : 'hover:bg-surface text-content-secondary hover:text-content-primary'
                                )}
                              >
                                <FontAwesomeIcon icon={faMessage} className="h-3.5 w-3.5 flex-shrink-0 opacity-60" />
                                <span className="flex-1 truncate">{session.title}</span>
                                <button
                                  onClick={(e) => deleteSession(session.id, e)}
                                  className="opacity-0 group-hover:opacity-100 p-1.5 hover:text-red-500 transition-all rounded-lg hover:bg-surface-hover"
                                >
                                  <FontAwesomeIcon icon={faTrash} className="h-3 w-3" />
                                </button>
                              </button>
                            ))}
                          </div>
                        ) : (
                          <div className="text-center py-6">
                            <FontAwesomeIcon icon={faMessage} className="h-8 w-8 text-content-muted/30 mb-2" />
                            <p className="text-xs text-content-muted">暂无历史对话</p>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>

                <div className="h-4 w-px bg-surface-border" />
                <div className="flex items-center gap-2">
                  {currentMode && (
                    <span className="inline-flex items-center gap-1.5 px-2 py-1 rounded-lg text-xs font-medium bg-accent-primary/10 text-accent-primary">
                      <FontAwesomeIcon icon={currentMode.icon} className="h-3 w-3" />
                      {currentMode.label}
                    </span>
                  )}
                  {hasContext && (
                    <span className="inline-flex items-center gap-1.5 px-2 py-1 rounded-lg text-xs font-medium bg-accent-success/10 text-accent-success">
                      <FontAwesomeIcon icon={contextType === 'database' ? faDatabase : faGlobe} className="h-3 w-3" />
                      {contextType === 'database' ? selectedProduct?.name : '外部链接'}
                    </span>
                  )}
                </div>
              </div>
              <button
                onClick={createNewSession}
                className="flex items-center gap-1.5 px-3 py-2 rounded-xl text-sm text-content-secondary hover:bg-surface hover:text-content-primary transition-colors"
              >
                <FontAwesomeIcon icon={faPlus} className="h-3 w-3" />
                新对话
              </button>
            </div>

            {/* 消息列表 */}
            <div className="flex-1 overflow-y-auto px-4 py-4">
              <div className="max-w-3xl mx-auto space-y-6">
                {messages.map((message) => (
                  <ChatMessage
                    key={message.id}
                    message={message}
                    onRetry={message.role === 'assistant' ? () => handleRetry(message.id) : undefined}
                  />
                ))}
                <div ref={messagesEndRef} />
              </div>
            </div>

            {/* 固定底部输入区域 - 简洁样式 */}
            <div className="px-4 py-4">
              <div className="max-w-3xl mx-auto">
                <div className="relative bg-surface/50 rounded-2xl border border-surface-border focus-within:border-accent-primary/50 focus-within:ring-2 focus-within:ring-accent-primary/20 transition-all">
                  <div className="flex items-end gap-3 px-4 py-3">
                    <textarea
                      ref={inputRef}
                      value={input}
                      onChange={(e) => setInput(e.target.value)}
                      onKeyDown={handleKeyDown}
                      placeholder="继续提问..."
                      className="flex-1 bg-transparent resize-none text-content-primary placeholder:text-content-muted focus:outline-none min-h-[24px] max-h-32 text-sm leading-relaxed"
                      rows={1}
                      disabled={isLoading}
                      onInput={(e) => {
                        const target = e.target as HTMLTextAreaElement
                        target.style.height = 'auto'
                        target.style.height = Math.min(target.scrollHeight, 128) + 'px'
                      }}
                    />
                    <button
                      onClick={() => sendMessage()}
                      disabled={!input.trim() || isLoading}
                      className={cn(
                        'flex-shrink-0 w-9 h-9 rounded-xl flex items-center justify-center transition-all',
                        input.trim() && !isLoading
                          ? 'bg-accent-primary text-white hover:bg-accent-primary/90'
                          : 'bg-surface-hover text-content-muted cursor-not-allowed'
                      )}
                    >
                      {isLoading ? (
                        <FontAwesomeIcon icon={faSpinner} className="h-4 w-4 animate-spin" />
                      ) : (
                        <FontAwesomeIcon icon={faPaperPlane} className="h-4 w-4" />
                      )}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
