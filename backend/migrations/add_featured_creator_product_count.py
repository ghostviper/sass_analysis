"""
Add product_count column to featured_creators table

运行方式：
    cd backend
    python -m migrations.add_featured_creator_product_count
"""

import asyncio
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

from sqlalchemy import text
from database.db import get_db_session, IS_POSTGRESQL


async def migrate():
    """执行迁移"""
    print(f"Database: {'PostgreSQL' if IS_POSTGRESQL else 'SQLite'}")
    print("Starting migration: add_featured_creator_product_count")
    
    async with get_db_session() as db:
        try:
            if IS_POSTGRESQL:
                await db.execute(text(
                    "ALTER TABLE featured_creators ADD COLUMN IF NOT EXISTS product_count INTEGER"
                ))
            else:
                # SQLite doesn't support IF NOT EXISTS for columns
                # Check if column exists first
                result = await db.execute(text("PRAGMA table_info(featured_creators)"))
                columns = [row[1] for row in result.fetchall()]
                if 'product_count' not in columns:
                    await db.execute(text(
                        "ALTER TABLE featured_creators ADD COLUMN product_count INTEGER"
                    ))
            
            await db.commit()
            print("Migration completed successfully!")
        except Exception as e:
            if "already exists" in str(e).lower() or "duplicate column" in str(e).lower():
                print("Column already exists, skipping")
            else:
                print(f"Error: {e}")
                raise


if __name__ == "__main__":
    asyncio.run(migrate())
