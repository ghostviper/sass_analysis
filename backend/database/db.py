"""
Database connection and session management

Supports PostgreSQL (Supabase), MySQL, and SQLite.
Set DATABASE_URL environment variable to configure:
- PostgreSQL/Supabase: postgresql://user:password@host:port/database
- MySQL: mysql://user:password@host:port/database
- SQLite: sqlite:///path/to/database.db
"""

import os
from pathlib import Path
from contextlib import asynccontextmanager, contextmanager
from urllib.parse import quote_plus, urlparse, urlunparse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from .models import Base

# Data directory: backend/data/ (for SQLite fallback)
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# Database URL - 使用环境变量或默认路径
_db_url = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR}/sass_analysis.db")

# 处理相对路径：将 sqlite:///data/ 转换为绝对路径
if _db_url == "sqlite:///data/sass_analysis.db":
    _db_url = f"sqlite:///{DATA_DIR}/sass_analysis.db"


def _encode_password_in_url(url: str) -> str:
    """
    Encode special characters in password part of database URL.
    This handles passwords with @, #, %, etc.
    """
    # Skip SQLite URLs
    if url.startswith("sqlite"):
        return url

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


def _get_async_url(url: str) -> str:
    """Convert database URL to async format."""
    # SQLite
    if url.startswith("sqlite:///"):
        return url.replace("sqlite:///", "sqlite+aiosqlite:///")
    # MySQL
    elif url.startswith("mysql://"):
        return url.replace("mysql://", "mysql+aiomysql://")
    elif url.startswith("mysql+pymysql://"):
        return url.replace("mysql+pymysql://", "mysql+aiomysql://")
    # PostgreSQL (Supabase)
    elif url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://")
    elif url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+asyncpg://")
    elif url.startswith("postgresql+psycopg2://"):
        return url.replace("postgresql+psycopg2://", "postgresql+asyncpg://")
    return url


def _get_db_type(url: str) -> str:
    """Determine database type from URL."""
    url_lower = url.lower()
    if "sqlite" in url_lower:
        return "sqlite"
    elif "mysql" in url_lower:
        return "mysql"
    elif "postgres" in url_lower:
        return "postgresql"
    return "unknown"


# Encode password and convert to async URL format
_db_url = _encode_password_in_url(_db_url)
DATABASE_URL = _get_async_url(_db_url)

# Determine database type
DB_TYPE = _get_db_type(DATABASE_URL)
IS_SQLITE = DB_TYPE == "sqlite"
IS_MYSQL = DB_TYPE == "mysql"
IS_POSTGRESQL = DB_TYPE == "postgresql"

# Create async engine with appropriate settings
if IS_SQLITE:
    # SQLite configuration - use StaticPool for single connection
    engine = create_async_engine(
        DATABASE_URL,
        echo=os.getenv("DB_ECHO", "false").lower() == "true",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    print(f"[Database] Using SQLite: {DATA_DIR}/sass_analysis.db")
else:
    # PostgreSQL/MySQL configuration - use connection pooling
    connect_args = {}

    # Add SSL for Supabase cloud
    if IS_POSTGRESQL and "supabase.co" in DATABASE_URL:
        connect_args["ssl"] = "require"

    engine = create_async_engine(
        DATABASE_URL,
        echo=os.getenv("DB_ECHO", "false").lower() == "true",
        pool_size=int(os.getenv("DB_POOL_SIZE", "10")),
        max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "20")),
        pool_timeout=int(os.getenv("DB_POOL_TIMEOUT", "30")),
        pool_recycle=int(os.getenv("DB_POOL_RECYCLE", "3600")),
        pool_pre_ping=True,
        connect_args=connect_args if connect_args else {},
    )
    # Print connection info (hide password)
    display_url = DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else 'configured'
    print(f"[Database] Using {DB_TYPE.upper()}: {display_url}")

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    if IS_SQLITE:
        print(f"[Database] SQLite initialized at: {DATA_DIR}/sass_analysis.db")
    else:
        print(f"[Database] {DB_TYPE.upper()} tables initialized")


async def get_db():
    """Dependency to get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


@asynccontextmanager
async def get_db_session():
    """Context manager to get database session (for non-FastAPI use)"""
    await init_db()  # 确保表已创建
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def close_db():
    """Close database connections (call on shutdown)"""
    await engine.dispose()
    print("[Database] Connections closed")


# =============================================================================
# Synchronous Session Support (for scripts and CLI tools)
# =============================================================================

def _get_sync_url(url: str) -> str:
    """Convert async database URL back to sync format."""
    if "sqlite+aiosqlite://" in url:
        return url.replace("sqlite+aiosqlite://", "sqlite://")
    elif "mysql+aiomysql://" in url:
        return url.replace("mysql+aiomysql://", "mysql+pymysql://")
    elif "postgresql+asyncpg://" in url:
        return url.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
    return url


# Create sync engine
SYNC_DATABASE_URL = _get_sync_url(DATABASE_URL)

if IS_SQLITE:
    sync_engine = create_engine(
        SYNC_DATABASE_URL,
        echo=os.getenv("DB_ECHO", "false").lower() == "true",
        connect_args={"check_same_thread": False},
    )
else:
    sync_engine = create_engine(
        SYNC_DATABASE_URL,
        echo=os.getenv("DB_ECHO", "false").lower() == "true",
        pool_size=int(os.getenv("DB_POOL_SIZE", "10")),
        max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "20")),
        pool_timeout=int(os.getenv("DB_POOL_TIMEOUT", "30")),
        pool_recycle=int(os.getenv("DB_POOL_RECYCLE", "3600")),
        pool_pre_ping=True,
    )

SyncSessionLocal = sessionmaker(bind=sync_engine, expire_on_commit=False)


@contextmanager
def get_sync_session():
    """Context manager to get synchronous database session"""
    Base.metadata.create_all(bind=sync_engine)
    session = SyncSessionLocal()
    try:
        yield session
    finally:
        session.close()
