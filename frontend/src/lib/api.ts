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

export async function getStartups(params?: {
  page?: number
  page_size?: number
  category?: string
  country_code?: string
  search?: string
  sort_by?: SortField
  sort_order?: SortOrder
}): Promise<{ items: Startup[]; total: number }> {
  const searchParams = new URLSearchParams()
  if (params?.page) searchParams.set('page', params.page.toString())
  if (params?.page_size) searchParams.set('limit', params.page_size.toString())
  if (params?.category) searchParams.set('category', params.category)
  if (params?.country_code) searchParams.set('country_code', params.country_code)
  if (params?.search) searchParams.set('search', params.search)
  if (params?.sort_by) searchParams.set('sort_by', params.sort_by)
  if (params?.sort_order) searchParams.set('sort_order', params.sort_order)

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
  min_products?: number
}): Promise<{
  items: FounderLeaderboardItem[]
  total: number
  pages: number
}> {
  const searchParams = new URLSearchParams()
  if (params?.sort_by) searchParams.set('sort_by', params.sort_by)
  if (params?.sort_order) searchParams.set('sort_order', params.sort_order)
  if (params?.limit) searchParams.set('limit', params.limit.toString())
  if (params?.page) searchParams.set('page', params.page.toString())
  if (params?.min_products) searchParams.set('min_products', params.min_products.toString())

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
