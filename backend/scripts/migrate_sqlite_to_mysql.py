"""
SQLite to MySQL Migration Script

This script migrates data from SQLite to MySQL database.
Run this after setting up your MySQL database and updating DATABASE_URL in .env

Usage:
    cd backend
    python scripts/migrate_sqlite_to_mysql.py
"""

import os
import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

import sqlalchemy as sa
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Import models
from database.models import (
    Base, Startup, LeaderboardEntry, Founder, CategoryAnalysis,
    ProductSelectionAnalysis, LandingPageSnapshot, LandingPageAnalysis,
    ComprehensiveAnalysis, RevenueHistory, ChatSession, ChatMessage
)


# SQLite source database
SQLITE_PATH = Path(__file__).parent.parent / "data" / "sass_analysis.db"
SQLITE_URL = f"sqlite:///{SQLITE_PATH}"

# MySQL target database (from environment)
MYSQL_URL = os.getenv("DATABASE_URL", "")

if not MYSQL_URL or "mysql" not in MYSQL_URL.lower():
    print("Error: DATABASE_URL must be set to a MySQL connection string")
    print("Example: mysql://user:password@localhost:3306/sass_analysis")
    sys.exit(1)

# Convert to sync URL if needed
if MYSQL_URL.startswith("mysql+aiomysql://"):
    MYSQL_URL = MYSQL_URL.replace("mysql+aiomysql://", "mysql+pymysql://")
elif MYSQL_URL.startswith("mysql://"):
    MYSQL_URL = MYSQL_URL.replace("mysql://", "mysql+pymysql://")


def get_table_order():
    """Return tables in order for migration (respecting foreign keys)"""
    return [
        Startup,
        LeaderboardEntry,
        Founder,
        CategoryAnalysis,
        ProductSelectionAnalysis,
        LandingPageSnapshot,  # Must be before LandingPageAnalysis
        LandingPageAnalysis,
        ComprehensiveAnalysis,
        RevenueHistory,
        ChatSession,
        ChatMessage,
    ]


def migrate_table(sqlite_session, mysql_session, model_class, batch_size=500):
    """Migrate a single table from SQLite to MySQL"""
    table_name = model_class.__tablename__
    print(f"\n[{table_name}] Starting migration...")

    # Count records in SQLite
    sqlite_count = sqlite_session.query(model_class).count()
    print(f"[{table_name}] Found {sqlite_count} records in SQLite")

    if sqlite_count == 0:
        print(f"[{table_name}] No records to migrate")
        return 0

    # Check existing records in MySQL
    mysql_count = mysql_session.query(model_class).count()
    if mysql_count > 0:
        print(f"[{table_name}] Warning: MySQL already has {mysql_count} records")
        response = input(f"[{table_name}] Clear existing data? (y/N): ").strip().lower()
        if response == 'y':
            mysql_session.execute(text(f"SET FOREIGN_KEY_CHECKS = 0"))
            mysql_session.query(model_class).delete()
            mysql_session.commit()
            mysql_session.execute(text(f"SET FOREIGN_KEY_CHECKS = 1"))
            print(f"[{table_name}] Cleared existing data")
        else:
            print(f"[{table_name}] Skipping migration (data exists)")
            return 0

    # Track unique keys to avoid duplicates
    seen_keys = set()
    unique_column = None

    # Identify unique columns for deduplication
    if model_class == Founder:
        unique_column = 'username'
    elif model_class == Startup:
        unique_column = 'slug'

    # Migrate in batches
    migrated = 0
    skipped = 0
    offset = 0

    while offset < sqlite_count:
        # Fetch batch from SQLite
        records = sqlite_session.query(model_class).offset(offset).limit(batch_size).all()

        if not records:
            break

        batch_records = []
        for record in records:
            # Create a new instance with the same data
            data = {}
            for column in model_class.__table__.columns:
                value = getattr(record, column.name)
                data[column.name] = value

            # Check for duplicates on unique columns
            if unique_column:
                key_value = data.get(unique_column)
                if key_value in seen_keys:
                    skipped += 1
                    continue
                seen_keys.add(key_value)

            batch_records.append(data)

        # Insert batch with no_autoflush to avoid premature flushes
        with mysql_session.no_autoflush:
            for data in batch_records:
                new_record = model_class(**data)
                mysql_session.merge(new_record)

        try:
            mysql_session.commit()
            migrated += len(batch_records)
        except Exception as e:
            mysql_session.rollback()
            print(f"[{table_name}] Batch error: {e}")
            # Try one by one
            for data in batch_records:
                try:
                    new_record = model_class(**data)
                    mysql_session.merge(new_record)
                    mysql_session.commit()
                    migrated += 1
                except Exception as e2:
                    mysql_session.rollback()
                    skipped += 1

        offset += batch_size
        print(f"[{table_name}] Progress: {migrated}/{sqlite_count} migrated, {skipped} skipped...")

    print(f"[{table_name}] Migration complete: {migrated} records migrated, {skipped} skipped")
    return migrated


def main():
    """Main migration function"""
    print("=" * 60)
    print("SQLite to MySQL Migration")
    print("=" * 60)

    # Check SQLite exists
    if not SQLITE_PATH.exists():
        print(f"Error: SQLite database not found at {SQLITE_PATH}")
        sys.exit(1)

    print(f"\nSource: {SQLITE_PATH}")
    print(f"Target: {MYSQL_URL.split('@')[-1] if '@' in MYSQL_URL else MYSQL_URL}")

    # Confirm
    response = input("\nProceed with migration? (y/N): ").strip().lower()
    if response != 'y':
        print("Migration cancelled")
        sys.exit(0)

    # Create engines
    print("\nConnecting to databases...")
    sqlite_engine = create_engine(SQLITE_URL)
    mysql_engine = create_engine(
        MYSQL_URL,
        pool_pre_ping=True,
        pool_recycle=3600,
    )

    # Drop and recreate tables in MySQL to ensure schema is up to date
    print("Recreating tables in MySQL (to apply schema changes)...")
    response = input("Drop and recreate all tables? This will DELETE existing data! (y/N): ").strip().lower()
    if response == 'y':
        Base.metadata.drop_all(mysql_engine)
        print("Tables dropped.")

    Base.metadata.create_all(mysql_engine)
    print("Tables created.")

    # Create sessions
    SQLiteSession = sessionmaker(bind=sqlite_engine)
    MySQLSession = sessionmaker(bind=mysql_engine)

    sqlite_session = SQLiteSession()
    mysql_session = MySQLSession()

    try:
        total_migrated = 0
        tables = get_table_order()

        for model_class in tables:
            try:
                count = migrate_table(sqlite_session, mysql_session, model_class)
                total_migrated += count
            except Exception as e:
                print(f"[{model_class.__tablename__}] Error: {e}")
                mysql_session.rollback()
                continue

        print("\n" + "=" * 60)
        print(f"Migration complete! Total records migrated: {total_migrated}")
        print("=" * 60)

        # Verify
        print("\nVerification:")
        for model_class in tables:
            mysql_count = mysql_session.query(model_class).count()
            sqlite_count = sqlite_session.query(model_class).count()
            status = "✓" if mysql_count >= sqlite_count * 0.95 else "✗"  # Allow 5% loss due to duplicates
            print(f"  {status} {model_class.__tablename__}: {mysql_count}/{sqlite_count}")

    finally:
        sqlite_session.close()
        mysql_session.close()
        sqlite_engine.dispose()
        mysql_engine.dispose()


if __name__ == "__main__":
    main()
