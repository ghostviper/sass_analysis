"""
策展 Agent

基于规则的专题生成，从母题判断结果中筛选产品并生成专题。

v3: 支持中英文双语
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


HIGH_FOLLOWER_THRESHOLD = 5000


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
            "mvp_clarity": ["清晰可执行"],
            "primary_risk": {"exclude": ["技术实现"]},
            "success_driver": {"exclude": ["IP/创作者驱动"]},
        },
        topic_templates=[
            TopicTemplate(
                title_zh="最适合独立开发者的产品方向",
                title_en="Best Products for Solo Developers",
                pattern="action",
                description_zh="单人可做、功能边界清晰、维护成本低，且不依赖个人影响力。",
                description_en="Solo-buildable, clear scope, low maintenance, and not reliant on personal influence.",
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
            "primary_risk": {"exclude": ["技术实现"]},
        },
        topic_templates=[
            TopicTemplate(
                title_zh="周末就能启动的项目",
                title_en="Weekend Launchable Projects",
                pattern="action",
                description_zh="核心流程短、功能集中，适合快速验证和最小实现。",
                description_en="Short core flow, focused features, ideal for quick validation and MVP.",
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
                description_zh="用户主动搜索、需求明确，获客路径和付费意愿更清晰。",
                description_en="Active search demand with clearer acquisition and willingness to pay.",
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
                description_zh="看起来很有想象力，但需求或变现存在明显风险。",
                description_en="Looks exciting, but demand or monetization carries obvious risks.",
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
                description_zh="产品体验和功能驱动增长，用户愿意为价值付费。",
                description_en="Product experience and utility drive growth, users pay for clear value.",
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
                description_zh="用户画像明确、场景集中，功能围绕单一任务展开。",
                description_en="Clear audience, focused scenario, and features centered on one job-to-be-done.",
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
                description_zh="功能相似但体验更顺滑，降低学习成本和使用摩擦。",
                description_en="Similar features, smoother UX, lower learning curve and friction.",
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
                description_zh="用户好找、功能不复杂，重点在定价和付费转化。",
                description_en="Easy to build and reach users; pricing and conversion are the key.",
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
                description_zh="内容带来流量，产品承接转化，适合内容能力强的人。",
                description_en="Content brings traffic, products convert it; ideal for strong creators.",
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
                description_zh="使用场景具体、功能边界清晰，用户判断成本低。",
                description_en="Specific use case, clear scope, and low decision friction for users.",
            ),
        ],
    ),
}


# =============================================================================
# 筛选逻辑
# =============================================================================

def _normalize_judgments(product: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """根据结构化信号校正母题判断（避免高粉丝被误判为非IP驱动）"""
    judgments = product.get("mother_theme_judgments", {})
    if not judgments:
        return {}

    normalized = {k: dict(v) for k, v in judgments.items() if isinstance(v, dict)}
    followers = product.get("founder_followers")
    driver = normalized.get("success_driver", {})
    driver_value = driver.get("judgment")

    if isinstance(followers, int) and followers >= HIGH_FOLLOWER_THRESHOLD:
        if driver_value and driver_value != "IP/创作者驱动":
            driver["judgment"] = "IP/创作者驱动"
            driver.setdefault("confidence", "中")
            driver["_normalized"] = True
            normalized["success_driver"] = driver

    return normalized


def _select_products(
    filtered: List[Dict[str, Any]],
    used_products: set,
    max_products: int,
    allow_reuse_rate: float,
) -> List[Dict[str, Any]]:
    """在减少主题重叠的前提下选择产品"""
    if not filtered:
        return []

    total_needed = min(max_products, len(filtered))
    unused = [p for p in filtered if p.get("id") not in used_products]
    reusable = [p for p in filtered if p.get("id") in used_products]

    min_unused = max(1, int(total_needed * (1 - allow_reuse_rate)))
    selected = unused[:total_needed]

    if len(selected) < total_needed and reusable:
        selected.extend(reusable[:total_needed - len(selected)])

    if len(unused) < min_unused:
        # 如果新产品不足，仍允许复用补齐，但会降低多样性
        return selected

    return selected


def filter_products_by_rules(
    products: List[Dict[str, Any]], 
    filter_rules: Dict[str, Any],
    sort_by_revenue: bool = True,
) -> List[Dict[str, Any]]:
    """根据筛选规则过滤产品"""
    result = []
    for product in products:
        judgments = _normalize_judgments(product)
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
    allow_reuse_rate: float = 0.3,
) -> List[Dict[str, Any]]:
    """生成所有符合条件的专题（双语）"""
    if roles is None:
        roles = CURATOR_ROLES
    
    topics = []
    used_products = set()
    
    for role_index, (role_name, role_config) in enumerate(roles.items()):
        filtered = filter_products_by_rules(products, role_config.filter_rules)
        
        if len(filtered) < min_products:
            continue
        
        for template_index, template in enumerate(role_config.topic_templates):
            selected = _select_products(
                filtered=filtered,
                used_products=used_products,
                max_products=max_products,
                allow_reuse_rate=allow_reuse_rate,
            )

            if len(selected) < min_products:
                continue

            topic_key = f"{role_name}_{template.pattern}_{role_index}"
            if template_index > 0:
                topic_key = f"{topic_key}_{template_index}"
            top_products = selected

            for p in top_products:
                pid = p.get("id")
                if pid:
                    used_products.add(pid)
            
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
        allow_reuse_rate: float = 0.3,
    ) -> List[Dict[str, Any]]:
        """生成专题"""
        return generate_topics(
            products=products,
            roles=self.roles,
            min_products=min_products,
            max_products=max_products,
            allow_reuse_rate=allow_reuse_rate,
        )
    
    def get_role(self, role_name: str) -> Optional[CuratorRole]:
        """获取指定角色配置"""
        return self.roles.get(role_name)
    
    def list_roles(self) -> List[str]:
        """列出所有角色名称"""
        return list(self.roles.keys())
