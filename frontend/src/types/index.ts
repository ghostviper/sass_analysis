// 产品/Startup 类型
export interface Startup {
  id: number
  slug: string
  name: string
  description: string | null
  category: string | null
  website_url: string | null
  logo_url: string | null
  revenue_30d: number | null
  revenue_prev_30d: number | null
  revenue_change: number | null
  mrr: number | null
  arr: number | null
  founded_date: string | null
  twitter_followers: number | null
  created_at: string
  updated_at: string
}

// 赛道分析类型
export interface CategoryAnalysis {
  id: number
  category: string
  analysis_date: string
  total_projects: number
  total_revenue: number
  avg_revenue: number
  median_revenue: number
  revenue_per_project: number
  top10_revenue_share: number
  top50_revenue_share: number
  revenue_std_dev: number
  gini_coefficient: number
  market_type: MarketType
  market_type_reason: string
}

// 市场类型
export type MarketType =
  | 'blue_ocean'
  | 'red_ocean'
  | 'emerging'
  | 'moderate'
  | 'concentrated'
  | 'weak_demand'

// 选品分析类型
export interface ProductSelectionAnalysis {
  id: number
  startup_id: number
  is_product_driven: boolean
  ip_dependency_score: number
  is_small_and_beautiful: boolean
  description_word_count: number
  tech_complexity_level: 'low' | 'medium' | 'high'
  uses_llm_api: boolean
  requires_compliance: boolean
  combo1_match: boolean
  combo2_match: boolean
  combo3_match: boolean
  individual_dev_suitability: number
  has_follower_data: boolean
  data_quality_notes: string | null
  analyzed_at: string
}

// Landing Page 分析类型
export interface LandingPageAnalysis {
  id: number
  startup_id: number
  snapshot_id: number | null
  // 用户分析
  target_audience: string[] | null
  target_roles: string[] | null
  use_cases: string[] | null
  // 功能分析
  core_features: string[] | null
  feature_count: number
  value_propositions: string[] | null
  // 痛点分析
  pain_points: string[] | null
  pain_point_sharpness: number | null
  uses_before_after: boolean
  uses_emotional_words: boolean
  // 护城河
  potential_moats: string[] | null
  // 定价分析
  pricing_model: string | null
  pricing_tiers: any[] | null
  pricing_clarity_score: number | null
  has_free_tier: boolean | null
  has_trial: boolean | null
  // 转化分析
  cta_count: number
  cta_texts: string[] | null
  conversion_funnel_steps: number
  has_instant_value_demo: boolean
  conversion_friendliness_score: number | null
  // 关键词
  industry_keywords: Record<string, number> | null
  headline_text: string | null
  tagline_text: string | null
  // 综合评分
  positioning_clarity_score: number | null
  replication_difficulty_score: number | null
  individual_replicability_score: number | null
  product_maturity_score: number | null
  // 元数据
  ai_model_used: string | null
  analyzed_at: string
}

// 综合分析类型
export interface ComprehensiveAnalysis {
  id: number
  startup_id: number
  maturity_score: number
  positioning_clarity: number
  pain_point_sharpness: number
  pricing_clarity: number
  conversion_friendliness: number
  individual_replicability: number
  overall_recommendation: number
  analysis_summary: AnalysisSummary
  analyzed_at: string
}

// 分析摘要
export interface AnalysisSummary {
  product_name: string
  category: string | null
  revenue_30d: number | null
  analysis_date: string
  data_sources: {
    has_selection_analysis: boolean
    has_landing_analysis: boolean
    has_category_analysis: boolean
    has_revenue_data: boolean
    has_follower_data: boolean
  }
  data_completeness: number
  scores: Record<string, number>
  strengths: string[]
  risks: string[]
  recommendations: string[]
  market_position: {
    type: MarketType
    reason: string
    category_revenue: number
    category_projects: number
  } | null
}

// 机会产品响应
export interface OpportunityProduct {
  startup: Startup
  analysis: ProductSelectionAnalysis
}

// 综合推荐响应
export interface ComprehensiveRecommendation {
  startup: Startup
  analysis: ComprehensiveAnalysis
}

// API 响应包装
export interface ApiResponse<T> {
  data: T
  total?: number
  page?: number
  page_size?: number
}

// 市场类型配置
export const MARKET_TYPE_CONFIG: Record<MarketType, {
  label: string
  color: string
  bgColor: string
  description: string
  icon: string
}> = {
  blue_ocean: {
    label: '蓝海市场',
    color: 'text-market-blue-ocean',
    bgColor: 'bg-market-blue-ocean/10',
    description: '竞争少，多数产品盈利',
    icon: 'water',
  },
  emerging: {
    label: '新兴市场',
    color: 'text-market-emerging',
    bgColor: 'bg-market-emerging/10',
    description: '新兴市场，早期机会',
    icon: 'rocket',
  },
  moderate: {
    label: '适中市场',
    color: 'text-market-moderate',
    bgColor: 'bg-market-moderate/10',
    description: '中等竞争，需要差异化',
    icon: 'scale-balanced',
  },
  concentrated: {
    label: '集中市场',
    color: 'text-market-concentrated',
    bgColor: 'bg-market-concentrated/10',
    description: '头部集中，新手慎入',
    icon: 'crown',
  },
  red_ocean: {
    label: '红海市场',
    color: 'text-market-red-ocean',
    bgColor: 'bg-market-red-ocean/10',
    description: '竞争激烈，建议避开',
    icon: 'fire',
  },
  weak_demand: {
    label: '弱需求',
    color: 'text-market-weak-demand',
    bgColor: 'bg-market-weak-demand/10',
    description: '需求不足，建议避开',
    icon: 'triangle-exclamation',
  },
}

// 复杂度配置
export const COMPLEXITY_CONFIG: Record<string, {
  label: string
  color: string
  bgColor: string
}> = {
  low: {
    label: '低',
    color: 'text-accent-success',
    bgColor: 'bg-accent-success/10',
  },
  medium: {
    label: '中',
    color: 'text-accent-warning',
    bgColor: 'bg-accent-warning/10',
  },
  high: {
    label: '高',
    color: 'text-accent-danger',
    bgColor: 'bg-accent-danger/10',
  },
}
