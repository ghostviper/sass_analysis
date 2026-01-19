/**
 * Discover Page Types - 发现页类型定义
 * 支持双语 (i18n)
 */

// =============================================================================
// 1. TopicCollections - 专题合集
// =============================================================================

export interface TopProduct {
  name: string
  revenue_30d: number | null
}

export interface TopicSummary {
  id: string
  title: string
  title_zh: string
  title_en: string
  description: string
  description_zh: string
  description_en: string
  curator_role: string
  curator_display_name?: string
  curator_display_name_zh?: string
  curator_display_name_en?: string
  pattern?: string
  product_count: number
  emoji?: string
  gradient?: string
  top_products: TopProduct[]
}

export interface TopicsResponse {
  topics: TopicSummary[]
}

export interface KeyTag {
  key: string
  label: string
  label_zh?: string
  label_en?: string
  value: string
}

export interface ProductInTopic {
  id: number
  name: string
  slug: string
  category: string | null
  logo_url: string | null
  revenue_30d: number | null
  key_tags: KeyTag[]
}

export interface TopicDetail {
  id: string
  title: string
  title_zh: string
  title_en: string
  description: string
  description_zh: string
  description_en: string
  curator_role: string
  curator_display_name?: string
  curator_display_name_zh?: string
  curator_display_name_en?: string
  pattern?: string
  product_count: number
  emoji?: string
  gradient?: string
  filter_rules?: Record<string, unknown>
}

export interface Pagination {
  total: number
  page: number
  limit: number
  total_pages: number
}

export interface TopicDetailResponse {
  topic: TopicDetail
  products: ProductInTopic[]
  pagination: Pagination
}

// =============================================================================
// 2. TodayCuration - 今日策展
// =============================================================================

export interface CurationProduct {
  name: string
  slug?: string
  mrr: string | null
  logo: string
  highlight_zh?: string | null
  highlight_en?: string | null
}

export interface Curation {
  id: number
  title: string
  title_zh: string
  title_en: string
  description: string
  description_zh: string
  description_en: string
  tag: string
  tag_zh: string
  tag_en: string
  tag_color: string
  insight: string
  insight_zh: string
  insight_en: string
  curation_type: string
  curation_date: string
  products: CurationProduct[]
}

export interface CurationsResponse {
  curations: Curation[]
}

// =============================================================================
// 3. SuccessBreakdown - 爆款解剖
// =============================================================================

export interface TimelineEvent {
  date: string
  event: string
  event_zh: string
  event_en: string
}

export interface KeyInsight {
  text: string
  text_zh: string
  text_en: string
}

export interface StoryProduct {
  name: string
  logo: string
  mrr: string | null
  founder: string | null
}

export interface SuccessStory {
  id: number
  title: string
  title_zh: string
  title_en: string
  subtitle: string
  subtitle_zh: string
  subtitle_en: string
  product: StoryProduct
  timeline: TimelineEvent[]
  key_insights: KeyInsight[]
  gradient: string
  accent_color: string
}

export interface StoriesResponse {
  stories: SuccessStory[]
}


// =============================================================================
// 4. CreatorUniverse - 创作者宇宙
// =============================================================================

export interface CreatorProduct {
  id?: number
  name: string
  mrr: string | null
}

export interface Creator {
  id: number | string
  name: string
  handle: string | null
  avatar: string
  avatar_url?: string | null
  bio: string | null
  bio_zh: string | null
  bio_en: string | null
  tag: string | null
  tag_zh: string | null
  tag_en: string | null
  tag_color: string
  total_mrr: string | null
  followers: string | null
  social_url?: string | null
  social_platform?: string | null
  products: CreatorProduct[]
  product_count: number
}

export interface CreatorsResponse {
  creators: Creator[]
}

// =============================================================================
// 5. ForYouSection - 为你推荐
// =============================================================================

export interface Recommendation {
  id: string
  direction: string
  direction_zh: string
  direction_en: string
  description: string
  description_zh: string
  description_en: string
  why_for_you: string | null
  why_for_you_zh: string | null
  why_for_you_en: string | null
  examples: string[]
  difficulty: string
  potential: string
  gradient: string
  accent_color: string
}

export interface RecommendationsResponse {
  recommendations: Recommendation[]
}

export interface UserPreference {
  id: number
  user_id: string
  preferred_roles: string[]
  interested_categories: string[]
  skill_level: string
  goal: string | null
  time_commitment: string | null
  tech_stack: string[]
  created_at: string
}

export interface UserPreferenceResponse {
  preference: UserPreference | null
}
