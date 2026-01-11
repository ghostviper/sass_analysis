"""
添加 checkpoint_id 字段到 ChatMessage 表

用于支持 Claude Agent SDK 的多轮对话恢复功能
"""

import sys
import os
from pathlib import Path

# 添加 backend 目录到 Python 路径
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# 加载 .env 文件
from dotenv import load_dotenv
env_file = backend_dir / ".env"
if env_file.exists():
    load_dotenv(env_file)
    print(f"✓ 已加载环境变量: {env_file}")
else:
    print(f"⚠ .env 文件不存在: {env_file}")

import asyncio
from sqlalchemy import text
from database.db import AsyncSessionLocal, IS_SQLITE, IS_MYSQL, IS_POSTGRESQL


async def add_checkpoint_id_column():
    """添加 checkpoint_id 列到 chat_messages 表"""
    async with AsyncSessionLocal() as db:
        try:
            # 检查列是否已存在
            if IS_SQLITE:
                result = await db.execute(text("PRAGMA table_info(chat_messages)"))
                columns = [row[1] for row in result.fetchall()]
            elif IS_MYSQL:
                result = await db.execute(text(
                    "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS "
                    "WHERE TABLE_NAME = 'chat_messages' AND COLUMN_NAME = 'checkpoint_id'"
                ))
                columns = [row[0] for row in result.fetchall()]
            elif IS_POSTGRESQL:
                result = await db.execute(text(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_name = 'chat_messages' AND column_name = 'checkpoint_id'"
                ))
                columns = [row[0] for row in result.fetchall()]
            else:
                print("Unknown database type")
                return

            if 'checkpoint_id' in columns or 'checkpoint_id' in [c.lower() for c in columns]:
                print("✓ checkpoint_id 列已存在")
                return

            # 添加列
            print("正在添加 checkpoint_id 列...")
            
            if IS_SQLITE:
                await db.execute(text(
                    "ALTER TABLE chat_messages ADD COLUMN checkpoint_id VARCHAR(64)"
                ))
            elif IS_MYSQL:
                await db.execute(text(
                    "ALTER TABLE chat_messages ADD COLUMN checkpoint_id VARCHAR(64)"
                ))
                # 添加索引
                await db.execute(text(
                    "CREATE INDEX ix_chat_messages_checkpoint_id ON chat_messages(checkpoint_id)"
                ))
            elif IS_POSTGRESQL:
                await db.execute(text(
                    "ALTER TABLE chat_messages ADD COLUMN checkpoint_id VARCHAR(64)"
                ))
                # 添加索引
                await db.execute(text(
                    "CREATE INDEX ix_chat_messages_checkpoint_id ON chat_messages(checkpoint_id)"
                ))

            await db.commit()
            print("✓ checkpoint_id 列添加成功")

        except Exception as e:
            print(f"✗ 添加列失败: {e}")
            await db.rollback()
            raise


async def main():
    """运行迁移"""
    print("=" * 60)
    print("开始数据库迁移: 添加 checkpoint_id 字段")
    print("=" * 60)
    
    # 显示数据库类型
    from database.db import DATABASE_URL, DB_TYPE
    print(f"\n数据库类型: {DB_TYPE}")
    print(f"连接字符串: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else 'SQLite'}")
    print()
    
    await add_checkpoint_id_column()
    
    print("\n" + "=" * 60)
    print("迁移完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
