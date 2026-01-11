"""
直接运行 PostgreSQL 迁移脚本
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
from database.db import AsyncSessionLocal, DATABASE_URL, DB_TYPE, IS_POSTGRESQL
async def run_migration():
    """运行 PostgreSQL 迁移"""
    print("=" * 60)
    print("PostgreSQL 数据库迁移")
    print("=" * 60)
    
    # 检查数据库类型
    print(f"\n数据库类型: {DB_TYPE}")
    if '@' in DATABASE_URL:
        display_url = DATABASE_URL.split('@')[-1]
        print(f"连接地址: {display_url}")
    
    if not IS_POSTGRESQL:
        print(f"\n⚠ 警告: 当前数据库类型是 {DB_TYPE}，不是 PostgreSQL")
        print("此脚本仅适用于 PostgreSQL 数据库")
        print("\n请检查 .env 文件中的 DATABASE_URL 配置")
        return False
    
    # 读取 SQL 文件
    sql_file = Path(__file__).parent / "add_checkpoint_id_postgres.sql"
    if not sql_file.exists():
        print(f"\n✗ SQL 文件不存在: {sql_file}")
        return False
    
    print(f"\n读取 SQL 文件: {sql_file.name}")
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # 执行迁移
    async with AsyncSessionLocal() as db:
        try:
            print("\n正在执行迁移...")
            
            # 执行 SQL
            await db.execute(text(sql_content))
            await db.commit()
            
            print("\n✓ 迁移执行成功")
            
            # 验证结果
            print("\n验证字段...")
            result = await db.execute(text("""
                SELECT 
                    column_name, 
                    data_type, 
                    character_maximum_length,
                    is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'chat_messages' 
                AND column_name = 'checkpoint_id'
            """))
            
            row = result.fetchone()
            if row:
                print(f"✓ 字段信息:")
                print(f"  名称: {row[0]}")
                print(f"  类型: {row[1]}")
                print(f"  长度: {row[2]}")
                print(f"  可空: {row[3]}")
            else:
                print("✗ 未找到 checkpoint_id 字段")
                return False
            
            # 检查索引
            print("\n检查索引...")
            result = await db.execute(text("""
                SELECT indexname 
                FROM pg_indexes 
                WHERE tablename = 'chat_messages' 
                AND indexname = 'ix_chat_messages_checkpoint_id'
            """))
            
            if result.fetchone():
                print("✓ 索引已创建")
            else:
                print("⚠ 索引未找到")
            
            return True
            
        except Exception as e:
            print(f"\n✗ 迁移失败: {e}")
            await db.rollback()
            import traceback
            traceback.print_exc()
            return False


async def main():
    """主函数"""
    success = await run_migration()
    
    print("\n" + "=" * 60)
    if success:
        print("迁移完成！")
        print("=" * 60)
        print("\n现在可以使用多轮对话功能了。")
        print("重启应用: python run_server.py")
    else:
        print("迁移失败")
        print("=" * 60)
        print("\n请检查:")
        print("1. .env 文件中的 DATABASE_URL 是否正确")
        print("2. PostgreSQL 服务是否正在运行")
        print("3. 数据库连接是否正常")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
