"""
Add founder_id to featured_creators table and backfill from founders.

Run:
    cd backend
    python -m migrations.add_featured_creator_founder_id
"""

import asyncio
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

from sqlalchemy import text

from database.db import get_db_session, IS_POSTGRESQL


async def migrate():
    """Run migration."""
    print(f"Database: {'PostgreSQL' if IS_POSTGRESQL else 'SQLite'}")
    print("Starting migration: add_featured_creator_founder_id")

    async with get_db_session() as db:
        try:
            if IS_POSTGRESQL:
                await db.execute(text(
                    "ALTER TABLE featured_creators "
                    "ADD COLUMN IF NOT EXISTS founder_id INTEGER "
                    "REFERENCES founders(id) ON DELETE SET NULL"
                ))
                await db.execute(text(
                    "CREATE INDEX IF NOT EXISTS ix_featured_creators_founder_id ON featured_creators(founder_id)"
                ))
            else:
                result = await db.execute(text("PRAGMA table_info(featured_creators)"))
                columns = [row[1] for row in result.fetchall()]
                if "founder_id" not in columns:
                    await db.execute(text(
                        "ALTER TABLE featured_creators ADD COLUMN founder_id INTEGER"
                    ))
                await db.execute(text(
                    "CREATE INDEX IF NOT EXISTS ix_featured_creators_founder_id ON featured_creators(founder_id)"
                ))

            await db.execute(text(
                """
                INSERT INTO founders (name, username, profile_url, scraped_at, updated_at)
                SELECT
                    COALESCE(NULLIF(trim(fc.name), ''), NULLIF(trim(fc.founder_username), ''), fc.handle) AS name,
                    lower(trim(replace(COALESCE(NULLIF(trim(fc.founder_username), ''), NULLIF(trim(fc.handle), '')), '@', ''))) AS username,
                    CASE
                        WHEN fc.handle LIKE 'http%' THEN fc.handle
                        ELSE 'https://x.com/' || lower(trim(replace(COALESCE(NULLIF(trim(fc.founder_username), ''), NULLIF(trim(fc.handle), '')), '@', '')))
                    END AS profile_url,
                    CURRENT_TIMESTAMP,
                    CURRENT_TIMESTAMP
                FROM featured_creators fc
                WHERE COALESCE(NULLIF(trim(fc.founder_username), ''), NULLIF(trim(fc.handle), '')) IS NOT NULL
                  AND COALESCE(NULLIF(trim(fc.founder_username), ''), NULLIF(trim(fc.handle), '')) != ''
                  AND NOT EXISTS (
                    SELECT 1
                    FROM founders f
                    WHERE lower(trim(replace(f.username, '@', ''))) = lower(trim(replace(COALESCE(NULLIF(trim(fc.founder_username), ''), NULLIF(trim(fc.handle), '')), '@', '')))
                  )
                """
            ))

            await db.execute(text(
                """
                UPDATE featured_creators
                SET founder_id = (
                    SELECT MIN(id)
                    FROM founders
                    WHERE lower(trim(replace(founders.username, '@', ''))) = lower(trim(replace(
                        COALESCE(NULLIF(trim(featured_creators.founder_username), ''), NULLIF(trim(featured_creators.handle), '')),
                        '@',
                        ''
                    )))
                )
                WHERE (founder_id IS NULL OR founder_id NOT IN (SELECT id FROM founders))
                  AND COALESCE(NULLIF(trim(featured_creators.founder_username), ''), NULLIF(trim(featured_creators.handle), '')) IS NOT NULL
                  AND COALESCE(NULLIF(trim(featured_creators.founder_username), ''), NULLIF(trim(featured_creators.handle), '')) != ''
                """
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
