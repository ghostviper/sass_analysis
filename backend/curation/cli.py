"""
策展系统命令行工具

使用方法：
    cd backend
    .\\venv\\Scripts\\python.exe -m curation.cli judge --limit 10
    .\\venv\\Scripts\\python.exe -m curation.cli curate
"""

from pathlib import Path
from dotenv import load_dotenv
_env_path = Path(__file__).parent.parent / ".env"
load_dotenv(_env_path)

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
import argparse

from sqlalchemy import select, delete, text
from sqlalchemy.dialects.postgresql import insert as pg_insert
from database.db import get_db_session, IS_POSTGRESQL
from database.models import (
    Startup,
    LandingPageAnalysis,
    ProductSelectionAnalysis,
    CategoryAnalysis,
    MotherThemeJudgment,
    DiscoverTopic,
    TopicProduct,
)
from services.openai_service import OpenAIService

from .config import MOTHER_THEMES, PROMPT_VERSION
from .judge import MotherThemeJudge
from .curator import CuratorAgent
from .validators import check_cross_theme_consistency

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OUTPUT_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR.mkdir(exist_ok=True)


async def get_products_for_judgment(
    db, limit: Optional[int] = 20, min_revenue: Optional[float] = None, skip_existing: bool = False,
) -> List[Tuple[Startup, LandingPageAnalysis]]:
    query = (
        select(Startup, LandingPageAnalysis)
        .join(LandingPageAnalysis, Startup.id == LandingPageAnalysis.startup_id)
        .where(LandingPageAnalysis.core_features.isnot(None))
    )
    if min_revenue is not None:
        query = query.where(Startup.revenue_30d >= min_revenue)
    if skip_existing:
        judged_subq = select(MotherThemeJudgment.startup_id).distinct()
        query = query.where(~Startup.id.in_(judged_subq))
    query = query.order_by(Startup.revenue_30d.desc().nullslast())
    if limit is not None:
        query = query.limit(limit)
    result = await db.execute(query)
    return result.all()


async def get_selection_analysis(db, startup_id: int) -> Optional[ProductSelectionAnalysis]:
    query = select(ProductSelectionAnalysis).where(ProductSelectionAnalysis.startup_id == startup_id)
    result = await db.execute(query)
    row = result.first()
    return row[0] if row else None


async def get_category_analysis(db, category: str) -> Optional[CategoryAnalysis]:
    if not category:
        return None
    query = select(CategoryAnalysis).where(CategoryAnalysis.category == category)
    result = await db.execute(query)
    row = result.first()
    return row[0] if row else None


async def save_judgments_to_db(db, startup_id: int, theme_results: Dict[str, Any], model_name: str) -> int:
    saved_count = 0
    for theme in MOTHER_THEMES:
        theme_key = theme["key"]
        result = theme_results.get(theme_key, {})
        if not result or "_error" in result:
            continue
        judgment_data = {
            "startup_id": startup_id,
            "theme_key": theme_key,
            "judgment": result.get("judgment"),
            "confidence": result.get("confidence"),
            "reasons": result.get("reasons"),
            "evidence_fields": result.get("evidence_used"),
            "uncertainties": result.get("uncertainties"),
            "prompt_version": PROMPT_VERSION,
            "model": model_name,
        }
        if IS_POSTGRESQL:
            stmt = pg_insert(MotherThemeJudgment).values(**judgment_data)
            stmt = stmt.on_conflict_do_update(
                index_elements=["startup_id", "theme_key"],
                set_={
                    "judgment": stmt.excluded.judgment,
                    "confidence": stmt.excluded.confidence,
                    "reasons": stmt.excluded.reasons,
                    "evidence_fields": stmt.excluded.evidence_fields,
                    "uncertainties": stmt.excluded.uncertainties,
                    "prompt_version": stmt.excluded.prompt_version,
                    "model": stmt.excluded.model,
                    "created_at": datetime.utcnow(),
                }
            )
            await db.execute(stmt)
        else:
            await db.execute(
                delete(MotherThemeJudgment).where(
                    MotherThemeJudgment.startup_id == startup_id,
                    MotherThemeJudgment.theme_key == theme_key,
                )
            )
            db.add(MotherThemeJudgment(**judgment_data))
        saved_count += 1
    await db.commit()
    return saved_count


async def run_judgment(
    limit: Optional[int] = 20, delay: float = 2.0, min_revenue: Optional[float] = None,
    fallback_on_invalid: bool = False, skip_existing: bool = False,
) -> None:
    logger.info("Starting judgment, limit: %s, min_revenue: %s", limit, min_revenue)
    results: List[Dict[str, Any]] = []
    model_name = "unknown"
    total_saved = 0

    async with get_db_session() as db:
        products = await get_products_for_judgment(db, limit, min_revenue, skip_existing)
        logger.info(f"Found {len(products)} products")
        if not products:
            return

        async with OpenAIService() as openai:
            judge = MotherThemeJudge(openai)
            model_name = openai.default_model

            for i, (startup, analysis) in enumerate(products):
                logger.info(f"[{i+1}/{len(products)}] {startup.name}")
                selection = await get_selection_analysis(db, startup.id)
                category_analysis = await get_category_analysis(db, startup.category)
                product_result = {"id": startup.id, "name": startup.name, "judgments": {}}

                try:
                    theme_results = await judge.judge_all_themes(
                        startup, analysis, selection=selection,
                        category_analysis=category_analysis, fallback_on_invalid=fallback_on_invalid,
                    )
                    if "_error" in theme_results:
                        product_result["judgments"] = {"_error": theme_results["_error"]}
                    else:
                        product_result["judgments"] = theme_results
                        saved = await save_judgments_to_db(db, startup.id, theme_results, model_name)
                        total_saved += saved
                        warnings = check_cross_theme_consistency(theme_results)
                        if warnings:
                            product_result["consistency_warnings"] = warnings
                except Exception as exc:
                    product_result["judgments"] = {"_error": str(exc)}
                    logger.error(f"  Failed: {exc}")

                results.append(product_result)
                if i < len(products) - 1:
                    await asyncio.sleep(delay)

    output_file = OUTPUT_DIR / "mother_theme_test_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({"results": results, "saved_to_db": total_saved}, f, ensure_ascii=False, indent=2)
    logger.info(f"Done! Saved {total_saved} judgments to DB")


async def save_topics_to_db(db, topics: List[Dict[str, Any]]) -> int:
    """Save topics to database with i18n fields"""
    saved_count = 0
    
    for idx, topic in enumerate(topics):
        topic_key = topic.get("topic_key", "")
        
        # Build topic data with i18n fields
        topic_data = {
            "topic_key": topic_key,
            "title": topic.get("title_zh", topic.get("title", "")),
            "title_zh": topic.get("title_zh", ""),
            "title_en": topic.get("title_en", ""),
            "description": topic.get("description_zh", topic.get("description", "")),
            "description_zh": topic.get("description_zh", ""),
            "description_en": topic.get("description_en", ""),
            "curator_role": topic.get("curator_role", ""),
            "generation_pattern": topic.get("generation_pattern", ""),
            "filter_rules": topic.get("filter_rules", {}),
            "cta_text": topic.get("cta_text_zh", topic.get("cta_text", "")),
            "cta_text_zh": topic.get("cta_text_zh", ""),
            "cta_text_en": topic.get("cta_text_en", ""),
            "is_active": True,
            "display_order": idx,
        }
        
        if IS_POSTGRESQL:
            stmt = pg_insert(DiscoverTopic).values(**topic_data)
            stmt = stmt.on_conflict_do_update(
                index_elements=["topic_key"],
                set_={
                    "title": stmt.excluded.title,
                    "title_zh": stmt.excluded.title_zh,
                    "title_en": stmt.excluded.title_en,
                    "description": stmt.excluded.description,
                    "description_zh": stmt.excluded.description_zh,
                    "description_en": stmt.excluded.description_en,
                    "curator_role": stmt.excluded.curator_role,
                    "generation_pattern": stmt.excluded.generation_pattern,
                    "filter_rules": stmt.excluded.filter_rules,
                    "cta_text": stmt.excluded.cta_text,
                    "cta_text_zh": stmt.excluded.cta_text_zh,
                    "cta_text_en": stmt.excluded.cta_text_en,
                    "is_active": stmt.excluded.is_active,
                    "display_order": stmt.excluded.display_order,
                    "updated_at": datetime.utcnow(),
                }
            )
            await db.execute(stmt)
            
            query = select(DiscoverTopic.id).where(DiscoverTopic.topic_key == topic_key)
            topic_result = await db.execute(query)
            topic_id = topic_result.scalar_one()
        else:
            # SQLite
            query = select(DiscoverTopic).where(DiscoverTopic.topic_key == topic_key)
            result = await db.execute(query)
            existing = result.scalar_one_or_none()
            
            if existing:
                for key, value in topic_data.items():
                    if key != "topic_key" and hasattr(existing, key):
                        setattr(existing, key, value)
                existing.updated_at = datetime.utcnow()
                topic_id = existing.id
            else:
                new_topic = DiscoverTopic(**topic_data)
                db.add(new_topic)
                await db.flush()
                topic_id = new_topic.id
        
        # Delete old product associations
        await db.execute(delete(TopicProduct).where(TopicProduct.topic_id == topic_id))
        
        # Add new product associations
        for order, pid in enumerate(topic.get("product_ids", [])):
            db.add(TopicProduct(topic_id=topic_id, startup_id=pid, display_order=order))
        
        saved_count += 1
    
    await db.commit()
    return saved_count


async def run_curation(
    min_products: int = 3,
    max_products: int = 15,
) -> None:
    """运行策展流程，生成专题并保存到数据库"""
    logger.info("Starting curation...")
    
    async with get_db_session() as db:
        # 获取所有有母题判断的产品
        query = (
            select(Startup, MotherThemeJudgment)
            .join(MotherThemeJudgment, Startup.id == MotherThemeJudgment.startup_id)
            .where(Startup.revenue_30d.isnot(None))
        )
        result = await db.execute(query)
        rows = result.all()
        
        # 按产品分组判断结果
        products_map: Dict[int, Dict[str, Any]] = {}
        for startup, judgment in rows:
            if startup.id not in products_map:
                products_map[startup.id] = {
                    "id": startup.id,
                    "name": startup.name,
                    "slug": startup.slug,
                    "category": startup.category,
                    "revenue_30d": startup.revenue_30d,
                    "mother_theme_judgments": {},
                }
            products_map[startup.id]["mother_theme_judgments"][judgment.theme_key] = {
                "judgment": judgment.judgment,
                "confidence": judgment.confidence,
            }
        
        products = list(products_map.values())
        logger.info(f"Found {len(products)} products with judgments")
        
        if not products:
            logger.warning("No products with judgments found")
            return
        
        # 生成专题
        curator = CuratorAgent()
        topics = curator.generate(
            products=products,
            min_products=min_products,
            max_products=max_products,
        )
        
        logger.info(f"Generated {len(topics)} topics")
        
        # 保存到数据库
        saved = await save_topics_to_db(db, topics)
        logger.info(f"Saved {saved} topics to database")
        
        # 同时保存到 JSON 文件（备份）
        output_file = OUTPUT_DIR / "generated_topics.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump({"topics": topics, "generated_at": datetime.utcnow().isoformat()}, f, ensure_ascii=False, indent=2)
        logger.info(f"Backup saved to {output_file}")


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description="策展系统命令行工具")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # judge 命令
    judge_parser = subparsers.add_parser("judge", help="运行母题判断")
    judge_parser.add_argument("--limit", type=int, default=20, help="处理产品数量限制")
    judge_parser.add_argument("--delay", type=float, default=2.0, help="请求间隔(秒)")
    judge_parser.add_argument("--min-revenue", type=float, help="最低收入筛选")
    judge_parser.add_argument("--fallback", action="store_true", help="无效响应时使用回退")
    judge_parser.add_argument("--skip-existing", action="store_true", help="跳过已判断的产品")
    
    # curate 命令
    curate_parser = subparsers.add_parser("curate", help="运行策展生成专题")
    curate_parser.add_argument("--min-products", type=int, default=3, help="专题最少产品数")
    curate_parser.add_argument("--max-products", type=int, default=15, help="专题最多产品数")
    
    args = parser.parse_args()
    
    if args.command == "judge":
        asyncio.run(run_judgment(
            limit=args.limit,
            delay=args.delay,
            min_revenue=args.min_revenue,
            fallback_on_invalid=args.fallback,
            skip_existing=args.skip_existing,
        ))
    elif args.command == "curate":
        asyncio.run(run_curation(
            min_products=args.min_products,
            max_products=args.max_products,
        ))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
