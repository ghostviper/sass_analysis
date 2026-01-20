"""
Seed Discover Page Data

插入示例数据用于测试 discover 页面各区块

运行方式：
    cd backend
    python -m scripts.seed_discover_data
    
    # 只生成每日策展
    python -m scripts.seed_discover_data --curations-only
    
    # 预览模板匹配情况
    python -m scripts.seed_discover_data --preview
"""

import argparse
import asyncio
from datetime import date, timedelta
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

from sqlalchemy import select, func
from sqlalchemy.orm import Session
from database.db import get_db_session, get_sync_session
from database.models import (
    DailyCuration, CurationProduct, SuccessStory,
    StoryTimelineEvent, StoryKeyInsight, FeaturedCreator, Startup, Founder
)
from curation.daily_generator import DailyCurationGenerator
from curation.daily_templates import ALL_TEMPLATES


async def seed_featured_creators(upsert: bool = False):
    """插入或更新精选创作者数据"""
    print("Seeding featured creators...")

    def normalize_username(value):
        if not value:
            return None
        trimmed = value.strip()
        if not trimmed:
            return None
        if trimmed.startswith("@"):
            trimmed = trimmed[1:]
        trimmed = trimmed.strip()
        return trimmed.lower() if trimmed else None
    
    creators_data = [
        {
            "name": "Pieter Levels",
            "handle": "@levelsio",
            "avatar": "🚀",
            "bio_zh": "不爱写推特，但很会赚钱的人",
            "bio_en": "Doesn't tweet much, but makes a lot of money",
            "tag": "Serial Maker",
            "tag_zh": "连续创业者",
            "tag_en": "Serial Maker",
            "tag_color": "amber",
            "total_mrr": "$160k+",
            "followers": "450k",
            "product_count": 5,
            "founder_username": "levelsio",
            "display_order": 1,
        },
        {
            "name": "Tony Dinh",
            "handle": "@tdinh_me",
            "avatar": "⚡",
            "bio_zh": "产品比人火的创作者",
            "bio_en": "Products more famous than the maker",
            "tag": "Efficiency Tools",
            "tag_zh": "效率工具专家",
            "tag_en": "Efficiency Tools Expert",
            "tag_color": "blue",
            "total_mrr": "$63k+",
            "followers": "85k",
            "product_count": 4,
            "founder_username": "tdinh_me",
            "display_order": 2,
        },
        {
            "name": "Marc Lou",
            "handle": "@marc_louvion",
            "avatar": "🎯",
            "bio_zh": "靠教程起家，靠 SaaS 变现",
            "bio_en": "Started with tutorials, monetized with SaaS",
            "tag": "Content Creator",
            "tag_zh": "内容创作者",
            "tag_en": "Content Creator",
            "tag_color": "violet",
            "total_mrr": "$45k+",
            "followers": "120k",
            "product_count": 3,
            "founder_username": "marc_louvion",
            "display_order": 3,
        },
        {
            "name": "Damon Chen",
            "handle": "@damengchen",
            "avatar": "🌟",
            "bio_zh": "一年只发布 2 个产品的人",
            "bio_en": "Only ships 2 products per year",
            "tag": "Quality Focus",
            "tag_zh": "精品路线",
            "tag_en": "Quality Focus",
            "tag_color": "emerald",
            "total_mrr": "$28k+",
            "followers": "45k",
            "product_count": 2,
            "founder_username": "damengchen",
            "display_order": 4,
        },
    ]
    
    async with get_db_session() as db:
        for data in creators_data:
            founder_username = normalize_username(data.get("founder_username") or data.get("handle"))
            if founder_username:
                data["founder_username"] = founder_username
                founder_result = await db.execute(
                    select(Founder)
                    .where(func.lower(func.replace(Founder.username, "@", "")) == founder_username)
                )
                founder = founder_result.scalar_one_or_none()
                if not founder:
                    founder = Founder(
                        name=data.get("name") or founder_username,
                        username=founder_username,
                        profile_url=f"https://x.com/{founder_username}",
                    )
                    db.add(founder)
                    await db.flush()
                data["founder_id"] = founder.id
            existing = await db.execute(
                select(FeaturedCreator).where(FeaturedCreator.handle == data["handle"])
            )
            existing_creator = existing.scalar_one_or_none()
            if existing_creator:
                if not upsert:
                    print(f"  Skipping {data['name']} (already exists)")
                    continue
                for key, value in data.items():
                    setattr(existing_creator, key, value)
                print(f"  Updated {data['name']}")
            else:
                creator = FeaturedCreator(**data)
                db.add(creator)
                print(f"  Added {data['name']}")
        
        await db.commit()
    
    print("Featured creators seeded!")


def seed_daily_curations_sync(force_regenerate: bool = False):
    """
    使用新的模板生成器插入每日策展数据（同步版本）
    
    基于 daily_templates.py 中定义的模板，自动筛选匹配的产品
    """
    print("Seeding daily curations with template-based generator...")
    
    with get_sync_session() as db:
        generator = DailyCurationGenerator(db)
        today = date.today()
        
        # 为今天和昨天生成策展
        dates_to_generate = [today, today - timedelta(days=1)]
        
        total_generated = 0
        for curation_date in dates_to_generate:
            print(f"\n  Generating for {curation_date}:")
            curations = generator.generate_all_for_date(
                curation_date, 
                force_regenerate=force_regenerate
            )
            for c in curations:
                print(f"    ✓ {c.curation_key} ({len(c.products)} products)")
            total_generated += len(curations)
        
        print(f"\nTotal curations generated: {total_generated}")


def preview_templates():
    """预览所有模板的匹配情况"""
    print("=" * 60)
    print("Template Preview - Checking product matches")
    print("=" * 60)
    
    with get_sync_session() as db:
        generator = DailyCurationGenerator(db)
        
        for template in ALL_TEMPLATES:
            result = generator.preview_template(template.key)
            
            status = "✓" if result["is_viable"] else "✗"
            print(f"\n{status} {template.key}")
            print(f"  标题: {template.title_zh}")
            print(f"  类型: {template.curation_type}")
            print(f"  匹配: {result['matched_count']}/{template.min_products} (最少需要)")
            
            if result["products"]:
                print("  产品示例:")
                for p in result["products"][:3]:
                    print(f"    - {p['name']}: ${p['revenue_30d']:,.0f}/mo, {p['highlight_zh']}")


async def seed_success_stories():
    """插入爆款故事数据"""
    print("Seeding success stories...")
    
    stories_data = [
        {
            "product_name": "Plausible Analytics",
            "product_logo": "📊",
            "product_mrr": "$20k+",
            "founder_name": "Uku Täht",
            "title": "这个 $20k MRR 产品，第一版其实很烂",
            "title_zh": "这个 $20k MRR 产品，第一版其实很烂",
            "title_en": "This $20k MRR product started really rough",
            "subtitle": "Plausible Analytics 的成长故事",
            "subtitle_zh": "Plausible Analytics 的成长故事",
            "subtitle_en": "The growth story of Plausible Analytics",
            "gradient": "from-emerald-500/10 to-teal-500/5",
            "accent_color": "emerald",
            "is_featured": True,
            "timeline": [
                ("2019.04", "第一版上线，功能简陋", "First version launched, basic features"),
                ("2019.08", "开源策略，获得关注", "Open source strategy gained attention"),
                ("2020.03", "隐私合规成为卖点", "Privacy compliance became selling point"),
                ("2021.01", "MRR 突破 $10k", "MRR exceeded $10k"),
            ],
            "insights": [
                ("隐私合规是差异化的关键", "Privacy compliance is key to differentiation"),
                ("开源带来信任和传播", "Open source brings trust and virality"),
                ("简单比功能多更重要", "Simplicity matters more than features"),
            ],
        },
        {
            "product_name": "Carrd",
            "product_logo": "🎴",
            "product_mrr": "$100k+",
            "founder_name": "AJ",
            "title": "这个 SaaS 的成功，80% 不在技术",
            "title_zh": "这个 SaaS 的成功，80% 不在技术",
            "title_en": "80% of this SaaS success is not about tech",
            "subtitle": "Carrd 的极简主义哲学",
            "subtitle_zh": "Carrd 的极简主义哲学",
            "subtitle_en": "Carrd's minimalist philosophy",
            "gradient": "from-violet-500/10 to-purple-500/5",
            "accent_color": "violet",
            "is_featured": True,
            "timeline": [
                ("2016.08", "一个人开发上线", "Solo developer launched"),
                ("2017.02", "免费版获得大量用户", "Free tier gained massive users"),
                ("2018.06", "Pro 版本推出", "Pro version launched"),
                ("2020.12", "MRR 突破 $100k", "MRR exceeded $100k"),
            ],
            "insights": [
                ("极简设计降低用户门槛", "Minimalist design lowers user barrier"),
                ("免费版是最好的营销", "Free tier is the best marketing"),
                ("一个人也能做大产品", "One person can build big products"),
            ],
        },
    ]
    
    async with get_db_session() as db:
        for data in stories_data:
            existing = await db.execute(
                select(SuccessStory).where(SuccessStory.product_name == data["product_name"])
            )
            if existing.scalar_one_or_none():
                print(f"  Skipping {data['product_name']} (already exists)")
                continue
            
            timeline = data.pop("timeline")
            insights = data.pop("insights")
            
            story = SuccessStory(**data)
            db.add(story)
            await db.flush()
            
            for i, (date_str, text_zh, text_en) in enumerate(timeline):
                event = StoryTimelineEvent(
                    story_id=story.id,
                    event_date=date_str,
                    event_text=text_zh,
                    event_text_zh=text_zh,
                    event_text_en=text_en,
                    display_order=i,
                )
                db.add(event)
            
            for i, (text_zh, text_en) in enumerate(insights):
                insight = StoryKeyInsight(
                    story_id=story.id,
                    insight_text=text_zh,
                    insight_text_zh=text_zh,
                    insight_text_en=text_en,
                    display_order=i,
                )
                db.add(insight)
            
            print(f"  Added {data['product_name']}")
        
        await db.commit()
    
    print("Success stories seeded!")


async def main():
    parser = argparse.ArgumentParser(description="Seed Discover Page Data")
    parser.add_argument("--curations-only", action="store_true", help="Only generate daily curations")
    parser.add_argument("--preview", action="store_true", help="Preview template matches without writing")
    parser.add_argument("--force", action="store_true", help="Force regenerate existing curations")
    parser.add_argument("--upsert", action="store_true", help="Update featured creators when they already exist")
    args = parser.parse_args()
    
    if args.preview:
        preview_templates()
        return
    
    print("=" * 50)
    print("Seeding Discover Page Data")
    print("=" * 50)
    
    if args.curations_only:
        seed_daily_curations_sync(force_regenerate=args.force)
    else:
        await seed_featured_creators(upsert=args.upsert)
        await seed_success_stories()
        seed_daily_curations_sync(force_regenerate=args.force)
    
    print("=" * 50)
    print("Done!")


if __name__ == "__main__":
    asyncio.run(main())
