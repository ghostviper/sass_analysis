'use client'

import { useParams, useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import AssistantChat from '../AssistantChat'
import { getChatSession } from '@/lib/api'
import { Loader2 } from 'lucide-react'

export default function SessionPage() {
  const params = useParams()
  const router = useRouter()
  const sessionId = params.sessionId as string
  const [initialData, setInitialData] = useState<{
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
  } | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function loadSession() {
      // 如果是 new，直接显示空白会话
      if (sessionId === 'new') {
        setInitialData(null)
        setLoading(false)
        return
      }

      try {
        const result = await getChatSession(sessionId)
        if (result) {
          setInitialData({
            sessionId: result.session.session_id,
            messages: result.messages.map(msg => ({
              id: msg.id.toString(),
              role: msg.role as 'user' | 'assistant',
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
            })),
            contextType: result.session.context_type as 'database' | 'url' | null,
            contextValue: result.session.context_value
          })
        } else {
          // 会话不存在，跳转到新会话
          router.replace('/assistant')
        }
      } catch (err) {
        console.error('Failed to load session:', err)
        setError('加载会话失败')
      } finally {
        setLoading(false)
      }
    }

    loadSession()
  }, [sessionId, router])

  if (loading) {
    return (
      <div className="h-[calc(100vh-3.5rem)] flex items-center justify-center bg-diagonal-grid bg-assistant-glow">
        <div className="flex flex-col items-center gap-3">
          <Loader2 className="h-8 w-8 animate-spin text-brand-500" />
          <span className="text-sm text-content-muted">加载会话中...</span>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="h-[calc(100vh-3.5rem)] flex items-center justify-center bg-diagonal-grid bg-assistant-glow">
        <div className="text-center">
          <p className="text-content-secondary mb-4">{error}</p>
          <button
            onClick={() => router.push('/assistant')}
            className="px-4 py-2 bg-brand-500 text-white rounded-lg hover:bg-brand-600 transition-colors"
          >
            返回新对话
          </button>
        </div>
      </div>
    )
  }

  return <AssistantChat initialData={initialData} />
}
