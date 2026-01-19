"""
Add Discover Page Tables Migration

新增表：
1. daily_curations - 每日策展（TodayCuration 区块）
2. curation_products - 策展-产品关联
3. success_stories - 爆款故事（SuccessBreakdown 区块）
4. story_timeline_events - 故事时间线事件
5. user_preferences - 用户偏好（ForYouSection 区块）

运行方式：
    cd backend
    python -m migrations.add_discover_tables
"""

import asyncio
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv(Path(__file__).parent.parent / ".env")

from sqlalchemy import text
from database.db import get_db_session, IS_POSTGRESQL


async def migrate():
    """执行迁移"""
    print(f"Database: {'PostgreSQL' if IS_POSTGRESQL else 'SQLite'}")
    print("Starting migration: add_discover_tables")
    
    async with get_db_session() as db:
        # PostgreSQL DDL
        if IS_POSTGRESQL:
            statements = [
                # 1. daily_curations
                """
                CREATE TABLE IF NOT EXISTS daily_curations (
                    id SERIAL PRIMARY KEY,
                    curation_key VARCHAR(100) UNIQUE NOT NULL,
                    title VARCHAR(200) NOT NULL,
                    title_zh VARCHAR(200),
                    title_en VARCHAR(200),
                    description TEXT,
                    description_zh TEXT,
                    description_en TEXT,
                    insight VARCHAR(300),
                    insight_zh VARCHAR(300),
                    insight_en VARCHAR(300),
                    tag VARCHAR(100),
                    tag_zh VARCHAR(100),
                    tag_en VARCHAR(100),
                    tag_color VARCHAR(20) DEFAULT 'amber',
                    curation_type VARCHAR(50),
                    filter_rules JSONB,
                    conflict_dimensions JSONB,
                    curation_date DATE NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    display_order INTEGER DEFAULT 0,
                    ai_generated BOOLEAN DEFAULT TRUE,
                    generation_model VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """,
                "CREATE INDEX IF NOT EXISTS ix_daily_curations_date ON daily_curations(curation_date)",
                "CREATE INDEX IF NOT EXISTS ix_daily_curations_active ON daily_curations(is_active)",
                
                # 2. curation_products
                """
                CREATE TABLE IF NOT EXISTS curation_products (
                    id SERIAL PRIMARY KEY,
                    curation_id INTEGER NOT NULL REFERENCES daily_curations(id) ON DELETE CASCADE,
                    startup_id INTEGER NOT NULL REFERENCES startups(id) ON DELETE CASCADE,
                    highlight_zh VARCHAR(200),
                    highlight_en VARCHAR(200),
                    display_order INTEGER DEFAULT 0,
                    UNIQUE(curation_id, startup_id)
                )
                """,
                "CREATE INDEX IF NOT EXISTS ix_curation_products_curation ON curation_products(curation_id)",
                
                # 3. success_stories
                """
                CREATE TABLE IF NOT EXISTS success_stories (
                    id SERIAL PRIMARY KEY,
                    startup_id INTEGER REFERENCES startups(id) ON DELETE SET NULL,
                    product_name VARCHAR(200) NOT NULL,
                    product_logo VARCHAR(20),
                    product_mrr VARCHAR(50),
                    founder_name VARCHAR(200),
                    title VARCHAR(300) NOT NULL,
                    title_zh VARCHAR(300),
                    title_en VARCHAR(300),
                    subtitle VARCHAR(300),
                    subtitle_zh VARCHAR(300),
                    subtitle_en VARCHAR(300),
                    gradient VARCHAR(100) DEFAULT 'from-emerald-500/10 to-teal-500/5',
                    accent_color VARCHAR(20) DEFAULT 'emerald',
                    is_featured BOOLEAN DEFAULT FALSE,
                    is_active BOOLEAN DEFAULT TRUE,
                    display_order INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """,
                "CREATE INDEX IF NOT EXISTS ix_success_stories_featured ON success_stories(is_featured)",
                "CREATE INDEX IF NOT EXISTS ix_success_stories_active ON success_stories(is_active)",
                
                # 4. story_timeline_events
                """
                CREATE TABLE IF NOT EXISTS story_timeline_events (
                    id SERIAL PRIMARY KEY,
                    story_id INTEGER NOT NULL REFERENCES success_stories(id) ON DELETE CASCADE,
                    event_date VARCHAR(20) NOT NULL,
                    event_text VARCHAR(500) NOT NULL,
                    event_text_zh VARCHAR(500),
                    event_text_en VARCHAR(500),
                    display_order INTEGER DEFAULT 0
                )
                """,
                "CREATE INDEX IF NOT EXISTS ix_story_timeline_story ON story_timeline_events(story_id)",
                
                # 5. story_key_insights
                """
                CREATE TABLE IF NOT EXISTS story_key_insights (
                    id SERIAL PRIMARY KEY,
                    story_id INTEGER NOT NULL REFERENCES success_stories(id) ON DELETE CASCADE,
                    insight_text VARCHAR(300) NOT NULL,
                    insight_text_zh VARCHAR(300),
                    insight_text_en VARCHAR(300),
                    display_order INTEGER DEFAULT 0
                )
                """,
                "CREATE INDEX IF NOT EXISTS ix_story_insights_story ON story_key_insights(story_id)",
                
                # 6. user_preferences
                """
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR(255) NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
                    preferred_roles JSONB DEFAULT '[]',
                    interested_categories JSONB DEFAULT '[]',
                    skill_level VARCHAR(20) DEFAULT 'beginner',
                    goal VARCHAR(50),
                    time_commitment VARCHAR(20),
                    tech_stack JSONB DEFAULT '[]',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id)
                )
                """,
                "CREATE INDEX IF NOT EXISTS ix_user_preferences_user ON user_preferences(user_id)",
                
                # 7. featured_creators
                """
                CREATE TABLE IF NOT EXISTS featured_creators (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(200) NOT NULL,
                    handle VARCHAR(100),
                    avatar VARCHAR(20),
                    bio_zh VARCHAR(300),
                    bio_en VARCHAR(300),
                    tag VARCHAR(100),
                    tag_zh VARCHAR(100),
                    tag_en VARCHAR(100),
                    tag_color VARCHAR(20) DEFAULT 'amber',
                    total_mrr VARCHAR(50),
                    followers VARCHAR(50),
                    product_count INTEGER,
                    founder_username VARCHAR(255),
                    is_featured BOOLEAN DEFAULT TRUE,
                    display_order INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """,
                "CREATE INDEX IF NOT EXISTS ix_featured_creators_featured ON featured_creators(is_featured)",
            ]
        else:
            # SQLite DDL
            statements = [
                # 1. daily_curations
                """
                CREATE TABLE IF NOT EXISTS daily_curations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    curation_key VARCHAR(100) UNIQUE NOT NULL,
                    title VARCHAR(200) NOT NULL,
                    title_zh VARCHAR(200),
                    title_en VARCHAR(200),
                    description TEXT,
                    description_zh TEXT,
                    description_en TEXT,
                    insight VARCHAR(300),
                    insight_zh VARCHAR(300),
                    insight_en VARCHAR(300),
                    tag VARCHAR(100),
                    tag_zh VARCHAR(100),
                    tag_en VARCHAR(100),
                    tag_color VARCHAR(20) DEFAULT 'amber',
                    curation_type VARCHAR(50),
                    filter_rules TEXT,
                    conflict_dimensions TEXT,
                    curation_date DATE NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    display_order INTEGER DEFAULT 0,
                    ai_generated BOOLEAN DEFAULT 1,
                    generation_model VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """,
                "CREATE INDEX IF NOT EXISTS ix_daily_curations_date ON daily_curations(curation_date)",
                "CREATE INDEX IF NOT EXISTS ix_daily_curations_active ON daily_curations(is_active)",
                
                # 2. curation_products
                """
                CREATE TABLE IF NOT EXISTS curation_products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    curation_id INTEGER NOT NULL REFERENCES daily_curations(id) ON DELETE CASCADE,
                    startup_id INTEGER NOT NULL REFERENCES startups(id) ON DELETE CASCADE,
                    highlight_zh VARCHAR(200),
                    highlight_en VARCHAR(200),
                    display_order INTEGER DEFAULT 0,
                    UNIQUE(curation_id, startup_id)
                )
                """,
                "CREATE INDEX IF NOT EXISTS ix_curation_products_curation ON curation_products(curation_id)",
                
                # 3. success_stories
                """
                CREATE TABLE IF NOT EXISTS success_stories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    startup_id INTEGER REFERENCES startups(id) ON DELETE SET NULL,
                    product_name VARCHAR(200) NOT NULL,
                    product_logo VARCHAR(20),
                    product_mrr VARCHAR(50),
                    founder_name VARCHAR(200),
                    title VARCHAR(300) NOT NULL,
                    title_zh VARCHAR(300),
                    title_en VARCHAR(300),
                    subtitle VARCHAR(300),
                    subtitle_zh VARCHAR(300),
                    subtitle_en VARCHAR(300),
                    gradient VARCHAR(100) DEFAULT 'from-emerald-500/10 to-teal-500/5',
                    accent_color VARCHAR(20) DEFAULT 'emerald',
                    is_featured BOOLEAN DEFAULT 0,
                    is_active BOOLEAN DEFAULT 1,
                    display_order INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """,
                "CREATE INDEX IF NOT EXISTS ix_success_stories_featured ON success_stories(is_featured)",
                "CREATE INDEX IF NOT EXISTS ix_success_stories_active ON success_stories(is_active)",
                
                # 4. story_timeline_events
                """
                CREATE TABLE IF NOT EXISTS story_timeline_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    story_id INTEGER NOT NULL REFERENCES success_stories(id) ON DELETE CASCADE,
                    event_date VARCHAR(20) NOT NULL,
                    event_text VARCHAR(500) NOT NULL,
                    event_text_zh VARCHAR(500),
                    event_text_en VARCHAR(500),
                    display_order INTEGER DEFAULT 0
                )
                """,
                "CREATE INDEX IF NOT EXISTS ix_story_timeline_story ON story_timeline_events(story_id)",
                
                # 5. story_key_insights
                """
                CREATE TABLE IF NOT EXISTS story_key_insights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    story_id INTEGER NOT NULL REFERENCES success_stories(id) ON DELETE CASCADE,
                    insight_text VARCHAR(300) NOT NULL,
                    insight_text_zh VARCHAR(300),
                    insight_text_en VARCHAR(300),
                    display_order INTEGER DEFAULT 0
                )
                """,
                "CREATE INDEX IF NOT EXISTS ix_story_insights_story ON story_key_insights(story_id)",
                
                # 6. user_preferences
                """
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id VARCHAR(255) NOT NULL REFERENCES user(id) ON DELETE CASCADE,
                    preferred_roles TEXT DEFAULT '[]',
                    interested_categories TEXT DEFAULT '[]',
                    skill_level VARCHAR(20) DEFAULT 'beginner',
                    goal VARCHAR(50),
                    time_commitment VARCHAR(20),
                    tech_stack TEXT DEFAULT '[]',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id)
                )
                """,
                "CREATE INDEX IF NOT EXISTS ix_user_preferences_user ON user_preferences(user_id)",
                
                # 7. featured_creators
                """
                CREATE TABLE IF NOT EXISTS featured_creators (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(200) NOT NULL,
                    handle VARCHAR(100),
                    avatar VARCHAR(20),
                    bio_zh VARCHAR(300),
                    bio_en VARCHAR(300),
                    tag VARCHAR(100),
                    tag_zh VARCHAR(100),
                    tag_en VARCHAR(100),
                    tag_color VARCHAR(20) DEFAULT 'amber',
                    total_mrr VARCHAR(50),
                    followers VARCHAR(50),
                    product_count INTEGER,
                    founder_username VARCHAR(255),
                    is_featured BOOLEAN DEFAULT 1,
                    display_order INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """,
                "CREATE INDEX IF NOT EXISTS ix_featured_creators_featured ON featured_creators(is_featured)",
            ]
        
        for i, stmt in enumerate(statements):
            try:
                await db.execute(text(stmt))
                print(f"  [{i+1}/{len(statements)}] OK")
            except Exception as e:
                if "already exists" in str(e).lower():
                    print(f"  [{i+1}/{len(statements)}] Skipped (already exists)")
                else:
                    print(f"  [{i+1}/{len(statements)}] Error: {e}")
        
        await db.commit()
    
    print("Migration completed: add_discover_tables")


if __name__ == "__main__":
    asyncio.run(migrate())
