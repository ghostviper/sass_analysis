"""
策展 Agent

基于规则的专题生成，从母题判断结果中筛选产品并生成专题。

v3: 支持中英文双语
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class TopicTemplate:
    """专题模板 - 支持双语"""
    title_zh: str
    title_en: str
    pattern: str  # contrast / niche / cognitive / action / trending
    description_zh: str
    description_en: str
    cta_zh: str = "让我帮你分析：你能不能做类似的"
    cta_en: str = "Let me analyze: Can you build something similar?"


@dataclass
class CuratorRole:
    """策展角色配置"""
    name: str
    display_name_zh: str
    display_name_en: str
    filter_rules: Dict[str, Any]
    topic_templates: List[TopicTemplate] = field(default_factory=list)


# =============================================================================
# 策展角色配置 (v3 - 双语支持)
# =============================================================================

CURATOR_ROLES: Dict[str, CuratorRole] = {
    # -------------------------------------------------------------------------
    # 角色1: 谨慎的独立开发者 - 最严格筛选
    # -------------------------------------------------------------------------
    "cautious_indie_dev": CuratorRole(
        name="cautious_indie_dev",
        display_name_zh="谨慎的独立开发者",
        display_name_en="Cautious Indie Dev",
        filter_rules={
            "solo_feasibility": ["非常适合"],
            "opportunity_validity": ["真实机会"],
            "entry_barrier": ["低门槛快启动"],
            "primary_risk": {"exclude": ["技术实现"]},
        },
        topic_templates=[
            TopicTemplate(
                title_zh="最适合独立开发者的产品方向",
                title_en="Best Products for Solo Developers",
                pattern="action",
                description_zh="这些产品一个人就能做、门槛低、风险可控，是独立开发者的理想选择。",
                description_en="Products that one person can build, with low barriers and manageable risks - ideal for indie developers.",
            ),
        ],
    ),

    # -------------------------------------------------------------------------
    # 角色2: 快速启动者 - 周末项目
    # -------------------------------------------------------------------------
    "quick_starter": CuratorRole(
        name="quick_starter",
        display_name_zh="快速启动者",
        display_name_en="Quick Starter",
        filter_rules={
            "entry_barrier": ["低门槛快启动"],
            "mvp_clarity": ["清晰可执行"],
            "solo_feasibility": ["非常适合"],
            "opportunity_validity": ["真实机会"],
        },
        topic_templates=[
            TopicTemplate(
                title_zh="周末就能启动的项目",
                title_en="Weekend Launchable Projects",
                pattern="action",
                description_zh="MVP 清晰、门槛低、一个人能做，适合快速验证想法。",
                description_en="Clear MVP, low barrier, solo-friendly - perfect for quick idea validation.",
            ),
        ],
    ),

    # -------------------------------------------------------------------------
    # 角色3: 机会嗅觉型 - 获客友好
    # -------------------------------------------------------------------------
    "opportunity_hunter": CuratorRole(
        name="opportunity_hunter",
        display_name_zh="机会嗅觉型创业者",
        display_name_en="Opportunity Hunter",
        filter_rules={
            "opportunity_validity": ["真实机会"],
            "demand_type": ["主动搜索型"],
            "entry_barrier": ["低门槛快启动"],
            "solo_feasibility": ["非常适合", "有挑战但可行"],
        },
        topic_templates=[
            TopicTemplate(
                title_zh="获客路径最清晰的机会",
                title_en="Clearest Customer Acquisition Paths",
                pattern="action",
                description_zh="用户会主动搜索解决方案，不需要教育市场，获客成本低。",
                description_en="Users actively search for solutions - no market education needed, low acquisition cost.",
            ),
        ],
    ),

    # -------------------------------------------------------------------------
    # 角色4: 反泡沫角色 - 风险警示
    # -------------------------------------------------------------------------
    "anti_bubble": CuratorRole(
        name="anti_bubble",
        display_name_zh="反泡沫角色",
        display_name_en="Anti-Bubble Analyst",
        filter_rules={
            "opportunity_validity": ["存在风险", "伪机会"],
        },
        topic_templates=[
            TopicTemplate(
                title_zh="看起来性感但风险很高的产品",
                title_en="Sexy-Looking but High-Risk Products",
                pattern="cognitive",
                description_zh="这些产品营销做得好，但仔细分析会发现明显的风险点。",
                description_en="Great marketing, but careful analysis reveals significant risk factors.",
            ),
        ],
    ),

    # -------------------------------------------------------------------------
    # 角色5: 产品驱动爱好者 - 不靠粉丝
    # -------------------------------------------------------------------------
    "product_driven_fan": CuratorRole(
        name="product_driven_fan",
        display_name_zh="产品驱动爱好者",
        display_name_en="Product-Driven Enthusiast",
        filter_rules={
            "success_driver": ["产品驱动"],
            "opportunity_validity": ["真实机会"],
            "solo_feasibility": ["非常适合"],
            "demand_type": ["主动搜索型"],
        },
        topic_templates=[
            TopicTemplate(
                title_zh="不靠粉丝也能成功的产品",
                title_en="Products That Succeed Without Followers",
                pattern="contrast",
                description_zh="产品本身就是最好的营销，用户主动搜索，靠产品力获客。",
                description_en="The product is the marketing - users search for it, growth driven by product quality.",
            ),
        ],
    ),

    # -------------------------------------------------------------------------
    # 角色6: 细分市场猎手 - 精准垂直
    # -------------------------------------------------------------------------
    "niche_hunter": CuratorRole(
        name="niche_hunter",
        display_name_zh="细分市场猎手",
        display_name_en="Niche Hunter",
        filter_rules={
            "positioning_insight": ["精准垂直"],
            "opportunity_validity": ["真实机会"],
            "solo_feasibility": ["非常适合", "有挑战但可行"],
        },
        topic_templates=[
            TopicTemplate(
                title_zh="小众但精准的细分市场",
                title_en="Small but Precise Niche Markets",
                pattern="niche",
                description_zh="这些产品瞄准特定人群，竞争小但需求真实。",
                description_en="Products targeting specific audiences - less competition, real demand.",
            ),
        ],
    ),

    # -------------------------------------------------------------------------
    # 角色7: 体验差异化追求者
    # -------------------------------------------------------------------------
    "ux_differentiator": CuratorRole(
        name="ux_differentiator",
        display_name_zh="体验差异化追求者",
        display_name_en="UX Differentiator",
        filter_rules={
            "differentiation_point": ["体验差异化"],
            "opportunity_validity": ["真实机会"],
            "solo_feasibility": ["非常适合", "有挑战但可行"],
        },
        topic_templates=[
            TopicTemplate(
                title_zh="靠体验打赢竞品的产品",
                title_en="Products Winning Through Better UX",
                pattern="contrast",
                description_zh="功能相似的产品很多，但这些产品靠更好的体验脱颖而出。",
                description_en="Many similar products exist, but these stand out through superior user experience.",
            ),
        ],
    ),

    # -------------------------------------------------------------------------
    # 角色8: 低风险入门者
    # -------------------------------------------------------------------------
    "low_risk_starter": CuratorRole(
        name="low_risk_starter",
        display_name_zh="低风险入门者",
        display_name_en="Low-Risk Starter",
        filter_rules={
            "primary_risk": ["变现转化"],
            "opportunity_validity": ["真实机会"],
            "solo_feasibility": ["非常适合"],
            "entry_barrier": ["低门槛快启动"],
        },
        topic_templates=[
            TopicTemplate(
                title_zh="技术和获客都不难，只需专注变现",
                title_en="Easy Tech & Acquisition, Focus on Monetization",
                pattern="action",
                description_zh="这些产品技术简单、用户好找，主要挑战在于如何变现。",
                description_en="Simple tech, easy user acquisition - main challenge is monetization.",
            ),
        ],
    ),

    # -------------------------------------------------------------------------
    # 角色9: 内容创作者转型
    # -------------------------------------------------------------------------
    "content_to_product": CuratorRole(
        name="content_to_product",
        display_name_zh="内容创作者转型",
        display_name_en="Content Creator Transition",
        filter_rules={
            "success_driver": ["内容驱动"],
            "opportunity_validity": ["真实机会"],
            "solo_feasibility": ["非常适合", "有挑战但可行"],
        },
        topic_templates=[
            TopicTemplate(
                title_zh="内容创作者可以做的产品",
                title_en="Products for Content Creators",
                pattern="niche",
                description_zh="这些产品靠内容获客，适合有内容能力的创作者转型。",
                description_en="Content-driven acquisition - perfect for creators transitioning to products.",
            ),
        ],
    ),

    # -------------------------------------------------------------------------
    # 角色10: 场景具体型
    # -------------------------------------------------------------------------
    "scenario_focused": CuratorRole(
        name="scenario_focused",
        display_name_zh="场景聚焦者",
        display_name_en="Scenario Focused",
        filter_rules={
            "positioning_insight": ["场景具体"],
            "opportunity_validity": ["真实机会"],
            "mvp_clarity": ["清晰可执行"],
        },
        topic_templates=[
            TopicTemplate(
                title_zh="场景定义清晰的产品",
                title_en="Products with Clear Use Cases",
                pattern="niche",
                description_zh="这些产品解决的场景非常具体，用户一看就知道是不是自己需要的。",
                description_en="Very specific use cases - users instantly know if it's for them.",
            ),
        ],
    ),
}


# =============================================================================
# 筛选逻辑
# =============================================================================

def filter_products_by_rules(
    products: List[Dict[str, Any]], 
    filter_rules: Dict[str, Any],
    sort_by_revenue: bool = True,
) -> List[Dict[str, Any]]:
    """根据筛选规则过滤产品"""
    result = []
    for product in products:
        judgments = product.get("mother_theme_judgments", {})
        match = True
        
        for theme_key, rule in filter_rules.items():
            judgment_value = judgments.get(theme_key, {}).get("judgment")
            
            if isinstance(rule, list):
                if judgment_value not in rule:
                    match = False
                    break
            elif isinstance(rule, dict) and "exclude" in rule:
                if judgment_value in rule["exclude"]:
                    match = False
                    break
        
        if match:
            result.append(product)
    
    if sort_by_revenue:
        result = sorted(
            result,
            key=lambda x: x.get("revenue_30d") or 0,
            reverse=True,
        )
    
    return result


def generate_topics(
    products: List[Dict[str, Any]],
    roles: Optional[Dict[str, CuratorRole]] = None,
    min_products: int = 3,
    max_products: int = 15,
) -> List[Dict[str, Any]]:
    """生成所有符合条件的专题（双语）"""
    if roles is None:
        roles = CURATOR_ROLES
    
    topics = []
    
    for role_name, role_config in roles.items():
        filtered = filter_products_by_rules(products, role_config.filter_rules)
        
        if len(filtered) < min_products:
            continue
        
        for template in role_config.topic_templates:
            topic_key = f"{role_name}_{template.pattern}_{len(topics)}"
            top_products = filtered[:max_products]
            
            topics.append({
                "topic_key": topic_key,
                # 双语标题
                "title": template.title_zh,  # 默认中文（兼容旧版）
                "title_zh": template.title_zh,
                "title_en": template.title_en,
                # 双语描述
                "description": template.description_zh,  # 默认中文
                "description_zh": template.description_zh,
                "description_en": template.description_en,
                # 角色信息
                "curator_role": role_name,
                "curator_display_name": role_config.display_name_zh,
                "curator_display_name_zh": role_config.display_name_zh,
                "curator_display_name_en": role_config.display_name_en,
                # 其他
                "generation_pattern": template.pattern,
                "filter_rules": role_config.filter_rules,
                "products": top_products,
                "product_ids": [p.get("id") for p in top_products],
                "product_count": len(filtered),
                "cta_text": template.cta_zh,
                "cta_text_zh": template.cta_zh,
                "cta_text_en": template.cta_en,
            })
    
    return topics


class CuratorAgent:
    """策展 Agent - 基于规则的专题生成"""
    
    def __init__(self, roles: Optional[Dict[str, CuratorRole]] = None):
        self.roles = roles or CURATOR_ROLES
    
    def generate(
        self,
        products: List[Dict[str, Any]],
        min_products: int = 3,
        max_products: int = 15,
    ) -> List[Dict[str, Any]]:
        """生成专题"""
        return generate_topics(
            products=products,
            roles=self.roles,
            min_products=min_products,
            max_products=max_products,
        )
    
    def get_role(self, role_name: str) -> Optional[CuratorRole]:
        """获取指定角色配置"""
        return self.roles.get(role_name)
    
    def list_roles(self) -> List[str]:
        """列出所有角色名称"""
        return list(self.roles.keys())
