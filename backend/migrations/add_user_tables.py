"""
用户体系数据库迁移脚本

创建 better-auth 所需的表结构：
- users: 用户表（扩展字段）
- accounts: 第三方账户关联表
- sessions: 会话表
- verifications: 验证令牌表

同时更新 chat_sessions 表添加 user_id 字段
"""

import asyncio
import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# 加载 .env 文件
from dotenv import load_dotenv
load_dotenv(backend_dir / ".env")

from sqlalchemy import text
from database.db import engine, IS_SQLITE, IS_POSTGRESQL, IS_MYSQL


async def run_migration():
    """执行迁移"""
    print("[Migration] Starting user tables migration...")
    
    async with engine.begin() as conn:
        # 检查 users 表是否已存在
        if IS_SQLITE:
            result = await conn.execute(text(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='user'"
            ))
        elif IS_POSTGRESQL:
            result = await conn.execute(text(
                "SELECT tablename FROM pg_tables WHERE tablename='user'"
            ))
        else:  # MySQL
            result = await conn.execute(text(
                "SELECT table_name FROM information_schema.tables WHERE table_name='user'"
            ))
        
        if result.fetchone():
            print("[Migration] User tables already exist, skipping creation...")
        else:
            print("[Migration] Creating user tables...")
            
            # better-auth 使用的表名是 user, account, session, verification
            # 注意：better-auth 会自动创建这些表，这里只是预创建以添加扩展字段
            
            if IS_POSTGRESQL:
                # PostgreSQL DDL
                await conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS "user" (
                        id TEXT PRIMARY KEY,
                        email TEXT UNIQUE NOT NULL,
                        email_verified BOOLEAN DEFAULT FALSE,
                        name TEXT,
                        image TEXT,
                        
                        -- 扩展字段
                        plan TEXT DEFAULT 'free',
                        plan_expires_at TIMESTAMP,
                        locale TEXT DEFAULT 'zh-CN',
                        daily_chat_limit INTEGER DEFAULT 10,
                        daily_chat_used INTEGER DEFAULT 0,
                        total_tokens_used BIGINT DEFAULT 0,
                        preferences JSONB DEFAULT '{}',
                        
                        created_at TIMESTAMP DEFAULT NOW(),
                        updated_at TIMESTAMP DEFAULT NOW()
                    )
                """))
                
                await conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS account (
                        id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
                        account_id TEXT NOT NULL,
                        provider_id TEXT NOT NULL,
                        access_token TEXT,
                        refresh_token TEXT,
                        access_token_expires_at TIMESTAMP,
                        scope TEXT,
                        id_token TEXT,
                        password TEXT,
                        created_at TIMESTAMP DEFAULT NOW(),
                        updated_at TIMESTAMP DEFAULT NOW(),
                        UNIQUE(provider_id, account_id)
                    )
                """))
                
                await conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS session (
                        id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
                        token TEXT UNIQUE NOT NULL,
                        expires_at TIMESTAMP NOT NULL,
                        ip_address TEXT,
                        user_agent TEXT,
                        created_at TIMESTAMP DEFAULT NOW(),
                        updated_at TIMESTAMP DEFAULT NOW()
                    )
                """))
                
                await conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS verification (
                        id TEXT PRIMARY KEY,
                        identifier TEXT NOT NULL,
                        value TEXT NOT NULL,
                        expires_at TIMESTAMP NOT NULL,
                        created_at TIMESTAMP DEFAULT NOW(),
                        updated_at TIMESTAMP DEFAULT NOW()
                    )
                """))
                
                # 创建索引
                await conn.execute(text('CREATE INDEX IF NOT EXISTS idx_user_email ON "user"(email)'))
                await conn.execute(text('CREATE INDEX IF NOT EXISTS idx_account_user_id ON account(user_id)'))
                await conn.execute(text('CREATE INDEX IF NOT EXISTS idx_session_user_id ON session(user_id)'))
                await conn.execute(text('CREATE INDEX IF NOT EXISTS idx_session_token ON session(token)'))
                await conn.execute(text('CREATE INDEX IF NOT EXISTS idx_verification_identifier ON verification(identifier)'))
                
            elif IS_SQLITE:
                # SQLite DDL
                await conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS user (
                        id TEXT PRIMARY KEY,
                        email TEXT UNIQUE NOT NULL,
                        email_verified INTEGER DEFAULT 0,
                        name TEXT,
                        image TEXT,
                        
                        plan TEXT DEFAULT 'free',
                        plan_expires_at TEXT,
                        locale TEXT DEFAULT 'zh-CN',
                        daily_chat_limit INTEGER DEFAULT 10,
                        daily_chat_used INTEGER DEFAULT 0,
                        total_tokens_used INTEGER DEFAULT 0,
                        preferences TEXT DEFAULT '{}',
                        
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                await conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS account (
                        id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL REFERENCES user(id) ON DELETE CASCADE,
                        account_id TEXT NOT NULL,
                        provider_id TEXT NOT NULL,
                        access_token TEXT,
                        refresh_token TEXT,
                        access_token_expires_at TEXT,
                        scope TEXT,
                        id_token TEXT,
                        password TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(provider_id, account_id)
                    )
                """))
                
                await conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS session (
                        id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL REFERENCES user(id) ON DELETE CASCADE,
                        token TEXT UNIQUE NOT NULL,
                        expires_at TEXT NOT NULL,
                        ip_address TEXT,
                        user_agent TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                await conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS verification (
                        id TEXT PRIMARY KEY,
                        identifier TEXT NOT NULL,
                        value TEXT NOT NULL,
                        expires_at TEXT NOT NULL,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # SQLite 索引
                await conn.execute(text('CREATE INDEX IF NOT EXISTS idx_user_email ON user(email)'))
                await conn.execute(text('CREATE INDEX IF NOT EXISTS idx_account_user_id ON account(user_id)'))
                await conn.execute(text('CREATE INDEX IF NOT EXISTS idx_session_user_id ON session(user_id)'))
                await conn.execute(text('CREATE INDEX IF NOT EXISTS idx_session_token ON session(token)'))
                await conn.execute(text('CREATE INDEX IF NOT EXISTS idx_verification_identifier ON verification(identifier)'))
            
            else:  # MySQL
                # MySQL DDL
                await conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS user (
                        id VARCHAR(255) PRIMARY KEY,
                        email VARCHAR(255) UNIQUE NOT NULL,
                        email_verified BOOLEAN DEFAULT FALSE,
                        name VARCHAR(255),
                        image VARCHAR(512),
                        
                        plan VARCHAR(20) DEFAULT 'free',
                        plan_expires_at DATETIME,
                        locale VARCHAR(10) DEFAULT 'zh-CN',
                        daily_chat_limit INT DEFAULT 10,
                        daily_chat_used INT DEFAULT 0,
                        total_tokens_used BIGINT DEFAULT 0,
                        preferences JSON,
                        
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        
                        INDEX idx_user_email (email)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """))
                
                await conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS account (
                        id VARCHAR(255) PRIMARY KEY,
                        user_id VARCHAR(255) NOT NULL,
                        account_id VARCHAR(255) NOT NULL,
                        provider_id VARCHAR(255) NOT NULL,
                        access_token TEXT,
                        refresh_token TEXT,
                        access_token_expires_at DATETIME,
                        scope TEXT,
                        id_token TEXT,
                        password VARCHAR(255),
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        
                        UNIQUE KEY unique_provider_account (provider_id, account_id),
                        INDEX idx_account_user_id (user_id),
                        FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """))
                
                await conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS session (
                        id VARCHAR(255) PRIMARY KEY,
                        user_id VARCHAR(255) NOT NULL,
                        token VARCHAR(255) UNIQUE NOT NULL,
                        expires_at DATETIME NOT NULL,
                        ip_address VARCHAR(45),
                        user_agent TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        
                        INDEX idx_session_user_id (user_id),
                        INDEX idx_session_token (token),
                        FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """))
                
                await conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS verification (
                        id VARCHAR(255) PRIMARY KEY,
                        identifier VARCHAR(255) NOT NULL,
                        value VARCHAR(255) NOT NULL,
                        expires_at DATETIME NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        
                        INDEX idx_verification_identifier (identifier)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """))
            
            print("[Migration] User tables created successfully!")
        
        # 更新 chat_sessions 表添加 user_id 字段
        print("[Migration] Checking chat_sessions table for user_id column...")
        
        try:
            if IS_SQLITE:
                # SQLite 检查列是否存在
                result = await conn.execute(text("PRAGMA table_info(chat_sessions)"))
                columns = [row[1] for row in result.fetchall()]
                if 'user_id' not in columns:
                    await conn.execute(text("ALTER TABLE chat_sessions ADD COLUMN user_id TEXT"))
                    print("[Migration] Added user_id column to chat_sessions")
                else:
                    print("[Migration] user_id column already exists in chat_sessions")
            elif IS_POSTGRESQL:
                # PostgreSQL 检查并添加列
                result = await conn.execute(text("""
                    SELECT column_name FROM information_schema.columns 
                    WHERE table_name='chat_sessions' AND column_name='user_id'
                """))
                if not result.fetchone():
                    await conn.execute(text("ALTER TABLE chat_sessions ADD COLUMN user_id TEXT"))
                    await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id ON chat_sessions(user_id)"))
                    print("[Migration] Added user_id column to chat_sessions")
                else:
                    print("[Migration] user_id column already exists in chat_sessions")
            else:  # MySQL
                result = await conn.execute(text("""
                    SELECT column_name FROM information_schema.columns 
                    WHERE table_name='chat_sessions' AND column_name='user_id'
                """))
                if not result.fetchone():
                    await conn.execute(text("ALTER TABLE chat_sessions ADD COLUMN user_id VARCHAR(255)"))
                    await conn.execute(text("CREATE INDEX idx_chat_sessions_user_id ON chat_sessions(user_id)"))
                    print("[Migration] Added user_id column to chat_sessions")
                else:
                    print("[Migration] user_id column already exists in chat_sessions")
        except Exception as e:
            print(f"[Migration] Warning: Could not update chat_sessions: {e}")
    
    print("[Migration] Migration completed!")


if __name__ == "__main__":
    asyncio.run(run_migration())
