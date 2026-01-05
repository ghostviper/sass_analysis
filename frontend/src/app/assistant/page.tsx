'use client'

import { useState, useRef, useEffect, useCallback } from 'react'
import { cn } from '@/lib/utils'
import {
  Send,
  Loader2,
  Search,
  Link2,
  Database,
  Globe,
  X,
  Plus,
  ChevronDown,
  Check,
  Sparkles,
  History,
  Trash2,
  MessageSquare,
  Compass,
  Square,
  RotateCcw,
} from 'lucide-react'
import { ChatMessage, MessageRole } from '@/components/assistant/ChatMessage'
import { SuggestedPrompts } from '@/components/assistant/SuggestedPrompts'
import { getStartups } from '@/lib/api'
import type { Startup } from '@/types'
import { useLocale } from '@/contexts/LocaleContext'

// 渠道图标组件
const RedditIcon = ({ className, style }: { className?: string; style?: React.CSSProperties }) => (
  <svg className={className} style={style} viewBox="0 0 24 24" fill="currentColor">
    <path d="M12 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0zm5.01 4.744c.688 0 1.25.561 1.25 1.249a1.25 1.25 0 0 1-2.498.056l-2.597-.547-.8 3.747c1.824.07 3.48.632 4.674 1.488.308-.309.73-.491 1.207-.491.968 0 1.754.786 1.754 1.754 0 .716-.435 1.333-1.01 1.614a3.111 3.111 0 0 1 .042.52c0 2.694-3.13 4.87-7.004 4.87-3.874 0-7.004-2.176-7.004-4.87 0-.183.015-.366.043-.534A1.748 1.748 0 0 1 4.028 12c0-.968.786-1.754 1.754-1.754.463 0 .898.196 1.207.49 1.207-.883 2.878-1.43 4.744-1.487l.885-4.182a.342.342 0 0 1 .14-.197.35.35 0 0 1 .238-.042l2.906.617a1.214 1.214 0 0 1 1.108-.701zM9.25 12C8.561 12 8 12.562 8 13.25c0 .687.561 1.248 1.25 1.248.687 0 1.248-.561 1.248-1.249 0-.688-.561-1.249-1.249-1.249zm5.5 0c-.687 0-1.248.561-1.248 1.25 0 .687.561 1.248 1.249 1.248.688 0 1.249-.561 1.249-1.249 0-.687-.562-1.249-1.25-1.249zm-5.466 3.99a.327.327 0 0 0-.231.094.33.33 0 0 0 0 .463c.842.842 2.484.913 2.961.913.477 0 2.105-.056 2.961-.913a.361.361 0 0 0 .029-.463.33.33 0 0 0-.464 0c-.547.533-1.684.73-2.512.73-.828 0-1.979-.196-2.512-.73a.326.326 0 0 0-.232-.095z"/>
  </svg>
)

const IndieHackersIcon = ({ className, style }: { className?: string; style?: React.CSSProperties }) => (
  <svg className={className} style={style} viewBox="0 0 24 24" fill="currentColor">
    <path d="M0 0h24v24H0V0zm3.18 6h2.1v12h-2.1V6zm5.88 0h2.1v12h-2.1V6zm5.88 0h2.1v12h-2.1V6z"/>
  </svg>
)

const ProductHuntIcon = ({ className, style }: { className?: string; style?: React.CSSProperties }) => (
  <svg className={className} style={style} viewBox="0 0 24 24" fill="currentColor">
    <path d="M13.604 8.4h-3.405V12h3.405c.995 0 1.801-.806 1.801-1.801 0-.993-.805-1.799-1.801-1.799zM12 0C5.372 0 0 5.372 0 12s5.372 12 12 12 12-5.372 12-12S18.628 0 12 0zm1.604 14.4h-3.405V18H7.801V6h5.804c2.319 0 4.2 1.88 4.2 4.199 0 2.321-1.881 4.201-4.201 4.201z"/>
  </svg>
)

const GoogleIcon = ({ className, style }: { className?: string; style?: React.CSSProperties }) => (
  <svg className={className} style={style} viewBox="0 0 24 24" fill="currentColor">
    <path d="M12.48 10.92v3.28h7.84c-.24 1.84-.853 3.187-1.787 4.133-1.147 1.147-2.933 2.4-6.053 2.4-4.827 0-8.6-3.893-8.6-8.72s3.773-8.72 8.6-8.72c2.6 0 4.507 1.027 5.907 2.347l2.307-2.307C18.747 1.44 16.133 0 12.48 0 5.867 0 .307 5.387.307 12s5.56 12 12.173 12c3.573 0 6.267-1.173 8.373-3.36 2.16-2.16 2.84-5.213 2.84-7.667 0-.76-.053-1.467-.173-2.053H12.48z"/>
  </svg>
)

// 渠道配置
const CHANNELS = [
  { id: 'reddit', name: 'Reddit', Icon: RedditIcon, color: '#FF4500' },
  { id: 'indiehacker', name: 'IndieHackers', Icon: IndieHackersIcon, color: '#0E76A8' },
  { id: 'producthunt', name: 'Product Hunt', Icon: ProductHuntIcon, color: '#DA552F' },
  { id: 'google', name: 'Google', Icon: GoogleIcon, color: '#4285F4' },
] as const

type ChannelId = typeof CHANNELS[number]['id']

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
  // 内容块数组 - 用于区分 thinking、text、tool 等不同类型的内容
  contentBlocks?: ContentBlock[]
}

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

// SSE 事件类型
interface StreamEvent {
  type: 'text' | 'thinking' | 'tool_start' | 'tool_end' | 'status' | 'done' | 'error'
  content?: string
  tool_name?: string
  tool_input?: Record<string, unknown>
  tool_result?: string
  cost?: number
  session_id?: string  // Backend session ID for multi-turn conversations
}

// 会话类型
interface ChatSession {
  id: string
  title: string
  messages: Message[]
  context: {
    type: 'database' | 'url' | null
    value: string | null
  }
  serverSessionId?: string  // Backend session ID for multi-turn conversations
  createdAt: Date
  updatedAt: Date
}

export default function AssistantPage() {
  const { t } = useLocale()

  // 会话管理
  const [sessions, setSessions] = useState<ChatSession[]>([])
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null)
  const [showHistory, setShowHistory] = useState(false)

  // Backend session ID for multi-turn conversations (separate from UI session)
  const [serverSessionId, setServerSessionId] = useState<string | null>(null)

  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [showScrollToLatest, setShowScrollToLatest] = useState(false)

  // 中断控制
  const abortControllerRef = useRef<AbortController | null>(null)
  const [isInterrupted, setIsInterrupted] = useState(false)

  // 上下文相关
  const [showContextMenu, setShowContextMenu] = useState(false)
  const [contextType, setContextType] = useState<'database' | 'url' | null>(null)
  const [selectedProducts, setSelectedProducts] = useState<Startup[]>([])
  const [urlInput, setUrlInput] = useState('')

  // 渠道探索
  const [showChannelMenu, setShowChannelMenu] = useState(false)
  const [selectedChannels, setSelectedChannels] = useState<ChannelId[]>([])

  // 产品搜索
  const [products, setProducts] = useState<Startup[]>([])
  const [productSearch, setProductSearch] = useState('')
  const [isSearching, setIsSearching] = useState(false)

  // 兼容旧代码的单选产品（用于显示）
  const selectedProduct = selectedProducts.length > 0 ? selectedProducts[0] : null
  const setSelectedProduct = (product: Startup | null) => {
    if (product) {
      setSelectedProducts([product])
    } else {
      setSelectedProducts([])
    }
  }

  const messagesEndRef = useRef<HTMLDivElement>(null)
  const messagesContainerRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)
  const contextMenuRef = useRef<HTMLDivElement>(null)
  const channelMenuRef = useRef<HTMLDivElement>(null)
  const historyMenuRef = useRef<HTMLDivElement>(null)

  // 获取当前会话
  const currentSession = sessions.find(s => s.id === currentSessionId)

  // 点击外部关闭菜单
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (contextMenuRef.current && !contextMenuRef.current.contains(e.target as Node)) {
        setShowContextMenu(false)
      }
      if (channelMenuRef.current && !channelMenuRef.current.contains(e.target as Node)) {
        setShowChannelMenu(false)
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
    if (messagesContainerRef.current) {
      messagesContainerRef.current.scrollTo({
        top: messagesContainerRef.current.scrollHeight,
        behavior: 'smooth'
      })
    } else {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }
    setShowScrollToLatest(false)
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages, scrollToBottom])

  // 监听用户滚动：如果用户向上滚动离开底部，则显示“回到底部”按钮
  useEffect(() => {
    const container = messagesContainerRef.current
    if (!container) return

    const handleScroll = () => {
      const distanceFromBottom = container.scrollHeight - container.scrollTop - container.clientHeight
      const isAwayFromBottom = distanceFromBottom > 120
      setShowScrollToLatest(isAwayFromBottom)
    }

    container.addEventListener('scroll', handleScroll, { passive: true })
    return () => container.removeEventListener('scroll', handleScroll)
  }, [])

  // 调用后端 SSE 流式 API
  const streamFromBackend = async (
    userMessage: string,
    aiMessageId: string,
    sessionId: string | null,  // Backend session ID for multi-turn
    onText: (text: string) => void,
    onThinking: (thinking: string) => void,  // 思考内容回调
    onToolStart: (tool: ToolStatus) => void,
    onToolEnd: (toolName: string, result: string) => void,
    onError: (error: string) => void,
    onDone: (cost?: number, newSessionId?: string) => void,
    signal?: AbortSignal  // 添加中断信号
  ): Promise<void> => {
    try {
      const response = await fetch('/api/chat/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMessage,
          session_id: sessionId,  // Pass session_id for multi-turn conversations
          context: contextType ? {
            type: contextType,
            value: contextType === 'database' ? selectedProduct?.name : urlInput
          } : undefined
        }),
        signal  // 传递中断信号
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
                case 'thinking':
                  if (event.content) {
                    onThinking(event.content)
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
                  onError(event.content || t('assistant.unknownError'))
                  break
                case 'done':
                  // 传递成本信息和 session_id
                  onDone(event.cost, event.session_id)
                  break
              }
            } catch {
              console.warn('Failed to parse SSE event:', data)
            }
          }
        }
      }
    } catch (error) {
      // 检查是否是中断错误
      if (error instanceof Error && error.name === 'AbortError') {
        console.log('Request was interrupted')
        return
      }
      console.error('Stream error:', error)
      onError(error instanceof Error ? error.message : t('assistant.connectionFailed'))
    }
  }

  // 创建新会话
  const createNewSession = () => {
    // 如果正在加载，先中断
    if (isLoading && abortControllerRef.current) {
      abortControllerRef.current.abort()
    }
    setCurrentSessionId(null)
    setServerSessionId(null)  // Reset backend session for new conversation
    setMessages([])
    setContextType(null)
    setSelectedProduct(null)
    setUrlInput('')
    setShowHistory(false)
    setIsInterrupted(false)
  }

  // 中断当前请求
  const interruptRequest = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
      setIsInterrupted(true)
      setIsLoading(false)

      // 标记当前正在流式传输的消息为已中断
      setMessages(prev => prev.map(msg => {
        if (msg.isStreaming) {
          return {
            ...msg,
            isStreaming: false,
            content: msg.content + '\n\n*[' + t('assistant.interrupted') + ']*',
            contentBlocks: (msg.contentBlocks || []).map(block => ({
              ...block,
              isStreaming: false
            }))
          }
        }
        return msg
      }))
    }
  }

  // 恢复/继续对话
  const resumeConversation = () => {
    setIsInterrupted(false)
    // 可以在这里添加恢复逻辑，比如重新发送最后一条消息
  }

  // 切换会话
  const switchSession = (sessionId: string) => {
    const session = sessions.find(s => s.id === sessionId)
    if (session) {
      setCurrentSessionId(sessionId)
      setServerSessionId(session.serverSessionId || null)  // Restore backend session
      setMessages(session.messages)
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
    setIsInterrupted(false)

    // 创建新的 AbortController
    abortControllerRef.current = new AbortController()

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

    // 累积响应文本、思考内容和成本
    let accumulatedText = ''
    let accumulatedThinking = ''
    let totalCost = 0
    let newServerSessionId: string | undefined

    // 辅助函数：更新消息的内容块
    const updateContentBlocks = (msgId: string, updateFn: (blocks: ContentBlock[]) => ContentBlock[]) => {
      setMessages(prev => prev.map(msg => {
        if (msg.id !== msgId) return msg
        const currentBlocks = msg.contentBlocks || []
        return { ...msg, contentBlocks: updateFn(currentBlocks) }
      }))
    }

    try {
      await streamFromBackend(
        text,
        aiMessageId,
        serverSessionId,  // Pass current backend session ID
        // onText - 处理文本流
        (textChunk) => {
          accumulatedText += textChunk
          setMessages(prev => prev.map(msg => {
            if (msg.id !== aiMessageId) return msg
            // 更新 content 用于兼容
            const newMsg = { ...msg, content: accumulatedText }
            // 更新或创建 text 内容块
            const blocks = [...(msg.contentBlocks || [])]
            const textBlockIndex = blocks.findIndex(b => b.type === 'text')
            if (textBlockIndex >= 0) {
              blocks[textBlockIndex] = { ...blocks[textBlockIndex], content: accumulatedText }
            } else {
              blocks.push({ type: 'text', content: accumulatedText })
            }
            newMsg.contentBlocks = blocks
            return newMsg
          }))
        },
        // onThinking - 处理思考流
        (thinkingChunk) => {
          accumulatedThinking += thinkingChunk
          setMessages(prev => prev.map(msg => {
            if (msg.id !== aiMessageId) return msg
            // 更新或创建 thinking 内容块
            const blocks = [...(msg.contentBlocks || [])]
            const thinkingBlockIndex = blocks.findIndex(b => b.type === 'thinking')
            if (thinkingBlockIndex >= 0) {
              blocks[thinkingBlockIndex] = { ...blocks[thinkingBlockIndex], content: accumulatedThinking, isStreaming: true }
            } else {
              // thinking 块应该在最前面
              blocks.unshift({ type: 'thinking', content: accumulatedThinking, isStreaming: true })
            }
            return { ...msg, contentBlocks: blocks }
          }))
        },
        // onToolStart - 工具开始调用
        (tool) => {
          setMessages(prev => prev.map(msg => {
            if (msg.id !== aiMessageId) return msg
            const existingTools = msg.toolStatus || []
            return {
              ...msg,
              toolStatus: [...existingTools, tool]
            }
          }))
        },
        // onToolEnd - 工具调用完成
        (toolName, result) => {
          setMessages(prev => prev.map(msg => {
            if (msg.id !== aiMessageId) return msg
            const updatedTools = (msg.toolStatus || []).map(t =>
              t.name === toolName ? { ...t, status: 'completed' as const, result } : t
            )
            return { ...msg, toolStatus: updatedTools }
          }))
        },
        // onError - 错误处理
        (errorMsg) => {
          setMessages(prev => prev.map(msg =>
            msg.id === aiMessageId
              ? { ...msg, content: `${t('assistant.errorOccurred')}：${errorMsg}`, isStreaming: false }
              : msg
          ))
        },
        // onDone - 完成处理
        (cost, returnedSessionId) => {
          totalCost = cost || 0
          newServerSessionId = returnedSessionId
          // 将仍在运行的工具标记为已完成，避免卡在旋转状态
          setMessages(prev => prev.map(msg => {
            if (msg.id !== aiMessageId) return msg
            const updatedTools = (msg.toolStatus || []).map(t =>
              t.status === 'running' ? { ...t, status: 'completed' as const } : t
            )
            return { ...msg, toolStatus: updatedTools }
          }))
        },
        abortControllerRef.current.signal  // 传递中断信号
      )

      // 标记流式传输完成，计算耗时
      const duration = (Date.now() - startTime) / 1000

      // Update serverSessionId if we got a new one from the backend
      if (newServerSessionId) {
        setServerSessionId(newServerSessionId)
      }

      setMessages(prev => {
        const finalMessages = prev.map(msg => {
          if (msg.id !== aiMessageId) return msg
          // 标记 thinking 块为非流式状态
          const blocks = (msg.contentBlocks || []).map(block => {
            if (block.type === 'thinking') {
              return { ...block, isStreaming: false }
            }
            return block
          })
          return {
            ...msg,
            isStreaming: false,
            contentBlocks: blocks,
            metrics: {
              duration,
              cost: totalCost,
            }
          }
        })
        // 保存到会话 (including serverSessionId)
        setSessions(prevSessions => prevSessions.map(s =>
          s.id === sessionId
            ? {
                ...s,
                messages: finalMessages,
                serverSessionId: newServerSessionId || s.serverSessionId,
                updatedAt: new Date()
              }
            : s
        ))
        return finalMessages
      })
    } catch {
      setMessages(prev => prev.map(msg =>
        msg.id === aiMessageId ? { ...msg, content: t('assistant.errorRetry'), isStreaming: false } : msg
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
    // 支持多选产品
    setSelectedProducts(prev => {
      const isSelected = prev.some(p => p.id === product.id)
      if (isSelected) {
        return prev.filter(p => p.id !== product.id)
      } else {
        return [...prev, product]
      }
    })
  }

  // 切换渠道选择
  const toggleChannel = (channelId: ChannelId) => {
    setSelectedChannels(prev => {
      const isSelected = prev.includes(channelId)
      if (isSelected) {
        return prev.filter(id => id !== channelId)
      } else {
        return [...prev, channelId]
      }
    })
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
                  className="flex items-center gap-2 px-3 py-2 rounded-xl text-sm text-content-secondary hover:bg-surface/60 hover:text-content-primary transition-all duration-200"
                >
                  <History className="h-3.5 w-3.5" />
                  <span className="font-medium">{t('assistant.history')}</span>
                  {sessions.length > 0 && (
                    <span className="px-1.5 py-0.5 bg-brand-500/10 text-brand-600 dark:text-brand-400 text-[10px] rounded-full font-semibold">
                      {sessions.length}
                    </span>
                  )}
                  <ChevronDown
                    className={cn('h-2.5 w-2.5 opacity-60 transition-transform duration-200', showHistory && 'rotate-180')}
                  />
                </button>

                {/* 历史对话下拉弹层 */}
                {showHistory && (
                  <div className="absolute left-0 top-full mt-2 w-80 bg-background/95 backdrop-blur-xl border border-surface-border/80 rounded-xl shadow-xl z-20 overflow-hidden animate-in fade-in slide-in-from-top-2 duration-200">
                    <div className="p-3 border-b border-surface-border/50 flex items-center justify-between">
                      <span className="text-sm font-semibold text-content-primary">{t('assistant.history')}</span>
                      <button
                        onClick={createNewSession}
                        className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-gradient-to-r from-brand-500 to-brand-600 text-white text-xs font-semibold hover:from-brand-600 hover:to-brand-700 transition-all shadow-sm"
                      >
                        <Plus className="h-3 w-3" />
                        {t('assistant.newChat')}
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
                                'w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-left text-sm transition-all group',
                                currentSessionId === session.id
                                  ? 'bg-brand-500/10 text-brand-600 dark:text-brand-400'
                                  : 'hover:bg-surface/60 text-content-secondary hover:text-content-primary'
                              )}
                            >
                              <MessageSquare className="h-3.5 w-3.5 flex-shrink-0 opacity-60" />
                              <span className="flex-1 truncate font-medium">{session.title}</span>
                              <button
                                onClick={(e) => deleteSession(session.id, e)}
                                className="opacity-0 group-hover:opacity-100 p-1.5 hover:text-rose-500 transition-all rounded-lg hover:bg-surface-hover"
                              >
                                <Trash2 className="h-3 w-3" />
                              </button>
                            </button>
                          ))}
                        </div>
                      ) : (
                        <div className="text-center py-6">
                          <MessageSquare className="h-8 w-8 text-content-muted/30 mx-auto mb-2" />
                          <p className="text-xs text-content-muted font-medium">{t('assistant.noHistory')}</p>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* 欢迎内容 - 整体上移 */}
            <div className="flex-1 flex flex-col items-center justify-center px-4 -mt-24">
              <div className="w-full max-w-3xl mx-auto flex flex-col items-center">
                {/* 标题区域 */}
                <div className="flex items-center gap-4 mb-8">
                  <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-brand-500 via-brand-600 to-accent-secondary flex items-center justify-center shadow-lg shadow-brand-500/20">
                    <Sparkles className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <h1 className="text-2xl font-display font-bold tracking-tight bg-gradient-to-r from-content-primary via-content-primary to-brand-600 dark:to-brand-400 bg-clip-text text-transparent">
                      {t('assistant.title')}
                    </h1>
                    <p className="text-sm text-content-tertiary mt-0.5 tracking-wide">
                      {t('assistant.subtitle')}
                    </p>
                  </div>
                </div>

                {/* 输入框 */}
                <div className="w-full mb-5">
                  <div className="relative bg-surface/70 backdrop-blur-sm rounded-2xl border border-surface-border/80 focus-within:border-brand-500/60 focus-within:ring-2 focus-within:ring-brand-500/20 focus-within:shadow-lg focus-within:shadow-brand-500/5 transition-all duration-300 shadow-sm">
                    <div className="flex items-end gap-3 px-5 py-4">
                      <textarea
                        ref={inputRef}
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder={t('assistant.inputPlaceholder')}
                        className="flex-1 bg-transparent resize-none text-content-primary placeholder:text-content-muted/70 focus:outline-none min-h-[72px] max-h-48 text-[0.9375rem] leading-relaxed font-normal"
                        rows={3}
                        disabled={isLoading}
                      />
                      <button
                        onClick={() => sendMessage()}
                        disabled={!input.trim() || isLoading}
                        className={cn(
                          'flex-shrink-0 w-11 h-11 rounded-xl flex items-center justify-center transition-all duration-200 mb-1',
                          input.trim() && !isLoading
                            ? 'bg-gradient-to-r from-brand-500 to-brand-600 text-white hover:from-brand-600 hover:to-brand-700 shadow-md shadow-brand-500/25'
                            : 'bg-surface-hover text-content-muted cursor-not-allowed'
                        )}
                      >
                        {isLoading ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          <Send className="h-4 w-4" />
                        )}
                      </button>
                    </div>

                    {/* 底部工具栏 - 渠道探索 + 关联产品 */}
                    <div className="flex items-center gap-2.5 px-5 pb-4">
                      {/* 渠道探索 */}
                      <div className="relative" ref={channelMenuRef}>
                        <button
                          onClick={() => setShowChannelMenu(!showChannelMenu)}
                          className={cn(
                            'relative inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all duration-200',
                            selectedChannels.length > 0
                              ? 'bg-brand-500/10 text-brand-600 dark:text-brand-400 ring-1 ring-brand-500/20'
                              : 'text-content-muted hover:text-content-secondary hover:bg-surface-hover/50'
                          )}
                        >
                          <Compass className="h-3 w-3" />
                          {selectedChannels.length > 0 ? t('assistant.selectedChannels').replace('{count}', String(selectedChannels.length)) : t('assistant.channelExplore')}
                          <ChevronDown
                            className={cn('h-2 w-2 transition-transform duration-200', showChannelMenu && 'rotate-180')}
                          />
                          {selectedChannels.length > 0 && (
                            <span
                              onClick={(e) => {
                                e.stopPropagation()
                                setSelectedChannels([])
                              }}
                              className="absolute -top-1.5 -right-1.5 w-4 h-4 flex items-center justify-center bg-content-muted hover:bg-content-secondary text-white rounded-full cursor-pointer transition-colors"
                              title={t('assistant.clearSelection')}
                            >
                              <X className="h-2 w-2" />
                            </span>
                          )}
                        </button>

                        {showChannelMenu && (
                          <div className="absolute left-0 top-full mt-2 w-56 bg-background/95 backdrop-blur-xl border border-surface-border/80 rounded-xl shadow-xl z-50 overflow-hidden">
                            <div className="p-2 border-b border-surface-border/50">
                              <span className="text-[11px] text-content-muted px-2 font-semibold tracking-wide">{t('assistant.selectDataSource')}</span>
                            </div>
                            <div className="p-2 space-y-1">
                              {CHANNELS.map((channel) => {
                                const isSelected = selectedChannels.includes(channel.id)
                                return (
                                  <button
                                    key={channel.id}
                                    onClick={() => toggleChannel(channel.id)}
                                    className={cn(
                                      'w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-left transition-all',
                                      isSelected
                                        ? 'bg-brand-500/10'
                                        : 'hover:bg-surface/60'
                                    )}
                                  >
                                    <div
                                      className="w-7 h-7 rounded-lg flex items-center justify-center transition-all"
                                      style={{ backgroundColor: `${channel.color}15` }}
                                    >
                                      <channel.Icon
                                        className="h-4 w-4 transition-all"
                                        style={{ color: channel.color }}
                                      />
                                    </div>
                                    <span className={cn(
                                      'flex-1 text-sm',
                                      isSelected ? 'text-content-primary font-semibold' : 'text-content-secondary font-medium'
                                    )}>
                                      {channel.name}
                                    </span>
                                    <div className={cn(
                                      'w-4 h-4 rounded border-2 flex items-center justify-center transition-all',
                                      isSelected
                                        ? 'bg-brand-500 border-brand-500'
                                        : 'border-content-muted/30'
                                    )}>
                                      {isSelected && (
                                        <Check className="h-2.5 w-2.5 text-white" />
                                      )}
                                    </div>
                                  </button>
                                )
                              })}
                            </div>
                          </div>
                        )}
                      </div>

                      {/* 关联产品 */}
                      <div className="relative" ref={contextMenuRef}>
                        <button
                          onClick={() => {
                            setShowContextMenu(!showContextMenu)
                            if (!contextType) setContextType('database')
                          }}
                          className={cn(
                            'relative inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all duration-200',
                            hasContext
                              ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 ring-1 ring-emerald-500/20'
                              : 'text-content-muted hover:text-content-secondary hover:bg-surface-hover/50'
                          )}
                        >
                          <Link2 className="h-3 w-3" />
                          {hasContext
                            ? (contextType === 'database'
                                ? (selectedProducts.length > 1
                                    ? t('assistant.selectedProducts').replace('{count}', String(selectedProducts.length))
                                    : selectedProduct?.name)
                                : t('assistant.addedLink'))
                            : t('assistant.linkProduct')}
                          <ChevronDown
                            className={cn('h-2 w-2 transition-transform duration-200', showContextMenu && 'rotate-180')}
                          />
                          {hasContext && (
                            <span
                              onClick={(e) => {
                                e.stopPropagation()
                                setSelectedProducts([])
                                setUrlInput('')
                                setContextType(null)
                              }}
                              className="absolute -top-1.5 -right-1.5 w-4 h-4 flex items-center justify-center bg-content-muted hover:bg-content-secondary text-white rounded-full cursor-pointer transition-colors"
                              title={t('assistant.cancelLink')}
                            >
                              <X className="h-2 w-2" />
                            </span>
                          )}
                        </button>

                        {showContextMenu && (
                          <div className="absolute left-0 top-full mt-2 w-72 bg-background/95 backdrop-blur-xl border border-surface-border/80 rounded-xl shadow-xl z-50 overflow-hidden">
                            <div className="flex gap-1 p-2 border-b border-surface-border/50">
                              <button
                                onClick={() => setContextType('database')}
                                className={cn(
                                  'flex-1 flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg text-xs font-semibold transition-all',
                                  contextType === 'database' ? 'bg-brand-500/10 text-brand-600 dark:text-brand-400' : 'text-content-muted hover:bg-surface/60'
                                )}
                              >
                                <Database className="h-3 w-3" />
                                {t('assistant.existingProducts')}
                              </button>
                              <button
                                onClick={() => setContextType('url')}
                                className={cn(
                                  'flex-1 flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg text-xs font-semibold transition-all',
                                  contextType === 'url' ? 'bg-brand-500/10 text-brand-600 dark:text-brand-400' : 'text-content-muted hover:bg-surface/60'
                                )}
                              >
                                <Globe className="h-3 w-3" />
                                {t('assistant.externalLink')}
                              </button>
                            </div>
                            <div className="p-2.5">
                              {contextType === 'database' && (
                                <div>
                                  <div className="relative mb-2.5">
                                    {isSearching ? (
                                      <Loader2 className="absolute left-2.5 top-1/2 -translate-y-1/2 h-3 w-3 text-brand-500 animate-spin" />
                                    ) : (
                                      <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-3 w-3 text-content-muted" />
                                    )}
                                    <input
                                      type="text"
                                      value={productSearch}
                                      onChange={(e) => setProductSearch(e.target.value)}
                                      placeholder={t('assistant.searchProducts')}
                                      className="w-full pl-8 pr-3 py-2 bg-surface/60 rounded-lg text-sm font-medium focus:outline-none focus:ring-1 focus:ring-brand-500/30 placeholder:text-content-muted/60"
                                    />
                                  </div>
                                  <div className="max-h-48 overflow-y-auto space-y-0.5">
                                    {products.length > 0 ? products.map((product) => {
                                      const isSelected = selectedProducts.some(p => p.id === product.id)
                                      return (
                                        <button
                                          key={product.id}
                                          onClick={() => selectProduct(product)}
                                          className={cn(
                                            'w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-left transition-all',
                                            isSelected ? 'bg-brand-500/10' : 'hover:bg-surface/60'
                                          )}
                                        >
                                          {/* 产品 Logo */}
                                          <div className="w-8 h-8 rounded-lg bg-surface/60 flex items-center justify-center flex-shrink-0 overflow-hidden">
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
                                              'text-xs font-semibold text-content-muted',
                                              product.logo_url && 'hidden'
                                            )}>
                                              {product.name.slice(0, 2).toUpperCase()}
                                            </span>
                                          </div>
                                          <span className={cn(
                                            'flex-1 text-sm truncate',
                                            isSelected ? 'text-content-primary font-semibold' : 'text-content-primary font-medium'
                                          )}>{product.name}</span>
                                          <div className={cn(
                                            'w-4 h-4 rounded border-2 flex items-center justify-center transition-all flex-shrink-0',
                                            isSelected
                                              ? 'bg-brand-500 border-brand-500'
                                              : 'border-content-muted/30'
                                          )}>
                                            {isSelected && (
                                              <Check className="h-2.5 w-2.5 text-white" />
                                            )}
                                          </div>
                                        </button>
                                      )
                                    }) : (
                                      <p className="text-xs text-content-muted text-center py-3 font-medium">{isSearching ? t('assistant.searching') : t('assistant.noProducts')}</p>
                                    )}
                                  </div>
                                </div>
                              )}
                              {contextType === 'url' && (
                                <div>
                                  <p className="text-xs text-content-muted mb-2.5 font-medium">{t('assistant.enterUrl')}</p>
                                  <div className="flex gap-2">
                                    <input
                                      type="url"
                                      value={urlInput}
                                      onChange={(e) => setUrlInput(e.target.value)}
                                      placeholder="https://..."
                                      className="flex-1 px-3 py-2 bg-surface/60 rounded-lg text-sm font-medium focus:outline-none focus:ring-1 focus:ring-brand-500/30 placeholder:text-content-muted/60"
                                    />
                                    <button
                                      onClick={confirmUrl}
                                      disabled={!urlInput.trim()}
                                      className={cn(
                                        'px-4 py-2 rounded-lg text-sm font-semibold transition-all',
                                        urlInput.trim() ? 'bg-gradient-to-r from-brand-500 to-brand-600 text-white hover:from-brand-600 hover:to-brand-700' : 'bg-surface/60 text-content-muted'
                                      )}
                                    >
                                      {t('assistant.confirm')}
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
                  <p className="text-xs text-content-muted/70 mt-2.5 text-center font-medium tracking-wide">{t('assistant.sendTip')}</p>
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
                    className="flex items-center gap-2 px-3 py-2 rounded-xl text-sm text-content-secondary hover:bg-surface/60 hover:text-content-primary transition-all duration-200"
                  >
                    <History className="h-3.5 w-3.5" />
                    <span className="hidden sm:inline font-medium">{t('assistant.historyShort')}</span>
                    <ChevronDown
                      className={cn('h-2.5 w-2.5 opacity-60 transition-transform duration-200', showHistory && 'rotate-180')}
                    />
                  </button>

                  {/* 历史对话下拉弹层 */}
                  {showHistory && (
                    <div className="absolute left-0 top-full mt-2 w-80 bg-background/95 backdrop-blur-xl border border-surface-border/80 rounded-xl shadow-xl z-20 overflow-hidden animate-in fade-in slide-in-from-top-2 duration-200">
                      <div className="p-3 border-b border-surface-border/50 flex items-center justify-between">
                        <span className="text-sm font-semibold text-content-primary">{t('assistant.history')}</span>
                        <button
                          onClick={createNewSession}
                          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-gradient-to-r from-brand-500 to-brand-600 text-white text-xs font-semibold hover:from-brand-600 hover:to-brand-700 transition-all shadow-sm"
                        >
                          <Plus className="h-3 w-3" />
                          {t('assistant.newChat')}
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
                                  'w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-left text-sm transition-all group',
                                  currentSessionId === session.id
                                    ? 'bg-brand-500/10 text-brand-600 dark:text-brand-400'
                                    : 'hover:bg-surface/60 text-content-secondary hover:text-content-primary'
                                )}
                              >
                                <MessageSquare className="h-3.5 w-3.5 flex-shrink-0 opacity-60" />
                                <span className="flex-1 truncate font-medium">{session.title}</span>
                                <button
                                  onClick={(e) => deleteSession(session.id, e)}
                                  className="opacity-0 group-hover:opacity-100 p-1.5 hover:text-rose-500 transition-all rounded-lg hover:bg-surface-hover"
                                >
                                  <Trash2 className="h-3 w-3" />
                                </button>
                              </button>
                            ))}
                          </div>
                        ) : (
                          <div className="text-center py-6">
                            <MessageSquare className="h-8 w-8 text-content-muted/30 mx-auto mb-2" />
                            <p className="text-xs text-content-muted font-medium">{t('assistant.noHistory')}</p>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>

                <div className="h-4 w-px bg-surface-border/60" />
                <div className="flex items-center gap-2">
                  {hasContext && (
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 ring-1 ring-emerald-500/20">
                      {contextType === 'database' ? <Database className="h-3 w-3" /> : <Globe className="h-3 w-3" />}
                      {contextType === 'database' ? selectedProduct?.name : t('assistant.externalLink')}
                    </span>
                  )}
                </div>
              </div>
              <button
                onClick={createNewSession}
                className="flex items-center gap-1.5 px-3 py-2 rounded-xl text-sm text-content-secondary hover:bg-surface/60 hover:text-content-primary transition-all duration-200"
              >
                <Plus className="h-3 w-3" />
                <span className="font-medium">{t('assistant.newChat')}</span>
              </button>
            </div>

            {/* 消息列表 */}
            <div className="flex-1 overflow-y-auto px-4 py-4" ref={messagesContainerRef}>
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
          <div className="relative bg-surface/70 backdrop-blur-sm rounded-2xl border border-surface-border/80 focus-within:border-brand-500/60 focus-within:ring-2 focus-within:ring-brand-500/20 focus-within:shadow-lg focus-within:shadow-brand-500/5 transition-all duration-300">
            <div className="flex items-end gap-3 px-4 py-3">
              <textarea
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={t('assistant.continueChat')}
                className="flex-1 bg-transparent resize-none text-content-primary placeholder:text-content-muted/70 focus:outline-none min-h-[24px] max-h-32 text-sm leading-relaxed font-normal"
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
                  'flex-shrink-0 w-9 h-9 rounded-xl flex items-center justify-center transition-all duration-200',
                  input.trim() && !isLoading
                    ? 'bg-gradient-to-r from-brand-500 to-brand-600 text-white hover:from-brand-600 hover:to-brand-700 shadow-md shadow-brand-500/25'
                    : 'bg-surface-hover text-content-muted cursor-not-allowed'
                )}
              >
                {isLoading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Send className="h-4 w-4" />
                )}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* 回到最新输出按钮 */}
      {showScrollToLatest && (
        <button
          type="button"
          onClick={scrollToBottom}
          className="fixed bottom-28 right-6 z-30 inline-flex items-center gap-2 rounded-full bg-gradient-to-r from-brand-500 to-brand-600 text-white px-4 py-2.5 shadow-lg shadow-brand-500/25 hover:from-brand-600 hover:to-brand-700 transition-all font-semibold text-sm"
        >
          <ChevronDown className="h-4 w-4" />
          <span>{t('assistant.scrollToLatest')}</span>
        </button>
      )}
          </div>
        )}
      </div>
    </div>
  )
}
