"""
策展系统配置

包含：
- 母题定义（三层架构：筛选层、行动层、归因层）
- 证据字段定义
- 验证配置
"""

from typing import Any, Dict, List

# =============================================================================
# 版本与配置
# =============================================================================

PROMPT_VERSION = "v4.2"
CONFIDENCE_CHOICES = ["高", "中", "低"]
REQUIRED_FIELDS = ["judgment", "confidence", "reasons", "evidence_fields", "uncertainties"]

# =============================================================================
# 证据字段定义
# =============================================================================

# LandingPageAnalysis 字段
LANDING_PAGE_FIELDS = [
    "headline_text", "tagline_text", "core_features", "feature_count",
    "value_propositions", "target_audience", "pain_points", "use_cases",
    "pricing_model", "pricing_tiers", "has_free_tier", "has_trial",
    "cta_count", "cta_texts", "conversion_funnel_steps",
    "has_instant_value_demo", "conversion_friendliness_score",
    "potential_moats", "uses_before_after", "uses_emotional_words",
    "positioning_clarity_score", "replication_difficulty_score",
    "individual_replicability_score", "pain_point_sharpness",
]

# ProductSelectionAnalysis 字段
SELECTION_ANALYSIS_FIELDS = [
    "growth_driver", "is_product_driven", "ip_dependency_score",
    "follower_revenue_ratio", "tech_complexity_level", "feature_complexity",
    "ai_dependency_level", "startup_cost_level", "market_scope",
    "target_customer", "requires_realtime", "requires_large_data",
    "requires_compliance",
]

# Startup 基础字段
STARTUP_FIELDS = [
    "revenue_30d", "category", "description", "founder_followers", "team_size",
]

# CategoryAnalysis 字段
CATEGORY_FIELDS = ["market_type"]

# 合并所有证据字段
EVIDENCE_FIELDS = LANDING_PAGE_FIELDS + SELECTION_ANALYSIS_FIELDS + STARTUP_FIELDS + CATEGORY_FIELDS


# =============================================================================
# 母题定义 - 三层架构
# =============================================================================

# 筛选层：回答"这个方向值不值得研究？"（2个母题）
SCREENING_THEMES: List[Dict[str, Any]] = [
    {
        "key": "opportunity_validity",
        "name": "机会真实性",
        "layer": "screening",
        "options": ["真实机会", "存在风险", "伪机会", "证据不足/无法判断"],
        "hint": """判断这是真实的市场机会还是伪机会。
真实机会特征：pain_points具体可量化（如"每周花5小时做X"）、target_audience明确指向特定人群（如"Shopify店主"而非"电商卖家"）、cta_texts指向具体行动
伪机会特征（满足2个即判定）：pain_points抽象泛化（如"提高效率"）、value_propositions全是愿景无具体功能、cta_texts模糊（如"开始旅程"）、target_audience过宽（如"所有人"）""",
    },
    {
        "key": "demand_type",
        "name": "需求类型",
        "layer": "screening",
        "options": ["主动搜索型", "触发认知型", "需教育型", "证据不足/无法判断"],
        "hint": """判断用户获取这个产品的方式。
主动搜索型：pain_points描述的是用户会主动搜索的问题（如"PDF转Word"、"发票管理"）
触发认知型：pain_points是潜在需求，看到才意识到需要（如"团队协作效率低"）
需教育型：产品解决的问题用户通常不知道存在（如新概念、新范式）
关键证据：pain_points是否是用户会搜索的关键词、uses_before_after是否清晰""",
    },
]

# 行动层：回答"如果我想做，可行吗？怎么做？"（4个母题）
ACTION_THEMES: List[Dict[str, Any]] = [
    {
        "key": "solo_feasibility",
        "name": "独立可行性",
        "layer": "action",
        "options": ["非常适合", "有挑战但可行", "不适合", "证据不足/无法判断"],
        "hint": """判断一个人能否把这个产品做出来并维护。
非常适合：tech_complexity_level=low/medium、feature_complexity=simple/moderate、team_size<=2、不依赖重度AI或实时数据
有挑战但可行：tech_complexity_level=medium、功能复杂度中等、或需要特定领域知识
不适合：tech_complexity_level=high、或需要实时系统+大数据、或requires_compliance=true""",
    },
    {
        "key": "entry_barrier",
        "name": "入场门槛",
        "layer": "action",
        "options": ["低门槛快启动", "中等投入", "高门槛", "证据不足/无法判断"],
        "hint": """判断启动这个项目需要的时间和资金投入。
低门槛快启动：startup_cost_level=low、feature_count较少（<=5）、核心功能简单明确（2周内可出MVP）
中等投入：startup_cost_level=medium、feature_count中等、需要一定开发周期（1-2月出MVP）
高门槛：startup_cost_level=high、或ai_dependency_level=heavy、或requires_compliance=true、或需要大量初始数据""",
    },
    {
        "key": "primary_risk",
        "name": "主要风险",
        "layer": "action",
        "options": ["技术实现", "市场验证", "用户获取", "变现转化", "证据不足/无法判断"],
        "hint": """判断如果做这个方向失败，最可能死在哪个环节。
技术实现：tech_complexity_level=high、ai_dependency_level=heavy、或requires_realtime=true
市场验证：demand_type=需教育型、或pain_points抽象不具体
用户获取：potential_moats较弱、demand_type!=主动搜索型、target_audience过宽
变现转化：has_free_tier=true但pricing_tiers不清晰、pricing_model不明确、target_customer=b2c且无明确付费点""",
    },
    {
        "key": "mvp_clarity",
        "name": "MVP清晰度",
        "layer": "action",
        "options": ["清晰可执行", "基本清晰", "模糊", "证据不足/无法判断"],
        "hint": """判断这个产品的最小可行版本是否清晰。
清晰可执行：core_features有明确的1-3个核心功能、has_instant_value_demo=true、value_propositions聚焦单一价值点
基本清晰：core_features可识别但数量较多（4-8个）、或value_propositions有多个方向
模糊：core_features过多或过于抽象、value_propositions分散、headline_text过于宽泛""",
    },
]


# 归因层：回答"为什么成功？哪些值得借鉴？"（3个母题）
ATTRIBUTION_THEMES: List[Dict[str, Any]] = [
    {
        "key": "success_driver",
        "name": "成功驱动因素",
        "layer": "attribution",
        "options": ["产品驱动", "IP/创作者驱动", "内容驱动", "渠道驱动", "证据不足/无法判断"],
        "hint": """判断这个产品的成功主要靠什么驱动。
产品驱动：growth_driver=product_driven、或is_product_driven=true、或产品本身功能/体验是核心卖点
IP/创作者驱动：growth_driver=ip_driven、或founder_followers较高、或产品与创始人个人品牌强绑定
内容驱动：growth_driver=content_driven、或有明显博客/教程/课程内容、或通过内容获取用户
渠道驱动：依托特定平台（如Shopify app, Chrome extension, Notion integration），从description或core_features推断""",
    },
    {
        "key": "positioning_insight",
        "name": "定位洞察",
        "layer": "attribution",
        "options": ["精准垂直", "差异化定价", "痛点锋利", "场景具体", "无明显亮点", "证据不足/无法判断"],
        "hint": """判断这个产品的定位策略有什么值得学习的地方。
精准垂直：target_audience非常具体（如"Shopify店主"而非"电商卖家"）、或market_scope=vertical
差异化定价：pricing_model有创新（usage-based/一次性买断/lifetime deal等）
痛点锋利：pain_points描述非常具体的问题（有数字、有场景）、或uses_before_after=true
场景具体：use_cases明确且具体、或headline_text直接描述使用场景""",
    },
    {
        "key": "differentiation_point",
        "name": "差异化点",
        "layer": "attribution",
        "options": ["功能差异化", "体验差异化", "人群差异化", "定价差异化", "无明显差异化", "证据不足/无法判断"],
        "hint": """判断这个产品相比竞品的独特之处。
功能差异化：potential_moats包含技术/功能相关壁垒、或core_features中有独特功能描述
体验差异化：has_instant_value_demo=true、或value_propositions强调简单/快速/易用
人群差异化：target_audience非常细分、market_scope=vertical
定价差异化：pricing_model非主流订阅模式（如一次性买断、按用量付费）
无明显差异化：以上都不满足，与同类产品高度相似""",
    },
]

# 合并所有母题
MOTHER_THEMES: List[Dict[str, Any]] = SCREENING_THEMES + ACTION_THEMES + ATTRIBUTION_THEMES

# 母题分层映射
THEME_LAYERS = {
    "screening": [t["key"] for t in SCREENING_THEMES],
    "action": [t["key"] for t in ACTION_THEMES],
    "attribution": [t["key"] for t in ATTRIBUTION_THEMES],
}

# 母题 key 到定义的映射
THEME_BY_KEY = {t["key"]: t for t in MOTHER_THEMES}
