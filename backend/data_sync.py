"""
数据同步模块 - 统一管理HTML快照解析和数据库同步
"""
import asyncio
import logging
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import select, func, text
from database.db import init_db, AsyncSessionLocal
from database.models import Startup, Founder, LeaderboardEntry
from crawler.html_parser import parse_html_file

logger = logging.getLogger(__name__)

# HTML快照目录 (backend/data/html_snapshots)
SNAPSHOT_DIR = Path(__file__).parent / 'data' / 'html_snapshots'


class DataSyncManager:
    """数据同步管理器"""

    DEFAULT_SNAPSHOT_DIR = SNAPSHOT_DIR

    @staticmethod
    def _normalize_username(value: Optional[str]) -> Optional[str]:
        if not value:
            return None
        trimmed = value.strip()
        if not trimmed:
            return None
        if trimmed.startswith("@"):
            trimmed = trimmed[1:]
        trimmed = trimmed.strip()
        return trimmed.lower() if trimmed else None

    async def sync_founders_from_startups(self) -> int:
        """
        从Startup表同步founder数据到Founder表

        Returns:
            同步的founder数量
        """
        await init_db()

        async with AsyncSessionLocal() as session:
            # 查询所有有founder_username的startup
            result = await session.execute(
                select(Startup).where(Startup.founder_username.isnot(None))
            )
            startups = result.scalars().all()

            logger.info(f"找到 {len(startups)} 个有founder信息的startup")

            # 提取唯一的founder数据
            founders_data: Dict[str, Dict] = {}
            for startup in startups:
                username = self._normalize_username(startup.founder_username)
                if username and username not in founders_data:
                    founders_data[username] = {
                        'name': startup.founder_name or username,
                        'username': username,
                        'followers': startup.founder_followers,
                        'social_platform': startup.founder_social_platform,
                        'profile_url': f"https://trustmrr.com/founder/{username}",
                    }

            logger.info(f"提取到 {len(founders_data)} 个唯一founder")

            # 同步到数据库
            created_count = 0
            updated_count = 0

            for username, data in founders_data.items():
                result = await session.execute(
                    select(Founder).where(Founder.username == username)
                )
                founder = result.scalar_one_or_none()

                if founder:
                    # 更新现有记录
                    founder.name = data['name']
                    if data.get('followers'):
                        founder.followers = data['followers']
                    if data.get('social_platform'):
                        founder.social_platform = data['social_platform']
                    if data.get('profile_url'):
                        founder.profile_url = data['profile_url']
                    founder.updated_at = datetime.utcnow()
                    updated_count += 1
                else:
                    # 创建新记录
                    founder = Founder(
                        name=data['name'],
                        username=username,
                        followers=data.get('followers'),
                        social_platform=data.get('social_platform'),
                        profile_url=data.get('profile_url'),
                    )
                    session.add(founder)
                    created_count += 1

            await session.commit()

            logger.info(f"Founder同步完成: 创建 {created_count}, 更新 {updated_count}")
            await self._link_startups_to_founders()
            await self._ensure_founders_from_featured_creators()
            await self._link_featured_creators_to_founders()
            return created_count + updated_count

    async def update_from_snapshots(self, snapshot_dir: Optional[Path] = None) -> Dict:
        """
        从HTML快照更新数据库

        Args:
            snapshot_dir: HTML快照目录，默认使用标准路径

        Returns:
            统计信息字典
        """
        if snapshot_dir is None:
            snapshot_dir = self.DEFAULT_SNAPSHOT_DIR
        else:
            snapshot_dir = Path(snapshot_dir)

        if not snapshot_dir.exists():
            logger.error(f"快照目录不存在: {snapshot_dir}")
            return {'error': f'Directory not found: {snapshot_dir}'}

        await init_db()

        html_files = list(snapshot_dir.glob('*.html'))
        logger.info(f"找到 {len(html_files)} 个HTML快照")

        stats = {
            'total': len(html_files),
            'updated': 0,
            'created': 0,
            'errors': 0,
            'founders_synced': 0,
            'skipped_duplicates': 0,
        }

        founders_data: Dict[str, Dict] = {}

        async with AsyncSessionLocal() as session:
            for html_file in html_files:
                slug = html_file.stem

                try:
                    # 解析HTML
                    data = parse_html_file(html_file)

                    # 查找或创建Startup
                    result = await session.execute(
                        select(Startup).where(Startup.slug == slug)
                    )
                    startup = result.scalar_one_or_none()

                    if startup:
                        # 更新现有记录
                        self._update_startup_from_data(startup, data, html_file)
                        stats['updated'] += 1
                        logger.debug(f"更新: {slug}")
                    else:
                        # 检查 website_url 是否已存在（防止重复）
                        website_url = data.get('website_url')
                        if website_url:
                            result = await session.execute(
                                select(Startup).where(Startup.website_url == website_url)
                            )
                            existing = result.scalar_one_or_none()
                            if existing:
                                # 已存在相同 website_url 的记录，更新它而不是创建新的
                                self._update_startup_from_data(existing, data, html_file)
                                stats['skipped_duplicates'] += 1
                                logger.info(f"跳过重复: {slug} (website_url={website_url} 已存在于 {existing.slug})")
                                continue
                        
                        # 创建新记录
                        startup = self._create_startup_from_data(slug, data, html_file)
                        session.add(startup)
                        stats['created'] += 1
                        logger.debug(f"创建: {slug}")

                    # 收集founder数据
                    if data.get('founder_username'):
                        username = self._normalize_username(data.get('founder_username'))
                        if username and username not in founders_data:
                            founders_data[username] = {
                                'name': data.get('founder_name', username),
                                'username': username,
                                'followers': data.get('founder_followers'),
                                'social_platform': data.get('founder_social_platform'),
                                'profile_url': data.get('founder_profile_url') or f"https://trustmrr.com/founder/{username}",
                            }

                except Exception as e:
                    logger.error(f"处理 {slug} 时出错: {e}")
                    stats['errors'] += 1

            await session.commit()

        # 同步founders
        if founders_data:
            stats['founders_synced'] = await self._sync_founders_data(founders_data)
            await self._link_startups_to_founders()
            await self._ensure_founders_from_featured_creators()
            await self._link_featured_creators_to_founders()

        logger.info(f"快照更新完成: {stats}")
        return stats

    async def _sync_founders_data(self, founders_data: Dict[str, Dict]) -> int:
        """同步founder数据到数据库"""
        async with AsyncSessionLocal() as session:
            count = 0
            for username, data in founders_data.items():
                result = await session.execute(
                    select(Founder).where(Founder.username == username)
                )
                founder = result.scalar_one_or_none()

                if founder:
                    founder.name = data['name']
                    if data.get('followers'):
                        founder.followers = data['followers']
                    if data.get('social_platform'):
                        founder.social_platform = data['social_platform']
                    if data.get('profile_url'):
                        founder.profile_url = data['profile_url']
                    founder.updated_at = datetime.utcnow()
                else:
                    founder = Founder(
                        name=data['name'],
                        username=username,
                        followers=data.get('followers'),
                        social_platform=data.get('social_platform'),
                        profile_url=data.get('profile_url'),
                    )
                    session.add(founder)
                count += 1

            await session.commit()
        return count

    async def _link_startups_to_founders(self) -> int:
        """Populate startups.founder_id from founders.username."""
        async with AsyncSessionLocal() as session:
            result = await session.execute(text(
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
            await session.commit()
            return result.rowcount or 0

    async def _ensure_founders_from_featured_creators(self) -> int:
        """Insert missing founders based on featured_creators usernames/handles."""
        async with AsyncSessionLocal() as session:
            result = await session.execute(text(
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
            await session.commit()
            return result.rowcount or 0

    async def _link_featured_creators_to_founders(self) -> int:
        """Populate featured_creators.founder_id from founders.username."""
        async with AsyncSessionLocal() as session:
            result = await session.execute(text(
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
            await session.commit()
            return result.rowcount or 0

    def _update_startup_from_data(self, startup: Startup, data: dict, html_file: Path):
        """从解析的数据更新Startup对象"""
        # 基本信息
        if data.get('name'):
            startup.name = data['name']
        if data.get('description'):
            startup.description = data['description']

        # URLs
        if data.get('website_url'):
            startup.website_url = data['website_url']
        if data.get('logo_url'):
            startup.logo_url = data['logo_url']
        if data.get('trustmrr_url'):
            startup.profile_url = data['trustmrr_url']

        # Founder信息
        if data.get('founder_name'):
            startup.founder_name = data['founder_name']
        if data.get('founder_username'):
            startup.founder_username = data['founder_username']
        if data.get('founder_followers'):
            startup.founder_followers = data['founder_followers']
        if data.get('founder_social_platform'):
            startup.founder_social_platform = data['founder_social_platform']

        # 财务数据
        if data.get('total_revenue_raw'):
            startup.total_revenue = float(data['total_revenue_raw'])
        if data.get('mrr_raw'):
            startup.mrr = float(data['mrr_raw'])
        if data.get('revenue_last_4_weeks_raw'):
            startup.revenue_30d = float(data['revenue_last_4_weeks_raw'])

        # 增长率
        if data.get('revenue_change_percent'):
            growth_str = data['revenue_change_percent'].replace('%', '').strip()
            try:
                startup.growth_rate = float(growth_str)
            except ValueError:
                pass

        # 出售信息
        if 'is_for_sale' in data:
            startup.is_for_sale = data['is_for_sale']
        if data.get('asking_price_raw'):
            startup.asking_price = float(data['asking_price_raw'])
        if data.get('revenue_multiple'):
            multiple_str = data['revenue_multiple'].lower().replace('x', '').strip()
            try:
                startup.multiple = float(multiple_str)
            except ValueError:
                pass
        if data.get('buyers_interested'):
            startup.buyers_interested = data['buyers_interested']

        # 公司信息
        if data.get('founded'):
            startup.founded_date = data['founded']
        if data.get('country'):
            startup.country = data['country']
        if data.get('country_code'):
            startup.country_code = data['country_code']
        if data.get('category'):
            startup.category = data['category']

        # 排名和订阅数
        if data.get('rank'):
            startup.rank = data['rank']
        if data.get('active_subscriptions'):
            startup.customers_count = data['active_subscriptions']

        # 验证状态
        if data.get('verified_source'):
            startup.is_verified = True
            startup.verified_source = data['verified_source']

        # 元数据
        startup.html_snapshot_path = str(html_file)
        startup.updated_at = datetime.utcnow()

    def _create_startup_from_data(self, slug: str, data: dict, html_file: Path) -> Startup:
        """从解析的数据创建Startup对象"""
        startup = Startup(
            slug=slug,
            name=data.get('name', slug),
            html_snapshot_path=str(html_file),
        )
        self._update_startup_from_data(startup, data, html_file)
        return startup


async def sync_leaderboard_from_startups() -> int:
    """
    从Startup表的rank数据同步到LeaderboardEntry表

    Returns:
        同步的记录数量
    """
    await init_db()

    async with AsyncSessionLocal() as session:
        # 查询所有有rank的startup
        result = await session.execute(
            select(Startup).where(Startup.rank.isnot(None)).order_by(Startup.rank)
        )
        startups = result.scalars().all()

        logger.info(f"找到 {len(startups)} 个有rank数据的startup")

        # 创建leaderboard entries
        count = 0
        for startup in startups:
            entry = LeaderboardEntry(
                startup_slug=startup.slug,
                rank=startup.rank,
                revenue_30d=startup.revenue_30d,
                growth_rate=startup.growth_rate,
                multiple=startup.multiple,
            )
            session.add(entry)
            count += 1

        await session.commit()
        logger.info(f"Leaderboard同步完成: {count} 条记录")
        return count


async def get_database_stats() -> Dict:
    """获取数据库统计信息"""
    await init_db()

    async with AsyncSessionLocal() as session:
        startup_count = await session.scalar(select(func.count(Startup.id)))
        founder_count = await session.scalar(select(func.count(Founder.id)))
        leaderboard_count = await session.scalar(select(func.count(LeaderboardEntry.id)))

        # 获取各分类的startup数量
        categories_result = await session.execute(
            select(Startup.category, func.count(Startup.id))
            .group_by(Startup.category)
            .order_by(func.count(Startup.id).desc())
            .limit(10)
        )
        top_categories = [(cat or "Unknown", count) for cat, count in categories_result.all()]

        return {
            'startups': startup_count,
            'founders': founder_count,
            'leaderboard_entries': leaderboard_count,
            'top_categories': top_categories,
        }


# CLI入口（可独立测试）
if __name__ == '__main__':
    import sys

    async def main():
        manager = DataSyncManager()

        if len(sys.argv) > 1:
            command = sys.argv[1]
            if command == 'sync':
                await manager.sync_founders_from_startups()
            elif command == 'update':
                snapshot_dir = sys.argv[2] if len(sys.argv) > 2 else None
                await manager.update_from_snapshots(snapshot_dir)
            elif command == 'stats':
                stats = await get_database_stats()
                print("\n数据库统计:")
                print(f"  Startups: {stats['startups']}")
                print(f"  Founders: {stats['founders']}")
                print(f"  Leaderboard: {stats['leaderboard_entries']}")
        else:
            print("Usage: python data_sync.py [sync|update|stats]")

    asyncio.run(main())
