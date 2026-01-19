"""
每日策展模板定义

基于母题判断和产品分析维度，定义有反差感的策展模板。
每个模板包含：筛选规则、文案模板、冲突维度说明。
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class CurationTemplate:
    """策展模板"""
    key: str
    title_zh: str
    title_en: str
    description_zh: str
    description_en: str
    insight_zh: str
    insight_en: str
    tag_zh: str
    tag_en: str
    tag_color: str
    curation_type: str  # contrast / cognitive / action / niche
    filter_rules: Dict[str, Any]
    conflict_dimensions: List[str]
    min_products: int = 3
    max_products: int = 8
    priority: int = 5  # 优先级 1-10，数字越大优先级越高


# =============================================================================
# 反差型模板 (Contrast) - 打破常规认知
# =============================================================================

CONTRAST_TEMPLATES: List[CurationTemplate] = [
    # 1. 低粉丝高收入 - 产品驱动的证明
    CurationTemplate(
        key="low_followers_high_revenue",
        title_zh="粉丝不多，也能做到 $10k+ MRR",
        title_en="Few followers, still $10k+ MRR",
        description_zh="筛选粉丝 <1000 且产品驱动的收入型产品，证明产品力能直接变现",
        description_en="Products with <1k followers and product-driven revenue, proving product strength converts.",
        insight_zh="先把转化跑通，再谈影响力",
        insight_en="Prove conversion first, then grow influence.",
        tag_zh="反常识",
        tag_en="Counter-intuitive",
        tag_color="amber",
        curation_type="contrast",
        filter_rules={
            "startup": {
                "founder_followers": {"max": 1000},
                "revenue_30d": {"min": 10000}
            },
            "mother_theme": {
                "success_driver": ["产品驱动"]
            }
        },
        conflict_dimensions=["founder_followers", "revenue_30d", "success_driver"],
        priority=10  # 最高优先级：核心反差主题
    ),
    
    # 2. 功能极简但赚钱 - 少即是多
    CurationTemplate(
        key="simple_but_profitable",
        title_zh="功能不多，也能稳定月入 $5k+",
        title_en="Few features, still $5k+ MRR",
        description_zh="功能简单、落地页功能数不多的产品，核心价值更集中",
        description_en="Simple products with few listed features; the value is concentrated.",
        insight_zh="功能越少，价值越清晰",
        insight_en="Fewer features, clearer value.",
        tag_zh="少即是多",
        tag_en="Less is More",
        tag_color="emerald",
        curation_type="contrast",
        filter_rules={
            "startup": {
                "revenue_30d": {"min": 5000}
            },
            "selection": {
                "feature_complexity": ["simple"]
            },
            "landing_page": {
                "feature_count": {"max": 5}
            }
        },
        conflict_dimensions=["feature_complexity", "revenue_30d"],
        priority=9  # 高优先级：重要反差主题
    ),
    
    # 3. 无聊赛道高收入 - 闷声发财
    CurationTemplate(
        key="boring_but_rich",
        title_zh="无聊需求，稳定现金流",
        title_en="Boring needs, steady cash flow",
        description_zh="主动搜索型 + 真实机会的工具型产品，低竞争但付费明确",
        description_en="Active-search, real-opportunity tools with clear willingness to pay.",
        insight_zh="痛点越窄，收入越稳",
        insight_en="Narrower pain, steadier revenue.",
        tag_zh="闷声发财",
        tag_en="Silent Fortune",
        tag_color="slate",
        curation_type="contrast",
        filter_rules={
            "startup": {
                "revenue_30d": {"min": 3000}
            },
            "mother_theme": {
                "demand_type": ["主动搜索型"],
                "opportunity_validity": ["真实机会"]
            }
        },
        conflict_dimensions=["demand_type", "revenue_30d"],
        priority=7  # 中高优先级
    ),
    
    # 4. 高门槛但一人做成 - 技术壁垒
    CurationTemplate(
        key="high_barrier_solo",
        title_zh="高门槛也能小团队做成",
        title_en="High barrier, small team wins",
        description_zh="中高门槛 + 独立可行的产品，技术壁垒反而成护城河",
        description_en="Mid/high barrier yet solo-feasible products; tech becomes the moat.",
        insight_zh="敢啃硬骨头，竞争更少",
        insight_en="Hard problems mean fewer competitors.",
        tag_zh="硬核玩家",
        tag_en="Hardcore",
        tag_color="purple",
        curation_type="contrast",
        filter_rules={
            "startup": {
                "revenue_30d": {"min": 5000},
                "team_size": {"max": 2}
            },
            "mother_theme": {
                "entry_barrier": ["中等投入", "高门槛"],
                "solo_feasibility": ["有挑战但可行"]
            }
        },
        conflict_dimensions=["entry_barrier", "team_size", "solo_feasibility"],
        priority=8  # 高优先级：独特主题
    ),
]


# =============================================================================
# 认知型模板 (Cognitive) - 提供新视角
# =============================================================================

COGNITIVE_TEMPLATES: List[CurationTemplate] = [
    # 5. MVP清晰度高的产品 - 可执行的灵感
    CurationTemplate(
        key="clear_mvp_inspiration",
        title_zh="看完就知道先做什么的产品",
        title_en="Ideas with a clear first step",
        description_zh="MVP清晰 + 低门槛 + 真实机会，2周内可出原型",
        description_en="Clear MVP + low barrier + real opportunity; prototypable fast.",
        insight_zh="清晰的第一步比宏大愿景更重要",
        insight_en="A clear first step beats a big vision.",
        tag_zh="可执行",
        tag_en="Actionable",
        tag_color="blue",
        curation_type="cognitive",
        filter_rules={
            "mother_theme": {
                "mvp_clarity": ["清晰可执行"],
                "entry_barrier": ["低门槛快启动"],
                "opportunity_validity": ["真实机会"]
            }
        },
        conflict_dimensions=["mvp_clarity", "entry_barrier"],
        priority=8  # 高优先级：行动导向
    ),
    
    # 6. 定价差异化成功案例
    CurationTemplate(
        key="pricing_innovation",
        title_zh="用定价做差异化的产品",
        title_en="Products that differentiate on pricing",
        description_zh="一次性买断、按用量付费等定价方式，成为核心卖点",
        description_en="One-time, usage-based, or other pricing turns into the core edge.",
        insight_zh="定价是产品的一部分",
        insight_en="Pricing is part of the product.",
        tag_zh="定价创新",
        tag_en="Pricing Innovation",
        tag_color="orange",
        curation_type="cognitive",
        filter_rules={
            "startup": {
                "revenue_30d": {"min": 2000}
            },
            "mother_theme": {
                "positioning_insight": ["差异化定价"],
                "differentiation_point": ["定价差异化"]
            }
        },
        conflict_dimensions=["positioning_insight", "differentiation_point"],
        priority=6  # 中等优先级
    ),
    
    # 7. 垂直细分的成功
    CurationTemplate(
        key="vertical_niche_success",
        title_zh="服务小人群，也能赚到钱",
        title_en="Serve a small niche, still earn well",
        description_zh="精准垂直 + 真实机会，专注特定人群更容易占位",
        description_en="Vertical focus + real opportunity; easier to own a niche.",
        insight_zh="小池塘更容易称王",
        insight_en="Own a small pond.",
        tag_zh="精准垂直",
        tag_en="Vertical Focus",
        tag_color="teal",
        curation_type="cognitive",
        filter_rules={
            "startup": {
                "revenue_30d": {"min": 3000}
            },
            "mother_theme": {
                "positioning_insight": ["精准垂直"],
                "opportunity_validity": ["真实机会"]
            },
            "selection": {
                "market_scope": ["vertical"]
            }
        },
        conflict_dimensions=["positioning_insight", "market_scope"],
        priority=7  # 中高优先级
    ),
]


# =============================================================================
# 行动型模板 (Action) - 指导具体行动
# =============================================================================

ACTION_TEMPLATES: List[CurationTemplate] = [
    # 8. 周末可启动项目
    CurationTemplate(
        key="weekend_launchable",
        title_zh="周末可启动的项目",
        title_en="Projects you can start this weekend",
        description_zh="低门槛 + MVP清晰 + 低成本/简单功能，适合快速试水",
        description_en="Low barrier, clear MVP, low cost/simple features for fast starts.",
        insight_zh="先做出来，再优化",
        insight_en="Ship first, refine later.",
        tag_zh="快速启动",
        tag_en="Quick Start",
        tag_color="green",
        curation_type="action",
        filter_rules={
            "mother_theme": {
                "entry_barrier": ["低门槛快启动"],
                "mvp_clarity": ["清晰可执行"],
                "solo_feasibility": ["非常适合"]
            },
            "selection": {
                "startup_cost_level": ["low"],
                "feature_complexity": ["simple"]
            }
        },
        conflict_dimensions=["entry_barrier", "mvp_clarity", "startup_cost_level"],
        priority=9  # 高优先级：最实用的行动指南
    ),
    
    # 9. 不需要AI的赚钱产品
    CurationTemplate(
        key="no_ai_profitable",
        title_zh="不靠 AI 也能做到 $10k+ MRR",
        title_en="$10k+ MRR without heavy AI",
        description_zh="AI依赖低但真实需求明确，传统工具照样稳定赚钱",
        description_en="Low AI dependency with clear demand; traditional tools still win.",
        insight_zh="解决问题比堆技术重要",
        insight_en="Solve the problem, not the hype.",
        tag_zh="回归本质",
        tag_en="Back to Basics",
        tag_color="gray",
        curation_type="action",
        filter_rules={
            "startup": {
                "revenue_30d": {"min": 10000}
            },
            "selection": {
                "ai_dependency_level": ["none", "light"]
            },
            "mother_theme": {
                "opportunity_validity": ["真实机会"]
            }
        },
        conflict_dimensions=["ai_dependency_level", "revenue_30d"],
        priority=6  # 中等优先级
    ),
    
    # 10. 变现风险最低的方向
    CurationTemplate(
        key="low_monetization_risk",
        title_zh="更容易收钱的方向",
        title_en="Directions that monetize easier",
        description_zh="主动搜索 + B2B + 变现风险低，付费路径更清晰",
        description_en="Active search + B2B + lower monetization risk; clearer pay path.",
        insight_zh="付费路径越短越好",
        insight_en="Shorter pay paths convert better.",
        tag_zh="易变现",
        tag_en="Easy Money",
        tag_color="yellow",
        curation_type="action",
        filter_rules={
            "startup": {
                "revenue_30d": {"min": 2000}
            },
            "mother_theme": {
                "demand_type": ["主动搜索型"],
                "primary_risk": {"not": ["变现转化"]}
            },
            "selection": {
                "target_customer": ["b2b_smb", "b2b_enterprise"]
            }
        },
        conflict_dimensions=["demand_type", "primary_risk", "target_customer"],
        priority=7  # 中高优先级
    ),
]


# =============================================================================
# 利基型模板 (Niche) - 特定人群/场景
# =============================================================================

NICHE_TEMPLATES: List[CurationTemplate] = [
    # 11. 开发者工具
    CurationTemplate(
        key="dev_tools_gems",
        title_zh="做自己也愿意付费的开发者工具",
        title_en="Dev tools you'd pay for yourself",
        description_zh="B2D + 开发者品类，懂痛点的人做给同类用",
        description_en="B2D and dev categories built by insiders who feel the pain.",
        insight_zh="先当自己的第一个用户",
        insight_en="Be your first user.",
        tag_zh="开发者向",
        tag_en="For Devs",
        tag_color="indigo",
        curation_type="niche",
        filter_rules={
            "startup": {
                "revenue_30d": {"min": 1000},
                "category": {"contains": ["developer", "api", "devtool", "coding"]}
            },
            "selection": {
                "target_customer": ["b2d"]
            }
        },
        conflict_dimensions=["target_customer", "category"],
        priority=4  # 低优先级：利基市场
    ),
    
    # 12. Chrome扩展/插件生意
    CurationTemplate(
        key="extension_business",
        title_zh="平台生态里的小生意",
        title_en="Small businesses inside platforms",
        description_zh="渠道驱动的插件/模板类产品，借平台流量换增长",
        description_en="Channel-driven plugins/templates that ride platform traffic.",
        insight_zh="借平台流量，省获客成本",
        insight_en="Leverage platforms to cut CAC.",
        tag_zh="平台生态",
        tag_en="Platform Ecosystem",
        tag_color="cyan",
        curation_type="niche",
        filter_rules={
            "startup": {
                "revenue_30d": {"min": 1000}
            },
            "mother_theme": {
                "success_driver": ["渠道驱动"]
            }
        },
        conflict_dimensions=["success_driver"],
        priority=3  # 低优先级：利基市场
    ),
]


# =============================================================================
# 汇总所有模板
# =============================================================================

ALL_TEMPLATES: List[CurationTemplate] = (
    CONTRAST_TEMPLATES + 
    COGNITIVE_TEMPLATES + 
    ACTION_TEMPLATES + 
    NICHE_TEMPLATES
)

TEMPLATE_BY_KEY: Dict[str, CurationTemplate] = {t.key: t for t in ALL_TEMPLATES}


def get_templates_by_type(curation_type: str) -> List[CurationTemplate]:
    """按类型获取模板"""
    return [t for t in ALL_TEMPLATES if t.curation_type == curation_type]


def get_template(key: str) -> Optional[CurationTemplate]:
    """按key获取模板"""
    return TEMPLATE_BY_KEY.get(key)
