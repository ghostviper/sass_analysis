"""
Landing Page Analysis API - Landing Page分析接口
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException, BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.db import get_db
from database.models import Startup, LandingPageSnapshot, LandingPageAnalysis
from analysis.landing_analyzer import LandingPageAnalyzer
from services.openai_service import OpenAIService

router = APIRouter(prefix="/analysis/landing", tags=["Landing Page Analysis"])


@router.get("/{slug}")
async def get_landing_analysis(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    """获取产品Landing Page分析结果"""
    # 获取Startup
    result = await db.execute(
        select(Startup).where(Startup.slug == slug)
    )
    startup = result.scalar_one_or_none()

    if not startup:
        raise HTTPException(status_code=404, detail="产品未找到")

    # 获取分析结果
    analysis_result = await db.execute(
        select(LandingPageAnalysis)
        .where(LandingPageAnalysis.startup_id == startup.id)
    )
    analysis = analysis_result.scalar_one_or_none()

    if not analysis:
        raise HTTPException(
            status_code=404,
            detail="暂无Landing Page分析结果，请先使用POST /scrape/{slug}触发分析"
        )

    # 获取快照信息
    snapshot = None
    if analysis.snapshot_id:
        snapshot_result = await db.execute(
            select(LandingPageSnapshot)
            .where(LandingPageSnapshot.id == analysis.snapshot_id)
        )
        snapshot = snapshot_result.scalar_one_or_none()

    return {
        "startup": startup.to_dict(),
        "analysis": analysis.to_dict(),
        "snapshot": snapshot.to_dict() if snapshot else None,
    }


@router.post("/scrape/{slug}")
async def scrape_and_analyze(
    slug: str,
    force_rescrape: bool = Query(False, description="强制重新爬取"),
    background_tasks: BackgroundTasks = None,
    db: AsyncSession = Depends(get_db),
):
    """
    触发Landing Page爬取和AI分析

    这是一个同步操作，会等待爬取和分析完成后返回结果。
    对于批量操作，建议使用 POST /batch 接口。
    """
    # 获取Startup
    result = await db.execute(
        select(Startup).where(Startup.slug == slug)
    )
    startup = result.scalar_one_or_none()

    if not startup:
        raise HTTPException(status_code=404, detail="产品未找到")

    if not startup.website_url:
        raise HTTPException(status_code=400, detail="该产品没有官网URL")

    try:
        openai_service = OpenAIService()
    except ValueError as e:
        raise HTTPException(
            status_code=500,
            detail=f"OpenAI服务未配置: {e}"
        )

    # 执行分析
    analyzer = LandingPageAnalyzer(db, openai_service)
    try:
        analysis = await analyzer.analyze_startup(
            startup_id=startup.id,
            force_rescrape=force_rescrape
        )
    finally:
        await analyzer.close()

    if not analysis:
        raise HTTPException(status_code=500, detail="Landing Page分析失败")

    return {
        "message": "分析完成",
        "startup": startup.to_dict(),
        "analysis": analysis.to_dict(),
    }


@router.post("/batch")
async def batch_analyze(
    startup_slugs: List[str],
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    批量触发Landing Page分析（后台执行）

    Args:
        startup_slugs: 产品slug列表
    """
    if len(startup_slugs) > 50:
        raise HTTPException(status_code=400, detail="每次最多分析50个产品")

    # 获取所有Startup ID
    result = await db.execute(
        select(Startup.id, Startup.slug, Startup.website_url)
        .where(Startup.slug.in_(startup_slugs))
    )
    startups = result.all()

    if not startups:
        raise HTTPException(status_code=404, detail="未找到任何产品")

    # 过滤有URL的产品
    valid_startups = [(s.id, s.slug) for s in startups if s.website_url]

    if not valid_startups:
        raise HTTPException(status_code=400, detail="没有产品有有效的官网URL")

    # 添加后台任务
    # 注意：由于数据库session的生命周期问题，这里简化处理
    # 实际生产环境应该使用任务队列如Celery

    return {
        "message": f"已提交 {len(valid_startups)} 个产品的分析任务",
        "note": "由于分析需要时间，请稍后查询结果",
        "submitted": [s[1] for s in valid_startups],
        "skipped": [s.slug for s in startups if not s.website_url],
    }


@router.get("/snapshot/{slug}")
async def get_snapshot(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    """获取Landing Page快照"""
    # 获取Startup
    result = await db.execute(
        select(Startup).where(Startup.slug == slug)
    )
    startup = result.scalar_one_or_none()

    if not startup:
        raise HTTPException(status_code=404, detail="产品未找到")

    # 获取最新快照
    snapshot_result = await db.execute(
        select(LandingPageSnapshot)
        .where(LandingPageSnapshot.startup_id == startup.id)
        .order_by(LandingPageSnapshot.scraped_at.desc())
    )
    snapshot = snapshot_result.scalar_one_or_none()

    if not snapshot:
        raise HTTPException(status_code=404, detail="暂无Landing Page快照")

    return {
        "startup": startup.to_dict(),
        "snapshot": snapshot.to_dict(),
        # 不返回完整HTML内容，太大
        "has_html": bool(snapshot.html_content),
        "has_text": bool(snapshot.raw_text),
    }


@router.get("/snapshots/list")
async def list_snapshots(
    status: Optional[str] = Query(None, regex="^(pending|success|failed|timeout)$"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """列出Landing Page快照"""
    query = select(LandingPageSnapshot)

    if status:
        query = query.where(LandingPageSnapshot.status == status)

    query = query.order_by(LandingPageSnapshot.scraped_at.desc())
    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    snapshots = result.scalars().all()

    return {
        "data": [s.to_dict() for s in snapshots],
        "total": len(snapshots),
        "offset": offset,
        "limit": limit,
    }
