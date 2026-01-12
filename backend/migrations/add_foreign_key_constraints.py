"""
添加外键约束迁移脚本

为 chat_sessions.user_id 添加外键约束
为 chat_messages.session_id 添加 ON DELETE CASCADE

注意：此脚本仅适用于 PostgreSQL
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
    print("[Migration] Adding foreign key constraints...")
    
    if not IS_POSTGRESQL:
        print("[Migration] This script only supports PostgreSQL")
        print("[Migration] For SQLite, foreign keys are enforced at application level")
        return
    
    async with engine.begin() as conn:
        # 1. 检查 chat_sessions.user_id 外键是否已存在
        print("[Migration] Checking chat_sessions.user_id foreign key...")
        result = await conn.execute(text("""
            SELECT constraint_name 
            FROM information_schema.table_constraints 
            WHERE table_name = 'chat_sessions' 
            AND constraint_type = 'FOREIGN KEY'
            AND constraint_name LIKE '%user_id%'
        """))
        existing_fk = result.fetchone()
        
        if not existing_fk:
            print("[Migration] Adding foreign key constraint for chat_sessions.user_id...")
            try:
                # 先清理无效的 user_id 引用（指向不存在的用户）
                await conn.execute(text("""
                    UPDATE chat_sessions 
                    SET user_id = NULL 
                    WHERE user_id IS NOT NULL 
                    AND user_id NOT IN (SELECT id FROM "user")
                """))
                
                # 添加外键约束
                await conn.execute(text("""
                    ALTER TABLE chat_sessions 
                    ADD CONSTRAINT fk_chat_sessions_user_id 
                    FOREIGN KEY (user_id) REFERENCES "user"(id) 
                    ON DELETE SET NULL
                """))
                print("[Migration] Foreign key constraint added for chat_sessions.user_id")
            except Exception as e:
                print(f"[Migration] Warning: Could not add foreign key: {e}")
        else:
            print("[Migration] Foreign key for chat_sessions.user_id already exists")
        
        # 2. 检查 chat_messages.session_id 外键是否有 ON DELETE CASCADE
        print("[Migration] Checking chat_messages.session_id foreign key...")
        result = await conn.execute(text("""
            SELECT tc.constraint_name, rc.delete_rule
            FROM information_schema.table_constraints tc
            JOIN information_schema.referential_constraints rc 
                ON tc.constraint_name = rc.constraint_name
            WHERE tc.table_name = 'chat_messages' 
            AND tc.constraint_type = 'FOREIGN KEY'
        """))
        existing_fk = result.fetchone()
        
        if existing_fk:
            if existing_fk[1] != 'CASCADE':
                print(f"[Migration] Updating foreign key to add ON DELETE CASCADE...")
                try:
                    # 删除旧约束
                    await conn.execute(text(f"""
                        ALTER TABLE chat_messages 
                        DROP CONSTRAINT IF EXISTS {existing_fk[0]}
                    """))
                    
                    # 添加新约束
                    await conn.execute(text("""
                        ALTER TABLE chat_messages 
                        ADD CONSTRAINT fk_chat_messages_session_id 
                        FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id) 
                        ON DELETE CASCADE
                    """))
                    print("[Migration] Foreign key updated with ON DELETE CASCADE")
                except Exception as e:
                    print(f"[Migration] Warning: Could not update foreign key: {e}")
            else:
                print("[Migration] Foreign key already has ON DELETE CASCADE")
        else:
            print("[Migration] Adding foreign key constraint for chat_messages.session_id...")
            try:
                await conn.execute(text("""
                    ALTER TABLE chat_messages 
                    ADD CONSTRAINT fk_chat_messages_session_id 
                    FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id) 
                    ON DELETE CASCADE
                """))
                print("[Migration] Foreign key constraint added for chat_messages.session_id")
            except Exception as e:
                print(f"[Migration] Warning: Could not add foreign key: {e}")
    
    print("[Migration] Done!")

if __name__ == "__main__":
    asyncio.run(run_migration())
