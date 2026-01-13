"""清理重复的产品数据 - 基于 website_url 去重，保留最新记录"""
import asyncio
from sqlalchemy import select, func, delete
from database.db import AsyncSessionLocal, init_db
from database.models import Startup, LandingPageSnapshot, LandingPageAnalysis, ProductSelectionAnalysis


async def cleanup_duplicates(dry_run: bool = True):
    """
    清理重复数据
    
    Args:
        dry_run: 如果为 True，只显示将要删除的记录，不实际删除
    """
    await init_db()
    
    async with AsyncSessionLocal() as db:
        # 查找 website_url 重复的记录
        result = await db.execute(
            select(Startup.website_url, func.count(Startup.id).label('count'))
            .where(Startup.website_url.isnot(None))
            .where(Startup.website_url != '')
            .group_by(Startup.website_url)
            .having(func.count(Startup.id) > 1)
        )
        dup_urls = result.fetchall()
        
        if not dup_urls:
            print("✅ 没有发现重复的 website_url")
            return
        
        print(f"发现 {len(dup_urls)} 组重复的 website_url")
        print("=" * 80)
        
        ids_to_delete = []
        
        for row in dup_urls:
            url = row.website_url
            
            # 获取所有重复记录，按 scraped_at 降序排列
            result = await db.execute(
                select(Startup)
                .where(Startup.website_url == url)
                .order_by(Startup.scraped_at.desc())
            )
            startups = result.scalars().all()
            
            # 保留第一条（最新的），删除其他的
            keep = startups[0]
            to_delete = startups[1:]
            
            print(f"\n【{url}】")
            print(f"  保留: ID={keep.id}, slug={keep.slug}, name={keep.name}")
            print(f"        revenue_30d=${keep.revenue_30d}, scraped_at={keep.scraped_at}")
            
            for s in to_delete:
                print(f"  删除: ID={s.id}, slug={s.slug}, name={s.name}")
                print(f"        revenue_30d=${s.revenue_30d}, scraped_at={s.scraped_at}")
                ids_to_delete.append(s.id)
        
        print("\n" + "=" * 80)
        print(f"总计将删除 {len(ids_to_delete)} 条记录")
        
        if dry_run:
            print("\n⚠️  这是 DRY RUN 模式，没有实际删除数据")
            print("   运行 'python cleanup_duplicates.py --execute' 来实际执行删除")
        else:
            if ids_to_delete:
                # 先删除关联的分析数据
                await db.execute(
                    delete(LandingPageAnalysis)
                    .where(LandingPageAnalysis.startup_id.in_(ids_to_delete))
                )
                await db.execute(
                    delete(LandingPageSnapshot)
                    .where(LandingPageSnapshot.startup_id.in_(ids_to_delete))
                )
                await db.execute(
                    delete(ProductSelectionAnalysis)
                    .where(ProductSelectionAnalysis.startup_id.in_(ids_to_delete))
                )
                
                # 删除 startup 记录
                await db.execute(
                    delete(Startup)
                    .where(Startup.id.in_(ids_to_delete))
                )
                
                await db.commit()
                print(f"\n✅ 已删除 {len(ids_to_delete)} 条重复记录")


if __name__ == "__main__":
    import sys
    
    execute = '--execute' in sys.argv
    asyncio.run(cleanup_duplicates(dry_run=not execute))
