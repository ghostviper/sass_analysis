"""
Product Analysis API - 选品分析接口
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.db import get_db
from database.models import Startup, Founder, ProductSelectionAnalysis, ComprehensiveAnalysis
from analysis.product_selector import ProductSelector
from analysis.comprehensive import ComprehensiveAnalyzer
from analysis.domain_knowledge import DomainKnowledge
from analysis.leaderboards import LeaderboardService, LEADERBOARDS

router = APIRouter(prefix="/analysis/product", tags=["Product Analysis"])


def _merge_founder_info(startup: Startup, founder: Optional[Founder]) -> dict:
    """Prefer founder table data for display fields when available."""
    item = startup.to_dict()
    if not founder:
        return item
    if founder.username:
        item["founder_username"] = founder.username
    if founder.name:
        item["founder_name"] = founder.name
    if founder.followers is not None:
        item["founder_followers"] = founder.followers
    if founder.social_platform:
        item["founder_social_platform"] = founder.social_platform
    return item


async def _get_startup_with_founder_by_id(db: AsyncSession, startup_id: int):
    result = await db.execute(
        select(Startup, Founder)
        .outerjoin(Founder, Startup.founder_id == Founder.id)
        .where(Startup.id == startup_id)
    )
    return result.first()


async def _get_startup_with_founder_by_slug(db: AsyncSession, slug: str):
    result = await db.execute(
        select(Startup, Founder)
        .outerjoin(Founder, Startup.founder_id == Founder.id)
        .where(Startup.slug == slug)
    )
    return result.first()


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
        row = await _get_startup_with_founder_by_id(db, o.startup_id)
        if row:
            startup, founder = row
            result_data.append({
                "startup": _merge_founder_info(startup, founder),
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
        row = await _get_startup_with_founder_by_id(db, p.startup_id)
        if row:
            startup, founder = row
            result_data.append({
                "startup": _merge_founder_info(startup, founder),
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
        row = await _get_startup_with_founder_by_id(db, p.startup_id)
        if row:
            startup, founder = row
            result_data.append({
                "startup": _merge_founder_info(startup, founder),
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
    row = await _get_startup_with_founder_by_slug(db, slug)

    if not row:
        raise HTTPException(status_code=404, detail="产品未找到")
    startup, founder = row

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
        "startup": _merge_founder_info(startup, founder),
        "analysis": analysis.to_dict(),
    }


@router.get("/{slug}")
async def get_product_analysis(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    """获取单个产品的选品分析"""
    # 获取Startup
    row = await _get_startup_with_founder_by_slug(db, slug)

    if not row:
        raise HTTPException(status_code=404, detail="产品未找到")
    startup, founder = row

    # 检查是否已有分析
    analysis_result = await db.execute(
        select(ProductSelectionAnalysis)
        .where(ProductSelectionAnalysis.startup_id == startup.id)
    )
    existing_analysis = analysis_result.scalar_one_or_none()

    if existing_analysis:
        # 获取标签和洞察
        tags = existing_analysis.to_tags_dict()
        domain_insights = DomainKnowledge.get_insights(tags)
        summary_points = DomainKnowledge.get_summary_points(tags)
        risk_assessment = DomainKnowledge.get_risk_assessment(tags)

        return {
            "startup": _merge_founder_info(startup, founder),
            "analysis": existing_analysis.to_dict(),
            # 新增：结构化输出
            "data_layer": {
                "tags": tags,
                "scores": existing_analysis.to_scores_dict(),
            },
            "display_layer": {
                "summary_points": summary_points,
                "domain_insights": domain_insights,
                "risk_assessment": risk_assessment,
            }
        }

    # 生成新分析
    selector = ProductSelector(db)
    score = await selector.analyze_product(startup)

    # 保存分析
    analysis = await selector.save_analysis(score)

    # 获取标签和洞察
    tags = analysis.to_tags_dict()
    domain_insights = DomainKnowledge.get_insights(tags)
    summary_points = DomainKnowledge.get_summary_points(tags)
    risk_assessment = DomainKnowledge.get_risk_assessment(tags)

    return {
        "startup": _merge_founder_info(startup, founder),
        "analysis": analysis.to_dict(),
        # 新增：结构化输出
        "data_layer": {
            "tags": tags,
            "scores": analysis.to_scores_dict(),
        },
        "display_layer": {
            "summary_points": summary_points,
            "domain_insights": domain_insights,
            "risk_assessment": risk_assessment,
        }
    }


@router.post("/analyze/{slug}")
async def analyze_product(
    slug: str,
    force: bool = Query(False, description="强制重新分析"),
    db: AsyncSession = Depends(get_db),
):
    """触发产品选品分析"""
    # 获取Startup
    row = await _get_startup_with_founder_by_slug(db, slug)

    if not row:
        raise HTTPException(status_code=404, detail="产品未找到")
    startup, founder = row

    selector = ProductSelector(db)
    score = await selector.analyze_product(startup)
    analysis = await selector.save_analysis(score)

    return {
        "message": "分析完成",
        "startup": _merge_founder_info(startup, founder),
        "analysis": analysis.to_dict(),
    }


@router.post("/comprehensive/analyze/{slug}")
async def analyze_comprehensive(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    """触发产品综合分析"""
    # 获取Startup
    row = await _get_startup_with_founder_by_slug(db, slug)

    if not row:
        raise HTTPException(status_code=404, detail="产品未找到")
    startup, founder = row

    analyzer = ComprehensiveAnalyzer(db)
    analysis = await analyzer.analyze_startup(startup.id)

    if not analysis:
        raise HTTPException(status_code=500, detail="综合分析生成失败")

    return {
        "message": "综合分析完成",
        "startup": _merge_founder_info(startup, founder),
        "analysis": analysis.to_dict(),
    }


# ========== 榜单相关接口 ==========

@router.get("/leaderboards/list")
async def get_leaderboards():
    """获取所有榜单列表"""
    return {
        "data": LeaderboardService.get_all_leaderboards(),
        "total": len(LEADERBOARDS)
    }


@router.get("/leaderboards/stats")
async def get_leaderboards_stats(
    db: AsyncSession = Depends(get_db),
):
    """获取所有榜单的统计信息"""
    service = LeaderboardService(db)
    stats = await service.get_leaderboard_stats()
    return {
        "data": stats
    }


@router.get("/leaderboards/{leaderboard_id}")
async def get_leaderboard_products(
    leaderboard_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """获取指定榜单的产品列表"""
    service = LeaderboardService(db)
    result = await service.get_leaderboard_products(
        leaderboard_id=leaderboard_id,
        page=page,
        page_size=page_size
    )

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return result


# ========== 标签相关接口 ==========

@router.get("/{slug}/tags")
async def get_product_tags(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    """获取产品标签数据（AI友好格式）"""
    # 获取Startup
    result = await db.execute(
        select(Startup).where(Startup.slug == slug)
    )
    startup = result.scalar_one_or_none()

    if not startup:
        raise HTTPException(status_code=404, detail="产品未找到")

    # 获取分析
    analysis_result = await db.execute(
        select(ProductSelectionAnalysis)
        .where(ProductSelectionAnalysis.startup_id == startup.id)
    )
    analysis = analysis_result.scalar_one_or_none()

    if not analysis:
        # 生成新分析
        selector = ProductSelector(db)
        score = await selector.analyze_product(startup)
        analysis = await selector.save_analysis(score)

    return {
        "slug": slug,
        "tags": analysis.to_tags_dict(),
        "scores": analysis.to_scores_dict(),
    }


@router.get("/{slug}/insights")
async def get_product_insights(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    """获取产品的确定性洞察"""
    # 获取Startup
    result = await db.execute(
        select(Startup).where(Startup.slug == slug)
    )
    startup = result.scalar_one_or_none()

    if not startup:
        raise HTTPException(status_code=404, detail="产品未找到")

    # 获取分析
    analysis_result = await db.execute(
        select(ProductSelectionAnalysis)
        .where(ProductSelectionAnalysis.startup_id == startup.id)
    )
    analysis = analysis_result.scalar_one_or_none()

    if not analysis:
        # 生成新分析
        selector = ProductSelector(db)
        score = await selector.analyze_product(startup)
        analysis = await selector.save_analysis(score)

    tags = analysis.to_tags_dict()

    return {
        "slug": slug,
        "insights": DomainKnowledge.get_insights(tags),
        "summary_points": DomainKnowledge.get_summary_points(tags),
        "risk_assessment": DomainKnowledge.get_risk_assessment(tags),
    }
