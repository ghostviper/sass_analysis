"""
添加专题表的国际化字段

为 discover_topics 表添加双语支持字段：
- title_zh, title_en
- description_zh, description_en  
- cta_text_zh, cta_text_en
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
    async with get_db_session() as db:
        # 检查字段是否已存在
        if IS_POSTGRESQL:
            check_sql = """
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'discover_topics' AND column_name = 'title_zh'
            """
        else:
            check_sql = "PRAGMA table_info(discover_topics)"
        
        result = await db.execute(text(check_sql))
        existing = result.fetchall()
        
        # PostgreSQL 检查
        if IS_POSTGRESQL:
            if existing:
                print("双语字段已存在，跳过迁移")
                return
        else:
            # SQLite 检查
            columns = [row[1] for row in existing]
            if 'title_zh' in columns:
                print("双语字段已存在，跳过迁移")
                return
        
        print("开始添加双语字段...")
        
        # 添加新字段
        alter_statements = [
            "ALTER TABLE discover_topics ADD COLUMN title_zh VARCHAR(200)",
            "ALTER TABLE discover_topics ADD COLUMN title_en VARCHAR(200)",
            "ALTER TABLE discover_topics ADD COLUMN description_zh TEXT",
            "ALTER TABLE discover_topics ADD COLUMN description_en TEXT",
            "ALTER TABLE discover_topics ADD COLUMN cta_text_zh VARCHAR(200)",
            "ALTER TABLE discover_topics ADD COLUMN cta_text_en VARCHAR(200)",
        ]
        
        for stmt in alter_statements:
            try:
                await db.execute(text(stmt))
                print(f"  执行: {stmt[:50]}...")
            except Exception as e:
                print(f"  跳过 (可能已存在): {e}")
        
        # 将现有数据复制到中文字段
        update_sql = """
            UPDATE discover_topics 
            SET title_zh = title, 
                description_zh = description,
                cta_text_zh = cta_text
            WHERE title_zh IS NULL
        """
        await db.execute(text(update_sql))
        
        await db.commit()
        print("迁移完成！")


if __name__ == "__main__":
    asyncio.run(migrate())
