"""
Startups API Routes
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select, func, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession

from database.db import get_db
from database.models import Startup, Founder

router = APIRouter()


@router.get("/startups")
async def get_startups(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    country_code: Optional[str] = None,
    sort_by: str = Query("revenue_30d", regex="^(revenue_30d|asking_price|multiple|growth_rate|name|scraped_at)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    search: Optional[str] = None,
    min_revenue: Optional[float] = None,
    max_revenue: Optional[float] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Get paginated list of startups with filtering and sorting
    """
    # Base query
    query = select(Startup)
    count_query = select(func.count(Startup.id))

    # Apply filters
    if category:
        query = query.where(Startup.category == category)
        count_query = count_query.where(Startup.category == category)

    if country_code:
        query = query.where(Startup.country_code == country_code)
        count_query = count_query.where(Startup.country_code == country_code)

    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            (Startup.name.ilike(search_pattern)) |
            (Startup.description.ilike(search_pattern))
        )
        count_query = count_query.where(
            (Startup.name.ilike(search_pattern)) |
            (Startup.description.ilike(search_pattern))
        )
    
    if min_revenue is not None:
        query = query.where(Startup.revenue_30d >= min_revenue)
        count_query = count_query.where(Startup.revenue_30d >= min_revenue)
    
    if max_revenue is not None:
        query = query.where(Startup.revenue_30d <= max_revenue)
        count_query = count_query.where(Startup.revenue_30d <= max_revenue)
    
    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Apply sorting
    sort_column = getattr(Startup, sort_by)
    if sort_order == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))
    
    # Apply pagination
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit)
    
    # Execute query
    result = await db.execute(query)
    startups = result.scalars().all()
    
    return {
        "data": [s.to_dict() for s in startups],
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit,
        }
    }


@router.get("/startups/{slug}")
async def get_startup(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a single startup by slug"""
    result = await db.execute(
        select(Startup).where(Startup.slug == slug)
    )
    startup = result.scalar_one_or_none()
    
    if not startup:
        raise HTTPException(status_code=404, detail="Startup not found")
    
    return startup.to_dict()


@router.get("/categories")
async def get_categories(
    db: AsyncSession = Depends(get_db),
):
    """Get list of all categories with counts"""
    result = await db.execute(
        select(Startup.category, func.count(Startup.id).label("count"))
        .where(Startup.category.isnot(None))
        .group_by(Startup.category)
        .order_by(desc("count"))
    )
    categories = result.all()

    return {
        "categories": [
            {"name": cat, "count": count}
            for cat, count in categories
        ]
    }


@router.get("/countries")
async def get_countries(
    db: AsyncSession = Depends(get_db),
):
    """Get list of all countries with counts"""
    result = await db.execute(
        select(Startup.country_code, Startup.country, func.count(Startup.id).label("count"))
        .where(Startup.country_code.isnot(None))
        .group_by(Startup.country_code, Startup.country)
        .order_by(desc("count"))
    )
    countries = result.all()

    return {
        "countries": [
            {"code": code, "name": name or code, "count": count}
            for code, name, count in countries
        ]
    }


@router.get("/leaderboard")
async def get_leaderboard(
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Get founder leaderboard"""
    result = await db.execute(
        select(Founder)
        .order_by(asc(Founder.rank))
        .limit(limit)
    )
    founders = result.scalars().all()
    
    return {
        "data": [f.to_dict() for f in founders],
        "total": len(founders),
    }
