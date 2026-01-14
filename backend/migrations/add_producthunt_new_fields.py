"""
迁移脚本：为 producthunt_posts 表添加新字段

新增字段:
- website: 产品真实官网地址
- user: 创建者信息 (JSON)
- media: 媒体资源 (JSON)
- product_links: 产品链接 (JSON)

运行方式:
    python migrations/add_producthunt_new_fields.py
"""

import os
import sys
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import text
from database.db import engine

DATABASE_URL = os.getenv("DATABASE_URL", "")
IS_SQLITE = DATABASE_URL.startswith("sqlite")
IS_POSTGRESQL = DATABASE_URL.startswith("postgresql")
IS_MYSQL = DATABASE_URL.startswith("mysql")


async def column_exists(conn, table: str, column: str) -> bool:
    """检查列是否存在"""
    if IS_SQLITE:
        result = await conn.execute(text(f"PRAGMA table_info({table})"))
        columns = [row[1] for row in result.fetchall()]
        return column in columns
    elif IS_POSTGRESQL:
        result = await conn.execute(text(f"""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = '{table}' AND column_name = '{column}'
        """))
        return result.fetchone() is not None
    else:  # MySQL
        result = await conn.execute(text(f"""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = '{table}' AND column_name = '{column}'
        """))
        return result.fetchone() is not None


async def run_migration():
    print("[Migration] Adding new fields to producthunt_posts...")
    
    new_columns = [
        ("website", "VARCHAR(512)", "TEXT"),
        ("website_resolved", "VARCHAR(512)", "TEXT"),
        ("user", "TEXT", "TEXT"),
        ("media", "TEXT", "TEXT"),
        ("product_links", "TEXT", "TEXT"),
    ]
    
    async with engine.begin() as conn:
        for col_name, pg_type, sqlite_type in new_columns:
            exists = await column_exists(conn, "producthunt_posts", col_name)
            if exists:
                print(f"  [Skip] Column '{col_name}' already exists")
                continue
            
            print(f"  [Add] Adding column '{col_name}'...")
            
            if IS_SQLITE:
                await conn.execute(text(f"ALTER TABLE producthunt_posts ADD COLUMN {col_name} {sqlite_type}"))
            elif IS_POSTGRESQL:
                # PostgreSQL 中 user 是保留字，需要加引号
                col_ref = f'"{col_name}"' if col_name == "user" else col_name
                await conn.execute(text(f"ALTER TABLE producthunt_posts ADD COLUMN {col_ref} {pg_type}"))
            else:  # MySQL
                await conn.execute(text(f"ALTER TABLE producthunt_posts ADD COLUMN {col_name} {pg_type}"))
            
            print(f"  [Done] Column '{col_name}' added")
    
    print("[Migration] Completed!")


if __name__ == "__main__":
    asyncio.run(run_migration())
