// 产品/Startup 类型
export interface Startup {
  id: number
  slug: string
  name: string
  description: string | null
  category: string | null
  website_url: string | null
  logo_url: string | null
  profile_url: string | null
  revenue_30d: number | null
  revenue_prev_30d: number | null
  revenue_change: number | null
  mrr: number | null
  arr: number | null
  growth_rate: number | null
  founded_date: string | null
  twitter_followers: number | null
  founder_name: string | null
  founder_username: string | null
  founder_followers: number | null
  country: string | null
  country_code: string | null
  is_verified: boolean
  verified_source: string | null
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
  // 新增标签字段 (v2)
  revenue_tier: RevenueTier | null
  revenue_follower_ratio_level: RatioLevel | null
  growth_driver: GrowthDriver | null
  ai_dependency_level: AIDependencyLevel | null
  has_realtime_feature: boolean | null
  is_data_intensive: boolean | null
  has_compliance_requirement: boolean | null
  pricing_model: PricingModel | null
  target_customer: TargetCustomer | null
  market_scope: MarketScope | null
  feature_complexity: FeatureComplexity | null
  moat_type: string | null
  startup_cost_level: CostLevel | null
  product_stage: ProductStage | null
}

// ========== 新增标签类型定义 (v2) ==========

// 收入层级
export type RevenueTier = 'micro' | 'small' | 'medium' | 'large'

// 收入/粉丝比等级
export type RatioLevel = 'high' | 'medium' | 'low'

// 增长驱动类型
export type GrowthDriver = 'product_driven' | 'ip_driven' | 'content_driven' | 'community_driven'

// AI依赖程度
export type AIDependencyLevel = 'none' | 'light' | 'heavy'

// 定价模式
export type PricingModel = 'subscription' | 'one_time' | 'usage' | 'freemium'

// 目标客户
export type TargetCustomer = 'b2c' | 'b2b_smb' | 'b2b_enterprise' | 'b2d'

// 市场类型
export type MarketScope = 'horizontal' | 'vertical'

// 功能复杂度
export type FeatureComplexity = 'simple' | 'moderate' | 'complex'

// 成本等级
export type CostLevel = 'low' | 'medium' | 'high'

// 产品阶段
export type ProductStage = 'early' | 'growth' | 'mature'

// 产品标签（AI友好格式）
export interface ProductTags {
  revenue_tier: RevenueTier | null
  revenue_follower_ratio_level: RatioLevel | null
  growth_driver: GrowthDriver | null
  ai_dependency_level: AIDependencyLevel | null
  has_realtime_feature: boolean | null
  is_data_intensive: boolean | null
  has_compliance_requirement: boolean | null
  pricing_model: PricingModel | null
  target_customer: TargetCustomer | null
  market_scope: MarketScope | null
  feature_complexity: FeatureComplexity | null
  moat_type: string | null
  startup_cost_level: CostLevel | null
  product_stage: ProductStage | null
  tech_complexity_level: CostLevel | null
  maintenance_cost_level: CostLevel | null
}

// 产品评分
export interface ProductScores {
  individual_dev_suitability: number
  ip_dependency_score: number
  feature_simplicity_score: number
  follower_revenue_ratio: number
}

// 确定性洞察
export interface DomainInsight {
  type: 'positive' | 'warning' | 'info'
  title: string
  description: string
  confidence: 'high' | 'medium'
  source: string
  rule_name?: string
}

// 摘要要点
export interface SummaryPoint {
  type: 'positive' | 'warning' | 'info' | 'neutral'
  text: string
}

// 风险评估
export interface RiskAssessment {
  risk_score: number
  risk_level: 'low' | 'medium' | 'high'
  risk_label: string
  warning_count: number
  positive_count: number
  key_risks: string[]
  key_advantages: string[]
}

// 产品分析响应（新结构）
export interface ProductAnalysisResponse {
  startup: Startup
  analysis: ProductSelectionAnalysis
  data_layer: {
    tags: ProductTags
    scores: ProductScores
  }
  display_layer: {
    summary_points: SummaryPoint[]
    domain_insights: DomainInsight[]
    risk_assessment: RiskAssessment
  }
}

// 榜单配置
export interface LeaderboardConfig {
  id: string
  name: string
  name_en: string
  description: string
  description_en: string
  icon: string
}

// 榜单产品响应
export interface LeaderboardResponse {
  leaderboard: LeaderboardConfig
  products: (Startup & {
    analysis: ProductSelectionAnalysis | null
    tags: ProductTags | null
  })[]
  pagination: {
    page: number
    page_size: number
    total: number
    total_pages: number
  }
}

// 数据信息
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
  coverage_note: string
  coverage_note_en: string
  limitations: string[]
  limitations_en: string[]
}

// 筛选维度选项
export interface FilterOption {
  value: string
  label: string
  label_en: string
}

// 筛选维度配置
export interface FilterDimension {
  label: string
  label_en: string
  options: FilterOption[]
}

// 筛选器配置
export interface FilterDimensions {
  revenue_tier: FilterDimension
  tech_complexity_level: FilterDimension
  ai_dependency_level: FilterDimension
  target_customer: FilterDimension
  pricing_model: FilterDimension
  feature_complexity: FilterDimension
  growth_driver: FilterDimension
  product_stage: FilterDimension
  startup_cost_level: FilterDimension
  market_scope: FilterDimension
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
