"""
Database connection and session management
"""

import os
from pathlib import Path
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from .models import Base

# Data directory: backend/data/
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# Database URL - 使用环境变量或默认路径
_db_url = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR}/sass_analysis.db")

# 处理相对路径：将 sqlite:///data/ 转换为绝对路径
if _db_url == "sqlite:///data/sass_analysis.db":
    _db_url = f"sqlite:///{DATA_DIR}/sass_analysis.db"

# 转换为异步URL格式
if _db_url.startswith("sqlite:///"):
    DATABASE_URL = _db_url.replace("sqlite:///", "sqlite+aiosqlite:///")
else:
    DATABASE_URL = _db_url

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

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
    print(f"Database initialized at: {DATA_DIR}/sass_analysis.db")


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
