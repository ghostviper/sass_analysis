import type {
  Startup,
  CategoryAnalysis,
  OpportunityProduct,
  ComprehensiveRecommendation,
  LandingPageAnalysis,
  ComprehensiveAnalysis,
  ProductSelectionAnalysis,
} from '@/types'

const API_BASE = '/api'

// 通用请求函数
async function fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  })

  if (!response.ok) {
    throw new Error(`API Error: ${response.status} ${response.statusText}`)
  }

  return response.json()
}

// ============ Startups API ============

export interface Country {
  code: string
  name: string
  count: number
}

export type SortField = 'revenue_30d' | 'name' | 'scraped_at'
export type SortOrder = 'asc' | 'desc'

export interface StartupFilters {
  page?: number
  page_size?: number
  category?: string
  country_code?: string
  search?: string
  sort_by?: SortField
  sort_order?: SortOrder
  // 多维度筛选
  revenue_tier?: string[]
  tech_complexity_level?: string[]
  ai_dependency_level?: string[]
  target_customer?: string[]
  pricing_model?: string[]
  feature_complexity?: string[]
  growth_driver?: string[]
  product_stage?: string[]
  startup_cost_level?: string[]
  market_scope?: string[]
}

export async function getStartups(params?: StartupFilters): Promise<{ items: Startup[]; total: number }> {
  const searchParams = new URLSearchParams()
  if (params?.page) searchParams.set('page', params.page.toString())
  if (params?.page_size) searchParams.set('limit', params.page_size.toString())
  if (params?.category) searchParams.set('category', params.category)
  if (params?.country_code) searchParams.set('country_code', params.country_code)
  if (params?.search) searchParams.set('search', params.search)
  if (params?.sort_by) searchParams.set('sort_by', params.sort_by)
  if (params?.sort_order) searchParams.set('sort_order', params.sort_order)

  // 多维度筛选参数
  const tagFilters = [
    'revenue_tier', 'tech_complexity_level', 'ai_dependency_level',
    'target_customer', 'pricing_model', 'feature_complexity',
    'growth_driver', 'product_stage', 'startup_cost_level', 'market_scope'
  ] as const

  for (const key of tagFilters) {
    const values = params?.[key]
    if (values && values.length > 0) {
      searchParams.set(key, values.join(','))
    }
  }

  const query = searchParams.toString()
  const response = await fetchApi<{ data: Startup[]; pagination: { total: number } }>(
    `/startups${query ? `?${query}` : ''}`
  )
  return { items: response.data, total: response.pagination.total }
}

export async function getStartupBySlug(slug: string): Promise<Startup> {
  return fetchApi<Startup>(`/startups/${slug}`)
}

export async function getCountries(): Promise<Country[]> {
  try {
    const response = await fetchApi<{ countries: Country[] }>('/countries')
    return response.countries || []
  } catch (error) {
    console.error('Failed to fetch countries:', error)
    return []
  }
}

// ============ Category Analysis API ============

export async function getCategoryAnalysis(): Promise<CategoryAnalysis[]> {
  const response = await fetchApi<{ data: any[]; total: number }>('/analysis/category/')
  // 后端返回的是 CategoryMetrics 的 to_dict()，需要添加 id
  return response.data.map((item, index) => ({
    id: index + 1,
    analysis_date: new Date().toISOString().split('T')[0],
    ...item,
  }))
}

export async function getCategoryByName(name: string): Promise<CategoryAnalysis> {
  const response = await fetchApi<{ analysis: any }>(`/analysis/category/${encodeURIComponent(name)}`)
  return {
    id: 1,
    analysis_date: new Date().toISOString().split('T')[0],
    ...response.analysis,
  }
}

// ============ Product Selection API ============

export async function getOpportunityProducts(params?: {
  limit?: number
  min_revenue?: number
  max_complexity?: string
}): Promise<OpportunityProduct[]> {
  const searchParams = new URLSearchParams()
  if (params?.limit) searchParams.set('limit', params.limit.toString())
  if (params?.min_revenue) searchParams.set('min_revenue', params.min_revenue.toString())
  if (params?.max_complexity) searchParams.set('max_complexity', params.max_complexity)

  const query = searchParams.toString()
  const response = await fetchApi<{ data: any[] }>(
    `/analysis/product/opportunities${query ? `?${query}` : ''}`
  )

  // 转换为 OpportunityProduct 格式
  return response.data.map((item) => ({
    startup: item.startup || item,
    analysis: item.analysis || {
      id: item.startup?.id || item.id,
      startup_id: item.startup?.id || item.id,
      is_product_driven: item.is_product_driven || false,
      ip_dependency_score: item.ip_dependency_score || 0,
      is_small_and_beautiful: item.is_small_and_beautiful || false,
      description_word_count: item.description_word_count || 0,
      tech_complexity_level: item.tech_complexity_level || 'medium',
      uses_llm_api: item.uses_llm_api || false,
      requires_compliance: item.requires_compliance || false,
      combo1_match: item.combo1_match || false,
      combo2_match: item.combo2_match || false,
      combo3_match: item.combo3_match || false,
      individual_dev_suitability: item.individual_dev_suitability || 5,
      has_follower_data: item.has_follower_data ?? true,
      data_quality_notes: item.data_quality_notes || null,
      analyzed_at: item.analyzed_at || new Date().toISOString(),
    },
  }))
}

export async function getProductSelection(slug: string): Promise<ProductSelectionAnalysis> {
  const response = await fetchApi<{ startup: Startup; analysis: ProductSelectionAnalysis }>(
    `/analysis/product/${slug}`
  )
  return response.analysis
}

// ============ Landing Page Analysis API ============

export async function getLandingAnalysis(slug: string): Promise<LandingPageAnalysis> {
  const response = await fetchApi<{ startup: any; analysis: LandingPageAnalysis }>(`/analysis/landing/${slug}`)
  return response.analysis
}

// ============ Comprehensive Analysis API ============

export async function getComprehensiveAnalysis(slug: string): Promise<ComprehensiveAnalysis> {
  const response = await fetchApi<{ startup: Startup; analysis: any }>(`/analysis/product/comprehensive/${slug}`)
  return response.analysis
}

export async function getTopRecommendations(limit?: number): Promise<ComprehensiveRecommendation[]> {
  const query = limit ? `?limit=${limit}` : ''
  const response = await fetchApi<{ data: any[] }>(`/analysis/product/comprehensive/top${query}`)
  return response.data
}

// ============ Dashboard Stats API ============

export async function getDashboardStats(): Promise<{
  total_products: number
  products_with_revenue: number
  total_categories: number
  blue_ocean_categories: number
  opportunity_products: number
  avg_revenue: number
}> {
  // 聚合多个接口的数据
  try {
    const [startups, categories, opportunities] = await Promise.all([
      getStartups({ page_size: 1 }),
      getCategoryAnalysis(),
      getOpportunityProducts({ limit: 100 }),
    ])

    const productsWithRevenue = categories.reduce((sum, c) => sum + c.total_projects, 0)
    const blueOceanCount = categories.filter(c => c.market_type === 'blue_ocean').length
    const totalRevenue = categories.reduce((sum, c) => sum + c.total_revenue, 0)

    return {
      total_products: startups.total,
      products_with_revenue: productsWithRevenue,
      total_categories: categories.length,
      blue_ocean_categories: blueOceanCount,
      opportunity_products: opportunities.length,
      avg_revenue: productsWithRevenue > 0 ? totalRevenue / productsWithRevenue : 0,
    }
  } catch (error) {
    console.error('Failed to fetch dashboard stats:', error)
    return {
      total_products: 0,
      products_with_revenue: 0,
      total_categories: 0,
      blue_ocean_categories: 0,
      opportunity_products: 0,
      avg_revenue: 0,
    }
  }
}

// ============ Leaderboard API ============

export interface FounderLeaderboardItem {
  rank: number
  username: string
  name: string
  avatar_url: string | null
  product_count: number
  total_revenue: number
  avg_revenue: number
  max_growth: number
  followers: number
  social_platform: string
  social_url: string | null
}

export type LeaderboardSortField = 'total_revenue' | 'product_count' | 'avg_revenue' | 'max_growth' | 'followers'

export async function getFounderLeaderboard(params?: {
  sort_by?: LeaderboardSortField
  sort_order?: 'asc' | 'desc'
  limit?: number
  page?: number
  page_size?: number
  min_products?: number
  search?: string
}): Promise<{
  items: FounderLeaderboardItem[]
  total: number
  pages: number
}> {
  const searchParams = new URLSearchParams()
  if (params?.sort_by) searchParams.set('sort_by', params.sort_by)
  if (params?.sort_order) searchParams.set('sort_order', params.sort_order)
  if (params?.limit) searchParams.set('limit', params.limit.toString())
  if (params?.page_size) searchParams.set('limit', params.page_size.toString())
  if (params?.page) searchParams.set('page', params.page.toString())
  if (params?.min_products) searchParams.set('min_products', params.min_products.toString())
  if (params?.search) searchParams.set('search', params.search)

  const query = searchParams.toString()
  const response = await fetchApi<{
    data: FounderLeaderboardItem[]
    pagination: { total: number; pages: number }
  }>(`/leaderboard/founders${query ? `?${query}` : ''}`)

  return {
    items: response.data,
    total: response.pagination.total,
    pages: response.pagination.pages,
  }
}

export interface FounderDetail extends FounderLeaderboardItem {
  products: Startup[]
}

export async function getFounderDetail(username: string): Promise<FounderDetail | null> {
  try {
    const response = await fetchApi<{ data: FounderDetail | null }>(`/leaderboard/founders/${username}`)
    return response.data
  } catch {
    return null
  }
}

export interface LeaderboardStats {
  total_founders: number
  multi_product_founders: number
  total_revenue: number
  avg_founder_revenue: number
}

export async function getLeaderboardStats(): Promise<LeaderboardStats> {
  return fetchApi<LeaderboardStats>('/leaderboard/stats')
}

// ============ Tag Distribution API ============

export interface TagDistributionItem {
  value: string
  count: number
  percentage: number
}

export interface TagDistribution {
  [key: string]: TagDistributionItem[]
}

export async function getTagDistribution(): Promise<TagDistribution> {
  try {
    const response = await fetchApi<{ distribution: TagDistribution }>('/analytics/tag-distribution')
    return response.distribution || {}
  } catch (error) {
    console.error('Failed to fetch tag distribution:', error)
    return {}
  }
}

// ============ Filter Dimensions (静态定义) ============

import type { FilterDimensions } from '@/types'

export const FILTER_DIMENSIONS: FilterDimensions = {
  revenue_tier: {
    key: 'revenue_tier',
    label: '收入层级',
    label_en: 'Revenue Tier',
    options: [
      { value: 'micro', label: '微型 (<$1K)', label_en: 'Micro (<$1K)' },
      { value: 'small', label: '小型 ($1K-$10K)', label_en: 'Small ($1K-$10K)' },
      { value: 'medium', label: '中型 ($10K-$50K)', label_en: 'Medium ($10K-$50K)' },
      { value: 'large', label: '大型 ($50K-$100K)', label_en: 'Large ($50K-$100K)' },
      { value: 'enterprise', label: '企业级 (>$100K)', label_en: 'Enterprise (>$100K)' },
    ],
  },
  tech_complexity_level: {
    key: 'tech_complexity_level',
    label: '技术复杂度',
    label_en: 'Tech Complexity',
    options: [
      { value: 'low', label: '低', label_en: 'Low' },
      { value: 'medium', label: '中', label_en: 'Medium' },
      { value: 'high', label: '高', label_en: 'High' },
    ],
  },
  ai_dependency_level: {
    key: 'ai_dependency_level',
    label: 'AI 依赖程度',
    label_en: 'AI Dependency',
    options: [
      { value: 'none', label: '无依赖', label_en: 'None' },
      { value: 'light', label: '轻度依赖', label_en: 'Light' },
      { value: 'heavy', label: '重度依赖', label_en: 'Heavy' },
      { value: 'core', label: '核心依赖', label_en: 'Core' },
    ],
  },
  target_customer: {
    key: 'target_customer',
    label: '目标客户',
    label_en: 'Target Customer',
    options: [
      { value: 'b2c', label: '个人消费者', label_en: 'B2C' },
      { value: 'b2b_smb', label: '中小企业', label_en: 'B2B SMB' },
      { value: 'b2b_enterprise', label: '大型企业', label_en: 'B2B Enterprise' },
      { value: 'b2b2c', label: 'B2B2C', label_en: 'B2B2C' },
    ],
  },
  pricing_model: {
    key: 'pricing_model',
    label: '定价模式',
    label_en: 'Pricing Model',
    options: [
      { value: 'freemium', label: '免费增值', label_en: 'Freemium' },
      { value: 'subscription', label: '订阅制', label_en: 'Subscription' },
      { value: 'one_time', label: '一次性付费', label_en: 'One-time' },
      { value: 'usage_based', label: '按量计费', label_en: 'Usage-based' },
      { value: 'hybrid', label: '混合模式', label_en: 'Hybrid' },
    ],
  },
  feature_complexity: {
    key: 'feature_complexity',
    label: '功能复杂度',
    label_en: 'Feature Complexity',
    options: [
      { value: 'simple', label: '简单', label_en: 'Simple' },
      { value: 'moderate', label: '适中', label_en: 'Moderate' },
      { value: 'complex', label: '复杂', label_en: 'Complex' },
    ],
  },
  growth_driver: {
    key: 'growth_driver',
    label: '增长驱动',
    label_en: 'Growth Driver',
    options: [
      { value: 'product_led', label: '产品驱动', label_en: 'Product-led' },
      { value: 'sales_led', label: '销售驱动', label_en: 'Sales-led' },
      { value: 'marketing_led', label: '营销驱动', label_en: 'Marketing-led' },
      { value: 'ip_driven', label: 'IP驱动', label_en: 'IP-driven' },
    ],
  },
  product_stage: {
    key: 'product_stage',
    label: '产品阶段',
    label_en: 'Product Stage',
    options: [
      { value: 'early', label: '早期', label_en: 'Early' },
      { value: 'growth', label: '成长期', label_en: 'Growth' },
      { value: 'mature', label: '成熟期', label_en: 'Mature' },
    ],
  },
  startup_cost_level: {
    key: 'startup_cost_level',
    label: '启动成本',
    label_en: 'Startup Cost',
    options: [
      { value: 'low', label: '低', label_en: 'Low' },
      { value: 'medium', label: '中', label_en: 'Medium' },
      { value: 'high', label: '高', label_en: 'High' },
    ],
  },
  market_scope: {
    key: 'market_scope',
    label: '市场范围',
    label_en: 'Market Scope',
    options: [
      { value: 'niche', label: '细分市场', label_en: 'Niche' },
      { value: 'vertical', label: '垂直市场', label_en: 'Vertical' },
      { value: 'horizontal', label: '横向市场', label_en: 'Horizontal' },
      { value: 'global', label: '全球市场', label_en: 'Global' },
    ],
  },
}

// ============ Product Insights API ============

import type { DomainInsight, SummaryPoint, RiskAssessment } from '@/types'

export interface ProductInsightsResponse {
  insights: DomainInsight[]
  summary_points: SummaryPoint[]
  risk_assessment: RiskAssessment
}

export async function getProductInsights(slug: string): Promise<ProductInsightsResponse | null> {
  try {
    const response = await fetchApi<ProductInsightsResponse>(`/analysis/product/${slug}/insights`)
    return response
  } catch (error) {
    console.error('Failed to fetch product insights:', error)
    return null
  }
}

// ============ Product Leaderboards API ============

export interface ProductLeaderboard {
  id: string
  name: string
  name_en: string
  description: string
  description_en: string
  icon: string
}

export interface ProductLeaderboardStats {
  [key: string]: {
    id: string
    name: string
    name_en: string
    icon: string
    count: number
  }
}

export interface LeaderboardProduct {
  id: number
  name: string
  slug: string
  description: string
  category: string
  website_url: string
  logo_url: string | null
  revenue_30d: number
  mrr: number
  growth_rate: number
  country: string
  country_code: string
  analysis?: any
  tags?: any
}

export interface LeaderboardProductsResponse {
  leaderboard: ProductLeaderboard
  products: LeaderboardProduct[]
  pagination: {
    page: number
    page_size: number
    total: number
    total_pages: number
  }
}

export async function getProductLeaderboards(): Promise<ProductLeaderboard[]> {
  try {
    const response = await fetchApi<{ data: ProductLeaderboard[]; total: number }>(
      '/analysis/product/leaderboards/list'
    )
    return response.data || []
  } catch (error) {
    console.error('Failed to fetch product leaderboards:', error)
    return []
  }
}

export async function getProductLeaderboardStats(): Promise<ProductLeaderboardStats> {
  try {
    const response = await fetchApi<{ data: ProductLeaderboardStats }>(
      '/analysis/product/leaderboards/stats'
    )
    return response.data || {}
  } catch (error) {
    console.error('Failed to fetch leaderboard stats:', error)
    return {}
  }
}

export async function getLeaderboardProducts(
  leaderboardId: string,
  params?: { page?: number; page_size?: number }
): Promise<LeaderboardProductsResponse | null> {
  try {
    const searchParams = new URLSearchParams()
    if (params?.page) searchParams.set('page', params.page.toString())
    if (params?.page_size) searchParams.set('page_size', params.page_size.toString())

    const query = searchParams.toString()
    const response = await fetchApi<LeaderboardProductsResponse>(
      `/analysis/product/leaderboards/${leaderboardId}${query ? `?${query}` : ''}`
    )
    return response
  } catch (error) {
    console.error('Failed to fetch leaderboard products:', error)
    return null
  }
}

// ============ Data Info API ============

export interface DataInfo {
  data_source: string
  data_source_url: string
  total_products: number
  total_categories: number
  total_countries: number
  products_with_revenue: number
  analyzed_products: number
  last_crawl_time: string | null
  last_analysis_time: string | null
}

export async function getDataInfo(): Promise<DataInfo | null> {
  try {
    const response = await fetchApi<DataInfo>('/analytics/data-info')
    return response
  } catch (error) {
    console.error('Failed to fetch data info:', error)
    return null
  }
}

// ============ Chat Sessions API ============

export interface ChatSessionListItem {
  session_id: string
  title: string | null
  message_count: number
  turn_count: number
  created_at: string
  updated_at: string
  last_message_at: string | null
}

export interface ChatSessionDetail {
  id: number
  session_id: string
  title: string | null
  summary: string | null
  user_id: string | null
  enable_web_search: boolean
  context_type: string | null
  context_value: string | null
  context_products: string[] | null
  message_count: number
  turn_count: number
  total_cost: number
  total_input_tokens: number
  total_output_tokens: number
  is_archived: boolean
  created_at: string
  updated_at: string
  last_message_at: string | null
}

export interface ChatMessageItem {
  id: number
  session_id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  sequence: number
  tool_calls: Array<{
    name: string
    input: any
    output: string | null
    duration_ms: number | null
  }> | null
  input_tokens: number | null
  output_tokens: number | null
  cost: number | null
  model: string | null
  duration_ms: number | null
  created_at: string
}

export async function getChatSessions(params?: {
  user_id?: string
  include_archived?: boolean
  limit?: number
  offset?: number
}): Promise<{ sessions: ChatSessionListItem[]; total: number }> {
  const searchParams = new URLSearchParams()
  if (params?.user_id) searchParams.set('user_id', params.user_id)
  if (params?.include_archived) searchParams.set('include_archived', 'true')
  if (params?.limit) searchParams.set('limit', params.limit.toString())
  if (params?.offset) searchParams.set('offset', params.offset.toString())

  const query = searchParams.toString()
  const response = await fetchApi<{ sessions: ChatSessionListItem[]; total: number }>(
    `/sessions${query ? `?${query}` : ''}`
  )
  return response
}

export async function getChatSession(sessionId: string): Promise<{
  session: ChatSessionDetail
  messages: ChatMessageItem[]
} | null> {
  try {
    const response = await fetchApi<{
      session: ChatSessionDetail
      messages: ChatMessageItem[]
    }>(`/sessions/${sessionId}`)
    return response
  } catch (error) {
    console.error('Failed to fetch chat session:', error)
    return null
  }
}

export async function getChatSessionMessages(
  sessionId: string,
  params?: { limit?: number; offset?: number }
): Promise<ChatMessageItem[]> {
  const searchParams = new URLSearchParams()
  if (params?.limit) searchParams.set('limit', params.limit.toString())
  if (params?.offset) searchParams.set('offset', params.offset.toString())

  const query = searchParams.toString()
  const response = await fetchApi<{
    session_id: string
    messages: ChatMessageItem[]
    total: number
  }>(`/sessions/${sessionId}/messages${query ? `?${query}` : ''}`)
  return response.messages
}

export async function updateChatSession(
  sessionId: string,
  data: { title?: string; summary?: string; is_archived?: boolean }
): Promise<boolean> {
  try {
    await fetchApi(`/sessions/${sessionId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    })
    return true
  } catch (error) {
    console.error('Failed to update chat session:', error)
    return false
  }
}

export async function deleteChatSession(
  sessionId: string,
  hardDelete: boolean = false
): Promise<boolean> {
  try {
    const query = hardDelete ? '?hard_delete=true' : ''
    await fetchApi(`/sessions/${sessionId}${query}`, {
      method: 'DELETE',
    })
    return true
  } catch (error) {
    console.error('Failed to delete chat session:', error)
    return false
  }
}

export async function archiveChatSession(sessionId: string): Promise<boolean> {
  try {
    await fetchApi(`/sessions/${sessionId}/archive`, {
      method: 'POST',
    })
    return true
  } catch (error) {
    console.error('Failed to archive chat session:', error)
    return false
  }
}

export async function unarchiveChatSession(sessionId: string): Promise<boolean> {
  try {
    await fetchApi(`/sessions/${sessionId}/unarchive`, {
      method: 'POST',
    })
    return true
  } catch (error) {
    console.error('Failed to unarchive chat session:', error)
    return false
  }
}

export async function getChatSessionStats(): Promise<{
  total_sessions: number
  total_messages: number
  total_cost: number
} | null> {
  try {
    const response = await fetchApi<{
      total_sessions: number
      total_messages: number
      total_cost: number
    }>('/sessions/stats/overview')
    return response
  } catch (error) {
    console.error('Failed to fetch chat session stats:', error)
    return null
  }
}
