"""
添加 verification 表

用于邮箱验证和密码重置功能
"""

import asyncio
import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from dotenv import load_dotenv
load_dotenv(backend_dir / ".env")

from sqlalchemy import text
from database.db import engine, IS_POSTGRESQL, IS_SQLITE

async def run_migration():
    print("[Migration] Adding verification table...")
    
    async with engine.begin() as conn:
        # 检查表是否已存在
        if IS_POSTGRESQL:
            result = await conn.execute(text(
                "SELECT tablename FROM pg_tables WHERE tablename='verification'"
            ))
        else:  # SQLite
            result = await conn.execute(text(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='verification'"
            ))
        
        if result.fetchone():
            print("[Migration] verification table already exists")
            return
        
        # 创建表
        if IS_POSTGRESQL:
            await conn.execute(text('''
                CREATE TABLE verification (
                    id TEXT PRIMARY KEY,
                    identifier TEXT NOT NULL,
                    value TEXT NOT NULL,
                    "expiresAt" TIMESTAMP NOT NULL,
                    "createdAt" TIMESTAMP DEFAULT NOW(),
                    "updatedAt" TIMESTAMP DEFAULT NOW()
                )
            '''))
            await conn.execute(text('CREATE INDEX idx_verification_identifier ON verification(identifier)'))
            await conn.execute(text('CREATE INDEX idx_verification_value ON verification(value)'))
        else:  # SQLite
            await conn.execute(text('''
                CREATE TABLE verification (
                    id TEXT PRIMARY KEY,
                    identifier TEXT NOT NULL,
                    value TEXT NOT NULL,
                    expiresAt TEXT NOT NULL,
                    createdAt TEXT DEFAULT CURRENT_TIMESTAMP,
                    updatedAt TEXT DEFAULT CURRENT_TIMESTAMP
                )
            '''))
            await conn.execute(text('CREATE INDEX idx_verification_identifier ON verification(identifier)'))
            await conn.execute(text('CREATE INDEX idx_verification_value ON verification(value)'))
        
        print("[Migration] verification table created successfully!")

if __name__ == "__main__":
    asyncio.run(run_migration())
