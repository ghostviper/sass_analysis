"""
Product Analysis API - 选品分析接口
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.db import get_db
from database.models import Startup, ProductSelectionAnalysis, ComprehensiveAnalysis
from analysis.product_selector import ProductSelector
from analysis.comprehensive import ComprehensiveAnalyzer

router = APIRouter(prefix="/analysis/product", tags=["Product Analysis"])


@router.get("/opportunities")
async def get_opportunities(
    min_revenue: float = Query(3000, ge=0),
    max_complexity: str = Query("medium", regex="^(low|medium|high)$"),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """获取适合个人开发者的机会产品列表"""
    selector = ProductSelector(db)
    opportunities = await selector.find_opportunities(
        min_revenue=min_revenue,
        max_complexity=max_complexity,
        limit=limit
    )

    # 获取对应的startup信息
    result_data = []
    for o in opportunities:
        startup_result = await db.execute(
            select(Startup).where(Startup.id == o.startup_id)
        )
        startup = startup_result.scalar_one_or_none()
        if startup:
            result_data.append({
                "startup": startup.to_dict(),
                "analysis": o.to_dict()
            })

    return {
        "data": result_data,
        "total": len(result_data),
        "filters": {
            "min_revenue": min_revenue,
            "max_complexity": max_complexity,
        }
    }


@router.get("/filter/product-driven")
async def get_product_driven(
    min_revenue: float = Query(5000, ge=0),
    max_followers: int = Query(5000, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """筛选产品驱动型产品（高收入低粉丝）"""
    selector = ProductSelector(db)
    products = await selector.find_product_driven(
        min_revenue=min_revenue,
        max_followers=max_followers,
        limit=limit
    )

    # 获取对应的startup信息
    result_data = []
    for p in products:
        startup_result = await db.execute(
            select(Startup).where(Startup.id == p.startup_id)
        )
        startup = startup_result.scalar_one_or_none()
        if startup:
            result_data.append({
                "startup": startup.to_dict(),
                "analysis": p.to_dict()
            })

    return {
        "data": result_data,
        "total": len(result_data),
    }


@router.get("/filter/small-beautiful")
async def get_small_beautiful(
    max_description_words: int = Query(50, ge=10, le=200),
    min_revenue: float = Query(1000, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """筛选小而美产品"""
    selector = ProductSelector(db)
    products = await selector.find_small_beautiful(
        max_description_words=max_description_words,
        min_revenue=min_revenue,
        limit=limit
    )

    # 获取对应的startup信息
    result_data = []
    for p in products:
        startup_result = await db.execute(
            select(Startup).where(Startup.id == p.startup_id)
        )
        startup = startup_result.scalar_one_or_none()
        if startup:
            result_data.append({
                "startup": startup.to_dict(),
                "analysis": p.to_dict()
            })

    return {
        "data": result_data,
        "total": len(result_data),
    }


@router.get("/comprehensive/top")
async def get_top_recommendations(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """获取综合推荐指数最高的产品"""
    analyzer = ComprehensiveAnalyzer(db)
    recommendations = await analyzer.get_top_recommendations(limit)

    return {
        "data": recommendations,
        "total": len(recommendations),
    }


@router.get("/comprehensive/{slug}")
async def get_comprehensive_analysis(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    """获取产品综合分析报告"""
    # 获取Startup
    result = await db.execute(
        select(Startup).where(Startup.slug == slug)
    )
    startup = result.scalar_one_or_none()

    if not startup:
        raise HTTPException(status_code=404, detail="产品未找到")

    # 检查是否已有综合分析
    analysis_result = await db.execute(
        select(ComprehensiveAnalysis)
        .where(ComprehensiveAnalysis.startup_id == startup.id)
    )
    analysis = analysis_result.scalar_one_or_none()

    if not analysis:
        # 生成综合分析
        analyzer = ComprehensiveAnalyzer(db)
        analysis = await analyzer.analyze_startup(startup.id)

    if not analysis:
        raise HTTPException(status_code=500, detail="分析生成失败")

    return {
        "startup": startup.to_dict(),
        "analysis": analysis.to_dict(),
    }


@router.get("/{slug}")
async def get_product_analysis(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    """获取单个产品的选品分析"""
    # 获取Startup
    result = await db.execute(
        select(Startup).where(Startup.slug == slug)
    )
    startup = result.scalar_one_or_none()

    if not startup:
        raise HTTPException(status_code=404, detail="产品未找到")

    # 检查是否已有分析
    analysis_result = await db.execute(
        select(ProductSelectionAnalysis)
        .where(ProductSelectionAnalysis.startup_id == startup.id)
    )
    existing_analysis = analysis_result.scalar_one_or_none()

    if existing_analysis:
        return {
            "startup": startup.to_dict(),
            "analysis": existing_analysis.to_dict(),
        }

    # 生成新分析
    selector = ProductSelector(db)
    score = await selector.analyze_product(startup)

    # 保存分析
    analysis = await selector.save_analysis(score)

    return {
        "startup": startup.to_dict(),
        "analysis": analysis.to_dict(),
    }


@router.post("/analyze/{slug}")
async def analyze_product(
    slug: str,
    force: bool = Query(False, description="强制重新分析"),
    db: AsyncSession = Depends(get_db),
):
    """触发产品选品分析"""
    # 获取Startup
    result = await db.execute(
        select(Startup).where(Startup.slug == slug)
    )
    startup = result.scalar_one_or_none()

    if not startup:
        raise HTTPException(status_code=404, detail="产品未找到")

    selector = ProductSelector(db)
    score = await selector.analyze_product(startup)
    analysis = await selector.save_analysis(score)

    return {
        "message": "分析完成",
        "startup": startup.to_dict(),
        "analysis": analysis.to_dict(),
    }


@router.post("/comprehensive/analyze/{slug}")
async def analyze_comprehensive(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    """触发产品综合分析"""
    # 获取Startup
    result = await db.execute(
        select(Startup).where(Startup.slug == slug)
    )
    startup = result.scalar_one_or_none()

    if not startup:
        raise HTTPException(status_code=404, detail="产品未找到")

    analyzer = ComprehensiveAnalyzer(db)
    analysis = await analyzer.analyze_startup(startup.id)

    if not analysis:
        raise HTTPException(status_code=500, detail="综合分析生成失败")

    return {
        "message": "综合分析完成",
        "startup": startup.to_dict(),
        "analysis": analysis.to_dict(),
    }
