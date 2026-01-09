"""
Agent tools for querying and analyzing SaaS data

Enhanced with:
- Fuzzy matching for text fields
- Multi-field combination queries
- Rich filtering dimensions based on ProductSelectionAnalysis
- Revenue history analysis
"""

from typing import Optional, List, Dict, Any, Union
from sqlalchemy import select, func, desc, asc, or_, and_, case
from sqlalchemy.ext.asyncio import AsyncSession
import json
from datetime import datetime, timedelta

from database.db import AsyncSessionLocal
from database.models import (
    Startup, Founder, ProductSelectionAnalysis, LandingPageAnalysis,
    ComprehensiveAnalysis, RevenueHistory, CategoryAnalysis
)

try:
    from claude_agent_sdk import tool
    HAS_CLAUDE_SDK = True
except ImportError:
    HAS_CLAUDE_SDK = False
    # Dummy decorator if SDK not installed
    def tool(name, description, input_schema):
        def decorator(func):
            return func
        return decorator


async def query_startups(
    # === 基础搜索 ===
    search: Optional[str] = None,  # 模糊搜索：名称、描述
    name_contains: Optional[str] = None,  # 名称包含
    description_contains: Optional[str] = None,  # 描述包含
    category: Optional[str] = None,  # 精确分类
    categories: Optional[List[str]] = None,  # 多分类 OR 查询
    
    # === 收入过滤 ===
    min_revenue: Optional[float] = None,
    max_revenue: Optional[float] = None,
    revenue_tier: Optional[str] = None,  # micro/small/medium/large
    
    # === 增长过滤 ===
    min_growth_rate: Optional[float] = None,
    max_growth_rate: Optional[float] = None,
    
    # === 创始人过滤 ===
    founder_name_contains: Optional[str] = None,
    min_followers: Optional[int] = None,
    max_followers: Optional[int] = None,
    
    # === 技术维度 ===
    tech_complexity: Optional[str] = None,  # low, medium, high
    ai_dependency: Optional[str] = None,  # none, light, heavy
    has_realtime_feature: Optional[bool] = None,
    is_data_intensive: Optional[bool] = None,
    
    # === 商业模式维度 ===
    target_customer: Optional[str] = None,  # b2c, b2b_smb, b2b_enterprise, b2d
    pricing_model: Optional[str] = None,  # subscription, one_time, usage, freemium
    market_scope: Optional[str] = None,  # horizontal, vertical
    
    # === 可复制性维度 ===
    feature_complexity: Optional[str] = None,  # simple, moderate, complex
    startup_cost_level: Optional[str] = None,  # low, medium, high
    product_stage: Optional[str] = None,  # early, growth, mature
    
    # === 评分过滤 ===
    min_suitability: Optional[float] = None,  # 最低独立开发适合度 (0-10)
    min_recommendation: Optional[float] = None,  # 最低综合推荐指数 (0-10)
    
    # === 布尔标签 ===
    is_product_driven: Optional[bool] = None,
    is_small_and_beautiful: Optional[bool] = None,
    is_for_sale: Optional[bool] = None,
    is_verified: Optional[bool] = None,
    
    # === 排序与分页 ===
    sort_by: str = "revenue_30d",  # revenue_30d, growth_rate, suitability, recommendation, followers
    sort_order: str = "desc",  # asc, desc
    limit: int = 20,
    offset: int = 0,
    
    # === 输出控制 ===
    include_analysis: bool = True,
    include_landing_analysis: bool = False,
    include_revenue_history: bool = False,
) -> Dict[str, Any]:
    """
    Query startups with comprehensive filters, fuzzy matching, and combination queries.
    
    This is the primary tool for finding SaaS products based on various criteria.
    Supports fuzzy text search, multi-value filters, and rich analysis dimensions.

    Args:
        search: Fuzzy search across name AND description (OR logic)
        name_contains: Fuzzy match on product name only
        description_contains: Fuzzy match on description only
        category: Exact category match
        categories: List of categories (OR logic) - e.g., ["AI", "SaaS", "Developer Tools"]
        
        min_revenue/max_revenue: Revenue range filter (30-day revenue)
        revenue_tier: Quick filter - micro(<$500), small($500-2K), medium($2K-10K), large(>$10K)
        
        min_growth_rate/max_growth_rate: Growth rate percentage filter
        
        founder_name_contains: Fuzzy match on founder name
        min_followers/max_followers: Founder follower count range
        
        tech_complexity: Technical complexity level (low/medium/high)
        ai_dependency: AI/LLM dependency (none/light/heavy)
        has_realtime_feature: Whether product has realtime features
        is_data_intensive: Whether product is data-intensive
        
        target_customer: Target customer type (b2c/b2b_smb/b2b_enterprise/b2d)
        pricing_model: Pricing model (subscription/one_time/usage/freemium)
        market_scope: Market scope (horizontal/vertical)
        
        feature_complexity: Feature complexity (simple/moderate/complex)
        startup_cost_level: Startup cost (low/medium/high)
        product_stage: Product lifecycle (early/growth/mature)
        
        min_suitability: Minimum indie developer suitability score (0-10)
        min_recommendation: Minimum overall recommendation score (0-10)
        
        is_product_driven: Filter for product-driven growth
        is_small_and_beautiful: Filter for "small and beautiful" products
        is_for_sale: Filter products that are for sale
        is_verified: Filter verified products
        
        sort_by: Sort field (revenue_30d/growth_rate/suitability/recommendation/followers)
        sort_order: Sort direction (asc/desc)
        limit: Max results (capped at 100)
        offset: Pagination offset
        
        include_analysis: Include ProductSelectionAnalysis data
        include_landing_analysis: Include LandingPageAnalysis data
        include_revenue_history: Include recent revenue history (last 30 days)

    Returns:
        Dictionary with:
        - results: List of startup dictionaries
        - total: Total matching count
        - filters_applied: Summary of active filters
    """
    async with AsyncSessionLocal() as db:
        # 基础查询
        query = select(Startup)
        count_query = select(func.count(Startup.id))
        
        # 收集应用的过滤条件
        filters_applied = []
        
        # === 文本模糊搜索 ===
        if search:
            pattern = f"%{search}%"
            query = query.where(
                or_(
                    Startup.name.ilike(pattern),
                    Startup.description.ilike(pattern)
                )
            )
            count_query = count_query.where(
                or_(
                    Startup.name.ilike(pattern),
                    Startup.description.ilike(pattern)
                )
            )
            filters_applied.append(f"search='{search}'")
        
        if name_contains:
            pattern = f"%{name_contains}%"
            query = query.where(Startup.name.ilike(pattern))
            count_query = count_query.where(Startup.name.ilike(pattern))
            filters_applied.append(f"name_contains='{name_contains}'")
        
        if description_contains:
            pattern = f"%{description_contains}%"
            query = query.where(Startup.description.ilike(pattern))
            count_query = count_query.where(Startup.description.ilike(pattern))
            filters_applied.append(f"description_contains='{description_contains}'")
        
        if founder_name_contains:
            pattern = f"%{founder_name_contains}%"
            query = query.where(Startup.founder_name.ilike(pattern))
            count_query = count_query.where(Startup.founder_name.ilike(pattern))
            filters_applied.append(f"founder_name_contains='{founder_name_contains}'")
        
        # === 分类过滤 ===
        if category:
            query = query.where(Startup.category == category)
            count_query = count_query.where(Startup.category == category)
            filters_applied.append(f"category='{category}'")
        
        if categories:
            query = query.where(Startup.category.in_(categories))
            count_query = count_query.where(Startup.category.in_(categories))
            filters_applied.append(f"categories={categories}")
        
        # === 收入过滤 ===
        if min_revenue is not None:
            query = query.where(Startup.revenue_30d >= min_revenue)
            count_query = count_query.where(Startup.revenue_30d >= min_revenue)
            filters_applied.append(f"min_revenue={min_revenue}")
        
        if max_revenue is not None:
            query = query.where(Startup.revenue_30d <= max_revenue)
            count_query = count_query.where(Startup.revenue_30d <= max_revenue)
            filters_applied.append(f"max_revenue={max_revenue}")
        
        # === 增长率过滤 ===
        if min_growth_rate is not None:
            query = query.where(Startup.growth_rate >= min_growth_rate)
            count_query = count_query.where(Startup.growth_rate >= min_growth_rate)
            filters_applied.append(f"min_growth_rate={min_growth_rate}")
        
        if max_growth_rate is not None:
            query = query.where(Startup.growth_rate <= max_growth_rate)
            count_query = count_query.where(Startup.growth_rate <= max_growth_rate)
            filters_applied.append(f"max_growth_rate={max_growth_rate}")
        
        # === 创始人粉丝过滤 ===
        if min_followers is not None:
            query = query.where(Startup.founder_followers >= min_followers)
            count_query = count_query.where(Startup.founder_followers >= min_followers)
            filters_applied.append(f"min_followers={min_followers}")
        
        if max_followers is not None:
            query = query.where(Startup.founder_followers <= max_followers)
            count_query = count_query.where(Startup.founder_followers <= max_followers)
            filters_applied.append(f"max_followers={max_followers}")
        
        # === 布尔过滤 ===
        if is_for_sale is not None:
            query = query.where(Startup.is_for_sale == is_for_sale)
            count_query = count_query.where(Startup.is_for_sale == is_for_sale)
            filters_applied.append(f"is_for_sale={is_for_sale}")
        
        if is_verified is not None:
            query = query.where(Startup.is_verified == is_verified)
            count_query = count_query.where(Startup.is_verified == is_verified)
            filters_applied.append(f"is_verified={is_verified}")
        
        # === 分析维度过滤 (需要 JOIN) ===
        needs_selection_join = any([
            tech_complexity, ai_dependency, target_customer, product_stage,
            min_suitability, feature_complexity, startup_cost_level,
            pricing_model, market_scope, revenue_tier, is_product_driven,
            is_small_and_beautiful, has_realtime_feature, is_data_intensive
        ])
        
        needs_comprehensive_join = min_recommendation is not None
        
        if needs_selection_join:
            query = query.join(
                ProductSelectionAnalysis,
                Startup.id == ProductSelectionAnalysis.startup_id,
                isouter=True
            )
            count_query = count_query.join(
                ProductSelectionAnalysis,
                Startup.id == ProductSelectionAnalysis.startup_id,
                isouter=True
            )
            
            if tech_complexity:
                query = query.where(ProductSelectionAnalysis.tech_complexity_level == tech_complexity)
                count_query = count_query.where(ProductSelectionAnalysis.tech_complexity_level == tech_complexity)
                filters_applied.append(f"tech_complexity='{tech_complexity}'")
            
            if ai_dependency:
                query = query.where(ProductSelectionAnalysis.ai_dependency_level == ai_dependency)
                count_query = count_query.where(ProductSelectionAnalysis.ai_dependency_level == ai_dependency)
                filters_applied.append(f"ai_dependency='{ai_dependency}'")
            
            if target_customer:
                query = query.where(ProductSelectionAnalysis.target_customer == target_customer)
                count_query = count_query.where(ProductSelectionAnalysis.target_customer == target_customer)
                filters_applied.append(f"target_customer='{target_customer}'")
            
            if product_stage:
                query = query.where(ProductSelectionAnalysis.product_stage == product_stage)
                count_query = count_query.where(ProductSelectionAnalysis.product_stage == product_stage)
                filters_applied.append(f"product_stage='{product_stage}'")
            
            if feature_complexity:
                query = query.where(ProductSelectionAnalysis.feature_complexity == feature_complexity)
                count_query = count_query.where(ProductSelectionAnalysis.feature_complexity == feature_complexity)
                filters_applied.append(f"feature_complexity='{feature_complexity}'")
            
            if startup_cost_level:
                query = query.where(ProductSelectionAnalysis.startup_cost_level == startup_cost_level)
                count_query = count_query.where(ProductSelectionAnalysis.startup_cost_level == startup_cost_level)
                filters_applied.append(f"startup_cost_level='{startup_cost_level}'")
            
            if pricing_model:
                query = query.where(ProductSelectionAnalysis.pricing_model == pricing_model)
                count_query = count_query.where(ProductSelectionAnalysis.pricing_model == pricing_model)
                filters_applied.append(f"pricing_model='{pricing_model}'")
            
            if market_scope:
                query = query.where(ProductSelectionAnalysis.market_scope == market_scope)
                count_query = count_query.where(ProductSelectionAnalysis.market_scope == market_scope)
                filters_applied.append(f"market_scope='{market_scope}'")
            
            if revenue_tier:
                query = query.where(ProductSelectionAnalysis.revenue_tier == revenue_tier)
                count_query = count_query.where(ProductSelectionAnalysis.revenue_tier == revenue_tier)
                filters_applied.append(f"revenue_tier='{revenue_tier}'")
            
            if min_suitability is not None:
                query = query.where(ProductSelectionAnalysis.individual_dev_suitability >= min_suitability)
                count_query = count_query.where(ProductSelectionAnalysis.individual_dev_suitability >= min_suitability)
                filters_applied.append(f"min_suitability={min_suitability}")
            
            if is_product_driven is not None:
                query = query.where(ProductSelectionAnalysis.is_product_driven == is_product_driven)
                count_query = count_query.where(ProductSelectionAnalysis.is_product_driven == is_product_driven)
                filters_applied.append(f"is_product_driven={is_product_driven}")
            
            if is_small_and_beautiful is not None:
                query = query.where(ProductSelectionAnalysis.is_small_and_beautiful == is_small_and_beautiful)
                count_query = count_query.where(ProductSelectionAnalysis.is_small_and_beautiful == is_small_and_beautiful)
                filters_applied.append(f"is_small_and_beautiful={is_small_and_beautiful}")
            
            if has_realtime_feature is not None:
                query = query.where(ProductSelectionAnalysis.has_realtime_feature == has_realtime_feature)
                count_query = count_query.where(ProductSelectionAnalysis.has_realtime_feature == has_realtime_feature)
                filters_applied.append(f"has_realtime_feature={has_realtime_feature}")
            
            if is_data_intensive is not None:
                query = query.where(ProductSelectionAnalysis.is_data_intensive == is_data_intensive)
                count_query = count_query.where(ProductSelectionAnalysis.is_data_intensive == is_data_intensive)
                filters_applied.append(f"is_data_intensive={is_data_intensive}")
        
        if needs_comprehensive_join:
            query = query.join(
                ComprehensiveAnalysis,
                Startup.id == ComprehensiveAnalysis.startup_id,
                isouter=True
            )
            count_query = count_query.join(
                ComprehensiveAnalysis,
                Startup.id == ComprehensiveAnalysis.startup_id,
                isouter=True
            )
            
            if min_recommendation is not None:
                query = query.where(ComprehensiveAnalysis.overall_recommendation >= min_recommendation)
                count_query = count_query.where(ComprehensiveAnalysis.overall_recommendation >= min_recommendation)
                filters_applied.append(f"min_recommendation={min_recommendation}")
        
        # === 排序 ===
        order_func = desc if sort_order.lower() == "desc" else asc
        
        if sort_by == "revenue_30d":
            query = query.order_by(order_func(Startup.revenue_30d))
        elif sort_by == "growth_rate":
            query = query.order_by(order_func(Startup.growth_rate))
        elif sort_by == "followers":
            query = query.order_by(order_func(Startup.founder_followers))
        elif sort_by == "suitability" and needs_selection_join:
            query = query.order_by(order_func(ProductSelectionAnalysis.individual_dev_suitability))
        elif sort_by == "recommendation" and needs_comprehensive_join:
            query = query.order_by(order_func(ComprehensiveAnalysis.overall_recommendation))
        else:
            query = query.order_by(order_func(Startup.revenue_30d))
        
        # === 分页 ===
        query = query.offset(offset).limit(min(limit, 100))
        
        # === 执行查询 ===
        result = await db.execute(query)
        startups = result.scalars().all()
        
        # 获取总数
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        # === 构建返回数据 ===
        results = []
        for s in startups:
            data = s.to_dict()
            
            if include_analysis:
                # 获取产品选品分析
                selection_result = await db.execute(
                    select(ProductSelectionAnalysis).where(ProductSelectionAnalysis.startup_id == s.id)
                )
                selection = selection_result.scalar_one_or_none()
                if selection:
                    data['selection_analysis'] = selection.to_tags_dict()
                    data['selection_scores'] = selection.to_scores_dict()
                
                # 获取综合分析评分
                comp_result = await db.execute(
                    select(ComprehensiveAnalysis).where(ComprehensiveAnalysis.startup_id == s.id)
                )
                comp = comp_result.scalar_one_or_none()
                if comp:
                    data['comprehensive_analysis'] = {
                        'overall_recommendation': comp.overall_recommendation,
                        'maturity_score': comp.maturity_score,
                        'positioning_clarity': comp.positioning_clarity,
                        'individual_replicability': comp.individual_replicability,
                    }
            
            if include_landing_analysis:
                landing_result = await db.execute(
                    select(LandingPageAnalysis).where(LandingPageAnalysis.startup_id == s.id)
                )
                landing = landing_result.scalar_one_or_none()
                if landing:
                    data['landing_analysis'] = {
                        'target_audience': landing.target_audience,
                        'core_features': landing.core_features,
                        'pain_points': landing.pain_points,
                        'pricing_model': landing.pricing_model,
                        'headline_text': landing.headline_text,
                        'tagline_text': landing.tagline_text,
                    }
            
            if include_revenue_history:
                # 获取最近30天收入历史
                thirty_days_ago = datetime.utcnow().date() - timedelta(days=30)
                history_result = await db.execute(
                    select(RevenueHistory)
                    .where(RevenueHistory.startup_id == s.id)
                    .where(RevenueHistory.date >= thirty_days_ago)
                    .order_by(RevenueHistory.date)
                )
                history = history_result.scalars().all()
                if history:
                    data['revenue_history'] = [h.to_dict() for h in history]
            
            results.append(data)
        
        return {
            "results": results,
            "total": total,
            "limit": min(limit, 100),
            "offset": offset,
            "filters_applied": filters_applied,
        }


async def get_category_analysis(category: Optional[str] = None) -> Dict[str, Any]:
    """
    Get detailed analysis for a specific category or all categories.
    
    Args:
        category: Category to analyze (None for all categories)
        
    Returns:
        Dictionary with category statistics and insights
    """
    async with AsyncSessionLocal() as db:
        if category:
            # Single category analysis
            result = await db.execute(
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
            stats = result.first()
            
            # Top performers in category
            top_result = await db.execute(
                select(Startup)
                .where(Startup.category == category)
                .order_by(desc(Startup.revenue_30d))
                .limit(5)
            )
            top_startups = top_result.scalars().all()
            
            return {
                "category": category,
                "count": stats.count or 0,
                "total_revenue": round(stats.total_revenue or 0, 2),
                "avg_revenue": round(stats.avg_revenue or 0, 2),
                "avg_price": round(stats.avg_price or 0, 2),
                "avg_multiple": round(stats.avg_multiple or 0, 2),
                "avg_growth": round(stats.avg_growth or 0, 2),
                "max_revenue": round(stats.max_revenue or 0, 2),
                "min_revenue": round(stats.min_revenue or 0, 2),
                "top_performers": [s.to_dict() for s in top_startups],
            }
        else:
            # All categories summary
            result = await db.execute(
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
            categories = result.all()
            
            return {
                "categories": [
                    {
                        "name": cat,
                        "count": count,
                        "total_revenue": round(total_rev or 0, 2),
                        "avg_revenue": round(avg_rev or 0, 2),
                    }
                    for cat, count, total_rev, avg_rev in categories
                ]
            }


async def get_product_by_slug(slug: str, include_all_analysis: bool = True) -> Dict[str, Any]:
    """
    Get detailed information about a specific product by its slug.
    
    Args:
        slug: Product slug (URL-friendly identifier)
        include_all_analysis: Include all analysis data
        
    Returns:
        Complete product information with all analysis
    """
    async with AsyncSessionLocal() as db:
        # Get startup
        result = await db.execute(
            select(Startup).where(Startup.slug == slug)
        )
        startup = result.scalar_one_or_none()
        
        if not startup:
            return {"error": f"Product with slug '{slug}' not found"}
        
        data = startup.to_dict()
        
        if include_all_analysis:
            # Selection analysis
            selection_result = await db.execute(
                select(ProductSelectionAnalysis).where(ProductSelectionAnalysis.startup_id == startup.id)
            )
            selection = selection_result.scalar_one_or_none()
            if selection:
                data['selection_analysis'] = selection.to_dict()
            
            # Landing page analysis
            landing_result = await db.execute(
                select(LandingPageAnalysis).where(LandingPageAnalysis.startup_id == startup.id)
            )
            landing = landing_result.scalar_one_or_none()
            if landing:
                data['landing_analysis'] = landing.to_dict()
            
            # Comprehensive analysis
            comp_result = await db.execute(
                select(ComprehensiveAnalysis).where(ComprehensiveAnalysis.startup_id == startup.id)
            )
            comp = comp_result.scalar_one_or_none()
            if comp:
                data['comprehensive_analysis'] = comp.to_dict()
            
            # Revenue history (last 90 days)
            ninety_days_ago = datetime.utcnow().date() - timedelta(days=90)
            history_result = await db.execute(
                select(RevenueHistory)
                .where(RevenueHistory.startup_id == startup.id)
                .where(RevenueHistory.date >= ninety_days_ago)
                .order_by(RevenueHistory.date)
            )
            history = history_result.scalars().all()
            if history:
                data['revenue_history'] = [h.to_dict() for h in history]
        
        return data


async def get_revenue_trends(
    slug: Optional[str] = None,
    startup_id: Optional[int] = None,
    days: int = 30,
) -> Dict[str, Any]:
    """
    Get revenue trend analysis for a specific product.
    
    Args:
        slug: Product slug
        startup_id: Product ID (alternative to slug)
        days: Number of days to analyze
        
    Returns:
        Revenue trend data with statistics
    """
    async with AsyncSessionLocal() as db:
        # Get startup
        if slug:
            result = await db.execute(select(Startup).where(Startup.slug == slug))
            startup = result.scalar_one_or_none()
            if not startup:
                return {"error": f"Product with slug '{slug}' not found"}
            startup_id = startup.id
        elif not startup_id:
            return {"error": "Either slug or startup_id must be provided"}
        
        # Get revenue history
        start_date = datetime.utcnow().date() - timedelta(days=days)
        history_result = await db.execute(
            select(RevenueHistory)
            .where(RevenueHistory.startup_id == startup_id)
            .where(RevenueHistory.date >= start_date)
            .order_by(RevenueHistory.date)
        )
        history = history_result.scalars().all()
        
        if not history:
            return {"error": "No revenue history available", "startup_id": startup_id}
        
        # Calculate statistics
        revenues = [h.revenue / 100 for h in history if h.revenue]  # Convert cents to dollars
        
        if not revenues:
            return {"error": "No revenue data available", "startup_id": startup_id}
        
        avg_revenue = sum(revenues) / len(revenues)
        min_revenue = min(revenues)
        max_revenue = max(revenues)
        
        # Calculate trend (simple linear regression)
        if len(revenues) > 1:
            x_values = list(range(len(revenues)))
            x_mean = sum(x_values) / len(x_values)
            y_mean = avg_revenue
            
            numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, revenues))
            denominator = sum((x - x_mean) ** 2 for x in x_values)
            
            slope = numerator / denominator if denominator != 0 else 0
            trend = "growing" if slope > 0 else "declining" if slope < 0 else "stable"
        else:
            slope = 0
            trend = "insufficient_data"
        
        return {
            "startup_id": startup_id,
            "days_analyzed": days,
            "data_points": len(history),
            "statistics": {
                "avg_revenue": round(avg_revenue, 2),
                "min_revenue": round(min_revenue, 2),
                "max_revenue": round(max_revenue, 2),
                "trend": trend,
                "daily_change": round(slope, 2),
            },
            "history": [
                {
                    "date": h.date.isoformat(),
                    "revenue": h.revenue / 100 if h.revenue else 0,
                    "mrr": h.mrr / 100 if h.mrr else 0,
                }
                for h in history
            ]
        }


async def compare_products(
    slugs: List[str],
    comparison_fields: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Compare multiple products side by side.
    
    Args:
        slugs: List of product slugs to compare
        comparison_fields: Specific fields to compare (None for all)
        
    Returns:
        Comparison data for all products
    """
    if not slugs or len(slugs) < 2:
        return {"error": "At least 2 product slugs required for comparison"}
    
    if len(slugs) > 10:
        return {"error": "Maximum 10 products can be compared at once"}
    
    async with AsyncSessionLocal() as db:
        products = []
        
        for slug in slugs:
            result = await db.execute(
                select(Startup).where(Startup.slug == slug)
            )
            startup = result.scalar_one_or_none()
            
            if not startup:
                products.append({"slug": slug, "error": "Not found"})
                continue
            
            data = {
                "slug": startup.slug,
                "name": startup.name,
                "category": startup.category,
                "revenue_30d": startup.revenue_30d,
                "growth_rate": startup.growth_rate,
                "founder_followers": startup.founder_followers,
            }
            
            # Get selection analysis
            selection_result = await db.execute(
                select(ProductSelectionAnalysis).where(ProductSelectionAnalysis.startup_id == startup.id)
            )
            selection = selection_result.scalar_one_or_none()
            if selection:
                data.update({
                    "tech_complexity": selection.tech_complexity_level,
                    "ai_dependency": selection.ai_dependency_level,
                    "target_customer": selection.target_customer,
                    "feature_complexity": selection.feature_complexity,
                    "startup_cost": selection.startup_cost_level,
                    "suitability_score": selection.individual_dev_suitability,
                })
            
            # Get comprehensive analysis
            comp_result = await db.execute(
                select(ComprehensiveAnalysis).where(ComprehensiveAnalysis.startup_id == startup.id)
            )
            comp = comp_result.scalar_one_or_none()
            if comp:
                data["recommendation_score"] = comp.overall_recommendation
            
            products.append(data)
        
        return {
            "comparison": products,
            "count": len(products),
        }


async def get_trend_report() -> Dict[str, Any]:
    """
    Generate a comprehensive trend report for the SaaS market.
    
    Returns:
        Dictionary with market trends, top categories, and insights
    """
    async with AsyncSessionLocal() as db:
        # Overall stats
        overall = await db.execute(
            select(
                func.count(Startup.id).label("total"),
                func.sum(Startup.revenue_30d).label("total_revenue"),
                func.avg(Startup.revenue_30d).label("avg_revenue"),
                func.avg(Startup.multiple).label("avg_multiple"),
            )
        )
        overall_stats = overall.first()
        
        # Top categories by revenue
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
        
        # Fastest growing
        growing = await db.execute(
            select(Startup)
            .where(Startup.growth_rate.isnot(None))
            .order_by(desc(Startup.growth_rate))
            .limit(5)
        )
        fast_growing = growing.scalars().all()
        
        # Best deals (lowest multiple)
        deals = await db.execute(
            select(Startup)
            .where(Startup.multiple.isnot(None))
            .where(Startup.multiple > 0)
            .order_by(Startup.multiple)
            .limit(5)
        )
        best_deals = deals.scalars().all()
        
        # Highest revenue
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
            "fastest_growing": [s.to_dict() for s in fast_growing],
            "best_deals": [s.to_dict() for s in best_deals],
            "top_revenue": [s.to_dict() for s in top_revenue],
        }


async def get_leaderboard(limit: int = 20) -> List[Dict[str, Any]]:
    """
    Get the founder leaderboard.

    Args:
        limit: Number of founders to return

    Returns:
        List of founder dictionaries
    """
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Founder)
            .order_by(Founder.rank)
            .limit(limit)
        )
        founders = result.scalars().all()

        return [f.to_dict() for f in founders]


# ============================================================================
# MCP Tools for Claude Agent SDK
# ============================================================================

@tool(
    "query_startups",
    """Query startups with comprehensive filters, fuzzy matching, and combination queries.
    
    PRIMARY USE CASES:
    - Find products by fuzzy text search (name, description, founder)
    - Filter by multiple categories, revenue ranges, growth rates
    - Filter by technical characteristics (AI dependency, complexity, realtime features)
    - Filter by business model (pricing, target customer, market scope)
    - Filter by indie dev suitability (complexity, cost, stage)
    - Combine multiple filters for precise targeting
    
    FUZZY SEARCH:
    - search: Search across name AND description (use for general queries)
    - name_contains: Search only in product names
    - description_contains: Search only in descriptions
    - founder_name_contains: Search by founder name
    
    MULTI-VALUE FILTERS:
    - categories: Pass list like ["AI", "Developer Tools", "SaaS"] for OR logic
    
    QUICK FILTERS:
    - revenue_tier: micro/small/medium/large (instead of min/max revenue)
    - tech_complexity: low/medium/high
    - ai_dependency: none/light/heavy
    - feature_complexity: simple/moderate/complex
    - startup_cost_level: low/medium/high
    
    SORTING:
    - sort_by: revenue_30d, growth_rate, suitability, recommendation, followers
    - sort_order: asc or desc
    
    PAGINATION:
    - limit: Max results per page (default 20, max 100)
    - offset: Skip N results for pagination
    
    Returns: {results: [...], total: N, filters_applied: [...]}
    """,
    {
        "search": str,
        "name_contains": str,
        "description_contains": str,
        "category": str,
        "categories": list,
        "min_revenue": float,
        "max_revenue": float,
        "revenue_tier": str,
        "min_growth_rate": float,
        "max_growth_rate": float,
        "founder_name_contains": str,
        "min_followers": int,
        "max_followers": int,
        "tech_complexity": str,
        "ai_dependency": str,
        "has_realtime_feature": bool,
        "is_data_intensive": bool,
        "target_customer": str,
        "pricing_model": str,
        "market_scope": str,
        "feature_complexity": str,
        "startup_cost_level": str,
        "product_stage": str,
        "min_suitability": float,
        "min_recommendation": float,
        "is_product_driven": bool,
        "is_small_and_beautiful": bool,
        "is_for_sale": bool,
        "is_verified": bool,
        "sort_by": str,
        "sort_order": str,
        "limit": int,
        "offset": int,
        "include_analysis": bool,
        "include_landing_analysis": bool,
        "include_revenue_history": bool,
    }
)
async def query_startups_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """MCP tool wrapper for query_startups with enhanced filtering"""
    try:
        result = await query_startups(
            search=args.get("search"),
            name_contains=args.get("name_contains"),
            description_contains=args.get("description_contains"),
            category=args.get("category"),
            categories=args.get("categories"),
            min_revenue=args.get("min_revenue"),
            max_revenue=args.get("max_revenue"),
            revenue_tier=args.get("revenue_tier"),
            min_growth_rate=args.get("min_growth_rate"),
            max_growth_rate=args.get("max_growth_rate"),
            founder_name_contains=args.get("founder_name_contains"),
            min_followers=args.get("min_followers"),
            max_followers=args.get("max_followers"),
            tech_complexity=args.get("tech_complexity"),
            ai_dependency=args.get("ai_dependency"),
            has_realtime_feature=args.get("has_realtime_feature"),
            is_data_intensive=args.get("is_data_intensive"),
            target_customer=args.get("target_customer"),
            pricing_model=args.get("pricing_model"),
            market_scope=args.get("market_scope"),
            feature_complexity=args.get("feature_complexity"),
            startup_cost_level=args.get("startup_cost_level"),
            product_stage=args.get("product_stage"),
            min_suitability=args.get("min_suitability"),
            min_recommendation=args.get("min_recommendation"),
            is_product_driven=args.get("is_product_driven"),
            is_small_and_beautiful=args.get("is_small_and_beautiful"),
            is_for_sale=args.get("is_for_sale"),
            is_verified=args.get("is_verified"),
            sort_by=args.get("sort_by", "revenue_30d"),
            sort_order=args.get("sort_order", "desc"),
            limit=min(args.get("limit", 20), 100),
            offset=args.get("offset", 0),
            include_analysis=args.get("include_analysis", True),
            include_landing_analysis=args.get("include_landing_analysis", False),
            include_revenue_history=args.get("include_revenue_history", False),
        )

        return {
            "content": [{
                "type": "text",
                "text": json.dumps(result, indent=2, ensure_ascii=False)
            }]
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": json.dumps({"error": str(e), "type": "query_error"}, ensure_ascii=False)
            }],
            "is_error": True
        }


@tool(
    "get_category_analysis",
    "Get detailed statistical analysis for a specific category or all categories. Returns metrics like count, total revenue, average revenue, pricing multiples, growth rates, and top performers in the category.",
    {"category": str}
)
async def get_category_analysis_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """MCP tool wrapper for get_category_analysis"""
    try:
        result = await get_category_analysis(
            category=args.get("category")
        )

        return {
            "content": [{
                "type": "text",
                "text": json.dumps(result, indent=2, ensure_ascii=False)
            }]
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": json.dumps({"error": str(e), "type": "analysis_error"}, ensure_ascii=False)
            }],
            "is_error": True
        }


@tool(
    "get_product_by_slug",
    "Get complete detailed information about a specific product by its slug (URL identifier). Returns all available data including basic info, selection analysis, landing page analysis, comprehensive scores, and revenue history. Use this when you need deep dive into a single product.",
    {
        "slug": str,
        "include_all_analysis": bool
    }
)
async def get_product_by_slug_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """MCP tool wrapper for get_product_by_slug"""
    try:
        result = await get_product_by_slug(
            slug=args.get("slug", ""),
            include_all_analysis=args.get("include_all_analysis", True)
        )

        return {
            "content": [{
                "type": "text",
                "text": json.dumps(result, indent=2, ensure_ascii=False)
            }]
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": json.dumps({"error": str(e), "type": "product_lookup_error"}, ensure_ascii=False)
            }],
            "is_error": True
        }


@tool(
    "get_revenue_trends",
    "Analyze revenue trends for a specific product over time. Returns historical revenue data, statistics (avg/min/max), trend direction (growing/declining/stable), and daily change rate. Useful for understanding product growth patterns.",
    {
        "slug": str,
        "startup_id": int,
        "days": int
    }
)
async def get_revenue_trends_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """MCP tool wrapper for get_revenue_trends"""
    try:
        result = await get_revenue_trends(
            slug=args.get("slug"),
            startup_id=args.get("startup_id"),
            days=args.get("days", 30)
        )

        return {
            "content": [{
                "type": "text",
                "text": json.dumps(result, indent=2, ensure_ascii=False)
            }]
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": json.dumps({"error": str(e), "type": "trend_analysis_error"}, ensure_ascii=False)
            }],
            "is_error": True
        }


@tool(
    "compare_products",
    "Compare multiple products side by side. Provide 2-10 product slugs and get a comparison of their key metrics including revenue, growth, technical complexity, target customer, costs, and suitability scores. Perfect for evaluating similar products or making selection decisions.",
    {
        "slugs": list,
        "comparison_fields": list
    }
)
async def compare_products_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """MCP tool wrapper for compare_products"""
    try:
        result = await compare_products(
            slugs=args.get("slugs", []),
            comparison_fields=args.get("comparison_fields")
        )

        return {
            "content": [{
                "type": "text",
                "text": json.dumps(result, indent=2, ensure_ascii=False)
            }]
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": json.dumps({"error": str(e), "type": "comparison_error"}, ensure_ascii=False)
            }],
            "is_error": True
        }


@tool(
    "get_trend_report",
    "Generate a comprehensive trend report for the SaaS market. Returns overall market statistics, top categories by revenue, fastest growing startups, best investment deals (lowest multiples), and highest revenue startups.",
    {}
)
async def get_trend_report_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """MCP tool wrapper for get_trend_report"""
    try:
        result = await get_trend_report()

        return {
            "content": [{
                "type": "text",
                "text": json.dumps(result, indent=2, ensure_ascii=False)
            }]
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": json.dumps({"error": str(e), "type": "trend_error"}, ensure_ascii=False)
            }],
            "is_error": True
        }


@tool(
    "get_leaderboard",
    "Get the founder leaderboard rankings. Returns information about top founders including their total MRR, number of products, and social profiles.",
    {"limit": int}
)
async def get_leaderboard_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """MCP tool wrapper for get_leaderboard"""
    try:
        result = await get_leaderboard(
            limit=min(args.get("limit", 20), 100)  # Cap at 100
        )

        return {
            "content": [{
                "type": "text",
                "text": json.dumps(result, indent=2, ensure_ascii=False)
            }]
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": json.dumps({"error": str(e), "type": "leaderboard_error"}, ensure_ascii=False)
            }],
            "is_error": True
        }


async def find_excellent_developers(
    min_products: int = 2,
    min_total_revenue: Optional[float] = None,
    min_avg_revenue: Optional[float] = None,
    min_followers: Optional[int] = None,
    sort_by: str = "total_revenue",  # total_revenue, avg_revenue, product_count, followers
    limit: int = 20,
) -> List[Dict[str, Any]]:
    """
    Find excellent indie developers based on their product portfolio and metrics.

    Args:
        min_products: Minimum number of products (default: 2)
        min_total_revenue: Minimum total revenue across all products
        min_avg_revenue: Minimum average revenue per product
        min_followers: Minimum follower count
        sort_by: Sort criteria (total_revenue/avg_revenue/product_count/followers)
        limit: Maximum number of developers to return

    Returns:
        List of developer profiles with their products and metrics
    """
    async with AsyncSessionLocal() as db:
        # 查询创始人及其产品
        query = select(
            Startup.founder_username,
            Startup.founder_name,
            Startup.founder_followers,
            Startup.founder_social_platform,
            Startup.founder_avatar_url,
            func.count(Startup.id).label("product_count"),
            func.sum(Startup.revenue_30d).label("total_revenue"),
            func.avg(Startup.revenue_30d).label("avg_revenue"),
            func.max(Startup.revenue_30d).label("max_revenue"),
        ).where(
            Startup.founder_username.isnot(None)
        ).group_by(
            Startup.founder_username,
            Startup.founder_name,
            Startup.founder_followers,
            Startup.founder_social_platform,
            Startup.founder_avatar_url,
        )

        # 应用过滤条件
        query = query.having(func.count(Startup.id) >= min_products)

        if min_total_revenue is not None:
            query = query.having(func.sum(Startup.revenue_30d) >= min_total_revenue)

        if min_avg_revenue is not None:
            query = query.having(func.avg(Startup.revenue_30d) >= min_avg_revenue)

        if min_followers is not None:
            query = query.having(Startup.founder_followers >= min_followers)

        # 排序
        if sort_by == "total_revenue":
            query = query.order_by(desc("total_revenue"))
        elif sort_by == "avg_revenue":
            query = query.order_by(desc("avg_revenue"))
        elif sort_by == "product_count":
            query = query.order_by(desc("product_count"))
        elif sort_by == "followers":
            query = query.order_by(desc(Startup.founder_followers))

        query = query.limit(limit)

        result = await db.execute(query)
        developers = result.all()

        # 为每个开发者获取产品列表
        developer_profiles = []
        for dev in developers:
            # 获取该开发者的所有产品
            products_query = select(Startup).where(
                Startup.founder_username == dev.founder_username
            ).order_by(desc(Startup.revenue_30d))

            products_result = await db.execute(products_query)
            products = products_result.scalars().all()

            # 构建开发者档案
            profile = {
                "username": dev.founder_username,
                "name": dev.founder_name,
                "followers": dev.founder_followers,
                "social_platform": dev.founder_social_platform,
                "avatar_url": dev.founder_avatar_url,
                "metrics": {
                    "product_count": dev.product_count,
                    "total_revenue": round(dev.total_revenue or 0, 2),
                    "avg_revenue": round(dev.avg_revenue or 0, 2),
                    "max_revenue": round(dev.max_revenue or 0, 2),
                },
                "products": [
                    {
                        "name": p.name,
                        "slug": p.slug,
                        "category": p.category,
                        "revenue_30d": p.revenue_30d,
                        "growth_rate": p.growth_rate,
                        "website_url": p.website_url,
                        "description": p.description,
                    }
                    for p in products
                ]
            }

            developer_profiles.append(profile)

        return developer_profiles


@tool(
    "find_excellent_developers",
    "Find excellent indie developers based on their product portfolio and success metrics. Returns developer profiles with their products, total/average revenue, follower counts, and product categories. Use this to discover successful indie developers, learn from their product strategies, or find potential collaborators/mentors.",
    {
        "min_products": int,
        "min_total_revenue": float,
        "min_avg_revenue": float,
        "min_followers": int,
        "sort_by": str,  # total_revenue, avg_revenue, product_count, followers
        "limit": int
    }
)
async def find_excellent_developers_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """MCP tool wrapper for find_excellent_developers"""
    try:
        result = await find_excellent_developers(
            min_products=args.get("min_products", 2),
            min_total_revenue=args.get("min_total_revenue"),
            min_avg_revenue=args.get("min_avg_revenue"),
            min_followers=args.get("min_followers"),
            sort_by=args.get("sort_by", "total_revenue"),
            limit=min(args.get("limit", 20), 50)  # Cap at 50
        )

        return {
            "content": [{
                "type": "text",
                "text": json.dumps(result, indent=2, ensure_ascii=False)
            }]
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": json.dumps({"error": str(e), "type": "developer_query_error"}, ensure_ascii=False)
            }],
            "is_error": True
        }


# ============================================================================
# Web Search Tool
# ============================================================================

async def web_search(
    query: str,
    limit: int = 10,
    site: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Search the web using Tavily (AI-optimized search)

    Args:
        query: Search query
        limit: Maximum number of results
        site: Optional site to restrict search (e.g., "reddit.com", "indiehackers.com")

    Returns:
        List of search results
    """
    from services.search.factory import SearchServiceFactory

    try:
        # Check if Tavily is configured
        if not SearchServiceFactory.is_available():
            return [{
                "error": "Tavily search not configured. Please set TAVILY_API_KEY in .env file.",
                "title": "Configuration Required",
                "url": "",
                "snippet": "Set TAVILY_API_KEY to enable web search functionality"
            }]

        service = SearchServiceFactory.get_search_service()

        # Search with or without site restriction
        if site:
            response = await service.search_site(query, site, limit=limit)
        else:
            response = await service.search(query, limit=limit)

        # Convert to list of dicts
        return [result.to_dict() for result in response.results]

    except Exception as e:
        return [{
            "error": str(e),
            "title": "Search Error",
            "url": "",
            "snippet": f"Failed to search: {str(e)}"
        }]


@tool(
    "web_search",
    "Search the web for information about SaaS products, market trends, indie hacker discussions, or any topic. Automatically searches across multiple sources including Reddit, IndieHackers, Product Hunt, and general web. Can optionally restrict search to specific websites using the site parameter (e.g., 'reddit.com', 'indiehackers.com', 'producthunt.com').",
    {
        "query": str,
        "limit": int,
        "site": str,  # Optional: "reddit.com", "indiehackers.com", "producthunt.com", etc.
    }
)
async def web_search_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """MCP tool wrapper for web search"""
    try:
        results = await web_search(
            query=args.get("query", ""),
            limit=args.get("limit", 10),
            site=args.get("site"),
        )

        return {
            "content": [{
                "type": "text",
                "text": json.dumps(results, indent=2, ensure_ascii=False)
            }]
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": json.dumps({"error": str(e), "type": "search_error"}, ensure_ascii=False)
            }],
            "is_error": True
        }
