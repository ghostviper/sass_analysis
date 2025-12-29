"""
Category Analyzer - 赛道/领域分析
"""

import logging
import statistics
from datetime import date
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, asdict
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Startup, CategoryAnalysis

logger = logging.getLogger(__name__)


@dataclass
class CategoryMetrics:
    """赛道分析指标"""
    category: str
    total_projects: int
    total_revenue: float
    avg_revenue: float
    median_revenue: float
    revenue_per_project: float
    top10_revenue_share: float
    top50_revenue_share: float
    revenue_std_dev: float
    gini_coefficient: float
    market_type: str  # red_ocean, blue_ocean, weak_demand, moderate
    market_type_reason: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class CategoryAnalyzer:
    """赛道/领域分析器"""

    # 市场分类阈值 (基于产品数据集动态计算)
    # AI分类有较多产品，其他分类相对较少，阈值需要区分
    RED_OCEAN_PROJECT_THRESHOLD = 20  # 有收入项目数超过此值（约前5%分类）
    RED_OCEAN_REVENUE_PER_PROJECT_THRESHOLD = 500  # 单项目收入低于此值（中位数$264）
    BLUE_OCEAN_MIN_REVENUE_PER_PROJECT = 2000  # 蓝海单项目收入门槛（约前25%产品）
    WEAK_DEMAND_MAX_TOTAL_REVENUE = 5000  # 弱需求市场总收入上限

    # 收入集中度阈值
    HIGH_CONCENTRATION_TOP10_SHARE = 70  # TOP10占比超过70%算集中

    def __init__(self, db: AsyncSession):
        self.db = db

    async def analyze_category(self, category: str) -> CategoryMetrics:
        """
        分析单个赛道

        Args:
            category: 赛道/领域名称

        Returns:
            CategoryMetrics对象
        """
        # 获取该赛道所有有收入数据的产品
        result = await self.db.execute(
            select(Startup)
            .where(Startup.category == category)
            .where(Startup.revenue_30d.isnot(None))
            .where(Startup.revenue_30d > 0)
            .order_by(desc(Startup.revenue_30d))
        )
        startups = result.scalars().all()

        if not startups:
            return CategoryMetrics(
                category=category,
                total_projects=0,
                total_revenue=0,
                avg_revenue=0,
                median_revenue=0,
                revenue_per_project=0,
                top10_revenue_share=0,
                top50_revenue_share=0,
                revenue_std_dev=0,
                gini_coefficient=0,
                market_type="weak_demand",
                market_type_reason="该赛道没有有效收入数据的产品"
            )

        # 收集收入数据
        revenues = [s.revenue_30d for s in startups]
        total_projects = len(revenues)
        total_revenue = sum(revenues)

        # 基础统计
        avg_revenue = statistics.mean(revenues)
        median_revenue = statistics.median(revenues)
        revenue_per_project = total_revenue / total_projects

        # 计算TOP收入占比
        top10_count = max(1, int(total_projects * 0.1))
        top50_count = max(1, int(total_projects * 0.5))

        top10_revenue = sum(revenues[:top10_count])
        top50_revenue = sum(revenues[:top50_count])

        top10_share = (top10_revenue / total_revenue * 100) if total_revenue > 0 else 0
        top50_share = (top50_revenue / total_revenue * 100) if total_revenue > 0 else 0

        # 标准差
        std_dev = statistics.stdev(revenues) if len(revenues) > 1 else 0

        # 计算基尼系数
        gini = self._calculate_gini(revenues)

        # 判断市场类型
        market_type, reason = self._classify_market_type(
            total_projects=total_projects,
            total_revenue=total_revenue,
            revenue_per_project=revenue_per_project,
            median_revenue=median_revenue,
            top10_share=top10_share
        )

        return CategoryMetrics(
            category=category,
            total_projects=total_projects,
            total_revenue=round(total_revenue, 2),
            avg_revenue=round(avg_revenue, 2),
            median_revenue=round(median_revenue, 2),
            revenue_per_project=round(revenue_per_project, 2),
            top10_revenue_share=round(top10_share, 2),
            top50_revenue_share=round(top50_share, 2),
            revenue_std_dev=round(std_dev, 2),
            gini_coefficient=round(gini, 4),
            market_type=market_type,
            market_type_reason=reason
        )

    def _calculate_gini(self, values: List[float]) -> float:
        """计算基尼系数（衡量收入分布不均匀程度）"""
        if not values or len(values) < 2:
            return 0

        sorted_values = sorted(values)
        n = len(sorted_values)
        cumulative = 0
        total = sum(sorted_values)

        if total == 0:
            return 0

        for i, value in enumerate(sorted_values, 1):
            cumulative += (n + 1 - i) * value

        gini = (n + 1 - 2 * cumulative / total) / n
        return max(0, min(1, gini))  # 确保在0-1范围内

    def _classify_market_type(
        self,
        total_projects: int,
        total_revenue: float,
        revenue_per_project: float,
        median_revenue: float,
        top10_share: float
    ) -> tuple:
        """
        判断市场类型

        核心逻辑：
        - 蓝海：项目少但赚钱（适合进入）
        - 红海：项目多且内卷（竞争激烈）
        - 集中：头部吃掉大部分（新手难进入）
        - 弱需求：整体没什么收入（市场可能不存在）
        - 适中：有机会但需努力

        Returns:
            (market_type, reason) 元组
        """
        # 弱需求市场：总收入很低，说明这个分类整体没什么人赚钱
        if total_revenue < self.WEAK_DEMAND_MAX_TOTAL_REVENUE:
            return (
                "weak_demand",
                f"市场总收入低(${total_revenue:.0f})，需求可能不足或分类过于细分"
            )

        # 收入高度集中 - 头部效应明显，新进入者难获得份额
        if top10_share > self.HIGH_CONCENTRATION_TOP10_SHARE:
            return (
                "concentrated",
                f"头部集中(TOP10占{top10_share:.0f}%)，少数产品占据大部分收入"
            )

        # 红海市场：项目多、中位数收入低（说明大部分产品赚不到钱）
        if (total_projects > self.RED_OCEAN_PROJECT_THRESHOLD and
                median_revenue < self.RED_OCEAN_REVENUE_PER_PROJECT_THRESHOLD):
            return (
                "red_ocean",
                f"竞争激烈({total_projects}个产品)，中位数收入仅${median_revenue:.0f}"
            )

        # 蓝海市场：项目少但中位数收入不错（说明进入者都能赚钱）
        if (total_projects <= self.RED_OCEAN_PROJECT_THRESHOLD and
                median_revenue > self.BLUE_OCEAN_MIN_REVENUE_PER_PROJECT):
            return (
                "blue_ocean",
                f"竞争较少({total_projects}个产品)，中位数收入${median_revenue:.0f}，多数产品盈利"
            )

        # 新兴机会：项目少、有一定收入但还未形成格局
        if total_projects <= 10 and total_revenue > self.WEAK_DEMAND_MAX_TOTAL_REVENUE:
            return (
                "emerging",
                f"新兴市场({total_projects}个产品)，总收入${total_revenue:.0f}，可能是早期机会"
            )

        # 适中市场：有一定竞争，但也有机会
        return (
            "moderate",
            f"竞争适中({total_projects}个产品，中位数${median_revenue:.0f})，需差异化竞争"
        )

    async def analyze_all_categories(self) -> List[CategoryMetrics]:
        """分析所有赛道"""
        # 获取所有不重复的分类
        result = await self.db.execute(
            select(Startup.category)
            .where(Startup.category.isnot(None))
            .distinct()
        )
        categories = [row[0] for row in result.all()]

        analyses = []
        for category in categories:
            analysis = await self.analyze_category(category)
            analyses.append(analysis)

        # 按市场机会排序（蓝海和新兴优先）
        type_order = {"blue_ocean": 0, "emerging": 1, "moderate": 2, "concentrated": 3, "red_ocean": 4, "weak_demand": 5}
        analyses.sort(key=lambda x: (type_order.get(x.market_type, 6), -x.median_revenue))

        return analyses

    async def find_template_products(self, category: str) -> List[Dict]:
        """
        查找模板化产品（名称/定位相似的产品）

        Args:
            category: 赛道名称

        Returns:
            模板产品分组列表
        """
        result = await self.db.execute(
            select(Startup)
            .where(Startup.category == category)
        )
        startups = result.scalars().all()

        if not startups:
            return []

        # 按名称关键词分组
        keyword_patterns = [
            "ai", "hub", "tool", "kit", "app", "pro", "labs", "studio",
            "maker", "builder", "generator", "manager", "tracker"
        ]

        clusters = {}
        for startup in startups:
            name_lower = startup.name.lower()
            for pattern in keyword_patterns:
                if pattern in name_lower:
                    if pattern not in clusters:
                        clusters[pattern] = []
                    clusters[pattern].append({
                        "name": startup.name,
                        "slug": startup.slug,
                        "revenue_30d": startup.revenue_30d,
                        "description": startup.description[:100] if startup.description else None
                    })
                    break

        # 只返回有3个及以上产品的分组
        result_clusters = []
        for pattern, products in clusters.items():
            if len(products) >= 3:
                result_clusters.append({
                    "pattern": pattern,
                    "count": len(products),
                    "products": sorted(products, key=lambda x: x.get("revenue_30d") or 0, reverse=True)[:5]
                })

        return result_clusters

    async def save_analysis(self, metrics: CategoryMetrics) -> CategoryAnalysis:
        """保存分析结果到数据库"""
        # 检查是否已有今天的分析
        today = date.today()
        result = await self.db.execute(
            select(CategoryAnalysis)
            .where(CategoryAnalysis.category == metrics.category)
            .where(CategoryAnalysis.analysis_date == today)
        )
        existing = result.scalar_one_or_none()

        if existing:
            # 更新现有记录
            for key, value in metrics.to_dict().items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
            analysis = existing
        else:
            # 创建新记录
            analysis = CategoryAnalysis(
                category=metrics.category,
                analysis_date=today,
                total_projects=metrics.total_projects,
                total_revenue=metrics.total_revenue,
                avg_revenue=metrics.avg_revenue,
                median_revenue=metrics.median_revenue,
                revenue_per_project=metrics.revenue_per_project,
                top10_revenue_share=metrics.top10_revenue_share,
                top50_revenue_share=metrics.top50_revenue_share,
                revenue_std_dev=metrics.revenue_std_dev,
                gini_coefficient=metrics.gini_coefficient,
                market_type=metrics.market_type,
                market_type_reason=metrics.market_type_reason,
            )
            self.db.add(analysis)

        await self.db.commit()
        await self.db.refresh(analysis)
        return analysis

    async def get_blue_ocean_categories(self, limit: int = 10) -> List[CategoryMetrics]:
        """获取蓝海赛道列表"""
        all_analyses = await self.analyze_all_categories()
        blue_oceans = [a for a in all_analyses if a.market_type == "blue_ocean"]
        return blue_oceans[:limit]

    async def compare_categories(self, category_names: List[str]) -> List[CategoryMetrics]:
        """对比多个赛道"""
        analyses = []
        for name in category_names:
            analysis = await self.analyze_category(name)
            analyses.append(analysis)
        return analyses
