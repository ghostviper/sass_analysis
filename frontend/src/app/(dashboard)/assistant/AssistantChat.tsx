'use client'

import { useState, useRef, useEffect, useCallback } from 'react'
import { useRouter } from 'next/navigation'
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
  Square,
  User,
} from 'lucide-react'
import { ChatMessage, MessageRole } from '@/components/assistant/ChatMessage'
import { SuggestedPrompts } from '@/components/assistant/SuggestedPrompts'
import { ContextSelector, SelectedItem } from '@/components/assistant/ContextSelector'
import { getStartups, getChatSessions, getChatSession, deleteChatSession, getFounderLeaderboard } from '@/lib/api'
import type { Startup } from '@/types'
import type { ChatSessionListItem, ChatMessageItem, FounderLeaderboardItem } from '@/lib/api'
import { useLocale } from '@/contexts/LocaleContext'
import { saveCurrentSession, getLastSession } from '@/lib/sessionStorage'

// 工具调用状态
interface ToolStatus {
  name: string
  toolId?: string
  status: 'running' | 'completed'
  displayText?: string
}

// 消息统计
interface MessageMetrics {
  duration?: number
  tokens?: number
  cost?: number
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
  startTime?: number
  contentBlocks?: ContentBlock[]
}

// 内容块类型
type ContentBlockType = 'thinking' | 'text' | 'tool_use' | 'tool_result'

interface ContentBlock {
  type: ContentBlockType
  content: string
  isStreaming?: boolean
}

// SSE 事件类型
type OutputLayer = 'primary' | 'process' | 'debug'

interface StreamEventV2 {
  type: 'block_start' | 'block_delta' | 'block_end' | 'tool_start' | 'tool_end' | 'status' | 'done' | 'error'
  layer?: OutputLayer
  block_id?: string
  block_type?: 'thinking' | 'text' | 'tool_use' | 'tool_result'
  block_index?: number
  content?: string
  tool_name?: string
  tool_id?: string
  tool_input?: Record<string, unknown>
  tool_result?: string
  display_text?: string
  cost?: number
  session_id?: string
  timestamp?: number
}

type StreamEvent = StreamEventV2

// 会话类型
interface ChatSession {
  id: string
  title: string
  messages: Message[]
  context: {
    type: 'database' | 'url' | null
    value: string | null
  }
  serverSessionId?: string
  createdAt: Date
  updatedAt: Date
}

// Props 类型
interface AssistantChatProps {
  initialData?: {
    sessionId: string
    messages: Array<{
      id: string
      role: 'user' | 'assistant'
      content: string
      timestamp: Date
      toolStatus?: Array<{ name: string; status: 'completed' }>
      metrics?: { cost?: number; duration?: number }
    }>
    contextType: 'database' | 'url' | null
    contextValue: string | null
  } | null
  initialMessage?: string
}

// 将后端消息转换为前端消息格式
function convertBackendMessage(msg: ChatMessageItem): Message {
  return {
    id: msg.id.toString(),
    role: msg.role as MessageRole,
    content: msg.content,
    timestamp: new Date(msg.created_at),
    toolStatus: msg.tool_calls?.map(tc => ({
      name: tc.name,
      status: 'completed' as const
    })),
    metrics: msg.cost || msg.duration_ms ? {
      cost: msg.cost || undefined,
      duration: msg.duration_ms ? msg.duration_ms / 1000 : undefined
    } : undefined
  }
}

export default function AssistantChat({ initialData, initialMessage }: AssistantChatProps) {
  const { t } = useLocale()
  const router = useRouter()

  // 会话管理
  const [sessions, setSessions] = useState<ChatSession[]>([])
  const [dbSessions, setDbSessions] = useState<ChatSessionListItem[]>([])
  const [isLoadingSessions, setIsLoadingSessions] = useState(false)
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(initialData?.sessionId || null)
  const [showHistory, setShowHistory] = useState(false)

  // Backend session ID for multi-turn conversations
  const [serverSessionId, setServerSessionId] = useState<string | null>(initialData?.sessionId || null)

  // 初始化消息
  const [messages, setMessages] = useState<Message[]>(() => {
    if (initialData?.messages) {
      return initialData.messages.map(msg => ({
        ...msg,
        toolStatus: msg.toolStatus?.map(ts => ({ ...ts, status: ts.status as 'completed' }))
      }))
    }
    return []
  })
  
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [showScrollToLatest, setShowScrollToLatest] = useState(false)
  const [currentToolLabel, setCurrentToolLabel] = useState<string>('')

  // 中断控制
  const abortControllerRef = useRef<AbortController | null>(null)

  // 上下文相关 - 旧变量保留用于兼容
  const [showContextMenu, setShowContextMenu] = useState(false)
  const [contextType, setContextType] = useState<'database' | 'url' | null>(initialData?.contextType || null)
  const [urlInput, setUrlInput] = useState(initialData?.contextType === 'url' ? initialData.contextValue || '' : '')

  // 关联分析 - 新的统一状态
  const [selectedItems, setSelectedItems] = useState<SelectedItem[]>([])

  // 产品搜索
  const [products, setProducts] = useState<Startup[]>([])
  const [productSearch, setProductSearch] = useState('')
  const [isSearching, setIsSearching] = useState(false)

  // 创作者搜索
  const [creators, setCreators] = useState<Array<{
    id: number
    username: string
    display_name?: string
    avatar_url?: string
    total_revenue?: number
    product_count?: number
  }>>([])
  const [isSearchingCreators, setIsSearchingCreators] = useState(false)

  const messagesEndRef = useRef<HTMLDivElement>(null)
  const messagesContainerRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)
  const historyMenuRef = useRef<HTMLDivElement>(null)

  const currentSession = sessions.find(s => s.id === currentSessionId)

  // 保存当前会话到 localStorage
  useEffect(() => {
    saveCurrentSession(currentSessionId)
  }, [currentSessionId])

  // 点击外部关闭菜单
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (historyMenuRef.current && !historyMenuRef.current.contains(e.target as Node)) {
        setShowHistory(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  // 加载历史会话列表
  const loadSessions = useCallback(async () => {
    setIsLoadingSessions(true)
    try {
      const result = await getChatSessions({ limit: 50 })
      setDbSessions(result.sessions)
    } catch (error) {
      console.error('Failed to load sessions:', error)
    } finally {
      setIsLoadingSessions(false)
    }
  }, [])

  useEffect(() => {
    loadSessions()
  }, [loadSessions])

  // Handle initialMessage from URL params - auto-fill input
  useEffect(() => {
    if (initialMessage && !initialData?.sessionId) {
      setInput(initialMessage)
      // Focus the input after a short delay
      setTimeout(() => {
        inputRef.current?.focus()
      }, 100)
    }
  }, [initialMessage, initialData?.sessionId])

  // 初始加载产品列表
  useEffect(() => {
    const loadInitialProducts = async () => {
      setIsSearching(true)
      try {
        const data = await getStartups({
          page: 1,
          page_size: 8,
        })
        setProducts(data.items)
      } catch (error) {
        console.error('Failed to load products:', error)
      } finally {
        setIsSearching(false)
      }
    }
    loadInitialProducts()
  }, [])

  // 初始加载创作者列表
  useEffect(() => {
    const loadInitialCreators = async () => {
      setIsSearchingCreators(true)
      try {
        const data = await getFounderLeaderboard({ page_size: 8 })
        if (data.items && data.items.length > 0) {
          setCreators(data.items.map((f) => ({
            id: f.rank,
            username: f.username,
            display_name: f.name,
            avatar_url: f.avatar_url || undefined,
            total_revenue: f.total_revenue,
            product_count: f.product_count,
          })))
        }
      } catch (error) {
        console.error('Failed to load creators:', error)
      } finally {
        setIsSearchingCreators(false)
      }
    }
    loadInitialCreators()
  }, [])

  // 搜索产品 - 由 productSearch 变化触发
  useEffect(() => {
    // 跳过初始空值
    if (productSearch === '') return

    const search = async () => {
      setIsSearching(true)
      try {
        const data = await getStartups({
          page: 1,
          page_size: 8,
          search: productSearch,
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
  }, [productSearch])

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
    sessionId: string | null,
    onText: (text: string) => void,
    onThinking: (thinking: string) => void,
    onToolStart: (tool: ToolStatus) => void,
    onToolEnd: (toolId: string, toolName: string, result: string, displayText?: string) => void,
    onError: (error: string) => void,
    onDone: (cost?: number, newSessionId?: string) => void,
    signal?: AbortSignal
  ): Promise<void> => {
    const activeBlocks: Map<string, { type: string; content: string }> = new Map()

    // 构建 context - 基于新的 selectedItems
    const buildContext = () => {
      if (selectedItems.length === 0) return undefined
      
      const productItems = selectedItems.filter(item => item.type === 'product')
      const urlItems = selectedItems.filter(item => item.type === 'url')
      const creatorItems = selectedItems.filter(item => item.type === 'creator')
      
      return {
        type: 'analysis' as const,
        products: productItems.map(item => {
          const product = item.data as Startup
          return { id: product.id, name: product.name, slug: product.slug }
        }),
        urls: urlItems.map(item => item.data as string),
        creators: creatorItems.map(item => {
          const creator = item.data as { id: number; username: string; display_name?: string }
          return { id: creator.id, username: creator.username, display_name: creator.display_name }
        }),
      }
    }

    try {
      const response = await fetch('/api/chat/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMessage,
          session_id: sessionId,
          context: buildContext()
        }),
        signal
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
                case 'block_start': {
                  const blockId = event.block_id || `block_${Date.now()}`
                  activeBlocks.set(blockId, {
                    type: event.block_type || 'text',
                    content: ''
                  })
                  if (event.block_type === 'tool_use' && event.tool_name) {
                    onToolStart({
                      name: event.tool_name,
                      status: 'running',
                      displayText: event.display_text
                    })
                  }
                  break
                }

                case 'block_delta': {
                  const blockId = event.block_id
                  const blockInfo = blockId ? activeBlocks.get(blockId) : null

                  if (event.content) {
                    const blockType = event.block_type || blockInfo?.type

                    if (blockType === 'thinking') {
                      if (blockInfo) {
                        blockInfo.content += event.content
                      }
                      onThinking(event.content)
                    } else if (blockType === 'text') {
                      if (event.layer === 'primary' || !event.layer) {
                        if (blockInfo) {
                          blockInfo.content += event.content
                        }
                        onText(event.content)
                      }
                    }
                  }
                  break
                }

                case 'block_end': {
                  const blockId = event.block_id
                  if (blockId) {
                    activeBlocks.delete(blockId)
                  }
                  break
                }

                case 'tool_start':
                  if (event.tool_name) {
                    onToolStart({
                      name: event.tool_name,
                      toolId: event.tool_id,
                      status: 'running',
                      displayText: event.display_text
                    })
                  }
                  break

                case 'tool_end':
                  if (event.tool_name || event.tool_id) {
                    onToolEnd(event.tool_id || '', event.tool_name || '', event.tool_result || '', event.display_text)
                  }
                  break

                case 'error':
                  onError(event.content || t('assistant.unknownError'))
                  break

                case 'done':
                  onDone(event.cost, event.session_id)
                  break

                case 'status':
                  break
              }
            } catch {
              console.warn('Failed to parse SSE event:', data)
            }
          }
        }
      }
    } catch (error) {
      if (error instanceof Error && error.name === 'AbortError') {
        console.log('Request was interrupted')
        return
      }
      console.error('Stream error:', error)
      onError(error instanceof Error ? error.message : t('assistant.connectionFailed'))
    }
  }

  // 创建新会话 - 更新 URL
  const createNewSession = () => {
    if (isLoading && abortControllerRef.current) {
      abortControllerRef.current.abort()
    }
    setCurrentSessionId(null)
    setServerSessionId(null)
    setMessages([])
    setContextType(null)
    setSelectedItems([])
    setUrlInput('')
    setShowHistory(false)
    // 导航到新会话页面
    router.push('/assistant')
  }

  // 中断当前请求
  const interruptRequest = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
      setIsLoading(false)
      setCurrentToolLabel('')

      setMessages(prev => prev.map(msg => {
        if (msg.isStreaming) {
          const updatedTools = (msg.toolStatus || []).map(tool => 
            tool.status === 'running' 
              ? { ...tool, status: 'completed' as const }
              : tool
          )
          return {
            ...msg,
            isStreaming: false,
            toolStatus: updatedTools,
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

  // 切换会话 - 使用路由导航
  const switchSession = async (sessionId: string) => {
    setShowHistory(false)
    // 使用路由导航，让页面重新加载会话数据
    router.push(`/assistant/${sessionId}`)
  }

  // 删除会话
  const deleteSession = async (sessionId: string, e: React.MouseEvent) => {
    e.stopPropagation()

    try {
      await deleteChatSession(sessionId)
      setSessions(prev => prev.filter(s => s.id !== sessionId))
      setDbSessions(prev => prev.filter(s => s.session_id !== sessionId))

      if (currentSessionId === sessionId) {
        setCurrentSessionId(null)
        setServerSessionId(null)
        setMessages([])
        router.push('/assistant')
      }
    } catch (error) {
      console.error('Failed to delete session:', error)
    }
  }


  // 发送消息
  const sendMessage = async (messageText?: string) => {
    const text = messageText || input.trim()
    if (!text || isLoading) return

    // 构建 context 描述
    const getContextDescription = () => {
      if (selectedItems.length === 0) return null
      const names = selectedItems.map(item => item.name).join(', ')
      return names
    }

    // 如果没有当前会话，创建一个新的（临时 ID，后端会返回真实 ID）
    let sessionId = currentSessionId
    if (!sessionId) {
      const tempId = Date.now().toString()
      const newSession: ChatSession = {
        id: tempId,
        title: text.slice(0, 20) + (text.length > 20 ? '...' : ''),
        messages: [],
        context: {
          type: selectedItems.length > 0 ? 'database' : null,
          value: getContextDescription()
        },
        createdAt: new Date(),
        updatedAt: new Date(),
      }
      setSessions(prev => [newSession, ...prev])
      sessionId = tempId
      setCurrentSessionId(sessionId)
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: text,
      timestamp: new Date(),
      context: selectedItems.length > 0 ? {
        type: 'product',
        value: getContextDescription() || undefined
      } : undefined
    }

    const newMessages = [...messages, userMessage]
    setMessages(newMessages)
    setInput('')
    setIsLoading(true)

    abortControllerRef.current = new AbortController()

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

    let accumulatedText = ''
    let accumulatedThinking = ''
    let totalCost = 0
    let newServerSessionId: string | undefined

    try {
      await streamFromBackend(
        text,
        aiMessageId,
        serverSessionId,
        (textChunk) => {
          accumulatedText += textChunk
          console.log('[DEBUG Frontend] Text chunk received:', textChunk.substring(0, 50))
          console.log('[DEBUG Frontend] Accumulated text length:', accumulatedText.length)
          console.log('[DEBUG Frontend] Accumulated text preview:', accumulatedText.substring(0, 100))
          setMessages(prev => prev.map(msg => {
            if (msg.id !== aiMessageId) return msg
            const newMsg = { ...msg, content: accumulatedText }
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
        (thinkingChunk) => {
          accumulatedThinking += thinkingChunk
          setMessages(prev => prev.map(msg => {
            if (msg.id !== aiMessageId) return msg
            const blocks = [...(msg.contentBlocks || [])]
            const thinkingBlockIndex = blocks.findIndex(b => b.type === 'thinking')
            if (thinkingBlockIndex >= 0) {
              blocks[thinkingBlockIndex] = { ...blocks[thinkingBlockIndex], content: accumulatedThinking, isStreaming: true }
            } else {
              blocks.unshift({ type: 'thinking', content: accumulatedThinking, isStreaming: true })
            }
            return { ...msg, contentBlocks: blocks }
          }))
        },
        (tool) => {
          setCurrentToolLabel(tool.displayText || tool.name)
          setMessages(prev => prev.map(msg => {
            if (msg.id !== aiMessageId) return msg
            const existingTools = msg.toolStatus || []
            return { ...msg, toolStatus: [...existingTools, tool] }
          }))
        },
        (toolId, toolName, result, displayText) => {
          setMessages(prev => prev.map(msg => {
            if (msg.id !== aiMessageId) return msg
            const existingTools = msg.toolStatus || []
            const updatedTools = existingTools.map(t => ({
              ...t,
              status: 'completed' as const
            }))
            return { ...msg, toolStatus: updatedTools }
          }))
        },
        (errorMsg) => {
          setMessages(prev => prev.map(msg =>
            msg.id === aiMessageId
              ? { ...msg, content: `${t('assistant.errorOccurred')}：${errorMsg}`, isStreaming: false }
              : msg
          ))
        },
        (cost, returnedSessionId) => {
          totalCost = cost || 0
          newServerSessionId = returnedSessionId
          setCurrentToolLabel('')
          setMessages(prev => prev.map(msg => {
            if (msg.id !== aiMessageId) return msg
            const updatedTools = (msg.toolStatus || []).map(t =>
              t.status === 'running' ? { ...t, status: 'completed' as const } : t
            )
            return { ...msg, toolStatus: updatedTools }
          }))
        },
        abortControllerRef.current.signal
      )

      const duration = (Date.now() - startTime) / 1000

      // 更新 serverSessionId 并导航到新 URL
      if (newServerSessionId) {
        setServerSessionId(newServerSessionId)
        // 如果是新会话，更新 URL 到真实的 session ID
        if (!initialData?.sessionId) {
          // 更新本地会话 ID
          setSessions(prev => prev.map(s =>
            s.id === sessionId
              ? { ...s, id: newServerSessionId!, serverSessionId: newServerSessionId }
              : s
          ))
          setCurrentSessionId(newServerSessionId)
          // 使用 replace 而不是 push，避免产生多余的历史记录
          router.replace(`/assistant/${newServerSessionId}`)
        }
      }

      setMessages(prev => {
        const finalMessages = prev.map(msg => {
          if (msg.id !== aiMessageId) return msg
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
        setSessions(prevSessions => prevSessions.map(s =>
          s.id === sessionId || s.id === newServerSessionId
            ? {
                ...s,
                id: newServerSessionId || s.id,
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

  // 创作者搜索处理
  const handleCreatorSearch = useCallback(async (query: string) => {
    setIsSearchingCreators(true)
    try {
      const data = await getFounderLeaderboard({ 
        search: query.trim() || undefined, 
        page_size: 8 
      })
      if (data.items && data.items.length > 0) {
        setCreators(data.items.map((f) => ({
          id: f.rank,
          username: f.username,
          display_name: f.name,
          avatar_url: f.avatar_url || undefined,
          total_revenue: f.total_revenue,
          product_count: f.product_count,
        })))
      } else {
        setCreators([])
      }
    } catch (error) {
      console.error('Failed to search creators:', error)
      setCreators([])
    } finally {
      setIsSearchingCreators(false)
    }
  }, [])

  const handleSuggestedPrompt = (prompt: string) => {
    setInput(prompt)
    inputRef.current?.focus()
  }

  const handleRetry = (messageId: string) => {
    const messageIndex = messages.findIndex(m => m.id === messageId)
    if (messageIndex <= 0) return

    const userMessage = messages[messageIndex - 1]
    if (userMessage.role !== 'user') return

    setMessages(prev => prev.filter(m => m.id !== messageId))
    sendMessage(userMessage.content)
  }

  const hasMessages = messages.length > 0
  const hasContext = selectedItems.length > 0

  const allSessions = [
    ...sessions,
    ...dbSessions
      .filter(dbS => !sessions.some(s => s.id === dbS.session_id))
      .map(dbS => ({
        id: dbS.session_id,
        title: dbS.title || '新对话',
        messages: [],
        context: { type: null as 'database' | 'url' | null, value: null },
        createdAt: new Date(dbS.created_at),
        updatedAt: new Date(dbS.updated_at)
      }))
  ].sort((a, b) => b.updatedAt.getTime() - a.updatedAt.getTime())


  return (
    <div className="h-[calc(100vh-3.5rem)] flex relative bg-diagonal-grid bg-assistant-glow">
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {!hasMessages ? (
          <div className="flex-1 flex flex-col">
            <div className="flex items-center justify-between px-4 py-3">
              <div className="relative" ref={historyMenuRef}>
                <button
                  onClick={() => setShowHistory(!showHistory)}
                  className="flex items-center gap-2 px-3 py-2 rounded-xl text-sm text-content-secondary hover:bg-surface/60 hover:text-content-primary transition-all duration-200"
                >
                  <History className="h-3.5 w-3.5" />
                  <span className="font-medium">{t('assistant.history')}</span>
                  {allSessions.length > 0 && (
                    <span className="px-1.5 py-0.5 bg-brand-500/10 text-brand-600 dark:text-brand-400 text-[10px] rounded-full font-semibold">
                      {allSessions.length}
                    </span>
                  )}
                  <ChevronDown className={cn('h-2.5 w-2.5 opacity-60 transition-transform duration-200', showHistory && 'rotate-180')} />
                </button>

                {showHistory && (
                  <div className="absolute left-0 top-full mt-2 w-80 bg-background/95 backdrop-blur-xl border border-surface-border/80 rounded-xl shadow-xl z-20 overflow-hidden animate-in fade-in slide-in-from-top-2 duration-200">
                    <div className="p-3 border-b border-surface-border/50 flex items-center justify-between">
                      <span className="text-sm font-semibold text-content-primary">{t('assistant.history')}</span>
                      <button onClick={createNewSession} className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-gradient-to-r from-brand-500 to-brand-600 text-white text-xs font-semibold hover:from-brand-600 hover:to-brand-700 transition-all shadow-sm">
                        <Plus className="h-3 w-3" />
                        {t('assistant.newChat')}
                      </button>
                    </div>
                    <div className="max-h-72 overflow-y-auto p-2">
                      {isLoadingSessions ? (
                        <div className="flex items-center justify-center py-6"><Loader2 className="h-5 w-5 animate-spin text-brand-500" /></div>
                      ) : allSessions.length > 0 ? (
                        <div className="space-y-1">
                          {allSessions.map(session => (
                            <button key={session.id} onClick={() => switchSession(session.id)} className={cn('w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-left text-sm transition-all group', currentSessionId === session.id ? 'bg-brand-500/10 text-brand-600 dark:text-brand-400' : 'hover:bg-surface/60 text-content-secondary hover:text-content-primary')}>
                              <MessageSquare className="h-3.5 w-3.5 flex-shrink-0 opacity-60" />
                              <span className="flex-1 truncate font-medium">{session.title}</span>
                              <button onClick={(e) => deleteSession(session.id, e)} className="opacity-0 group-hover:opacity-100 p-1.5 hover:text-rose-500 transition-all rounded-lg hover:bg-surface-hover"><Trash2 className="h-3 w-3" /></button>
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

            <div className="flex-1 flex flex-col items-center justify-center px-4 -mt-24">
              <div className="w-full max-w-3xl mx-auto flex flex-col items-center">
                <div className="flex items-center gap-4 mb-8">
                  <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-brand-500 via-brand-600 to-accent-secondary flex items-center justify-center shadow-lg shadow-brand-500/20">
                    <Sparkles className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <h1 className="text-2xl font-display font-bold tracking-tight bg-gradient-to-r from-content-primary via-content-primary to-brand-600 dark:to-brand-400 bg-clip-text text-transparent">{t('assistant.title')}</h1>
                    <p className="text-sm text-content-tertiary mt-0.5 tracking-wide">{t('assistant.subtitle')}</p>
                  </div>
                </div>

                <div className="w-full mb-5">
                  <div className="relative bg-surface/70 backdrop-blur-sm rounded-2xl border border-surface-border/80 focus-within:border-brand-500/60 focus-within:ring-2 focus-within:ring-brand-500/20 focus-within:shadow-lg focus-within:shadow-brand-500/5 transition-all duration-300 shadow-sm">
                    <div className="flex items-end gap-3 px-5 py-4">
                      <textarea ref={inputRef} value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={handleKeyDown} placeholder={t('assistant.inputPlaceholder')} className="flex-1 bg-transparent resize-none text-content-secondary placeholder:text-content-muted/60 focus:outline-none min-h-[72px] max-h-48 text-[0.9375rem] leading-relaxed font-normal" rows={3} disabled={isLoading} />
                      <button onClick={() => isLoading ? interruptRequest() : sendMessage()} disabled={!input.trim() && !isLoading} className={cn('flex-shrink-0 w-11 h-11 rounded-xl flex items-center justify-center transition-all duration-200 mb-1', isLoading ? 'bg-rose-500/10 text-rose-500 hover:bg-rose-500/20 ring-1 ring-rose-500/20' : input.trim() ? 'bg-gradient-to-r from-brand-500 to-brand-600 text-white hover:from-brand-600 hover:to-brand-700 shadow-md shadow-brand-500/25' : 'bg-surface-hover text-content-muted cursor-not-allowed')} title={isLoading ? t('assistant.stop') : t('assistant.send')}>
                        {isLoading ? <Square className="h-4 w-4 fill-current" /> : <Send className="h-4 w-4" />}
                      </button>
                    </div>

                    <div className="flex items-center gap-2.5 px-5 pb-4">
                      <ContextSelector
                        selectedItems={selectedItems}
                        onItemsChange={setSelectedItems}
                        products={products}
                        onProductSearch={setProductSearch}
                        isSearchingProducts={isSearching}
                        creators={creators}
                        onCreatorSearch={handleCreatorSearch}
                        isSearchingCreators={isSearchingCreators}
                        maxItems={5}
                      />
                    </div>
                  </div>
                  <p className="text-xs text-content-muted/70 mt-2.5 text-center font-medium tracking-wide">{t('assistant.sendTip')}</p>
                </div>

                <div className="w-full">
                  <SuggestedPrompts onSelect={handleSuggestedPrompt} />
                </div>
              </div>
            </div>
          </div>
        ) : (

          <div className="flex-1 flex flex-col min-h-0">
            <div className="flex items-center justify-between px-4 py-3">
              <div className="flex items-center gap-3">
                <div className="relative" ref={historyMenuRef}>
                  <button onClick={() => setShowHistory(!showHistory)} className="flex items-center gap-2 px-3 py-2 rounded-xl text-sm text-content-secondary hover:bg-surface/60 hover:text-content-primary transition-all duration-200">
                    <History className="h-3.5 w-3.5" />
                    <span className="hidden sm:inline font-medium">{t('assistant.historyShort')}</span>
                    <ChevronDown className={cn('h-2.5 w-2.5 opacity-60 transition-transform duration-200', showHistory && 'rotate-180')} />
                  </button>

                  {showHistory && (
                    <div className="absolute left-0 top-full mt-2 w-80 bg-background/95 backdrop-blur-xl border border-surface-border/80 rounded-xl shadow-xl z-20 overflow-hidden animate-in fade-in slide-in-from-top-2 duration-200">
                      <div className="p-3 border-b border-surface-border/50 flex items-center justify-between">
                        <span className="text-sm font-semibold text-content-primary">{t('assistant.history')}</span>
                        <button onClick={createNewSession} className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-gradient-to-r from-brand-500 to-brand-600 text-white text-xs font-semibold hover:from-brand-600 hover:to-brand-700 transition-all shadow-sm">
                          <Plus className="h-3 w-3" />
                          {t('assistant.newChat')}
                        </button>
                      </div>
                      <div className="max-h-72 overflow-y-auto p-2">
                        {isLoadingSessions ? (
                          <div className="flex items-center justify-center py-6"><Loader2 className="h-5 w-5 animate-spin text-brand-500" /></div>
                        ) : allSessions.length > 0 ? (
                          <div className="space-y-1">
                            {allSessions.map(session => (
                              <button key={session.id} onClick={() => switchSession(session.id)} className={cn('w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-left text-sm transition-all group', currentSessionId === session.id ? 'bg-brand-500/10 text-brand-600 dark:text-brand-400' : 'hover:bg-surface/60 text-content-secondary hover:text-content-primary')}>
                                <MessageSquare className="h-3.5 w-3.5 flex-shrink-0 opacity-60" />
                                <span className="flex-1 truncate font-medium">{session.title}</span>
                                <button onClick={(e) => deleteSession(session.id, e)} className="opacity-0 group-hover:opacity-100 p-1.5 hover:text-rose-500 transition-all rounded-lg hover:bg-surface-hover"><Trash2 className="h-3 w-3" /></button>
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
                <div className="flex items-center gap-2 flex-wrap">
                  {selectedItems.map((item) => (
                    <span
                      key={item.id}
                      className={cn(
                        'inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold ring-1',
                        item.type === 'product' && 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 ring-emerald-500/20',
                        item.type === 'url' && 'bg-amber-500/10 text-amber-600 dark:text-amber-400 ring-amber-500/20',
                        item.type === 'creator' && 'bg-blue-500/10 text-blue-600 dark:text-blue-400 ring-blue-500/20'
                      )}
                    >
                      {item.type === 'product' && <Database className="h-3 w-3" />}
                      {item.type === 'url' && <Globe className="h-3 w-3" />}
                      {item.type === 'creator' && <User className="h-3 w-3" />}
                      <span className="max-w-[100px] truncate">{item.name}</span>
                    </span>
                  ))}
                </div>
              </div>
              <button onClick={createNewSession} className="flex items-center gap-1.5 px-3 py-2 rounded-xl text-sm text-content-secondary hover:bg-surface/60 hover:text-content-primary transition-all duration-200">
                <Plus className="h-3 w-3" />
                <span className="font-medium">{t('assistant.newChat')}</span>
              </button>
            </div>

            <div className="flex-1 overflow-y-auto px-4 py-4" ref={messagesContainerRef}>
              <div className="max-w-3xl mx-auto space-y-5">
                {messages.map((message) => (
                  <ChatMessage key={message.id} message={message} onRetry={message.role === 'assistant' ? () => handleRetry(message.id) : undefined} />
                ))}
                <div ref={messagesEndRef} />
              </div>
            </div>

            <div className="px-4 pb-3 pt-2">
              <div className="max-w-3xl mx-auto">
                <div className="relative bg-surface/70 backdrop-blur-sm rounded-2xl border border-surface-border/80 focus-within:border-brand-500/60 focus-within:ring-2 focus-within:ring-brand-500/20 focus-within:shadow-lg focus-within:shadow-brand-500/5 transition-all duration-300">
                  <div className="flex items-center gap-3 px-4 py-2.5">
                    {isLoading && currentToolLabel && <Loader2 className="flex-shrink-0 h-4 w-4 text-brand-500 animate-spin" />}
                    <textarea ref={inputRef} value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={handleKeyDown} placeholder={isLoading ? (currentToolLabel ? `${t('assistant.tools.executing').replace('...', '')} ${currentToolLabel}...` : t('assistant.continueChat')) : t('assistant.continueChat')} className="flex-1 bg-transparent resize-none text-content-secondary placeholder:text-content-muted/60 focus:outline-none min-h-[36px] max-h-32 text-sm leading-[36px] font-normal py-0" rows={1} disabled={isLoading} onInput={(e) => { const target = e.target as HTMLTextAreaElement; target.style.height = 'auto'; target.style.height = Math.min(target.scrollHeight, 128) + 'px'; if (target.scrollHeight > 36) { target.style.lineHeight = '1.5'; target.style.paddingTop = '6px'; target.style.paddingBottom = '6px'; } else { target.style.lineHeight = '36px'; target.style.paddingTop = '0'; target.style.paddingBottom = '0'; } }} />
                    <button onClick={() => isLoading ? interruptRequest() : sendMessage()} disabled={!input.trim() && !isLoading} className={cn('flex-shrink-0 w-9 h-9 rounded-xl flex items-center justify-center transition-all duration-200', isLoading ? 'bg-rose-500/10 text-rose-500 hover:bg-rose-500/20 ring-1 ring-rose-500/20' : input.trim() ? 'bg-gradient-to-r from-brand-500 to-brand-600 text-white hover:from-brand-600 hover:to-brand-700 shadow-md shadow-brand-500/25' : 'bg-surface-hover text-content-muted cursor-not-allowed')} title={isLoading ? t('assistant.stop') : t('assistant.send')}>
                      {isLoading ? <Square className="h-4 w-4 fill-current" /> : <Send className="h-4 w-4" />}
                    </button>
                  </div>
                </div>
              </div>
            </div>

            {showScrollToLatest && (
              <button 
                type="button" 
                onClick={scrollToBottom} 
                className="absolute left-1/2 -translate-x-1/2 bottom-24 z-30 w-10 h-10 rounded-full bg-surface/90 backdrop-blur-sm border border-surface-border/60 text-content-secondary hover:text-content-primary hover:bg-surface shadow-lg transition-all flex items-center justify-center"
                title={t('assistant.scrollToLatest')}
              >
                <ChevronDown className="h-5 w-5" />
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
