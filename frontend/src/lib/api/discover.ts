/**
 * Discover API Client - 发现页 API 调用
 */

import type {
  TopicsResponse,
  TopicDetailResponse,
  CurationsResponse,
  StoriesResponse,
  CreatorsResponse,
  RecommendationsResponse,
  UserPreferenceResponse,
  UserPreference,
} from '@/types/discover'

/**
 * 获取专题列表
 */
export async function getTopics(): Promise<TopicsResponse> {
  const res = await fetch(`/api/discover/topics`, {
    cache: 'no-store',
  })
  
  if (!res.ok) {
    throw new Error('Failed to fetch topics')
  }
  
  return res.json()
}

/**
 * 获取专题详情
 */
export async function getTopicDetail(
  topicId: string,
  options?: {
    page?: number
    limit?: number
    sort?: 'revenue' | 'name'
  }
): Promise<TopicDetailResponse> {
  const params = new URLSearchParams()
  if (options?.page) params.set('page', String(options.page))
  if (options?.limit) params.set('limit', String(options.limit))
  if (options?.sort) params.set('sort', options.sort)
  
  const url = `/api/discover/topics/${topicId}${params.toString() ? '?' + params.toString() : ''}`
  
  const res = await fetch(url, {
    cache: 'no-store',
  })
  
  if (!res.ok) {
    throw new Error('Failed to fetch topic detail')
  }
  
  return res.json()
}

/**
 * 获取策展列表
 */
export async function getCurations(options?: {
  limit?: number
  days?: number
}): Promise<CurationsResponse> {
  const params = new URLSearchParams()
  if (options?.limit) params.set('limit', String(options.limit))
  if (options?.days) params.set('days', String(options.days))

  const url = `/api/discover/curations${params.toString() ? '?' + params.toString() : ''}`

  const res = await fetch(url, {
    cache: 'no-store',
  })

  if (!res.ok) {
    throw new Error('Failed to fetch curations')
  }

  return res.json()
}

/**
 * 获取爆款故事
 */
export async function getStories(options?: {
  limit?: number
  featuredOnly?: boolean
}): Promise<StoriesResponse> {
  const params = new URLSearchParams()
  if (options?.limit) params.set('limit', String(options.limit))
  if (options?.featuredOnly !== undefined) {
    params.set('featured_only', String(options.featuredOnly))
  }

  const url = `/api/discover/stories${params.toString() ? '?' + params.toString() : ''}`

  const res = await fetch(url, {
    cache: 'no-store',
  })

  if (!res.ok) {
    throw new Error('Failed to fetch stories')
  }

  return res.json()
}

/**
 * 获取创作者列表
 */
export async function getCreators(options?: {
  limit?: number
  useFeatured?: boolean
}): Promise<CreatorsResponse> {
  const params = new URLSearchParams()
  if (options?.limit) params.set('limit', String(options.limit))
  if (options?.useFeatured !== undefined) {
    params.set('use_featured', String(options.useFeatured))
  }

  const url = `/api/discover/creators${params.toString() ? '?' + params.toString() : ''}`

  const res = await fetch(url, {
    cache: 'no-store',
  })

  if (!res.ok) {
    throw new Error('Failed to fetch creators')
  }

  return res.json()
}

/**
 * 获取推荐方向
 */
export async function getRecommendations(options?: {
  limit?: number
  userId?: string
}): Promise<RecommendationsResponse> {
  const params = new URLSearchParams()
  if (options?.limit) params.set('limit', String(options.limit))
  if (options?.userId) params.set('user_id', options.userId)

  const url = `/api/discover/recommendations${params.toString() ? '?' + params.toString() : ''}`

  const res = await fetch(url, {
    cache: 'no-store',
  })

  if (!res.ok) {
    throw new Error('Failed to fetch recommendations')
  }

  return res.json()
}

/**
 * 获取用户偏好
 */
export async function getUserPreference(userId: string): Promise<UserPreferenceResponse> {
  const params = new URLSearchParams()
  params.set('user_id', userId)

  const res = await fetch(`/api/discover/user-preference?${params.toString()}`, {
    cache: 'no-store',
  })

  if (!res.ok) {
    throw new Error('Failed to fetch user preference')
  }

  return res.json()
}

/**
 * 保存用户偏好
 */
export async function saveUserPreference(
  userId: string,
  preference: Partial<UserPreference>,
): Promise<UserPreferenceResponse> {
  const params = new URLSearchParams()
  params.set('user_id', userId)

  for (const role of preference.preferred_roles || []) {
    params.append('preferred_roles', role)
  }
  for (const category of preference.interested_categories || []) {
    params.append('interested_categories', category)
  }
  if (preference.skill_level) {
    params.set('skill_level', preference.skill_level)
  }
  if (preference.goal) {
    params.set('goal', preference.goal)
  }
  if (preference.time_commitment) {
    params.set('time_commitment', preference.time_commitment)
  }
  for (const tech of preference.tech_stack || []) {
    params.append('tech_stack', tech)
  }

  const res = await fetch(`/api/discover/user-preference?${params.toString()}`, {
    method: 'POST',
  })

  if (!res.ok) {
    throw new Error('Failed to save user preference')
  }

  return res.json()
}

/**
 * 格式化收入显示
 */
export function formatRevenue(revenue: number | null): string {
  if (revenue === null || revenue === undefined) return '-'
  if (revenue >= 1000) {
    return `$${(revenue / 1000).toFixed(1)}k`
  }
  return `$${revenue.toFixed(0)}`
}
