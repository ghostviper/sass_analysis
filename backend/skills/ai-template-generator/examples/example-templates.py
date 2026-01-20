"""
Example Generated Templates

These are examples of AI-generated templates with annotations explaining design choices.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List

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
    curation_type: str
    filter_rules: Dict[str, Any]
    conflict_dimensions: List[str]
    min_products: int = 3
    max_products: int = 8
    priority: int = 5


# Example 1: Contrast Template
# 反差型模板 - 打破"需要大量粉丝才能赚钱"的常规认知
low_followers_high_revenue = CurationTemplate(
    key="low_followers_high_revenue",
    title_zh="粉丝不多，也能做到 $10k+ MRR",
    title_en="Few followers, still $10k+ MRR",
    description_zh="筛选粉丝 <1000 且产品驱动的收入型产品，证明产品力能直接变现",
    description_en="Products with <1k followers and product-driven revenue, proving product strength converts.",
    insight_zh="先把转化跑通，再谈影响力",
    insight_en="Prove conversion first, then grow influence.",
    tag_zh="反常识",
    tag_en="Counter-intuitive",
    tag_color="amber",  # 琥珀色表示反直觉、惊喜
    curation_type="contrast",
    filter_rules={
        "startup": {
            "founder_followers": {"max": 1000},  # 低粉丝
            "revenue_30d": {"min": 10000}  # 高收入
        },
        "mother_theme": {
            "success_driver": ["产品驱动"]  # 产品驱动而非IP驱动
        }
    },
    conflict_dimensions=["founder_followers", "revenue_30d", "success_driver"],  # 三个维度产生反差
    priority=10,  # 最高优先级：核心反差主题
    min_products=3,
    max_products=8
)



# Example 2: Action Template
# 行动型模板 - 降低启动门槛，提供可执行路径
weekend_launchable = CurationTemplate(
    key="weekend_launchable",
    title_zh="周末可启动的项目",
    title_en="Projects you can start this weekend",
    description_zh="低门槛 + MVP清晰 + 低成本/简单功能，适合快速试水",
    description_en="Low barrier, clear MVP, low cost/simple features for fast starts.",
    insight_zh="先做出来，再优化",
    insight_en="Ship first, refine later.",
    tag_zh="快速启动",
    tag_en="Quick Start",
    tag_color="green",  # 绿色表示可行、积极
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
    priority=9,  # 高优先级：最实用的行动指南
    min_products=5,
    max_products=10
)


# Example 3: Cognitive Template
# 认知型模板 - 提供定位策略的新视角
vertical_niche_success = CurationTemplate(
    key="vertical_niche_success",
    title_zh="服务小人群，也能赚到钱",
    title_en="Serve a small niche, still earn well",
    description_zh="精准垂直 + 真实机会，专注特定人群更容易占位",
    description_en="Vertical focus + real opportunity; easier to own a niche.",
    insight_zh="小池塘更容易称王",
    insight_en="Own a small pond.",
    tag_zh="精准垂直",
    tag_en="Vertical Focus",
    tag_color="teal",  # 青色表示专业、细分
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
    priority=7,  # 中高优先级
    min_products=4,
    max_products=8
)



# Example 4: Niche Template
# 利基型模板 - 针对特定人群（开发者）
dev_tools_gems = CurationTemplate(
    key="dev_tools_gems",
    title_zh="做自己也愿意付费的开发者工具",
    title_en="Dev tools you'd pay for yourself",
    description_zh="B2D + 开发者品类，懂痛点的人做给同类用",
    description_en="B2D and dev categories built by insiders who feel the pain.",
    insight_zh="先当自己的第一个用户",
    insight_en="Be your first user.",
    tag_zh="开发者向",
    tag_en="For Devs",
    tag_color="indigo",  # 靛蓝色表示技术、开发者
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
    priority=4,  # 低优先级：利基市场
    min_products=3,
    max_products=6
)


# 注释说明：
# 1. 反差型模板优先级最高(8-10)，因为最能吸引注意力
# 2. 行动型模板优先级高(7-9)，因为最实用
# 3. 认知型模板优先级中等(6-8)，提供价值但不紧急
# 4. 利基型模板优先级较低(3-5)，服务特定小众

# 颜色选择原则：
# - amber: 反直觉、惊喜
# - green: 可行、积极、快速
# - teal: 专业、细分、垂直
# - indigo: 技术、开发者
# - purple: 高级、复杂
# - slate: 稳定、传统
# - orange: 创新、差异化
