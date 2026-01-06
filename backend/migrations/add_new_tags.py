"""
数据库迁移脚本：添加新的标签字段到 ProductSelectionAnalysis 表

运行方式：
    cd backend
    python -m migrations.add_new_tags
"""

import asyncio
import logging
from sqlalchemy import text
from database.db import engine as async_engine, AsyncSessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 新增的列定义
NEW_COLUMNS = [
    # 收入验证维度
    ("revenue_tier", "VARCHAR(20)"),
    ("revenue_follower_ratio_level", "VARCHAR(20)"),
    # 增长驱动维度
    ("growth_driver", "VARCHAR(20)"),
    # 技术特征维度
    ("ai_dependency_level", "VARCHAR(20)"),
    ("has_realtime_feature", "BOOLEAN"),
    ("is_data_intensive", "BOOLEAN"),
    ("has_compliance_requirement", "BOOLEAN"),
    # 商业模式维度
    ("pricing_model", "VARCHAR(20)"),
    ("target_customer", "VARCHAR(20)"),
    ("market_scope", "VARCHAR(20)"),
    # 可复制性维度
    ("feature_complexity", "VARCHAR(20)"),
    ("moat_type", "VARCHAR(100)"),
    ("startup_cost_level", "VARCHAR(20)"),
    # 生命周期维度
    ("product_stage", "VARCHAR(20)"),
]


async def check_column_exists(conn, table_name: str, column_name: str) -> bool:
    """检查列是否已存在"""
    result = await conn.execute(
        text(f"PRAGMA table_info({table_name})")
    )
    columns = result.fetchall()
    existing_columns = [col[1] for col in columns]
    return column_name in existing_columns


async def add_column(conn, table_name: str, column_name: str, column_type: str):
    """添加新列"""
    try:
        await conn.execute(
            text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
        )
        logger.info(f"✓ 添加列: {column_name} ({column_type})")
    except Exception as e:
        logger.error(f"✗ 添加列失败 {column_name}: {e}")
        raise


async def migrate():
    """执行迁移"""
    logger.info("=" * 50)
    logger.info("开始数据库迁移：添加新标签字段")
    logger.info("=" * 50)

    table_name = "product_selection_analysis"

    async with async_engine.begin() as conn:
        # 检查表是否存在
        result = await conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' AND name=:name"),
            {"name": table_name}
        )
        if not result.fetchone():
            logger.error(f"表 {table_name} 不存在，请先创建表")
            return False

        # 添加新列
        added_count = 0
        skipped_count = 0

        for column_name, column_type in NEW_COLUMNS:
            exists = await check_column_exists(conn, table_name, column_name)
            if exists:
                logger.info(f"- 跳过已存在的列: {column_name}")
                skipped_count += 1
            else:
                await add_column(conn, table_name, column_name, column_type)
                added_count += 1

        logger.info("=" * 50)
        logger.info(f"迁移完成: 添加 {added_count} 列, 跳过 {skipped_count} 列")
        logger.info("=" * 50)

    return True


async def verify_migration():
    """验证迁移结果"""
    logger.info("\n验证迁移结果...")

    async with async_engine.begin() as conn:
        result = await conn.execute(
            text("PRAGMA table_info(product_selection_analysis)")
        )
        columns = result.fetchall()

        logger.info(f"\n当前表结构 ({len(columns)} 列):")
        for col in columns:
            logger.info(f"  - {col[1]}: {col[2]}")

        # 检查所有新列是否存在
        existing_columns = [col[1] for col in columns]
        missing = []
        for column_name, _ in NEW_COLUMNS:
            if column_name not in existing_columns:
                missing.append(column_name)

        if missing:
            logger.warning(f"\n缺失的列: {missing}")
            return False
        else:
            logger.info("\n✓ 所有新列已成功添加")
            return True


async def main():
    """主函数"""
    try:
        success = await migrate()
        if success:
            await verify_migration()
    except Exception as e:
        logger.error(f"迁移失败: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
