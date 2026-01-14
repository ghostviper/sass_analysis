"""
Startups API Routes
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select, func, desc, asc, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from database.db import get_db
from database.models import Startup, Founder, ProductSelectionAnalysis

router = APIRouter()


@router.get("/startups")
async def get_startups(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    country_code: Optional[str] = None,
    sort_by: str = Query("revenue_30d", regex="^(revenue_30d|asking_price|multiple|growth_rate|name|scraped_at|individual_dev_suitability)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    search: Optional[str] = None,
    min_revenue: Optional[float] = None,
    max_revenue: Optional[float] = None,
    # 新增多维度筛选参数
    revenue_tier: Optional[str] = Query(None, description="收入层级，多选用逗号分隔: micro,small,medium,large"),
    tech_complexity_level: Optional[str] = Query(None, description="技术复杂度: low,medium,high"),
    ai_dependency_level: Optional[str] = Query(None, description="AI依赖: none,light,heavy"),
    target_customer: Optional[str] = Query(None, description="目标客户: b2c,b2b_smb,b2b_enterprise,b2d"),
    pricing_model: Optional[str] = Query(None, description="定价模式: subscription,one_time,usage,freemium"),
    feature_complexity: Optional[str] = Query(None, description="功能复杂度: simple,moderate,complex"),
    growth_driver: Optional[str] = Query(None, description="增长驱动: product_driven,ip_driven,content_driven,community_driven"),
    product_stage: Optional[str] = Query(None, description="产品阶段: early,growth,mature"),
    startup_cost_level: Optional[str] = Query(None, description="启动成本: low,medium,high"),
    market_scope: Optional[str] = Query(None, description="市场类型: horizontal,vertical"),
    has_compliance_requirement: Optional[bool] = Query(None, description="是否有合规要求"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get paginated list of startups with filtering and sorting
    支持多维度筛选，同一参数内多值用逗号分隔（OR关系），不同参数间为AND关系
    """
    # 判断是否需要join分析表
    need_analysis_join = any([
        revenue_tier, tech_complexity_level, ai_dependency_level,
        target_customer, pricing_model, feature_complexity,
        growth_driver, product_stage, startup_cost_level,
        market_scope, has_compliance_requirement is not None,
        sort_by == "individual_dev_suitability"
    ])

    # Base query
    if need_analysis_join:
        query = select(Startup, ProductSelectionAnalysis).outerjoin(
            ProductSelectionAnalysis,
            Startup.id == ProductSelectionAnalysis.startup_id
        )
        count_query = select(func.count(Startup.id)).outerjoin(
            ProductSelectionAnalysis,
            Startup.id == ProductSelectionAnalysis.startup_id
        )
    else:
        query = select(Startup)
        count_query = select(func.count(Startup.id))

    # 收集所有筛选条件
    conditions = []

    # 原有筛选条件
    if category:
        conditions.append(Startup.category == category)

    if country_code:
        conditions.append(Startup.country_code == country_code)

    if search:
        search_pattern = f"%{search}%"
        conditions.append(
            or_(
                Startup.name.ilike(search_pattern),
                Startup.description.ilike(search_pattern)
            )
        )

    if min_revenue is not None:
        conditions.append(Startup.revenue_30d >= min_revenue)

    if max_revenue is not None:
        conditions.append(Startup.revenue_30d <= max_revenue)

    # 新增多维度筛选条件
    if revenue_tier:
        values = [v.strip() for v in revenue_tier.split(",")]
        conditions.append(ProductSelectionAnalysis.revenue_tier.in_(values))

    if tech_complexity_level:
        values = [v.strip() for v in tech_complexity_level.split(",")]
        conditions.append(ProductSelectionAnalysis.tech_complexity_level.in_(values))

    if ai_dependency_level:
        values = [v.strip() for v in ai_dependency_level.split(",")]
        conditions.append(ProductSelectionAnalysis.ai_dependency_level.in_(values))

    if target_customer:
        values = [v.strip() for v in target_customer.split(",")]
        conditions.append(ProductSelectionAnalysis.target_customer.in_(values))

    if pricing_model:
        values = [v.strip() for v in pricing_model.split(",")]
        conditions.append(ProductSelectionAnalysis.pricing_model.in_(values))

    if feature_complexity:
        values = [v.strip() for v in feature_complexity.split(",")]
        conditions.append(ProductSelectionAnalysis.feature_complexity.in_(values))

    if growth_driver:
        values = [v.strip() for v in growth_driver.split(",")]
        conditions.append(ProductSelectionAnalysis.growth_driver.in_(values))

    if product_stage:
        values = [v.strip() for v in product_stage.split(",")]
        conditions.append(ProductSelectionAnalysis.product_stage.in_(values))

    if startup_cost_level:
        values = [v.strip() for v in startup_cost_level.split(",")]
        conditions.append(ProductSelectionAnalysis.startup_cost_level.in_(values))

    if market_scope:
        values = [v.strip() for v in market_scope.split(",")]
        conditions.append(ProductSelectionAnalysis.market_scope.in_(values))

    if has_compliance_requirement is not None:
        conditions.append(
            ProductSelectionAnalysis.has_compliance_requirement == has_compliance_requirement
        )

    # 应用所有条件
    if conditions:
        query = query.where(and_(*conditions))
        count_query = count_query.where(and_(*conditions))

    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply sorting
    # 优先显示有收入的产品，NULL 和 0 收入的排在后面
    if sort_by == "individual_dev_suitability":
        sort_column = ProductSelectionAnalysis.individual_dev_suitability
        # 对于适合度排序，NULL 值排在最后
        if sort_order == "desc":
            query = query.order_by(
                sort_column.is_(None).asc(),  # 非 NULL 优先
                desc(sort_column)
            )
        else:
            query = query.order_by(
                sort_column.is_(None).asc(),
                asc(sort_column)
            )
    elif sort_by == "revenue_30d":
        # 收入排序：有收入的优先，NULL 和 0 排在最后
        if sort_order == "desc":
            query = query.order_by(
                # 先按是否有有效收入排序（有收入的排前面）
                (Startup.revenue_30d.is_(None) | (Startup.revenue_30d == 0)).asc(),
                desc(Startup.revenue_30d)
            )
        else:
            query = query.order_by(
                (Startup.revenue_30d.is_(None) | (Startup.revenue_30d == 0)).asc(),
                asc(Startup.revenue_30d)
            )
    else:
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

    # 处理结果
    if need_analysis_join:
        rows = result.all()
        data = []
        for row in rows:
            startup = row[0]
            analysis = row[1]
            item = startup.to_dict()
            if analysis:
                item["analysis"] = analysis.to_dict()
                item["tags"] = analysis.to_tags_dict()
            else:
                item["analysis"] = None
                item["tags"] = None
            data.append(item)
    else:
        startups = result.scalars().all()
        data = [s.to_dict() for s in startups]

    return {
        "data": data,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit,
        }
    }


@router.get("/startups/filter-options")
async def get_filter_options(
    db: AsyncSession = Depends(get_db),
):
    """获取所有可用的筛选选项及其数量"""

    # 定义筛选维度配置
    filter_dimensions = {
        "revenue_tier": {
            "label": "收入规模",
            "label_en": "Revenue Tier",
            "options": [
                {"value": "micro", "label": "微型 (<$500)", "label_en": "Micro (<$500)"},
                {"value": "small", "label": "小型 ($500-2K)", "label_en": "Small ($500-2K)"},
                {"value": "medium", "label": "中型 ($2K-10K)", "label_en": "Medium ($2K-10K)"},
                {"value": "large", "label": "大型 (>$10K)", "label_en": "Large (>$10K)"},
            ]
        },
        "tech_complexity_level": {
            "label": "技术门槛",
            "label_en": "Tech Complexity",
            "options": [
                {"value": "low", "label": "低门槛", "label_en": "Low"},
                {"value": "medium", "label": "中等", "label_en": "Medium"},
                {"value": "high", "label": "高门槛", "label_en": "High"},
            ]
        },
        "ai_dependency_level": {
            "label": "AI依赖",
            "label_en": "AI Dependency",
            "options": [
                {"value": "none", "label": "不依赖AI", "label_en": "None"},
                {"value": "light", "label": "轻度使用", "label_en": "Light"},
                {"value": "heavy", "label": "核心依赖", "label_en": "Heavy"},
            ]
        },
        "target_customer": {
            "label": "目标客户",
            "label_en": "Target Customer",
            "options": [
                {"value": "b2c", "label": "个人消费者", "label_en": "B2C"},
                {"value": "b2b_smb", "label": "中小企业", "label_en": "B2B SMB"},
                {"value": "b2b_enterprise", "label": "大企业", "label_en": "B2B Enterprise"},
                {"value": "b2d", "label": "开发者", "label_en": "B2D"},
            ]
        },
        "pricing_model": {
            "label": "定价模式",
            "label_en": "Pricing Model",
            "options": [
                {"value": "subscription", "label": "订阅制", "label_en": "Subscription"},
                {"value": "one_time", "label": "一次性", "label_en": "One-time"},
                {"value": "usage", "label": "按量付费", "label_en": "Usage-based"},
                {"value": "freemium", "label": "免费增值", "label_en": "Freemium"},
            ]
        },
        "feature_complexity": {
            "label": "功能复杂度",
            "label_en": "Feature Complexity",
            "options": [
                {"value": "simple", "label": "简单", "label_en": "Simple"},
                {"value": "moderate", "label": "中等", "label_en": "Moderate"},
                {"value": "complex", "label": "复杂", "label_en": "Complex"},
            ]
        },
        "growth_driver": {
            "label": "增长驱动",
            "label_en": "Growth Driver",
            "options": [
                {"value": "product_driven", "label": "产品驱动", "label_en": "Product Driven"},
                {"value": "ip_driven", "label": "IP驱动", "label_en": "IP Driven"},
                {"value": "content_driven", "label": "内容驱动", "label_en": "Content Driven"},
                {"value": "community_driven", "label": "社区驱动", "label_en": "Community Driven"},
            ]
        },
        "product_stage": {
            "label": "产品阶段",
            "label_en": "Product Stage",
            "options": [
                {"value": "early", "label": "早期 (<6月)", "label_en": "Early (<6mo)"},
                {"value": "growth", "label": "成长期 (6-24月)", "label_en": "Growth (6-24mo)"},
                {"value": "mature", "label": "成熟期 (>24月)", "label_en": "Mature (>24mo)"},
            ]
        },
        "startup_cost_level": {
            "label": "启动成本",
            "label_en": "Startup Cost",
            "options": [
                {"value": "low", "label": "低 (<$100)", "label_en": "Low (<$100)"},
                {"value": "medium", "label": "中 ($100-1K)", "label_en": "Medium ($100-1K)"},
                {"value": "high", "label": "高 (>$1K)", "label_en": "High (>$1K)"},
            ]
        },
        "market_scope": {
            "label": "市场类型",
            "label_en": "Market Scope",
            "options": [
                {"value": "horizontal", "label": "通用市场", "label_en": "Horizontal"},
                {"value": "vertical", "label": "垂直市场", "label_en": "Vertical"},
            ]
        },
    }

    return {
        "dimensions": filter_dimensions
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
