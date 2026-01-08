"""
SQLite to PostgreSQL (Supabase) Migration Script

This script migrates data from SQLite to PostgreSQL/Supabase database.
Run this after setting up your Supabase database and updating DATABASE_URL in .env

Usage:
    cd backend
    python scripts/migrate_sqlite_to_postgres.py
"""

import os
import sys
from pathlib import Path
from urllib.parse import quote_plus, urlparse, urlunparse

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

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

# PostgreSQL target database (from environment)
PG_URL = os.getenv("DATABASE_URL", "")

if not PG_URL or "postgres" not in PG_URL.lower():
    print("Error: DATABASE_URL must be set to a PostgreSQL connection string")
    print("Example: postgresql://postgres:password@localhost:54322/postgres")
    sys.exit(1)


def encode_password_in_url(url: str) -> str:
    """
    Encode special characters in password part of database URL.
    This handles passwords with @, #, %, etc.
    """
    # Parse the URL
    parsed = urlparse(url)

    if parsed.password:
        # URL encode the password
        encoded_password = quote_plus(parsed.password)
        # Reconstruct netloc with encoded password
        if parsed.port:
            netloc = f"{parsed.username}:{encoded_password}@{parsed.hostname}:{parsed.port}"
        else:
            netloc = f"{parsed.username}:{encoded_password}@{parsed.hostname}"

        # Reconstruct the full URL
        encoded_url = urlunparse((
            parsed.scheme,
            netloc,
            parsed.path,
            parsed.params,
            parsed.query,
            parsed.fragment
        ))
        return encoded_url

    return url


# Encode password and convert to sync URL
PG_URL = encode_password_in_url(PG_URL)

if PG_URL.startswith("postgresql+asyncpg://"):
    PG_URL = PG_URL.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
elif PG_URL.startswith("postgresql://"):
    PG_URL = PG_URL.replace("postgresql://", "postgresql+psycopg2://")
elif PG_URL.startswith("postgres://"):
    PG_URL = PG_URL.replace("postgres://", "postgresql+psycopg2://")


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


def migrate_table(sqlite_session, pg_session, model_class, batch_size=500):
    """Migrate a single table from SQLite to PostgreSQL"""
    table_name = model_class.__tablename__
    print(f"\n[{table_name}] Starting migration...")

    # Count records in SQLite
    sqlite_count = sqlite_session.query(model_class).count()
    print(f"[{table_name}] Found {sqlite_count} records in SQLite")

    if sqlite_count == 0:
        print(f"[{table_name}] No records to migrate")
        return 0

    # Check existing records in PostgreSQL
    pg_count = pg_session.query(model_class).count()
    if pg_count > 0:
        print(f"[{table_name}] Warning: PostgreSQL already has {pg_count} records")
        response = input(f"[{table_name}] Clear existing data? (y/N): ").strip().lower()
        if response == 'y':
            pg_session.query(model_class).delete()
            pg_session.commit()
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
        with pg_session.no_autoflush:
            for data in batch_records:
                new_record = model_class(**data)
                pg_session.merge(new_record)

        try:
            pg_session.commit()
            migrated += len(batch_records)
        except Exception as e:
            pg_session.rollback()
            print(f"[{table_name}] Batch error: {e}")
            # Try one by one
            for data in batch_records:
                try:
                    new_record = model_class(**data)
                    pg_session.merge(new_record)
                    pg_session.commit()
                    migrated += 1
                except Exception as e2:
                    pg_session.rollback()
                    skipped += 1

        offset += batch_size
        print(f"[{table_name}] Progress: {migrated}/{sqlite_count} migrated, {skipped} skipped...")

    print(f"[{table_name}] Migration complete: {migrated} records migrated, {skipped} skipped")
    return migrated


def reset_sequences(pg_engine):
    """Reset PostgreSQL sequences to max ID + 1 for each table"""
    print("\n[Sequences] Resetting auto-increment sequences...")

    tables_with_id = [
        'startups', 'leaderboard_entries', 'founders', 'category_analysis',
        'product_selection_analysis', 'landing_page_snapshots', 'landing_page_analysis',
        'comprehensive_analysis', 'revenue_history', 'chat_sessions', 'chat_messages'
    ]

    with pg_engine.connect() as conn:
        for table in tables_with_id:
            try:
                # Get max ID
                result = conn.execute(text(f"SELECT MAX(id) FROM {table}"))
                max_id = result.scalar() or 0

                # Reset sequence
                seq_name = f"{table}_id_seq"
                conn.execute(text(f"SELECT setval('{seq_name}', {max_id + 1}, false)"))
                conn.commit()
                print(f"  [✓] {table}: sequence set to {max_id + 1}")
            except Exception as e:
                print(f"  [✗] {table}: {e}")


def main():
    """Main migration function"""
    print("=" * 60)
    print("SQLite to PostgreSQL (Supabase) Migration")
    print("=" * 60)

    # Check SQLite exists
    if not SQLITE_PATH.exists():
        print(f"Error: SQLite database not found at {SQLITE_PATH}")
        sys.exit(1)

    # Display connection info (hide password)
    display_url = PG_URL.split('@')[-1] if '@' in PG_URL else PG_URL
    print(f"\nSource: {SQLITE_PATH}")
    print(f"Target: {display_url}")

    # Confirm
    response = input("\nProceed with migration? (y/N): ").strip().lower()
    if response != 'y':
        print("Migration cancelled")
        sys.exit(0)

    # Create engines
    print("\nConnecting to databases...")
    sqlite_engine = create_engine(SQLITE_URL)

    try:
        pg_engine = create_engine(
            PG_URL,
            pool_pre_ping=True,
            pool_recycle=3600,
            connect_args={
                "sslmode": "require"  # Required for Supabase cloud
            } if "supabase.co" in PG_URL else {}
        )
        # Test connection
        with pg_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("PostgreSQL connection successful!")
    except Exception as e:
        print(f"Error connecting to PostgreSQL: {e}")
        print("\nTips:")
        print("1. Check your DATABASE_URL in .env")
        print("2. For Supabase cloud, use the connection string from:")
        print("   Dashboard → Settings → Database → Connection string → URI")
        print("3. Make sure to use port 6543 (Transaction pooler) for cloud")
        sys.exit(1)

    # Drop and recreate tables in PostgreSQL to ensure schema is up to date
    print("\nRecreating tables in PostgreSQL (to apply schema changes)...")
    response = input("Drop and recreate all tables? This will DELETE existing data! (y/N): ").strip().lower()
    if response == 'y':
        Base.metadata.drop_all(pg_engine)
        print("Tables dropped.")

    Base.metadata.create_all(pg_engine)
    print("Tables created.")

    # Create sessions
    SQLiteSession = sessionmaker(bind=sqlite_engine)
    PGSession = sessionmaker(bind=pg_engine)

    sqlite_session = SQLiteSession()
    pg_session = PGSession()

    try:
        total_migrated = 0
        tables = get_table_order()

        for model_class in tables:
            try:
                count = migrate_table(sqlite_session, pg_session, model_class)
                total_migrated += count
            except Exception as e:
                print(f"[{model_class.__tablename__}] Error: {e}")
                pg_session.rollback()
                continue

        # Reset sequences for auto-increment
        reset_sequences(pg_engine)

        print("\n" + "=" * 60)
        print(f"Migration complete! Total records migrated: {total_migrated}")
        print("=" * 60)

        # Verify
        print("\nVerification:")
        for model_class in tables:
            pg_count = pg_session.query(model_class).count()
            sqlite_count = sqlite_session.query(model_class).count()
            status = "✓" if pg_count >= sqlite_count * 0.95 else "✗"  # Allow 5% loss due to duplicates
            print(f"  {status} {model_class.__tablename__}: {pg_count}/{sqlite_count}")

    finally:
        sqlite_session.close()
        pg_session.close()
        sqlite_engine.dispose()
        pg_engine.dispose()


if __name__ == "__main__":
    main()
