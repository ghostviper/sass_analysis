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


# =============================================================================
# 反差型模板 (Contrast) - 打破常规认知
# =============================================================================

CONTRAST_TEMPLATES: List[CurationTemplate] = [
    # 1. 低粉丝高收入 - 产品驱动的证明
    CurationTemplate(
        key="low_followers_high_revenue",
        title_zh="粉丝不到1000，月入过万",
        title_en="<1K Followers, $10K+ MRR",
        description_zh="这些产品证明：好产品自己会说话，不需要网红光环",
        description_en="These products prove: great products speak for themselves",
        insight_zh="产品力 > 个人IP，专注解决问题比积累粉丝更重要",
        insight_en="Product > Personal brand. Focus on solving problems.",
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
        conflict_dimensions=["founder_followers", "revenue_30d", "success_driver"]
    ),
    
    # 2. 功能极简但赚钱 - 少即是多
    CurationTemplate(
        key="simple_but_profitable",
        title_zh="功能只有3个，月入$5K+",
        title_en="Only 3 Features, $5K+ MRR",
        description_zh="极简主义的胜利：这些产品证明功能少不是缺点",
        description_en="Minimalism wins: fewer features can mean more revenue",
        insight_zh="砍掉80%功能，专注20%核心价值",
        insight_en="Cut 80% features, focus on 20% core value",
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
        conflict_dimensions=["feature_complexity", "revenue_30d"]
    ),
    
    # 3. 无聊赛道高收入 - 闷声发财
    CurationTemplate(
        key="boring_but_rich",
        title_zh="最无聊的需求，最稳定的收入",
        title_en="Boring Problems, Stable Income",
        description_zh="PDF转换、发票管理、数据导出...这些「无聊」工具闷声发大财",
        description_en="PDF tools, invoice managers, data exporters... boring tools making real money",
        insight_zh="无聊 = 刚需 + 低竞争 + 高付费意愿",
        insight_en="Boring = Real need + Low competition + High willingness to pay",
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
        conflict_dimensions=["demand_type", "revenue_30d"]
    ),
    
    # 4. 高门槛但一人做成 - 技术壁垒
    CurationTemplate(
        key="high_barrier_solo",
        title_zh="别人说做不了，他一个人做成了",
        title_en="They Said Impossible, Solo Dev Did It",
        description_zh="这些「高门槛」产品被一个人攻克，技术壁垒反而成了护城河",
        description_en="These 'high barrier' products were built solo, tech barriers became moats",
        insight_zh="高门槛 = 高壁垒 = 低竞争，敢啃硬骨头的人更少",
        insight_en="High barrier = High moat = Less competition",
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
        conflict_dimensions=["entry_barrier", "team_size", "solo_feasibility"]
    ),
]


# =============================================================================
# 认知型模板 (Cognitive) - 提供新视角
# =============================================================================

COGNITIVE_TEMPLATES: List[CurationTemplate] = [
    # 5. MVP清晰度高的产品 - 可执行的灵感
    CurationTemplate(
        key="clear_mvp_inspiration",
        title_zh="看完就知道怎么做的产品",
        title_en="Products You Can Start Building Today",
        description_zh="MVP边界清晰，核心功能明确，2周内可出原型",
        description_en="Clear MVP scope, defined core features, prototype in 2 weeks",
        insight_zh="好的产品创意应该让你立刻知道第一步做什么",
        insight_en="A good idea should tell you exactly what to build first",
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
        conflict_dimensions=["mvp_clarity", "entry_barrier"]
    ),
    
    # 6. 定价差异化成功案例
    CurationTemplate(
        key="pricing_innovation",
        title_zh="不走寻常路的定价策略",
        title_en="Unconventional Pricing That Works",
        description_zh="一次性买断、按用量付费、lifetime deal...打破订阅制霸权",
        description_en="One-time purchase, usage-based, lifetime deals... breaking subscription dominance",
        insight_zh="定价模式本身就是差异化，不是所有产品都适合订阅制",
        insight_en="Pricing model itself is differentiation",
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
        conflict_dimensions=["positioning_insight", "differentiation_point"]
    ),
    
    # 7. 垂直细分的成功
    CurationTemplate(
        key="vertical_niche_success",
        title_zh="只服务一小撮人，赚得比谁都多",
        title_en="Serving a Tiny Niche, Earning More Than Most",
        description_zh="Shopify店主、播客主播、独立开发者...精准垂直的力量",
        description_en="Shopify owners, podcasters, indie devs... the power of vertical focus",
        insight_zh="宁做小池塘的大鱼，不做大海里的小虾米",
        insight_en="Better to be a big fish in a small pond",
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
        conflict_dimensions=["positioning_insight", "market_scope"]
    ),
]


# =============================================================================
# 行动型模板 (Action) - 指导具体行动
# =============================================================================

ACTION_TEMPLATES: List[CurationTemplate] = [
    # 8. 周末可启动项目
    CurationTemplate(
        key="weekend_launchable",
        title_zh="周末就能上线的产品",
        title_en="Launch This Weekend",
        description_zh="低门槛 + MVP清晰 + 技术简单 = 48小时出原型",
        description_en="Low barrier + Clear MVP + Simple tech = 48-hour prototype",
        insight_zh="别想太多，先做出来再说",
        insight_en="Stop overthinking, just ship it",
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
        conflict_dimensions=["entry_barrier", "mvp_clarity", "startup_cost_level"]
    ),
    
    # 9. 不需要AI的赚钱产品
    CurationTemplate(
        key="no_ai_profitable",
        title_zh="不用AI也能月入过万",
        title_en="$10K+ MRR Without AI",
        description_zh="在AI焦虑时代，这些传统工具依然稳稳赚钱",
        description_en="In the age of AI anxiety, these traditional tools still make steady money",
        insight_zh="不是所有问题都需要AI解决，简单直接往往更有效",
        insight_en="Not every problem needs AI. Simple and direct often works better.",
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
        conflict_dimensions=["ai_dependency_level", "revenue_30d"]
    ),
    
    # 10. 变现风险最低的方向
    CurationTemplate(
        key="low_monetization_risk",
        title_zh="最容易收到钱的产品类型",
        title_en="Easiest to Monetize",
        description_zh="主动搜索型需求 + 清晰定价 + B2B客户 = 付费转化率高",
        description_en="Active search demand + Clear pricing + B2B = High conversion",
        insight_zh="选对方向，变现不是问题",
        insight_en="Choose the right direction, monetization follows",
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
        conflict_dimensions=["demand_type", "primary_risk", "target_customer"]
    ),
]


# =============================================================================
# 利基型模板 (Niche) - 特定人群/场景
# =============================================================================

NICHE_TEMPLATES: List[CurationTemplate] = [
    # 11. 开发者工具
    CurationTemplate(
        key="dev_tools_gems",
        title_zh="开发者做给开发者的工具",
        title_en="Dev Tools by Devs for Devs",
        description_zh="最懂痛点的人做的产品，B2D赛道的隐藏宝藏",
        description_en="Products by people who truly understand the pain. Hidden B2D gems.",
        insight_zh="做自己会用的产品，你就是第一个用户",
        insight_en="Build what you'd use. You're your first customer.",
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
        conflict_dimensions=["target_customer", "category"]
    ),
    
    # 12. Chrome扩展/插件生意
    CurationTemplate(
        key="extension_business",
        title_zh="小插件，大生意",
        title_en="Small Extensions, Big Business",
        description_zh="Chrome扩展、Figma插件、Notion模板...平台生态里的掘金者",
        description_en="Chrome extensions, Figma plugins, Notion templates... platform ecosystem gold diggers",
        insight_zh="借平台之力，用最小成本触达精准用户",
        insight_en="Leverage platforms to reach users with minimal cost",
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
        conflict_dimensions=["success_driver"]
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
