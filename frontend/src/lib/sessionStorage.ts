/**
 * Session Storage Utilities
 * 
 * 使用 localStorage 存储会话元信息，用于：
 * 1. 快速恢复最近的会话 ID
 * 2. 缓存会话列表（减少 API 调用）
 * 3. 保存未完成的输入内容（防止意外丢失）
 * 
 * 数据库是唯一真实数据源，localStorage 仅用于 UX 优化
 */

const STORAGE_KEYS = {
  CURRENT_SESSION: 'chat_current_session',
  RECENT_SESSIONS: 'chat_recent_sessions',
  DRAFT_INPUT: 'chat_draft_input',
  SESSION_CACHE_TIME: 'chat_session_cache_time',
} as const

const CACHE_TTL = 5 * 60 * 1000 // 5 minutes

interface SessionMeta {
  sessionId: string
  title: string
  updatedAt: string
}

interface DraftInput {
  sessionId: string | null
  content: string
  timestamp: number
}

/**
 * 保存当前会话 ID
 */
export function saveCurrentSession(sessionId: string | null): void {
  try {
    if (sessionId) {
      localStorage.setItem(STORAGE_KEYS.CURRENT_SESSION, sessionId)
    } else {
      localStorage.removeItem(STORAGE_KEYS.CURRENT_SESSION)
    }
  } catch (e) {
    console.warn('Failed to save current session:', e)
  }
}

/**
 * 获取上次的会话 ID
 */
export function getLastSession(): string | null {
  try {
    return localStorage.getItem(STORAGE_KEYS.CURRENT_SESSION)
  } catch (e) {
    return null
  }
}

/**
 * 保存最近会话列表（用于快速显示）
 */
export function saveRecentSessions(sessions: SessionMeta[]): void {
  try {
    // 只保存最近 20 个
    const recent = sessions.slice(0, 20)
    localStorage.setItem(STORAGE_KEYS.RECENT_SESSIONS, JSON.stringify(recent))
    localStorage.setItem(STORAGE_KEYS.SESSION_CACHE_TIME, Date.now().toString())
  } catch (e) {
    console.warn('Failed to save recent sessions:', e)
  }
}

/**
 * 获取缓存的会话列表
 * 如果缓存过期返回 null
 */
export function getCachedSessions(): SessionMeta[] | null {
  try {
    const cacheTime = localStorage.getItem(STORAGE_KEYS.SESSION_CACHE_TIME)
    if (!cacheTime || Date.now() - parseInt(cacheTime) > CACHE_TTL) {
      return null
    }
    
    const data = localStorage.getItem(STORAGE_KEYS.RECENT_SESSIONS)
    return data ? JSON.parse(data) : null
  } catch (e) {
    return null
  }
}

/**
 * 保存草稿输入（防止意外丢失）
 */
export function saveDraftInput(sessionId: string | null, content: string): void {
  try {
    if (!content.trim()) {
      localStorage.removeItem(STORAGE_KEYS.DRAFT_INPUT)
      return
    }
    
    const draft: DraftInput = {
      sessionId,
      content,
      timestamp: Date.now(),
    }
    localStorage.setItem(STORAGE_KEYS.DRAFT_INPUT, JSON.stringify(draft))
  } catch (e) {
    console.warn('Failed to save draft:', e)
  }
}

/**
 * 获取草稿输入
 * 超过 1 小时的草稿会被忽略
 */
export function getDraftInput(sessionId: string | null): string | null {
  try {
    const data = localStorage.getItem(STORAGE_KEYS.DRAFT_INPUT)
    if (!data) return null
    
    const draft: DraftInput = JSON.parse(data)
    
    // 检查是否过期（1小时）
    if (Date.now() - draft.timestamp > 60 * 60 * 1000) {
      localStorage.removeItem(STORAGE_KEYS.DRAFT_INPUT)
      return null
    }
    
    // 检查是否是同一个会话
    if (draft.sessionId !== sessionId) {
      return null
    }
    
    return draft.content
  } catch (e) {
    return null
  }
}

/**
 * 清除草稿
 */
export function clearDraftInput(): void {
  try {
    localStorage.removeItem(STORAGE_KEYS.DRAFT_INPUT)
  } catch (e) {
    // ignore
  }
}

/**
 * 清除所有会话相关的 localStorage 数据
 */
export function clearAllSessionData(): void {
  try {
    Object.values(STORAGE_KEYS).forEach(key => {
      localStorage.removeItem(key)
    })
  } catch (e) {
    console.warn('Failed to clear session data:', e)
  }
}
