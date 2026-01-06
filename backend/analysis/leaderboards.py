"""
Leaderboards - 多视角榜单模块

提供多个视角的产品榜单，让用户根据自己的需求选择关注的榜单。
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from sqlalchemy import select, desc, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Startup, ProductSelectionAnalysis


@dataclass
class LeaderboardConfig:
    """榜单配置"""
    id: str
    name: str
    name_en: str
    description: str
    description_en: str
    icon: str  # emoji or icon name
    sort_by: str
    sort_order: str  # asc or desc
    filters: Dict[str, Any]


# 榜单定义
LEADERBOARDS: Dict[str, LeaderboardConfig] = {
    "revenue_verified": LeaderboardConfig(
        id="revenue_verified",
        name="收入验证榜",
        name_en="Revenue Verified",
        description="按收入排序，证明市场需求存在",
        description_en="Sorted by revenue, proving market demand exists",
        icon="📊",
        sort_by="revenue_30d",
        sort_order="desc",
        filters={"revenue_30d_gt": 0}
    ),
    "quick_start": LeaderboardConfig(
        id="quick_start",
        name="快速启动榜",
        name_en="Quick Start",
        description="低复杂度 + 低启动成本，适合快速验证",
        description_en="Low complexity + low startup cost, ideal for quick validation",
        icon="🚀",
        sort_by="revenue_30d",
        sort_order="desc",
        filters={
            "tech_complexity_level": "low",
            "startup_cost_level": "low"
        }
    ),
    "small_beautiful": LeaderboardConfig(
        id="small_beautiful",
        name="小而美榜",
        name_en="Small & Beautiful",
        description="功能简单 + 稳定收入，专注单一价值",
        description_en="Simple features + stable revenue, focused on single value",
        icon="💎",
        sort_by="revenue_30d",
        sort_order="desc",
        filters={
            "feature_complexity": "simple",
            "revenue_tier_in": ["small", "medium", "large"]
        }
    ),
    "emerging": LeaderboardConfig(
        id="emerging",
        name="新兴机会榜",
        name_en="Emerging Opportunities",
        description="成立<12月 + 有收入，早期验证成功",
        description_en="Founded <12 months + has revenue, early validation success",
        icon="🔥",
        sort_by="revenue_30d",
        sort_order="desc",
        filters={
            "product_stage": "early",
            "revenue_30d_gt": 500
        }
    ),
    "low_risk": LeaderboardConfig(
        id="low_risk",
        name="低风险榜",
        name_en="Low Risk",
        description="不依赖AI + 无合规要求 + 低维护成本",
        description_en="No AI dependency + no compliance + low maintenance",
        icon="🛡️",
        sort_by="revenue_30d",
        sort_order="desc",
        filters={
            "ai_dependency_level": "none",
            "has_compliance_requirement": False,
            "maintenance_cost_level": "low"
        }
    ),
    "product_driven": LeaderboardConfig(
        id="product_driven",
        name="产品驱动榜",
        name_en="Product Driven",
        description="不依赖创始人IP，产品本身创造价值",
        description_en="Not relying on founder IP, product creates value itself",
        icon="⚡",
        sort_by="revenue_30d",
        sort_order="desc",
        filters={
            "growth_driver": "product_driven",
            "revenue_30d_gt": 1000
        }
    ),
    "b2d_tools": LeaderboardConfig(
        id="b2d_tools",
        name="开发者工具榜",
        name_en="Developer Tools",
        description="面向开发者的工具和服务",
        description_en="Tools and services for developers",
        icon="🛠️",
        sort_by="revenue_30d",
        sort_order="desc",
        filters={
            "target_customer": "b2d"
        }
    ),
    "no_ai": LeaderboardConfig(
        id="no_ai",
        name="非AI产品榜",
        name_en="Non-AI Products",
        description="不依赖AI的传统SaaS产品",
        description_en="Traditional SaaS products without AI dependency",
        icon="🔧",
        sort_by="revenue_30d",
        sort_order="desc",
        filters={
            "ai_dependency_level": "none",
            "revenue_30d_gt": 500
        }
    ),
}


class LeaderboardService:
    """榜单服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def get_all_leaderboards() -> List[Dict[str, Any]]:
        """获取所有榜单配置"""
        return [
            {
                "id": lb.id,
                "name": lb.name,
                "name_en": lb.name_en,
                "description": lb.description,
                "description_en": lb.description_en,
                "icon": lb.icon,
            }
            for lb in LEADERBOARDS.values()
        ]

    @staticmethod
    def get_leaderboard_config(leaderboard_id: str) -> Optional[LeaderboardConfig]:
        """获取单个榜单配置"""
        return LEADERBOARDS.get(leaderboard_id)

    async def get_leaderboard_products(
        self,
        leaderboard_id: str,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        获取榜单产品列表

        Args:
            leaderboard_id: 榜单ID
            page: 页码
            page_size: 每页数量

        Returns:
            包含产品列表和分页信息的字典
        """
        config = LEADERBOARDS.get(leaderboard_id)
        if not config:
            return {
                "error": f"Unknown leaderboard: {leaderboard_id}",
                "products": [],
                "total": 0
            }

        # 构建查询
        query = (
            select(Startup, ProductSelectionAnalysis)
            .outerjoin(
                ProductSelectionAnalysis,
                Startup.id == ProductSelectionAnalysis.startup_id
            )
        )

        # 应用筛选条件
        conditions = []
        filters = config.filters

        # 收入筛选
        if "revenue_30d_gt" in filters:
            conditions.append(Startup.revenue_30d > filters["revenue_30d_gt"])

        # 技术复杂度筛选
        if "tech_complexity_level" in filters:
            conditions.append(
                ProductSelectionAnalysis.tech_complexity_level == filters["tech_complexity_level"]
            )

        # 启动成本筛选
        if "startup_cost_level" in filters:
            conditions.append(
                ProductSelectionAnalysis.startup_cost_level == filters["startup_cost_level"]
            )

        # 功能复杂度筛选
        if "feature_complexity" in filters:
            conditions.append(
                ProductSelectionAnalysis.feature_complexity == filters["feature_complexity"]
            )

        # 收入层级筛选（多选）
        if "revenue_tier_in" in filters:
            conditions.append(
                ProductSelectionAnalysis.revenue_tier.in_(filters["revenue_tier_in"])
            )

        # 产品阶段筛选
        if "product_stage" in filters:
            conditions.append(
                ProductSelectionAnalysis.product_stage == filters["product_stage"]
            )

        # AI依赖筛选
        if "ai_dependency_level" in filters:
            conditions.append(
                ProductSelectionAnalysis.ai_dependency_level == filters["ai_dependency_level"]
            )

        # 合规要求筛选
        if "has_compliance_requirement" in filters:
            conditions.append(
                ProductSelectionAnalysis.has_compliance_requirement == filters["has_compliance_requirement"]
            )

        # 维护成本筛选
        if "maintenance_cost_level" in filters:
            conditions.append(
                ProductSelectionAnalysis.maintenance_cost_level == filters["maintenance_cost_level"]
            )

        # 增长驱动筛选
        if "growth_driver" in filters:
            conditions.append(
                ProductSelectionAnalysis.growth_driver == filters["growth_driver"]
            )

        # 目标客户筛选
        if "target_customer" in filters:
            conditions.append(
                ProductSelectionAnalysis.target_customer == filters["target_customer"]
            )

        if conditions:
            query = query.where(and_(*conditions))

        # 排序
        sort_column = getattr(Startup, config.sort_by, Startup.revenue_30d)
        if config.sort_order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(sort_column)

        # 计算总数
        count_query = select(Startup.id).outerjoin(
            ProductSelectionAnalysis,
            Startup.id == ProductSelectionAnalysis.startup_id
        )
        if conditions:
            count_query = count_query.where(and_(*conditions))

        count_result = await self.db.execute(count_query)
        total = len(count_result.all())

        # 分页
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        # 执行查询
        result = await self.db.execute(query)
        rows = result.all()

        # 格式化结果
        products = []
        for startup, analysis in rows:
            product_data = startup.to_dict()
            if analysis:
                product_data["analysis"] = analysis.to_dict()
                product_data["tags"] = analysis.to_tags_dict()
            else:
                product_data["analysis"] = None
                product_data["tags"] = None
            products.append(product_data)

        return {
            "leaderboard": {
                "id": config.id,
                "name": config.name,
                "name_en": config.name_en,
                "description": config.description,
                "description_en": config.description_en,
                "icon": config.icon,
            },
            "products": products,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": (total + page_size - 1) // page_size
            }
        }

    async def get_leaderboard_stats(self) -> Dict[str, Any]:
        """获取所有榜单的统计信息"""
        stats = {}

        for leaderboard_id, config in LEADERBOARDS.items():
            # 构建计数查询
            query = select(Startup.id).outerjoin(
                ProductSelectionAnalysis,
                Startup.id == ProductSelectionAnalysis.startup_id
            )

            conditions = []
            filters = config.filters

            if "revenue_30d_gt" in filters:
                conditions.append(Startup.revenue_30d > filters["revenue_30d_gt"])
            if "tech_complexity_level" in filters:
                conditions.append(
                    ProductSelectionAnalysis.tech_complexity_level == filters["tech_complexity_level"]
                )
            if "startup_cost_level" in filters:
                conditions.append(
                    ProductSelectionAnalysis.startup_cost_level == filters["startup_cost_level"]
                )
            if "feature_complexity" in filters:
                conditions.append(
                    ProductSelectionAnalysis.feature_complexity == filters["feature_complexity"]
                )
            if "revenue_tier_in" in filters:
                conditions.append(
                    ProductSelectionAnalysis.revenue_tier.in_(filters["revenue_tier_in"])
                )
            if "product_stage" in filters:
                conditions.append(
                    ProductSelectionAnalysis.product_stage == filters["product_stage"]
                )
            if "ai_dependency_level" in filters:
                conditions.append(
                    ProductSelectionAnalysis.ai_dependency_level == filters["ai_dependency_level"]
                )
            if "has_compliance_requirement" in filters:
                conditions.append(
                    ProductSelectionAnalysis.has_compliance_requirement == filters["has_compliance_requirement"]
                )
            if "maintenance_cost_level" in filters:
                conditions.append(
                    ProductSelectionAnalysis.maintenance_cost_level == filters["maintenance_cost_level"]
                )
            if "growth_driver" in filters:
                conditions.append(
                    ProductSelectionAnalysis.growth_driver == filters["growth_driver"]
                )
            if "target_customer" in filters:
                conditions.append(
                    ProductSelectionAnalysis.target_customer == filters["target_customer"]
                )

            if conditions:
                query = query.where(and_(*conditions))

            result = await self.db.execute(query)
            count = len(result.all())

            stats[leaderboard_id] = {
                "id": config.id,
                "name": config.name,
                "name_en": config.name_en,
                "icon": config.icon,
                "count": count
            }

        return stats
