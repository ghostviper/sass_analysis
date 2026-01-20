"""
Comprehensive Analyzer - 产品综合分析
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import (
    Startup,
    Founder,
    ProductSelectionAnalysis,
    LandingPageAnalysis,
    CategoryAnalysis,
    ComprehensiveAnalysis
)
from .category_analyzer import CategoryAnalyzer
from .product_selector import ProductSelector

logger = logging.getLogger(__name__)


class ComprehensiveAnalyzer:
    """综合分析器 - 整合所有分析维度生成综合评估"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.category_analyzer = CategoryAnalyzer(db)
        self.product_selector = ProductSelector(db)

    async def analyze_startup(self, startup_id: int) -> Optional[ComprehensiveAnalysis]:
        """
        生成产品综合分析报告

        整合:
        - 选品分析结果
        - Landing Page AI分析结果
        - 赛道分析结果

        Args:
            startup_id: 产品ID

        Returns:
            ComprehensiveAnalysis模型实例
        """
        # 获取产品基本信息
        startup_result = await self.db.execute(
            select(Startup).where(Startup.id == startup_id)
        )
        startup = startup_result.scalar_one_or_none()

        if not startup:
            logger.error(f"Startup {startup_id} not found")
            return None

        # 获取选品分析结果
        selection_result = await self.db.execute(
            select(ProductSelectionAnalysis)
            .where(ProductSelectionAnalysis.startup_id == startup_id)
        )
        selection_analysis = selection_result.scalar_one_or_none()

        # 如果没有选品分析，先生成
        if not selection_analysis:
            score = await self.product_selector.analyze_product(startup)
            selection_analysis = await self.product_selector.save_analysis(score)

        # 获取Landing Page分析结果
        landing_result = await self.db.execute(
            select(LandingPageAnalysis)
            .where(LandingPageAnalysis.startup_id == startup_id)
        )
        landing_analysis = landing_result.scalar_one_or_none()

        # 获取赛道分析结果
        category_metrics = None
        if startup.category:
            category_metrics = await self.category_analyzer.analyze_category(startup.category)

        # 计算综合评分
        scores = self._calculate_comprehensive_scores(
            startup=startup,
            selection_analysis=selection_analysis,
            landing_analysis=landing_analysis,
            category_metrics=category_metrics
        )

        # 生成分析摘要
        summary = self._generate_summary(
            startup=startup,
            scores=scores,
            selection_analysis=selection_analysis,
            landing_analysis=landing_analysis,
            category_metrics=category_metrics
        )

        # 保存综合分析结果
        analysis = await self._save_analysis(startup_id, scores, summary)

        return analysis

    def _calculate_comprehensive_scores(
        self,
        startup: Startup,
        selection_analysis: Optional[ProductSelectionAnalysis],
        landing_analysis: Optional[LandingPageAnalysis],
        category_metrics
    ) -> Dict[str, float]:
        """计算综合评分"""
        scores = {
            "maturity_score": 5.0,
            "positioning_clarity": 5.0,
            "pain_point_sharpness": 5.0,
            "pricing_clarity": 5.0,
            "conversion_friendliness": 5.0,
            "individual_replicability": 5.0,
            "overall_recommendation": 5.0,
        }

        weights = []

        # 从Landing Page分析获取评分
        if landing_analysis:
            scores["maturity_score"] = landing_analysis.product_maturity_score or 5.0
            scores["positioning_clarity"] = landing_analysis.positioning_clarity_score or 5.0
            scores["pain_point_sharpness"] = landing_analysis.pain_point_sharpness or 5.0
            scores["pricing_clarity"] = landing_analysis.pricing_clarity_score or 5.0
            scores["conversion_friendliness"] = landing_analysis.conversion_friendliness_score or 5.0
            scores["individual_replicability"] = landing_analysis.individual_replicability_score or 5.0
            weights.append(0.5)  # Landing Page分析权重

        # 从选品分析获取评分
        if selection_analysis:
            # 个人可复制性：结合选品分析
            selection_replicability = selection_analysis.individual_dev_suitability or 5.0

            # 如果有Landing Page分析，取平均；否则使用选品分析
            if landing_analysis:
                scores["individual_replicability"] = (
                    scores["individual_replicability"] * 0.6 +
                    selection_replicability * 0.4
                )
            else:
                scores["individual_replicability"] = selection_replicability

            # 技术复杂度影响成熟度评分
            if selection_analysis.tech_complexity_level == "low":
                scores["maturity_score"] = min(10, scores["maturity_score"] + 1)

            weights.append(0.3)  # 选品分析权重

        # 赛道分析影响
        if category_metrics:
            # 蓝海市场加分
            if category_metrics.market_type == "blue_ocean":
                scores["overall_recommendation"] = min(10, scores.get("overall_recommendation", 5) + 1.5)
            elif category_metrics.market_type == "red_ocean":
                scores["overall_recommendation"] = max(0, scores.get("overall_recommendation", 5) - 1)

            weights.append(0.2)

        # 计算综合推荐指数
        if weights:
            # 基于各维度评分计算
            dimension_scores = [
                scores["maturity_score"],
                scores["positioning_clarity"],
                scores["pain_point_sharpness"],
                scores["pricing_clarity"],
                scores["conversion_friendliness"],
                scores["individual_replicability"],
            ]
            scores["overall_recommendation"] = sum(dimension_scores) / len(dimension_scores)

            # 收入加成
            if startup.revenue_30d:
                if startup.revenue_30d > 10000:
                    scores["overall_recommendation"] = min(10, scores["overall_recommendation"] + 0.5)
                elif startup.revenue_30d > 5000:
                    scores["overall_recommendation"] = min(10, scores["overall_recommendation"] + 0.3)

        return scores

    def _generate_summary(
        self,
        startup: Startup,
        scores: Dict[str, float],
        selection_analysis: Optional[ProductSelectionAnalysis],
        landing_analysis: Optional[LandingPageAnalysis],
        category_metrics
    ) -> Dict[str, Any]:
        """生成分析摘要"""
        # 数据可用性标记
        data_sources = {
            "has_selection_analysis": selection_analysis is not None,
            "has_landing_analysis": landing_analysis is not None,
            "has_category_analysis": category_metrics is not None,
            "has_revenue_data": startup.revenue_30d is not None and startup.revenue_30d > 0,
            "has_follower_data": selection_analysis.has_follower_data if selection_analysis else False,
        }

        # 计算数据完整度
        data_completeness = sum(data_sources.values()) / len(data_sources) * 100

        summary = {
            "product_name": startup.name,
            "category": startup.category,
            "revenue_30d": startup.revenue_30d,
            "analysis_date": datetime.utcnow().isoformat(),

            # 数据可用性
            "data_sources": data_sources,
            "data_completeness": round(data_completeness, 1),

            # 评分摘要
            "scores": scores,

            # 优势
            "strengths": [],

            # 风险/劣势
            "risks": [],

            # 建议
            "recommendations": [],

            # 市场定位
            "market_position": None,
        }

        # 数据不完整提示
        if not landing_analysis:
            summary["risks"].append("缺少Landing Page分析，部分评分为默认值")
        if data_sources.get("has_follower_data") is False:
            summary["risks"].append("缺少粉丝数据，IP依赖度为估算值")

        # 分析优势
        if scores["individual_replicability"] >= 7:
            summary["strengths"].append("适合个人开发者复制")

        if scores["positioning_clarity"] >= 7:
            summary["strengths"].append("产品定位清晰")

        if scores["pain_point_sharpness"] >= 7:
            summary["strengths"].append("痛点描述锋利")

        if selection_analysis and selection_analysis.is_product_driven:
            summary["strengths"].append("产品驱动型（非IP依赖）")

        if selection_analysis and selection_analysis.is_small_and_beautiful:
            summary["strengths"].append("小而美产品特征")

        if landing_analysis and landing_analysis.has_free_tier:
            summary["strengths"].append("有免费层级，便于获客")

        # 分析风险
        if selection_analysis:
            if selection_analysis.uses_llm_api:
                summary["risks"].append("依赖大模型API，有成本和技术门槛")

            if selection_analysis.requires_compliance:
                summary["risks"].append("涉及合规领域，门槛较高")

            if selection_analysis.tech_complexity_level == "high":
                summary["risks"].append("技术复杂度高")

        if scores["pricing_clarity"] < 5:
            summary["risks"].append("定价不够清晰")

        if scores["conversion_friendliness"] < 5:
            summary["risks"].append("转化路径可能不够友好")

        # 市场定位
        if category_metrics:
            summary["market_position"] = {
                "type": category_metrics.market_type,
                "reason": category_metrics.market_type_reason,
                "category_revenue": category_metrics.total_revenue,
                "category_projects": category_metrics.total_projects,
            }

            if category_metrics.market_type == "red_ocean":
                summary["risks"].append(f"所在赛道竞争激烈({category_metrics.total_projects}个竞品)")

        # 生成建议
        if scores["overall_recommendation"] >= 7:
            summary["recommendations"].append("推荐关注：综合评分较高，值得深入研究")
        elif scores["overall_recommendation"] >= 5:
            summary["recommendations"].append("可以关注：有一定参考价值，但需注意风险点")
        else:
            summary["recommendations"].append("谨慎参考：综合评分较低，可能不太适合复制")

        if selection_analysis and selection_analysis.combo1_match:
            summary["recommendations"].append("符合'低粉丝+高收入+简单+年轻'组合，优先关注")

        return summary

    async def _save_analysis(
        self,
        startup_id: int,
        scores: Dict[str, float],
        summary: Dict[str, Any]
    ) -> ComprehensiveAnalysis:
        """保存综合分析结果"""
        # 检查是否已有分析
        result = await self.db.execute(
            select(ComprehensiveAnalysis)
            .where(ComprehensiveAnalysis.startup_id == startup_id)
        )
        existing = result.scalar_one_or_none()

        if existing:
            analysis = existing
        else:
            analysis = ComprehensiveAnalysis(startup_id=startup_id)
            self.db.add(analysis)

        # 更新评分
        analysis.maturity_score = scores["maturity_score"]
        analysis.positioning_clarity = scores["positioning_clarity"]
        analysis.pain_point_sharpness = scores["pain_point_sharpness"]
        analysis.pricing_clarity = scores["pricing_clarity"]
        analysis.conversion_friendliness = scores["conversion_friendliness"]
        analysis.individual_replicability = scores["individual_replicability"]
        analysis.overall_recommendation = scores["overall_recommendation"]
        analysis.analysis_summary = summary
        analysis.analyzed_at = datetime.utcnow()
        analysis.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(analysis)

        return analysis

    async def get_top_recommendations(self, limit: int = 20) -> list:
        """获取综合推荐指数最高的产品"""
        result = await self.db.execute(
            select(ComprehensiveAnalysis)
            .order_by(ComprehensiveAnalysis.overall_recommendation.desc())
            .limit(limit)
        )
        analyses = result.scalars().all()

        # 获取关联的Startup信息
        recommendations = []
        for analysis in analyses:
            startup_result = await self.db.execute(
                select(Startup, Founder)
                .outerjoin(Founder, Startup.founder_id == Founder.id)
                .where(Startup.id == analysis.startup_id)
            )
            row = startup_result.first()

            if row:
                startup, founder = row
                startup_data = startup.to_dict()
                if founder:
                    if founder.username:
                        startup_data["founder_username"] = founder.username
                    if founder.name:
                        startup_data["founder_name"] = founder.name
                    if founder.followers is not None:
                        startup_data["founder_followers"] = founder.followers
                    if founder.social_platform:
                        startup_data["founder_social_platform"] = founder.social_platform
                recommendations.append({
                    "startup": startup_data,
                    "analysis": analysis.to_dict(),
                })

        return recommendations
