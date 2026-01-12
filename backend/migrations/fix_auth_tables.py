"""
修复 better-auth 表结构

better-auth 使用 camelCase 列名，需要重建表
"""

import asyncio
import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from dotenv import load_dotenv
load_dotenv(backend_dir / ".env")

from sqlalchemy import text
from database.db import engine, IS_POSTGRESQL

async def run_migration():
    print("[Migration] Fixing auth tables for better-auth...")
    
    if not IS_POSTGRESQL:
        print("[Migration] This script only supports PostgreSQL")
        return
    
    async with engine.begin() as conn:
        # 删除旧表
        print("[Migration] Dropping old tables...")
        await conn.execute(text('DROP TABLE IF EXISTS verification CASCADE'))
        await conn.execute(text('DROP TABLE IF EXISTS session CASCADE'))
        await conn.execute(text('DROP TABLE IF EXISTS account CASCADE'))
        await conn.execute(text('DROP TABLE IF EXISTS "user" CASCADE'))
        
        # 创建新表 - 使用 better-auth 期望的 camelCase 列名
        print("[Migration] Creating user table...")
        await conn.execute(text('''
            CREATE TABLE "user" (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                "emailVerified" BOOLEAN DEFAULT FALSE,
                name TEXT,
                image TEXT,
                "createdAt" TIMESTAMP DEFAULT NOW(),
                "updatedAt" TIMESTAMP DEFAULT NOW(),
                -- additionalFields from auth.ts
                plan TEXT DEFAULT 'free',
                locale TEXT DEFAULT 'zh-CN',
                "dailyChatLimit" INTEGER DEFAULT 10,
                "dailyChatUsed" INTEGER DEFAULT 0
            )
        '''))
        
        print("[Migration] Creating account table...")
        await conn.execute(text('''
            CREATE TABLE account (
                id TEXT PRIMARY KEY,
                "userId" TEXT NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
                "accountId" TEXT NOT NULL,
                "providerId" TEXT NOT NULL,
                "accessToken" TEXT,
                "refreshToken" TEXT,
                "accessTokenExpiresAt" TIMESTAMP,
                scope TEXT,
                "idToken" TEXT,
                password TEXT,
                "createdAt" TIMESTAMP DEFAULT NOW(),
                "updatedAt" TIMESTAMP DEFAULT NOW(),
                UNIQUE("providerId", "accountId")
            )
        '''))
        
        print("[Migration] Creating session table...")
        await conn.execute(text('''
            CREATE TABLE session (
                id TEXT PRIMARY KEY,
                "userId" TEXT NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
                token TEXT UNIQUE NOT NULL,
                "expiresAt" TIMESTAMP NOT NULL,
                "ipAddress" TEXT,
                "userAgent" TEXT,
                "createdAt" TIMESTAMP DEFAULT NOW(),
                "updatedAt" TIMESTAMP DEFAULT NOW()
            )
        '''))
        
        print("[Migration] Creating verification table...")
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
        
        # 创建索引
        print("[Migration] Creating indexes...")
        await conn.execute(text('CREATE INDEX idx_user_email ON "user"(email)'))
        await conn.execute(text('CREATE INDEX idx_account_user_id ON account("userId")'))
        await conn.execute(text('CREATE INDEX idx_session_user_id ON session("userId")'))
        await conn.execute(text('CREATE INDEX idx_session_token ON session(token)'))
        await conn.execute(text('CREATE INDEX idx_verification_identifier ON verification(identifier)'))
        
    print("[Migration] Done! Auth tables created with camelCase columns.")

if __name__ == "__main__":
    asyncio.run(run_migration())
