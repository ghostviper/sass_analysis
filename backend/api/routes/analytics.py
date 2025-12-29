"""
Analytics API Routes - Trend analysis and statistics
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from database.db import get_db
from database.models import Startup

router = APIRouter()


@router.get("/analytics/overview")
async def get_overview(
    db: AsyncSession = Depends(get_db),
):
    """Get overall statistics overview"""
    # Total startups
    total_result = await db.execute(select(func.count(Startup.id)))
    total_startups = total_result.scalar() or 0
    
    # Total revenue
    revenue_result = await db.execute(select(func.sum(Startup.revenue_30d)))
    total_revenue = revenue_result.scalar() or 0
    
    # Average metrics
    avg_result = await db.execute(
        select(
            func.avg(Startup.revenue_30d).label("avg_revenue"),
            func.avg(Startup.asking_price).label("avg_price"),
            func.avg(Startup.multiple).label("avg_multiple"),
            func.avg(Startup.growth_rate).label("avg_growth"),
        )
    )
    avg_data = avg_result.first()
    
    # Category count
    cat_result = await db.execute(
        select(func.count(func.distinct(Startup.category)))
    )
    category_count = cat_result.scalar() or 0
    
    return {
        "total_startups": total_startups,
        "total_revenue_30d": round(total_revenue, 2),
        "avg_revenue_30d": round(avg_data.avg_revenue or 0, 2),
        "avg_asking_price": round(avg_data.avg_price or 0, 2),
        "avg_multiple": round(avg_data.avg_multiple or 0, 2),
        "avg_growth_rate": round(avg_data.avg_growth or 0, 2),
        "category_count": category_count,
    }


@router.get("/analytics/category-stats")
async def get_category_stats(
    db: AsyncSession = Depends(get_db),
):
    """Get statistics grouped by category"""
    result = await db.execute(
        select(
            Startup.category,
            func.count(Startup.id).label("count"),
            func.sum(Startup.revenue_30d).label("total_revenue"),
            func.avg(Startup.revenue_30d).label("avg_revenue"),
            func.avg(Startup.multiple).label("avg_multiple"),
            func.avg(Startup.growth_rate).label("avg_growth"),
        )
        .where(Startup.category.isnot(None))
        .group_by(Startup.category)
        .order_by(desc("total_revenue"))
    )
    categories = result.all()
    
    return {
        "data": [
            {
                "category": cat,
                "count": count,
                "total_revenue": round(total_rev or 0, 2),
                "avg_revenue": round(avg_rev or 0, 2),
                "avg_multiple": round(avg_mult or 0, 2),
                "avg_growth": round(avg_growth or 0, 2),
            }
            for cat, count, total_rev, avg_rev, avg_mult, avg_growth in categories
        ]
    }


@router.get("/analytics/top-growth")
async def get_top_growth(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """Get startups with highest growth rates"""
    result = await db.execute(
        select(Startup)
        .where(Startup.growth_rate.isnot(None))
        .order_by(desc(Startup.growth_rate))
        .limit(limit)
    )
    startups = result.scalars().all()
    
    return {
        "data": [s.to_dict() for s in startups]
    }


@router.get("/analytics/top-revenue")
async def get_top_revenue(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """Get startups with highest revenue"""
    result = await db.execute(
        select(Startup)
        .where(Startup.revenue_30d.isnot(None))
        .order_by(desc(Startup.revenue_30d))
        .limit(limit)
    )
    startups = result.scalars().all()
    
    return {
        "data": [s.to_dict() for s in startups]
    }


@router.get("/analytics/best-deals")
async def get_best_deals(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """Get startups with lowest multiples (best value)"""
    result = await db.execute(
        select(Startup)
        .where(Startup.multiple.isnot(None))
        .where(Startup.multiple > 0)
        .order_by(Startup.multiple)
        .limit(limit)
    )
    startups = result.scalars().all()
    
    return {
        "data": [s.to_dict() for s in startups]
    }


@router.get("/analytics/market-segments")
async def get_market_segments(
    db: AsyncSession = Depends(get_db),
):
    """Analyze B2B vs B2C market segments based on categories"""
    # B2B categories
    b2b_cats = ["Developer Tools", "SaaS", "Analytics", "Sales", "Recruiting", "Security"]
    # B2C categories
    b2c_cats = ["Health", "Education", "Social Media", "Content Creation", "Travel"]
    
    # B2B stats
    b2b_result = await db.execute(
        select(
            func.count(Startup.id).label("count"),
            func.sum(Startup.revenue_30d).label("total_revenue"),
            func.avg(Startup.revenue_30d).label("avg_revenue"),
        )
        .where(Startup.category.in_(b2b_cats))
    )
    b2b = b2b_result.first()
    
    # B2C stats
    b2c_result = await db.execute(
        select(
            func.count(Startup.id).label("count"),
            func.sum(Startup.revenue_30d).label("total_revenue"),
            func.avg(Startup.revenue_30d).label("avg_revenue"),
        )
        .where(Startup.category.in_(b2c_cats))
    )
    b2c = b2c_result.first()
    
    return {
        "b2b": {
            "categories": b2b_cats,
            "count": b2b.count or 0,
            "total_revenue": round(b2b.total_revenue or 0, 2),
            "avg_revenue": round(b2b.avg_revenue or 0, 2),
        },
        "b2c": {
            "categories": b2c_cats,
            "count": b2c.count or 0,
            "total_revenue": round(b2c.total_revenue or 0, 2),
            "avg_revenue": round(b2c.avg_revenue or 0, 2),
        }
    }
