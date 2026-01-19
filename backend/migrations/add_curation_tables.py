"""
Migration: Add curation system tables

Tables:
- mother_theme_judgments: 母题判断结果
- discover_topics: 发现页专题
- topic_products: 专题-产品关联

Run: python -m migrations.add_curation_tables
"""

import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Load .env before any other imports
load_dotenv(Path(__file__).parent.parent / ".env")

from sqlalchemy import text
from database.db import engine, IS_POSTGRESQL, IS_SQLITE


POSTGRESQL_SQL = """
-- 母题判断结果表
CREATE TABLE IF NOT EXISTS mother_theme_judgments (
    id SERIAL PRIMARY KEY,
    startup_id INTEGER NOT NULL REFERENCES startups(id) ON DELETE CASCADE,
    theme_key VARCHAR(50) NOT NULL,
    judgment VARCHAR(100),
    confidence VARCHAR(20),
    reasons JSONB,
    evidence_fields JSONB,
    uncertainties JSONB,
    prompt_version VARCHAR(20),
    model VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Unique index: one judgment per startup per theme
CREATE UNIQUE INDEX IF NOT EXISTS ix_judgment_startup_theme 
ON mother_theme_judgments(startup_id, theme_key);

-- Index for querying by theme
CREATE INDEX IF NOT EXISTS ix_mother_theme_judgments_theme_key 
ON mother_theme_judgments(theme_key);

-- 发现页专题表
CREATE TABLE IF NOT EXISTS discover_topics (
    id SERIAL PRIMARY KEY,
    topic_key VARCHAR(100) UNIQUE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    curator_role VARCHAR(50),
    generation_pattern VARCHAR(50),
    filter_rules JSONB,
    cta_text VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 专题-产品关联表
CREATE TABLE IF NOT EXISTS topic_products (
    id SERIAL PRIMARY KEY,
    topic_id INTEGER NOT NULL REFERENCES discover_topics(id) ON DELETE CASCADE,
    startup_id INTEGER NOT NULL REFERENCES startups(id) ON DELETE CASCADE,
    ai_label VARCHAR(200),
    counter_intuitive_point TEXT,
    display_order INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS ix_topic_products_topic_id ON topic_products(topic_id);
CREATE INDEX IF NOT EXISTS ix_topic_products_startup_id ON topic_products(startup_id);
"""

SQLITE_SQL = """
-- 母题判断结果表
CREATE TABLE IF NOT EXISTS mother_theme_judgments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    startup_id INTEGER NOT NULL REFERENCES startups(id) ON DELETE CASCADE,
    theme_key VARCHAR(50) NOT NULL,
    judgment VARCHAR(100),
    confidence VARCHAR(20),
    reasons JSON,
    evidence_fields JSON,
    uncertainties JSON,
    prompt_version VARCHAR(20),
    model VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS ix_judgment_startup_theme 
ON mother_theme_judgments(startup_id, theme_key);

CREATE INDEX IF NOT EXISTS ix_mother_theme_judgments_theme_key 
ON mother_theme_judgments(theme_key);

-- 发现页专题表
CREATE TABLE IF NOT EXISTS discover_topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_key VARCHAR(100) UNIQUE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    curator_role VARCHAR(50),
    generation_pattern VARCHAR(50),
    filter_rules JSON,
    cta_text VARCHAR(200),
    is_active BOOLEAN DEFAULT 1,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 专题-产品关联表
CREATE TABLE IF NOT EXISTS topic_products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id INTEGER NOT NULL REFERENCES discover_topics(id) ON DELETE CASCADE,
    startup_id INTEGER NOT NULL REFERENCES startups(id) ON DELETE CASCADE,
    ai_label VARCHAR(200),
    counter_intuitive_point TEXT,
    display_order INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS ix_topic_products_topic_id ON topic_products(topic_id);
CREATE INDEX IF NOT EXISTS ix_topic_products_startup_id ON topic_products(startup_id);
"""


async def run_migration():
    """Run the migration"""
    sql = POSTGRESQL_SQL if IS_POSTGRESQL else SQLITE_SQL
    
    print(f"[Migration] Running on {'PostgreSQL' if IS_POSTGRESQL else 'SQLite'}...")
    
    async with engine.begin() as conn:
        # Split and execute each statement
        for statement in sql.split(';'):
            statement = statement.strip()
            if statement:
                await conn.execute(text(statement))
    
    print("[Migration] Curation tables created successfully!")
    print("  - mother_theme_judgments")
    print("  - discover_topics")
    print("  - topic_products")


if __name__ == "__main__":
    asyncio.run(run_migration())
