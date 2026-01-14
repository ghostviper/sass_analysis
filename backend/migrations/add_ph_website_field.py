"""
添加 producthunt_posts.website 字段

用于存储产品的真实官网地址（之前的 url 字段存的是 PH 跟踪链接）
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import text
from database.db import engine


async def migrate():
    async with engine.begin() as conn:
        # 检查字段是否已存在
        result = await conn.execute(text("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'producthunt_posts' AND column_name = 'website'
        """))
        if result.fetchone():
            print("[Skip] website column already exists")
            return
        
        # 添加 website 字段
        await conn.execute(text("""
            ALTER TABLE producthunt_posts 
            ADD COLUMN website VARCHAR(512)
        """))
        print("[Done] Added website column to producthunt_posts")


if __name__ == "__main__":
    asyncio.run(migrate())
