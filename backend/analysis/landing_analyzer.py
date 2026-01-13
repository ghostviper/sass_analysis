"""
Landing Page Analyzer - 使用AI分析Landing Page内容
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Startup, LandingPageSnapshot, LandingPageAnalysis
from services.openai_service import OpenAIService
from crawler.browser import BrowserManager
from crawler.landing_page_scraper import LandingPageScraper

logger = logging.getLogger(__name__)


class LandingPageAnalyzer:
    """Landing Page AI分析器"""

    def __init__(self, db: AsyncSession, openai_service: Optional[OpenAIService] = None):
        self.db = db
        self._owns_openai = openai_service is None
        self.openai = openai_service or OpenAIService()

    async def close(self):
        """关闭资源"""
        if self._owns_openai:
            await self.openai.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def analyze_from_snapshot(
        self,
        startup: Startup,
        snapshot: LandingPageSnapshot
    ) -> LandingPageAnalysis:
        """
        从已有快照分析Landing Page

        Args:
            startup: Startup模型实例
            snapshot: LandingPageSnapshot模型实例

        Returns:
            LandingPageAnalysis模型实例
        """
        if not snapshot.raw_text:
            raise ValueError("Snapshot has no text content")

        # 调用AI分析
        startup_info = {
            "name": startup.name,
            "category": startup.category,
            "description": startup.description,
            "revenue_30d": startup.revenue_30d
        }

        ai_result = await self.openai.analyze_landing_page(
            page_content=snapshot.raw_text,
            startup_info=startup_info
        )

        # 保存或更新分析结果
        analysis = await self._save_analysis(startup.id, snapshot.id, ai_result)
        return analysis

    async def analyze_startup(
        self,
        startup_id: int,
        force_rescrape: bool = False
    ) -> Optional[LandingPageAnalysis]:
        """
        分析指定产品的Landing Page（完整流程）

        Args:
            startup_id: 产品ID
            force_rescrape: 是否强制重新爬取

        Returns:
            LandingPageAnalysis或None
        """
        # 获取产品信息
        result = await self.db.execute(
            select(Startup).where(Startup.id == startup_id)
        )
        startup = result.scalar_one_or_none()

        if not startup:
            logger.error(f"Startup {startup_id} not found")
            return None

        if not startup.website_url:
            logger.warning(f"Startup {startup_id} has no website URL")
            return None

        # 检查是否已有快照
        snapshot = None
        if not force_rescrape:
            snapshot_result = await self.db.execute(
                select(LandingPageSnapshot)
                .where(LandingPageSnapshot.startup_id == startup_id)
                .where(LandingPageSnapshot.status == "success")
                .order_by(LandingPageSnapshot.scraped_at.desc())
            )
            snapshot = snapshot_result.scalar_one_or_none()

        # 需要爬取
        if not snapshot:
            snapshot = await self._scrape_landing_page(startup)
            if not snapshot or snapshot.status != "success":
                logger.error(f"Failed to scrape landing page for {startup.name}")
                return None

        # AI分析
        try:
            analysis = await self.analyze_from_snapshot(startup, snapshot)
            return analysis
        except Exception as e:
            logger.error(f"AI analysis failed for {startup.name}: {e}")
            return None

    async def _scrape_landing_page(self, startup: Startup) -> Optional[LandingPageSnapshot]:
        """爬取Landing Page并保存快照"""
        browser = BrowserManager()
        await browser.start()

        try:
            # 检查今天是否已有快照
            today = datetime.utcnow().date()
            result = await self.db.execute(
                select(LandingPageSnapshot).where(
                    LandingPageSnapshot.startup_id == startup.id,
                    func.date(LandingPageSnapshot.scraped_at) == today
                )
            )
            existing_snapshot = result.scalar_one_or_none()
            
            if existing_snapshot and not force_rescrape:
                logger.info(f"今天已有快照，跳过: {startup.name}")
                return existing_snapshot
            
            scraper = LandingPageScraper(browser)
            result = await scraper.scrape_landing_page(
                startup_id=startup.id,
                url=startup.website_url,
                save_snapshot=True
            )

            if existing_snapshot:
                # 更新现有快照
                existing_snapshot.html_content = result.html_content
                existing_snapshot.raw_text = result.raw_text
                existing_snapshot.snapshot_path = result.snapshot_path
                existing_snapshot.status = result.status
                existing_snapshot.error_message = result.error_message
                existing_snapshot.page_load_time_ms = result.page_load_time_ms
                existing_snapshot.content_length = result.content_length
                existing_snapshot.scraped_at = datetime.utcnow()
                snapshot = existing_snapshot
            else:
                # 保存新快照到数据库
                snapshot = LandingPageSnapshot(
                    startup_id=startup.id,
                    url=startup.website_url,
                    html_content=result.html_content,
                    raw_text=result.raw_text,
                    snapshot_path=result.snapshot_path,
                    status=result.status,
                    error_message=result.error_message,
                    page_load_time_ms=result.page_load_time_ms,
                    content_length=result.content_length,
                )
                self.db.add(snapshot)
            
            await self.db.commit()
            await self.db.refresh(snapshot)

            return snapshot

        finally:
            await browser.stop()

    async def _save_analysis(
        self,
        startup_id: int,
        snapshot_id: int,
        ai_result: Dict[str, Any]
    ) -> LandingPageAnalysis:
        """保存AI分析结果到数据库"""
        # 检查是否已有分析
        result = await self.db.execute(
            select(LandingPageAnalysis)
            .where(LandingPageAnalysis.startup_id == startup_id)
        )
        existing = result.scalar_one_or_none()

        if existing:
            # 更新现有记录
            analysis = existing
            analysis.snapshot_id = snapshot_id
        else:
            # 创建新记录
            analysis = LandingPageAnalysis(
                startup_id=startup_id,
                snapshot_id=snapshot_id,
            )
            self.db.add(analysis)

        # 填充分析结果
        analysis.target_audience = ai_result.get("target_audience", [])
        analysis.target_roles = ai_result.get("target_roles", [])
        analysis.use_cases = ai_result.get("use_cases", [])

        analysis.core_features = ai_result.get("core_features", [])
        analysis.feature_count = ai_result.get("feature_count", 0)
        analysis.value_propositions = ai_result.get("value_propositions", [])

        analysis.pain_points = ai_result.get("pain_points", [])
        analysis.pain_point_sharpness = ai_result.get("pain_point_sharpness", 5.0)
        analysis.uses_before_after = ai_result.get("uses_before_after", False)
        analysis.uses_emotional_words = ai_result.get("uses_emotional_words", False)

        analysis.potential_moats = ai_result.get("potential_moats", [])

        analysis.pricing_model = ai_result.get("pricing_model", "unknown")
        analysis.pricing_tiers = ai_result.get("pricing_tiers", [])
        analysis.pricing_clarity_score = ai_result.get("pricing_clarity_score", 5.0)
        analysis.has_free_tier = ai_result.get("has_free_tier", False)
        analysis.has_trial = ai_result.get("has_trial", False)

        analysis.cta_count = ai_result.get("cta_count", 0)
        analysis.cta_texts = ai_result.get("cta_texts", [])
        analysis.conversion_funnel_steps = ai_result.get("conversion_funnel_steps", 0)
        analysis.has_instant_value_demo = ai_result.get("has_instant_value_demo", False)
        analysis.conversion_friendliness_score = ai_result.get("conversion_friendliness_score", 5.0)

        analysis.industry_keywords = ai_result.get("industry_keywords", {})
        analysis.headline_text = ai_result.get("headline_text", "")
        analysis.tagline_text = ai_result.get("tagline_text", "")

        analysis.positioning_clarity_score = ai_result.get("positioning_clarity_score", 5.0)
        analysis.replication_difficulty_score = ai_result.get("replication_difficulty_score", 5.0)
        analysis.individual_replicability_score = ai_result.get("individual_replicability_score", 5.0)
        analysis.product_maturity_score = ai_result.get("product_maturity_score", 5.0)

        analysis.ai_model_used = ai_result.get("ai_model_used", "unknown")
        analysis.ai_analysis_raw = ai_result
        analysis.analyzed_at = datetime.utcnow()
        analysis.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(analysis)

        return analysis

    async def get_analysis(self, startup_id: int) -> Optional[LandingPageAnalysis]:
        """获取已有的Landing Page分析结果"""
        result = await self.db.execute(
            select(LandingPageAnalysis)
            .where(LandingPageAnalysis.startup_id == startup_id)
        )
        return result.scalar_one_or_none()

    async def batch_analyze(
        self,
        startup_ids: list,
        delay_between: float = 5.0
    ) -> Dict[str, int]:
        """
        批量分析多个产品

        Args:
            startup_ids: 产品ID列表
            delay_between: 请求间隔秒数

        Returns:
            统计结果 {"success": N, "failed": N}
        """
        import asyncio

        stats = {"success": 0, "failed": 0, "skipped": 0}

        for i, startup_id in enumerate(startup_ids):
            logger.info(f"Analyzing {i + 1}/{len(startup_ids)}: startup_id={startup_id}")

            try:
                analysis = await self.analyze_startup(startup_id)
                if analysis:
                    stats["success"] += 1
                else:
                    stats["failed"] += 1
            except Exception as e:
                logger.error(f"Error analyzing {startup_id}: {e}")
                stats["failed"] += 1

            # 间隔等待
            if i < len(startup_ids) - 1:
                await asyncio.sleep(delay_between)

        logger.info(f"Batch analysis completed: {stats}")
        return stats
