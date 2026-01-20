"""
Add founder_id to startups table and backfill from founders.

Run:
    cd backend
    python -m migrations.add_startups_founder_id
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
    print("Starting migration: add_startups_founder_id")

    async with get_db_session() as db:
        try:
            if IS_POSTGRESQL:
                await db.execute(text(
                    "ALTER TABLE startups "
                    "ADD COLUMN IF NOT EXISTS founder_id INTEGER "
                    "REFERENCES founders(id) ON DELETE SET NULL"
                ))
                await db.execute(text(
                    "CREATE INDEX IF NOT EXISTS ix_startups_founder_id ON startups(founder_id)"
                ))
            else:
                result = await db.execute(text("PRAGMA table_info(startups)"))
                columns = [row[1] for row in result.fetchall()]
                if "founder_id" not in columns:
                    await db.execute(text(
                        "ALTER TABLE startups ADD COLUMN founder_id INTEGER"
                    ))
                await db.execute(text(
                    "CREATE INDEX IF NOT EXISTS ix_startups_founder_id ON startups(founder_id)"
                ))

            await db.execute(text(
                """
                UPDATE startups
                SET founder_id = (
                    SELECT MIN(id)
                    FROM founders
                    WHERE lower(trim(replace(founders.username, '@', ''))) = lower(trim(replace(NULLIF(trim(startups.founder_username), ''), '@', '')))
                )
                WHERE (founder_id IS NULL OR founder_id NOT IN (SELECT id FROM founders))
                  AND NULLIF(trim(startups.founder_username), '') IS NOT NULL
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
