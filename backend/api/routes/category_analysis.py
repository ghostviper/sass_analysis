"""
Category Analysis API - 赛道/领域分析接口
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database.db import get_db
from analysis.category_analyzer import CategoryAnalyzer

router = APIRouter(prefix="/analysis/category", tags=["Category Analysis"])


@router.get("/")
async def get_all_category_analysis(
    db: AsyncSession = Depends(get_db),
):
    """获取所有赛道分析概览"""
    analyzer = CategoryAnalyzer(db)
    analyses = await analyzer.analyze_all_categories()

    return {
        "data": [a.to_dict() for a in analyses],
        "total": len(analyses),
    }


@router.get("/blue-ocean")
async def get_blue_ocean_categories(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """获取蓝海赛道列表"""
    analyzer = CategoryAnalyzer(db)
    blue_oceans = await analyzer.get_blue_ocean_categories(limit)

    return {
        "data": [a.to_dict() for a in blue_oceans],
        "total": len(blue_oceans),
    }


@router.get("/compare")
async def compare_categories(
    categories: str = Query(..., description="逗号分隔的赛道名称"),
    db: AsyncSession = Depends(get_db),
):
    """对比多个赛道"""
    category_list = [c.strip() for c in categories.split(",") if c.strip()]

    if not category_list:
        raise HTTPException(status_code=400, detail="请提供至少一个赛道名称")

    if len(category_list) > 10:
        raise HTTPException(status_code=400, detail="最多支持对比10个赛道")

    analyzer = CategoryAnalyzer(db)
    analyses = await analyzer.compare_categories(category_list)

    return {
        "comparison": [a.to_dict() for a in analyses],
    }


@router.get("/{category}")
async def get_category_analysis(
    category: str,
    db: AsyncSession = Depends(get_db),
):
    """获取单个赛道详细分析"""
    analyzer = CategoryAnalyzer(db)
    analysis = await analyzer.analyze_category(category)

    if analysis.total_projects == 0:
        raise HTTPException(
            status_code=404,
            detail=f"赛道 '{category}' 未找到或没有有效数据"
        )

    # 获取模板化产品
    templates = await analyzer.find_template_products(category)

    return {
        "analysis": analysis.to_dict(),
        "template_products": templates,
    }


@router.post("/refresh")
async def refresh_category_analysis(
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """刷新赛道分析缓存"""
    analyzer = CategoryAnalyzer(db)

    if category:
        # 刷新单个赛道
        analysis = await analyzer.analyze_category(category)
        saved = await analyzer.save_analysis(analysis)
        return {
            "message": f"赛道 '{category}' 分析已刷新",
            "analysis": saved.to_dict(),
        }
    else:
        # 刷新所有赛道
        all_analyses = await analyzer.analyze_all_categories()
        count = 0
        for analysis in all_analyses:
            await analyzer.save_analysis(analysis)
            count += 1

        return {
            "message": f"已刷新 {count} 个赛道的分析",
            "total": count,
        }
