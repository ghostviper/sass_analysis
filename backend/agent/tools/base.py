"""
基础工具 - 产品查询、赛道分析、趋势报告
"""

import json
from typing import Optional, List, Dict, Any
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from database.db import AsyncSessionLocal
from database.models import (
    Startup,
    Founder,
    ProductSelectionAnalysis,
    LandingPageAnalysis,
    ComprehensiveAnalysis,
    CategoryAnalysis,
)
from .decorator import tool


# ============================================================================
# 底层查询函数
# ============================================================================

def _build_founder_social_url(username: str, platform: str) -> Optional[str]:
    """根据社交平台构建创始人的社交媒体链接"""
    if not username:
        return None
    
    platform_lower = (platform or "").lower()
    
    # X/Twitter
    if platform_lower in ['x', 'x (twitter)', 'twitter', '𝕏']:
        return f"https://x.com/{username}"
    # LinkedIn
    elif 'linkedin' in platform_lower:
        return f"https://linkedin.com/in/{username}"
    # 默认返回 X（大多数创始人使用 X）
    else:
        return f"https://x.com/{username}"


async def _build_product_profile(db: AsyncSession, startup: Startup) -> Dict[str, Any]:
    """构建完整的产品画像"""
    founder = None
    if startup.founder_id:
        founder_result = await db.execute(
            select(Founder).where(Founder.id == startup.founder_id)
        )
        founder = founder_result.scalar_one_or_none()

    founder_username = (founder.username if founder and founder.username else startup.founder_username)
    founder_name = (founder.name if founder and founder.name else startup.founder_name)
    founder_followers = (
        founder.followers if founder and founder.followers is not None else startup.founder_followers
    )
    founder_platform = (
        founder.social_platform if founder and founder.social_platform else startup.founder_social_platform
    )

    # 构建创始人社交媒体链接
    founder_social_url = _build_founder_social_url(
        founder_username,
        founder_platform,
    )
    
    # 构建系统内部产品详情页链接
    internal_product_url = f"/products/{startup.slug}" if startup.slug else None
    
    profile = {
        "id": startup.id,
        "name": startup.name,
        "slug": startup.slug,
        "description": startup.description,
        "category": startup.category,
        "website_url": startup.website_url,
        "internal_url": internal_product_url,  # 系统内部产品详情页链接
        "revenue_30d": startup.revenue_30d,
        "mrr": startup.mrr,
        "growth_rate": startup.growth_rate,
        "asking_price": startup.asking_price,
        "multiple": startup.multiple,
        "founder_name": founder_name,
        "founder_username": founder_username,
        "founder_followers": founder_followers,
        "founder_social_platform": founder_platform,
        "founder_social_url": founder_social_url,  # 创始人社交媒体链接
        "customers_count": startup.customers_count,
        "is_verified": startup.is_verified,
        "founded_date": startup.founded_date,
    }

    # 选品分析
    selection_result = await db.execute(
        select(ProductSelectionAnalysis).where(ProductSelectionAnalysis.startup_id == startup.id)
    )
    selection = selection_result.scalar_one_or_none()
    if selection:
        profile["analysis"] = {
            "tech_complexity": selection.tech_complexity_level,
            "ai_dependency": selection.ai_dependency_level,
            "target_customer": selection.target_customer,
            "pricing_model": selection.pricing_model,
            "product_stage": selection.product_stage,
            "feature_complexity": selection.feature_complexity,
            "startup_cost": selection.startup_cost_level,
            "growth_driver": selection.growth_driver,
            "suitability_score": selection.individual_dev_suitability,
            "is_product_driven": selection.is_product_driven,
            "is_small_and_beautiful": selection.is_small_and_beautiful,
            "uses_llm_api": selection.uses_llm_api,
            "requires_realtime": selection.requires_realtime,
            "requires_compliance": selection.requires_compliance,
        }

    # 落地页分析
    landing_result = await db.execute(
        select(LandingPageAnalysis).where(LandingPageAnalysis.startup_id == startup.id)
    )
    landing = landing_result.scalar_one_or_none()
    if landing:
        profile["landing"] = {
            "target_audience": landing.target_audience,
            "use_cases": landing.use_cases,
            "core_features": landing.core_features,
            "feature_count": landing.feature_count,
            "value_propositions": landing.value_propositions,
            "pain_points": landing.pain_points,
            "pain_point_sharpness": landing.pain_point_sharpness,
            "pricing_model": landing.pricing_model,
            "pricing_tiers": landing.pricing_tiers,
            "has_free_tier": landing.has_free_tier,
            "has_trial": landing.has_trial,
            "cta_texts": landing.cta_texts,
            "conversion_friendliness": landing.conversion_friendliness_score,
            "headline": landing.headline_text,
            "tagline": landing.tagline_text,
            "positioning_clarity": landing.positioning_clarity_score,
            "replication_difficulty": landing.replication_difficulty_score,
        }

    # 综合评分
    comprehensive_result = await db.execute(
        select(ComprehensiveAnalysis).where(ComprehensiveAnalysis.startup_id == startup.id)
    )
    comprehensive = comprehensive_result.scalar_one_or_none()
    if comprehensive:
        profile["scores"] = {
            "overall_recommendation": comprehensive.overall_recommendation,
            "maturity": comprehensive.maturity_score,
            "positioning_clarity": comprehensive.positioning_clarity,
            "pain_point_sharpness": comprehensive.pain_point_sharpness,
            "pricing_clarity": comprehensive.pricing_clarity,
            "conversion_friendliness": comprehensive.conversion_friendliness,
            "individual_replicability": comprehensive.individual_replicability,
        }

    # 赛道上下文
    if startup.category:
        category_result = await db.execute(
            select(CategoryAnalysis)
            .where(CategoryAnalysis.category == startup.category)
            .order_by(CategoryAnalysis.analysis_date.desc())
            .limit(1)
        )
        category = category_result.scalar_one_or_none()
        if category:
            profile["category_context"] = {
                "market_type": category.market_type,
                "market_type_reason": category.market_type_reason,
                "total_products": category.total_projects,
                "median_revenue": category.median_revenue,
                "gini_coefficient": category.gini_coefficient,
                "top10_share": category.top10_revenue_share,
            }

    return profile


async def _get_startups_by_ids(ids: List[int], include_full_profile: bool = True) -> List[Dict[str, Any]]:
    """通过 ID 列表查询产品"""
    async with AsyncSessionLocal() as db:
        query = select(Startup).where(Startup.id.in_(ids))
        result = await db.execute(query)
        startups = result.scalars().all()

        if include_full_profile:
            return [await _build_product_profile(db, s) for s in startups]
        return [s.to_dict() for s in startups]


async def _search_startups(keyword: str, limit: int = 20, include_full_profile: bool = True) -> List[Dict[str, Any]]:
    """通过关键词模糊搜索产品"""
    async with AsyncSessionLocal() as db:
        pattern = f"%{keyword}%"
        query = select(Startup).where(
            (Startup.name.ilike(pattern)) |
            (Startup.description.ilike(pattern)) |
            (Startup.slug.ilike(pattern))
        ).order_by(desc(Startup.revenue_30d)).limit(limit)
        result = await db.execute(query)
        startups = result.scalars().all()

        if include_full_profile:
            return [await _build_product_profile(db, s) for s in startups]
        return [s.to_dict() for s in startups]


async def _browse_startups(
    category: Optional[str] = None,
    min_revenue: Optional[float] = None,
    max_revenue: Optional[float] = None,
    limit: int = 20,
    include_full_profile: bool = True
) -> List[Dict[str, Any]]:
    """浏览筛选产品"""
    async with AsyncSessionLocal() as db:
        query = select(Startup)
        if category:
            query = query.where(Startup.category == category)
        if min_revenue is not None and min_revenue > 0:
            query = query.where(Startup.revenue_30d >= min_revenue)
        if max_revenue is not None:
            query = query.where(Startup.revenue_30d <= max_revenue)
        query = query.order_by(desc(Startup.revenue_30d)).limit(limit)
        result = await db.execute(query)
        startups = result.scalars().all()

        if include_full_profile:
            return [await _build_product_profile(db, s) for s in startups]
        return [s.to_dict() for s in startups]


# ============================================================================
# 高级查询函数
# ============================================================================

async def query_startups(
    ids: Optional[List[int]] = None,
    slugs: Optional[List[str]] = None,
    category: Optional[str] = None,
    min_revenue: Optional[float] = None,
    max_revenue: Optional[float] = None,
    search: Optional[str] = None,
    limit: int = 20,
) -> List[Dict[str, Any]]:
    """Query startups with optional filters - returns full product profiles with links"""
    async with AsyncSessionLocal() as db:
        query = select(Startup)
        
        if ids:
            if isinstance(ids, str):
                try:
                    ids = json.loads(ids) if ids.strip() not in ('', '[]') else None
                except:
                    ids = None
            if ids and isinstance(ids, list) and len(ids) > 0:
                query = query.where(Startup.id.in_(ids))
                query = query.limit(limit)
                result = await db.execute(query)
                startups = result.scalars().all()
                return [await _build_product_profile(db, s) for s in startups]
        
        if slugs:
            if isinstance(slugs, str):
                try:
                    slugs = json.loads(slugs) if slugs.strip() not in ('', '[]') else None
                except:
                    slugs = None
            if slugs and isinstance(slugs, list) and len(slugs) > 0:
                query = query.where(Startup.slug.in_(slugs))
                query = query.limit(limit)
                result = await db.execute(query)
                startups = result.scalars().all()
                return [await _build_product_profile(db, s) for s in startups]
        
        if search:
            pattern = f"%{search}%"
            query = query.where(
                (Startup.name.ilike(pattern)) | 
                (Startup.description.ilike(pattern)) |
                (Startup.slug.ilike(pattern))
            )
        else:
            if category:
                query = query.where(Startup.category == category)
            if min_revenue is not None and min_revenue > 0:
                query = query.where(Startup.revenue_30d >= min_revenue)
            if max_revenue is not None:
                query = query.where(Startup.revenue_30d <= max_revenue)
        
        query = query.order_by(desc(Startup.revenue_30d)).limit(limit)
        result = await db.execute(query)
        startups = result.scalars().all()
        return [await _build_product_profile(db, s) for s in startups]


async def get_category_analysis(category: Optional[str] = None) -> Dict[str, Any]:
    """Get category analysis"""
    async with AsyncSessionLocal() as db:
        if category:
            analysis_result = await db.execute(
                select(CategoryAnalysis)
                .where(CategoryAnalysis.category == category)
                .order_by(CategoryAnalysis.analysis_date.desc())
                .limit(1)
            )
            analysis = analysis_result.scalar_one_or_none()

            stats_result = await db.execute(
                select(
                    func.count(Startup.id).label("count"),
                    func.sum(Startup.revenue_30d).label("total_revenue"),
                    func.avg(Startup.revenue_30d).label("avg_revenue"),
                    func.avg(Startup.asking_price).label("avg_price"),
                    func.avg(Startup.multiple).label("avg_multiple"),
                    func.avg(Startup.growth_rate).label("avg_growth"),
                    func.max(Startup.revenue_30d).label("max_revenue"),
                    func.min(Startup.revenue_30d).label("min_revenue"),
                )
                .where(Startup.category == category)
            )
            stats = stats_result.first()

            top_result = await db.execute(
                select(Startup)
                .where(Startup.category == category)
                .order_by(desc(Startup.revenue_30d))
                .limit(5)
            )
            top_startups = top_result.scalars().all()

            result = {
                "category": category,
                "stats": {
                    "count": stats.count or 0,
                    "total_revenue": round(stats.total_revenue or 0, 2),
                    "avg_revenue": round(stats.avg_revenue or 0, 2),
                    "avg_price": round(stats.avg_price or 0, 2),
                    "avg_multiple": round(stats.avg_multiple or 0, 2),
                    "avg_growth": round(stats.avg_growth or 0, 2),
                    "max_revenue": round(stats.max_revenue or 0, 2),
                    "min_revenue": round(stats.min_revenue or 0, 2),
                },
                "top_products": [await _build_product_profile(db, s) for s in top_startups],
            }

            if analysis:
                result["market_analysis"] = {
                    "market_type": analysis.market_type,
                    "market_type_reason": analysis.market_type_reason,
                    "median_revenue": analysis.median_revenue,
                    "gini_coefficient": analysis.gini_coefficient,
                    "top10_revenue_share": analysis.top10_revenue_share,
                    "top50_revenue_share": analysis.top50_revenue_share,
                    "revenue_std_dev": analysis.revenue_std_dev,
                    "analysis_date": analysis.analysis_date.isoformat() if analysis.analysis_date else None,
                }

            return result
        else:
            analysis_result = await db.execute(
                select(CategoryAnalysis)
                .order_by(CategoryAnalysis.category, CategoryAnalysis.analysis_date.desc())
                .distinct(CategoryAnalysis.category)
            )
            analyses = {a.category: a for a in analysis_result.scalars().all()}

            stats_result = await db.execute(
                select(
                    Startup.category,
                    func.count(Startup.id).label("count"),
                    func.sum(Startup.revenue_30d).label("total_revenue"),
                    func.avg(Startup.revenue_30d).label("avg_revenue"),
                )
                .where(Startup.category.isnot(None))
                .group_by(Startup.category)
                .order_by(desc("total_revenue"))
            )
            categories = stats_result.all()

            return {
                "categories": [
                    {
                        "name": cat,
                        "count": count,
                        "total_revenue": round(total_rev or 0, 2),
                        "avg_revenue": round(avg_rev or 0, 2),
                        "market_type": analyses.get(cat).market_type if analyses.get(cat) else None,
                        "gini_coefficient": analyses.get(cat).gini_coefficient if analyses.get(cat) else None,
                        "median_revenue": analyses.get(cat).median_revenue if analyses.get(cat) else None,
                    }
                    for cat, count, total_rev, avg_rev in categories
                ]
            }


async def get_trend_report() -> Dict[str, Any]:
    """Generate trend report"""
    async with AsyncSessionLocal() as db:
        overall = await db.execute(
            select(
                func.count(Startup.id).label("total"),
                func.sum(Startup.revenue_30d).label("total_revenue"),
                func.avg(Startup.revenue_30d).label("avg_revenue"),
                func.avg(Startup.multiple).label("avg_multiple"),
            )
        )
        overall_stats = overall.first()
        
        cats = await db.execute(
            select(
                Startup.category,
                func.count(Startup.id).label("count"),
                func.sum(Startup.revenue_30d).label("total_revenue"),
            )
            .where(Startup.category.isnot(None))
            .group_by(Startup.category)
            .order_by(desc("total_revenue"))
            .limit(5)
        )
        top_categories = cats.all()
        
        growing = await db.execute(
            select(Startup)
            .where(Startup.growth_rate.isnot(None))
            .order_by(desc(Startup.growth_rate))
            .limit(5)
        )
        fast_growing = growing.scalars().all()
        
        deals = await db.execute(
            select(Startup)
            .where(Startup.multiple.isnot(None))
            .where(Startup.multiple > 0)
            .order_by(Startup.multiple)
            .limit(5)
        )
        best_deals = deals.scalars().all()
        
        top_rev = await db.execute(
            select(Startup)
            .where(Startup.revenue_30d.isnot(None))
            .order_by(desc(Startup.revenue_30d))
            .limit(5)
        )
        top_revenue = top_rev.scalars().all()
        
        return {
            "overview": {
                "total_startups": overall_stats.total or 0,
                "total_market_revenue": round(overall_stats.total_revenue or 0, 2),
                "avg_revenue": round(overall_stats.avg_revenue or 0, 2),
                "avg_multiple": round(overall_stats.avg_multiple or 0, 2),
            },
            "top_categories": [
                {"name": cat, "count": count, "total_revenue": round(rev or 0, 2)}
                for cat, count, rev in top_categories
            ],
            # 使用 _build_product_profile 确保包含 internal_url 和 founder_social_url
            "fastest_growing": [await _build_product_profile(db, s) for s in fast_growing],
            "best_deals": [await _build_product_profile(db, s) for s in best_deals],
            "top_revenue": [await _build_product_profile(db, s) for s in top_revenue],
        }


async def get_leaderboard(limit: int = 20) -> List[Dict[str, Any]]:
    """Get founder leaderboard with social URLs"""
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Founder)
            .order_by(Founder.rank)
            .limit(limit)
        )
        founders = result.scalars().all()
        
        # 为每个创始人添加 social_url
        leaderboard = []
        for f in founders:
            founder_dict = f.to_dict()
            # 构建社交媒体链接
            founder_dict["social_url"] = _build_founder_social_url(
                f.username,
                f.social_platform
            )
            leaderboard.append(founder_dict)
        
        return leaderboard


# ============================================================================
# MCP 工具定义
# ============================================================================

@tool(
    "get_startups_by_ids",
    "Get startups by their IDs. Use this when you have specific product IDs from the context.",
    {
        "type": "object",
        "properties": {
            "ids": {
                "type": "array",
                "items": {"type": "integer"},
                "description": "List of product IDs. Example: [4, 1]"
            }
        },
        "required": ["ids"]
    }
)
async def get_startups_by_ids_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """通过 ID 查询产品"""
    import time as time_module
    import asyncio as aio
    
    start_time = time_module.time()
    ids = args.get("ids", [])
    
    if isinstance(ids, str):
        try:
            ids = json.loads(ids)
        except:
            ids = []
    
    print(f"[TOOL] get_startups_by_ids called with ids={ids}", flush=True)
    
    if not ids:
        return {
            "content": [{"type": "text", "text": json.dumps({"error": "No IDs provided"}, ensure_ascii=False)}],
            "is_error": True
        }
    
    try:
        result = await aio.wait_for(_get_startups_by_ids(ids), timeout=30.0)
        elapsed = time_module.time() - start_time
        print(f"[TOOL] get_startups_by_ids completed in {elapsed:.2f}s, returned {len(result)} items", flush=True)
        return {"content": [{"type": "text", "text": json.dumps(result, indent=2, ensure_ascii=False)}]}
    except Exception as e:
        print(f"[TOOL] get_startups_by_ids failed: {e}", flush=True)
        return {"content": [{"type": "text", "text": json.dumps({"error": str(e)}, ensure_ascii=False)}], "is_error": True}


@tool(
    "search_startups",
    "Search startups by keyword (name or description). Use this when you need to find products by name.",
    {
        "type": "object",
        "properties": {
            "keyword": {"type": "string", "description": "Search keyword"},
            "limit": {"type": "integer", "description": "Maximum results. Default: 20"}
        },
        "required": ["keyword"]
    }
)
async def search_startups_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """通过关键词搜索产品"""
    import time as time_module
    import asyncio as aio
    
    start_time = time_module.time()
    keyword = args.get("keyword", "")
    limit = min(args.get("limit", 20), 100)
    
    print(f"[TOOL] search_startups called with keyword='{keyword}'", flush=True)
    
    if not keyword:
        return {
            "content": [{"type": "text", "text": json.dumps({"error": "No keyword provided"}, ensure_ascii=False)}],
            "is_error": True
        }
    
    try:
        result = await aio.wait_for(_search_startups(keyword, limit), timeout=30.0)
        elapsed = time_module.time() - start_time
        print(f"[TOOL] search_startups completed in {elapsed:.2f}s, returned {len(result)} items", flush=True)
        return {"content": [{"type": "text", "text": json.dumps(result, indent=2, ensure_ascii=False)}]}
    except Exception as e:
        print(f"[TOOL] search_startups failed: {e}", flush=True)
        return {"content": [{"type": "text", "text": json.dumps({"error": str(e)}, ensure_ascii=False)}], "is_error": True}


@tool(
    "browse_startups",
    "Browse startups with filters. Use this when exploring products by category or revenue range. Supports optional semantic query for smarter filtering.",
    {
        "type": "object",
        "properties": {
            "category": {"type": "string", "description": "Filter by category"},
            "min_revenue": {"type": "number", "description": "Minimum 30-day revenue"},
            "max_revenue": {"type": "number", "description": "Maximum 30-day revenue"},
            "semantic_query": {"type": "string", "description": "Optional: natural language description to filter results semantically"},
            "limit": {"type": "integer", "description": "Maximum results. Default: 20"}
        }
    }
)
async def browse_startups_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """浏览筛选产品（支持语义过滤）"""
    import time as time_module
    import asyncio as aio
    
    start_time = time_module.time()
    semantic_query = args.get("semantic_query")
    print(f"[TOOL] browse_startups called with args={args}", flush=True)
    
    try:
        # 如果有语义查询，先用向量搜索召回，再用结构化条件过滤
        if semantic_query:
            from services.vector_store import vector_store
            if vector_store.enabled:
                # 构建向量过滤条件
                filter_dict = {}
                if args.get("category"):
                    filter_dict["category"] = {"$eq": args["category"]}
                if args.get("min_revenue"):
                    filter_dict["revenue_30d"] = {"$gte": args["min_revenue"]}
                
                # 语义搜索
                results = await vector_store.search(
                    query=semantic_query,
                    namespace="products",
                    top_k=min(args.get("limit", 20), 100),
                    filter=filter_dict if filter_dict else None
                )
                
                # 获取完整数据
                startup_ids = [r["metadata"].get("startup_id") for r in results if r["metadata"].get("startup_id")]
                if startup_ids:
                    products = await _get_startups_by_ids(startup_ids, include_full_profile=True)
                    score_map = {r["metadata"]["startup_id"]: r["score"] for r in results}
                    for p in products:
                        p["similarity_score"] = round(score_map.get(p["id"], 0), 4)
                    products.sort(key=lambda x: x.get("similarity_score", 0), reverse=True)
                    
                    elapsed = time_module.time() - start_time
                    print(f"[TOOL] browse_startups (semantic) completed in {elapsed:.2f}s, returned {len(products)} items", flush=True)
                    return {"content": [{"type": "text", "text": json.dumps(products, indent=2, ensure_ascii=False)}]}
        
        # 普通结构化查询
        result = await aio.wait_for(
            _browse_startups(
                category=args.get("category"),
                min_revenue=args.get("min_revenue"),
                max_revenue=args.get("max_revenue"),
                limit=min(args.get("limit", 20), 100)
            ),
            timeout=30.0
        )
        elapsed = time_module.time() - start_time
        print(f"[TOOL] browse_startups completed in {elapsed:.2f}s, returned {len(result)} items", flush=True)
        return {"content": [{"type": "text", "text": json.dumps(result, indent=2, ensure_ascii=False)}]}
    except Exception as e:
        print(f"[TOOL] browse_startups failed: {e}", flush=True)
        return {"content": [{"type": "text", "text": json.dumps({"error": str(e)}, ensure_ascii=False)}], "is_error": True}


@tool(
    "get_category_analysis",
    "Get detailed statistical analysis for a specific category or all categories.",
    {"type": "object", "properties": {"category": {"type": "string", "description": "Category name (optional)"}}}
)
async def get_category_analysis_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """赛道分析"""
    try:
        result = await get_category_analysis(category=args.get("category"))
        return {"content": [{"type": "text", "text": json.dumps(result, indent=2, ensure_ascii=False)}]}
    except Exception as e:
        return {"content": [{"type": "text", "text": json.dumps({"error": str(e)}, ensure_ascii=False)}], "is_error": True}


@tool(
    "get_trend_report",
    "Generate a comprehensive trend report for the SaaS market.",
    {"type": "object", "properties": {}}
)
async def get_trend_report_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """趋势报告"""
    try:
        result = await get_trend_report()
        return {"content": [{"type": "text", "text": json.dumps(result, indent=2, ensure_ascii=False)}]}
    except Exception as e:
        return {"content": [{"type": "text", "text": json.dumps({"error": str(e)}, ensure_ascii=False)}], "is_error": True}


@tool(
    "get_leaderboard",
    "Get the founder leaderboard rankings.",
    {"type": "object", "properties": {"limit": {"type": "integer", "description": "Number of founders. Default: 20"}}}
)
async def get_leaderboard_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """创始人排行榜"""
    try:
        result = await get_leaderboard(limit=min(args.get("limit", 20), 100))
        return {"content": [{"type": "text", "text": json.dumps(result, indent=2, ensure_ascii=False)}]}
    except Exception as e:
        return {"content": [{"type": "text", "text": json.dumps({"error": str(e)}, ensure_ascii=False)}], "is_error": True}
