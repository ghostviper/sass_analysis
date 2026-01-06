"""
Analytics API Routes - Trend analysis and statistics
"""

from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from database.db import get_db
from database.models import Startup, ProductSelectionAnalysis

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


@router.get("/analytics/data-info")
async def get_data_info(
    db: AsyncSession = Depends(get_db),
):
    """
    获取数据源信息和统计
    用于在UI中展示数据说明和局限性
    """
    # 总产品数
    total_result = await db.execute(select(func.count(Startup.id)))
    total_products = total_result.scalar() or 0

    # 总分类数
    cat_result = await db.execute(
        select(func.count(func.distinct(Startup.category)))
    )
    total_categories = cat_result.scalar() or 0

    # 总国家数
    country_result = await db.execute(
        select(func.count(func.distinct(Startup.country_code)))
    )
    total_countries = country_result.scalar() or 0

    # 有收入数据的产品数
    revenue_result = await db.execute(
        select(func.count(Startup.id))
        .where(Startup.revenue_30d.isnot(None))
        .where(Startup.revenue_30d > 0)
    )
    products_with_revenue = revenue_result.scalar() or 0

    # 已分析的产品数
    analyzed_result = await db.execute(
        select(func.count(ProductSelectionAnalysis.id))
    )
    analyzed_products = analyzed_result.scalar() or 0

    # 最后爬取时间
    last_crawl_result = await db.execute(
        select(func.max(Startup.scraped_at))
    )
    last_crawl_time = last_crawl_result.scalar()

    # 最后分析时间
    last_analysis_result = await db.execute(
        select(func.max(ProductSelectionAnalysis.analyzed_at))
    )
    last_analysis_time = last_analysis_result.scalar()

    return {
        "data_source": "TrustMRR",
        "data_source_url": "https://trustmrr.com",
        "total_products": total_products,
        "total_categories": total_categories,
        "total_countries": total_countries,
        "products_with_revenue": products_with_revenue,
        "analyzed_products": analyzed_products,
        "last_crawl_time": last_crawl_time.isoformat() if last_crawl_time else None,
        "last_analysis_time": last_analysis_time.isoformat() if last_analysis_time else None,
        "coverage_note": "仅包含愿意公开收入数据的产品，非市场全貌",
        "coverage_note_en": "Only includes products willing to disclose revenue data, not a complete market picture",
        "limitations": [
            "数据来源单一，仅来自TrustMRR平台",
            "样本量有限，部分赛道数据较少",
            "收入数据为自报告，可能存在偏差",
            "部分产品缺少粉丝数据，IP依赖度为估算值",
        ],
        "limitations_en": [
            "Single data source from TrustMRR platform",
            "Limited sample size, some categories have sparse data",
            "Revenue data is self-reported, may have bias",
            "Some products lack follower data, IP dependency is estimated",
        ],
    }


@router.get("/analytics/tag-distribution")
async def get_tag_distribution(
    db: AsyncSession = Depends(get_db),
):
    """
    获取各标签维度的分布统计
    用于了解数据集的整体特征
    """
    distributions = {}

    # 收入层级分布
    revenue_tier_result = await db.execute(
        select(
            ProductSelectionAnalysis.revenue_tier,
            func.count(ProductSelectionAnalysis.id).label("count")
        )
        .where(ProductSelectionAnalysis.revenue_tier.isnot(None))
        .group_by(ProductSelectionAnalysis.revenue_tier)
    )
    distributions["revenue_tier"] = [
        {"value": tier, "count": count}
        for tier, count in revenue_tier_result.all()
    ]

    # 技术复杂度分布
    tech_result = await db.execute(
        select(
            ProductSelectionAnalysis.tech_complexity_level,
            func.count(ProductSelectionAnalysis.id).label("count")
        )
        .where(ProductSelectionAnalysis.tech_complexity_level.isnot(None))
        .group_by(ProductSelectionAnalysis.tech_complexity_level)
    )
    distributions["tech_complexity_level"] = [
        {"value": level, "count": count}
        for level, count in tech_result.all()
    ]

    # AI依赖分布
    ai_result = await db.execute(
        select(
            ProductSelectionAnalysis.ai_dependency_level,
            func.count(ProductSelectionAnalysis.id).label("count")
        )
        .where(ProductSelectionAnalysis.ai_dependency_level.isnot(None))
        .group_by(ProductSelectionAnalysis.ai_dependency_level)
    )
    distributions["ai_dependency_level"] = [
        {"value": level, "count": count}
        for level, count in ai_result.all()
    ]

    # 目标客户分布
    customer_result = await db.execute(
        select(
            ProductSelectionAnalysis.target_customer,
            func.count(ProductSelectionAnalysis.id).label("count")
        )
        .where(ProductSelectionAnalysis.target_customer.isnot(None))
        .group_by(ProductSelectionAnalysis.target_customer)
    )
    distributions["target_customer"] = [
        {"value": customer, "count": count}
        for customer, count in customer_result.all()
    ]

    # 增长驱动分布
    growth_result = await db.execute(
        select(
            ProductSelectionAnalysis.growth_driver,
            func.count(ProductSelectionAnalysis.id).label("count")
        )
        .where(ProductSelectionAnalysis.growth_driver.isnot(None))
        .group_by(ProductSelectionAnalysis.growth_driver)
    )
    distributions["growth_driver"] = [
        {"value": driver, "count": count}
        for driver, count in growth_result.all()
    ]

    # 产品阶段分布
    stage_result = await db.execute(
        select(
            ProductSelectionAnalysis.product_stage,
            func.count(ProductSelectionAnalysis.id).label("count")
        )
        .where(ProductSelectionAnalysis.product_stage.isnot(None))
        .group_by(ProductSelectionAnalysis.product_stage)
    )
    distributions["product_stage"] = [
        {"value": stage, "count": count}
        for stage, count in stage_result.all()
    ]

    # 功能复杂度分布
    feature_result = await db.execute(
        select(
            ProductSelectionAnalysis.feature_complexity,
            func.count(ProductSelectionAnalysis.id).label("count")
        )
        .where(ProductSelectionAnalysis.feature_complexity.isnot(None))
        .group_by(ProductSelectionAnalysis.feature_complexity)
    )
    distributions["feature_complexity"] = [
        {"value": complexity, "count": count}
        for complexity, count in feature_result.all()
    ]

    # 启动成本分布
    cost_result = await db.execute(
        select(
            ProductSelectionAnalysis.startup_cost_level,
            func.count(ProductSelectionAnalysis.id).label("count")
        )
        .where(ProductSelectionAnalysis.startup_cost_level.isnot(None))
        .group_by(ProductSelectionAnalysis.startup_cost_level)
    )
    distributions["startup_cost_level"] = [
        {"value": cost, "count": count}
        for cost, count in cost_result.all()
    ]

    return {
        "distributions": distributions
    }

