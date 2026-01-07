"""检查 RevenueHistory 表中的数据"""
import asyncio
from database.db import AsyncSessionLocal
from database.models import RevenueHistory
from sqlalchemy import select, func


async def check():
    async with AsyncSessionLocal() as session:
        # 统计总记录数
        result = await session.execute(select(func.count(RevenueHistory.id)))
        count = result.scalar()
        print(f'RevenueHistory 记录数: {count}')

        if count > 0:
            # 查看前5条记录
            result = await session.execute(select(RevenueHistory).limit(5))
            records = result.scalars().all()
            print('\n前5条记录:')
            for r in records:
                print(f'  startup_id={r.startup_id}, date={r.date}, revenue={r.revenue}, mrr={r.mrr}')
        else:
            print('\n数据库中没有收入时序数据！')


if __name__ == "__main__":
    asyncio.run(check())
