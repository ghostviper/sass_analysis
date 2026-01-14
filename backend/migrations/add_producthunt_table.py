"""
迁移脚本：创建 Product Hunt 数据表

运行方式:
    python migrations/add_producthunt_table.py
"""

import os
import sys
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import text
from database.db import engine

# 检测数据库类型
DATABASE_URL = os.getenv("DATABASE_URL", "")
IS_SQLITE = DATABASE_URL.startswith("sqlite")
IS_POSTGRESQL = DATABASE_URL.startswith("postgresql")
IS_MYSQL = DATABASE_URL.startswith("mysql")


async def run_migration():
    print("[Migration] Creating Product Hunt tables...")
    
    async with engine.begin() as conn:
        # 先删除旧表（如果存在）
        print("[Migration] Dropping existing table if exists...")
        if IS_POSTGRESQL:
            await conn.execute(text("DROP TABLE IF EXISTS producthunt_posts CASCADE"))
        else:
            await conn.execute(text("DROP TABLE IF EXISTS producthunt_posts"))
        
        # 创建表
        print("[Migration] Creating producthunt_posts table...")
        
        if IS_SQLITE:
            await conn.execute(text("""
                CREATE TABLE producthunt_posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ph_id VARCHAR(50) UNIQUE NOT NULL,
                    slug VARCHAR(255) UNIQUE NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    tagline VARCHAR(500),
                    description TEXT,
                    url VARCHAR(512),
                    website VARCHAR(512),
                    website_resolved VARCHAR(512),
                    ph_url VARCHAR(512),
                    thumbnail_url VARCHAR(512),
                    votes_count INTEGER DEFAULT 0,
                    comments_count INTEGER DEFAULT 0,
                    reviews_count INTEGER DEFAULT 0,
                    reviews_rating REAL,
                    featured_at DATETIME,
                    ph_created_at DATETIME,
                    topics TEXT,
                    makers TEXT,
                    user TEXT,
                    media TEXT,
                    product_links TEXT,
                    matched_startup_id INTEGER REFERENCES startups(id) ON DELETE SET NULL,
                    match_confidence REAL,
                    raw_data TEXT,
                    synced_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """))
            await conn.execute(text("CREATE INDEX ix_ph_posts_ph_id ON producthunt_posts(ph_id)"))
            await conn.execute(text("CREATE INDEX ix_ph_posts_slug ON producthunt_posts(slug)"))
            await conn.execute(text("CREATE INDEX ix_ph_posts_name ON producthunt_posts(name)"))
            await conn.execute(text("CREATE INDEX ix_ph_posts_votes ON producthunt_posts(votes_count)"))
            await conn.execute(text("CREATE INDEX ix_ph_posts_featured ON producthunt_posts(featured_at)"))
            await conn.execute(text("CREATE INDEX ix_ph_posts_synced ON producthunt_posts(synced_at)"))
            await conn.execute(text("CREATE INDEX ix_ph_posts_matched ON producthunt_posts(matched_startup_id)"))
            
        elif IS_POSTGRESQL:
            await conn.execute(text("""
                CREATE TABLE producthunt_posts (
                    id SERIAL PRIMARY KEY,
                    ph_id VARCHAR(50) UNIQUE NOT NULL,
                    slug VARCHAR(255) UNIQUE NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    tagline VARCHAR(500),
                    description TEXT,
                    url VARCHAR(512),
                    website VARCHAR(512),
                    website_resolved VARCHAR(512),
                    ph_url VARCHAR(512),
                    thumbnail_url VARCHAR(512),
                    votes_count INTEGER DEFAULT 0,
                    comments_count INTEGER DEFAULT 0,
                    reviews_count INTEGER DEFAULT 0,
                    reviews_rating FLOAT,
                    featured_at TIMESTAMP,
                    ph_created_at TIMESTAMP,
                    topics TEXT,
                    makers TEXT,
                    "user" TEXT,
                    media TEXT,
                    product_links TEXT,
                    matched_startup_id INTEGER REFERENCES startups(id) ON DELETE SET NULL,
                    match_confidence FLOAT,
                    raw_data TEXT,
                    synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            await conn.execute(text("CREATE INDEX ix_ph_posts_ph_id ON producthunt_posts(ph_id)"))
            await conn.execute(text("CREATE INDEX ix_ph_posts_slug ON producthunt_posts(slug)"))
            await conn.execute(text("CREATE INDEX ix_ph_posts_name ON producthunt_posts(name)"))
            await conn.execute(text("CREATE INDEX ix_ph_posts_votes ON producthunt_posts(votes_count DESC)"))
            await conn.execute(text("CREATE INDEX ix_ph_posts_featured ON producthunt_posts(featured_at DESC)"))
            await conn.execute(text("CREATE INDEX ix_ph_posts_synced ON producthunt_posts(synced_at DESC)"))
            await conn.execute(text("CREATE INDEX ix_ph_posts_matched ON producthunt_posts(matched_startup_id)"))
            
        else:  # MySQL
            await conn.execute(text("""
                CREATE TABLE producthunt_posts (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    ph_id VARCHAR(50) UNIQUE NOT NULL,
                    slug VARCHAR(255) UNIQUE NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    tagline VARCHAR(500),
                    description TEXT,
                    url VARCHAR(512),
                    website VARCHAR(512),
                    website_resolved VARCHAR(512),
                    ph_url VARCHAR(512),
                    thumbnail_url VARCHAR(512),
                    votes_count INT DEFAULT 0,
                    comments_count INT DEFAULT 0,
                    reviews_count INT DEFAULT 0,
                    reviews_rating FLOAT,
                    featured_at DATETIME,
                    ph_created_at DATETIME,
                    topics TEXT,
                    makers TEXT,
                    user TEXT,
                    media TEXT,
                    product_links TEXT,
                    matched_startup_id INT,
                    match_confidence FLOAT,
                    raw_data TEXT,
                    synced_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (matched_startup_id) REFERENCES startups(id) ON DELETE SET NULL,
                    INDEX ix_ph_posts_ph_id (ph_id),
                    INDEX ix_ph_posts_slug (slug),
                    INDEX ix_ph_posts_name (name),
                    INDEX ix_ph_posts_votes (votes_count),
                    INDEX ix_ph_posts_featured (featured_at),
                    INDEX ix_ph_posts_synced (synced_at),
                    INDEX ix_ph_posts_matched (matched_startup_id)
                )
            """))
        
        print("[Migration] Table 'producthunt_posts' created successfully!")
    
    print("[Migration] Product Hunt migration completed!")


if __name__ == "__main__":
    asyncio.run(run_migration())
