"""
数据审计脚本 - 检查数据库数据质量和完整性
"""
import asyncio
from dotenv import load_dotenv

load_dotenv()

async def audit_data():
    """审计数据库数据质量"""
    from database.db import get_db_session
    from sqlalchemy import select, func
    from database.models import Startup, LandingPageSnapshot, LandingPageAnalysis

    async with get_db_session() as db:
        print("=" * 60)
        print("数据库数据质量审计报告")
        print("=" * 60)

        # 1. 基础统计
        print("\n[1] 基础统计")
        total = await db.execute(select(func.count(Startup.id)))
        total_count = total.scalar()
        print(f"  总产品数: {total_count}")

        # 2. 关键字段完整性
        print("\n[2] 关键字段完整性检查")

        fields = [
            ("description", Startup.description.isnot(None)),
            ("category", Startup.category.isnot(None)),
            ("website_url", Startup.website_url.isnot(None)),
            ("revenue_30d", Startup.revenue_30d.isnot(None)),
            ("revenue_30d > 0", Startup.revenue_30d > 0),
            ("founder_followers", Startup.founder_followers.isnot(None)),
            ("founder_followers > 0", Startup.founder_followers > 0),
            ("founded_date", Startup.founded_date.isnot(None)),
            ("growth_rate", Startup.growth_rate.isnot(None)),
            ("mrr", Startup.mrr.isnot(None)),
            ("customers_count", Startup.customers_count.isnot(None)),
        ]

        for field_name, condition in fields:
            result = await db.execute(
                select(func.count(Startup.id)).where(condition)
            )
            count = result.scalar()
            pct = (count / total_count * 100) if total_count > 0 else 0
            status = "✓" if pct > 80 else "△" if pct > 50 else "✗"
            print(f"  {status} {field_name}: {count}/{total_count} ({pct:.1f}%)")

        # 3. 分类统计
        print("\n[3] 分类(Category)统计")
        result = await db.execute(
            select(Startup.category, func.count(Startup.id))
            .where(Startup.category.isnot(None))
            .group_by(Startup.category)
            .order_by(func.count(Startup.id).desc())
            .limit(15)
        )
        categories = result.all()
        for cat, count in categories:
            print(f"  {cat}: {count}")

        # 4. 收入分布
        print("\n[4] 收入分布 (revenue_30d)")
        result = await db.execute(
            select(Startup.revenue_30d)
            .where(Startup.revenue_30d.isnot(None))
            .where(Startup.revenue_30d > 0)
            .order_by(Startup.revenue_30d.desc())
        )
        revenues = [r[0] for r in result.all()]

        if revenues:
            print(f"  有收入产品数: {len(revenues)}")
            print(f"  总收入: ${sum(revenues):,.0f}")
            print(f"  平均收入: ${sum(revenues)/len(revenues):,.0f}")
            print(f"  中位数收入: ${sorted(revenues)[len(revenues)//2]:,.0f}")
            print(f"  最高收入: ${max(revenues):,.0f}")
            print(f"  最低收入: ${min(revenues):,.0f}")

            # 收入区间分布
            print("\n  收入区间分布:")
            brackets = [
                (0, 1000, "$0-1K"),
                (1000, 5000, "$1K-5K"),
                (5000, 10000, "$5K-10K"),
                (10000, 50000, "$10K-50K"),
                (50000, 100000, "$50K-100K"),
                (100000, float('inf'), "$100K+"),
            ]
            for low, high, label in brackets:
                count = len([r for r in revenues if low <= r < high])
                pct = count / len(revenues) * 100
                print(f"    {label}: {count} ({pct:.1f}%)")

        # 5. 粉丝数分布
        print("\n[5] 粉丝数分布 (founder_followers)")
        result = await db.execute(
            select(Startup.founder_followers)
            .where(Startup.founder_followers.isnot(None))
            .where(Startup.founder_followers > 0)
        )
        followers = [r[0] for r in result.all()]

        if followers:
            print(f"  有粉丝数据的产品: {len(followers)}")
            print(f"  平均粉丝数: {sum(followers)/len(followers):,.0f}")
            print(f"  中位数粉丝: {sorted(followers)[len(followers)//2]:,.0f}")

            # 粉丝区间
            print("\n  粉丝区间分布:")
            f_brackets = [
                (0, 1000, "0-1K"),
                (1000, 5000, "1K-5K"),
                (5000, 10000, "5K-10K"),
                (10000, 50000, "10K-50K"),
                (50000, float('inf'), "50K+"),
            ]
            for low, high, label in f_brackets:
                count = len([f for f in followers if low <= f < high])
                pct = count / len(followers) * 100
                print(f"    {label}: {count} ({pct:.1f}%)")

        # 6. 关键分析缺失
        print("\n[6] 关键分析数据缺失情况")

        # 有收入但没有粉丝数据的产品
        result = await db.execute(
            select(func.count(Startup.id))
            .where(Startup.revenue_30d > 0)
            .where((Startup.founder_followers.is_(None)) | (Startup.founder_followers == 0))
        )
        no_followers = result.scalar()
        print(f"  有收入但无粉丝数据: {no_followers}")

        # 没有description的产品
        result = await db.execute(
            select(func.count(Startup.id))
            .where(Startup.revenue_30d > 0)
            .where((Startup.description.is_(None)) | (Startup.description == ""))
        )
        no_desc = result.scalar()
        print(f"  有收入但无描述: {no_desc}")

        # 没有category的产品
        result = await db.execute(
            select(func.count(Startup.id))
            .where(Startup.revenue_30d > 0)
            .where(Startup.category.is_(None))
        )
        no_cat = result.scalar()
        print(f"  有收入但无分类: {no_cat}")

        # 7. Landing Page分析情况
        print("\n[7] Landing Page分析情况")

        lp_total = await db.execute(select(func.count(LandingPageSnapshot.id)))
        lp_count = lp_total.scalar()
        print(f"  Landing Page快照数: {lp_count}")

        lp_success = await db.execute(
            select(func.count(LandingPageSnapshot.id))
            .where(LandingPageSnapshot.status == "success")
        )
        print(f"  成功快照数: {lp_success.scalar()}")

        lp_analysis = await db.execute(select(func.count(LandingPageAnalysis.id)))
        print(f"  AI分析完成数: {lp_analysis.scalar()}")

        # 8. 数据分析可行性评估
        print("\n" + "=" * 60)
        print("数据分析可行性评估")
        print("=" * 60)

        has_revenue = len(revenues) if revenues else 0
        has_followers = len(followers) if followers else 0

        print(f"\n赛道分析可行性: ", end="")
        if has_revenue > 100 and len(categories) > 5:
            print("✓ 可行 (有足够收入数据和分类)")
        else:
            print("△ 数据不足")

        print(f"选品分析可行性: ", end="")
        if has_revenue > 100 and has_followers > 50:
            print("✓ 可行")
        else:
            print("△ 粉丝数据缺失严重，影响IP依赖度分析")

        print(f"组合分析1可行性: ", end="")
        # 低粉丝+高收入+简单描述+创立<1年
        result = await db.execute(
            select(func.count(Startup.id))
            .where(Startup.founded_date.isnot(None))
        )
        has_founded = result.scalar()
        if has_followers > 50 and has_founded > 50:
            print("✓ 可行")
        else:
            print(f"△ 数据不足 (粉丝数据:{has_followers}, 成立日期:{has_founded})")

        print()

if __name__ == "__main__":
    asyncio.run(audit_data())
