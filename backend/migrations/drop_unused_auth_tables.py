"""
删除未使用的认证表

当前使用 JWT 无状态认证，不需要以下表：
- session: 登录会话表
- verification: 验证令牌表
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
    print("[Migration] Dropping unused auth tables...")
    
    async with engine.begin() as conn:
        # 删除 session 表
        print("[Migration] Dropping session table...")
        try:
            await conn.execute(text('DROP TABLE IF EXISTS session CASCADE'))
            print("[Migration] session table dropped")
        except Exception as e:
            print(f"[Migration] Warning: {e}")
        
        # 删除 verification 表
        print("[Migration] Dropping verification table...")
        try:
            await conn.execute(text('DROP TABLE IF EXISTS verification CASCADE'))
            print("[Migration] verification table dropped")
        except Exception as e:
            print(f"[Migration] Warning: {e}")
    
    print("[Migration] Done! Unused tables removed.")

if __name__ == "__main__":
    asyncio.run(run_migration())
