"""
Founder Leaderboard API Routes
独立开发者排行榜接口
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, desc, asc, case
from sqlalchemy.ext.asyncio import AsyncSession

from database.db import get_db
from database.models import Startup, Founder

router = APIRouter(prefix="/leaderboard", tags=["Leaderboard"])


@router.get("/founders")
async def get_founder_leaderboard(
    sort_by: str = Query(
        "total_revenue",
        regex="^(total_revenue|product_count|avg_revenue|max_growth|followers)$"
    ),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    limit: int = Query(50, ge=1, le=200),
    page: int = Query(1, ge=1),
    min_products: int = Query(1, ge=1),
    search: Optional[str] = Query(None, description="Search by username or name"),
    db: AsyncSession = Depends(get_db),
):
    """
    获取创始人排行榜

    排序选项:
    - total_revenue: 总收入
    - product_count: 产品数量
    - avg_revenue: 平均收入
    - max_growth: 最高增长率
    - followers: 粉丝数
    """
    # 聚合查询：按创始人用户名分组
    # 使用 founder_username 作为唯一标识
    query = (
        select(
            Startup.founder_username.label("username"),
            func.max(Startup.founder_name).label("name"),
            func.count(Startup.id).label("product_count"),
            func.sum(func.coalesce(Startup.revenue_30d, 0)).label("total_revenue"),
            func.avg(func.coalesce(Startup.revenue_30d, 0)).label("avg_revenue"),
            func.max(func.coalesce(Startup.growth_rate, 0)).label("max_growth"),
            func.max(func.coalesce(Startup.founder_followers, 0)).label("followers"),
            func.max(Startup.founder_social_platform).label("social_platform"),
            func.max(Startup.founder_avatar_url).label("avatar_url"),
        )
        .where(Startup.founder_username.isnot(None))
        .where(Startup.founder_username != "")
        .group_by(Startup.founder_username)
        .having(func.count(Startup.id) >= min_products)
    )

    # 搜索过滤
    if search:
        search_pattern = f"%{search}%"
        query = query.having(
            (Startup.founder_username.ilike(search_pattern)) |
            (func.max(Startup.founder_name).ilike(search_pattern))
        )

    # 计算总数
    count_subquery = query.subquery()
    count_result = await db.execute(select(func.count()).select_from(count_subquery))
    total = count_result.scalar() or 0

    # 应用排序
    sort_column_map = {
        "total_revenue": "total_revenue",
        "product_count": "product_count",
        "avg_revenue": "avg_revenue",
        "max_growth": "max_growth",
        "followers": "followers",
    }
    sort_col = sort_column_map.get(sort_by, "total_revenue")

    if sort_order == "desc":
        query = query.order_by(desc(sort_col))
    else:
        query = query.order_by(asc(sort_col))

    # 分页
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    rows = result.all()

    # 构建响应数据
    founders = []
    for i, row in enumerate(rows):
        # 构建社交链接
        social_url = None
        if row.username:
            platform = row.social_platform or "twitter"
            if platform.lower() in ["twitter", "x"]:
                social_url = f"https://x.com/{row.username}"
            elif platform.lower() == "linkedin":
                social_url = f"https://linkedin.com/in/{row.username}"
            else:
                social_url = f"https://x.com/{row.username}"

        # 构建头像URL（如果没有则使用unavatar.io）
        avatar_url = row.avatar_url
        if not avatar_url and row.username:
            avatar_url = f"https://unavatar.io/x/{row.username}"

        founders.append({
            "rank": offset + i + 1,
            "username": row.username,
            "name": row.name or row.username,
            "avatar_url": avatar_url,
            "product_count": row.product_count,
            "total_revenue": round(row.total_revenue or 0, 2),
            "avg_revenue": round(row.avg_revenue or 0, 2),
            "max_growth": round(row.max_growth or 0, 2),
            "followers": row.followers or 0,
            "social_platform": row.social_platform or "twitter",
            "social_url": social_url,
        })

    return {
        "data": founders,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit if total > 0 else 0,
        },
        "sort": {
            "by": sort_by,
            "order": sort_order,
        }
    }


@router.get("/founders/{username}")
async def get_founder_detail(
    username: str,
    db: AsyncSession = Depends(get_db),
):
    """获取创始人详情及其所有产品"""
    # 获取该创始人的所有产品
    result = await db.execute(
        select(Startup)
        .where(Startup.founder_username == username)
        .order_by(desc(Startup.revenue_30d))
    )
    startups = result.scalars().all()

    if not startups:
        return {"error": "Founder not found", "data": None}

    # 聚合统计
    total_revenue = sum(s.revenue_30d or 0 for s in startups)
    avg_revenue = total_revenue / len(startups) if startups else 0
    max_growth = max((s.growth_rate or 0 for s in startups), default=0)
    followers = max((s.founder_followers or 0 for s in startups), default=0)

    first_startup = startups[0]
    social_platform = first_startup.founder_social_platform or "twitter"

    # 构建社交链接
    if social_platform.lower() in ["twitter", "x"]:
        social_url = f"https://x.com/{username}"
    elif social_platform.lower() == "linkedin":
        social_url = f"https://linkedin.com/in/{username}"
    else:
        social_url = f"https://x.com/{username}"

    return {
        "data": {
            "username": username,
            "name": first_startup.founder_name or username,
            "product_count": len(startups),
            "total_revenue": round(total_revenue, 2),
            "avg_revenue": round(avg_revenue, 2),
            "max_growth": round(max_growth, 2),
            "followers": followers,
            "social_platform": social_platform,
            "social_url": social_url,
            "products": [s.to_dict() for s in startups],
        }
    }


@router.get("/stats")
async def get_leaderboard_stats(
    db: AsyncSession = Depends(get_db),
):
    """获取排行榜统计概览"""
    # 统计有效创始人数量（有产品的）
    founder_count_result = await db.execute(
        select(func.count(func.distinct(Startup.founder_username)))
        .where(Startup.founder_username.isnot(None))
        .where(Startup.founder_username != "")
    )
    total_founders = founder_count_result.scalar() or 0

    # 统计有多个产品的创始人
    multi_product_result = await db.execute(
        select(func.count())
        .select_from(
            select(Startup.founder_username)
            .where(Startup.founder_username.isnot(None))
            .group_by(Startup.founder_username)
            .having(func.count(Startup.id) > 1)
            .subquery()
        )
    )
    multi_product_founders = multi_product_result.scalar() or 0

    # 总收入
    revenue_result = await db.execute(
        select(func.sum(Startup.revenue_30d))
    )
    total_revenue = revenue_result.scalar() or 0

    # 平均每个创始人的收入
    avg_founder_revenue = total_revenue / total_founders if total_founders > 0 else 0

    return {
        "total_founders": total_founders,
        "multi_product_founders": multi_product_founders,
        "total_revenue": round(total_revenue, 2),
        "avg_founder_revenue": round(avg_founder_revenue, 2),
    }
