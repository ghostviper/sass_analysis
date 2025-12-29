"""
Agent tools for querying and analyzing SaaS data
"""

from typing import Optional, List, Dict, Any
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
import json

from database.db import AsyncSessionLocal
from database.models import Startup, Founder

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
    category: Optional[str] = None,
    min_revenue: Optional[float] = None,
    max_revenue: Optional[float] = None,
    search: Optional[str] = None,
    limit: int = 20,
) -> List[Dict[str, Any]]:
    """
    Query startups from the database with optional filters.
    
    Args:
        category: Filter by category (e.g., "AI", "SaaS", "Fintech")
        min_revenue: Minimum 30-day revenue
        max_revenue: Maximum 30-day revenue
        search: Search term for name/description
        limit: Maximum number of results
        
    Returns:
        List of startup dictionaries with their data
    """
    async with AsyncSessionLocal() as db:
        query = select(Startup)
        
        if category:
            query = query.where(Startup.category == category)
        if min_revenue is not None:
            query = query.where(Startup.revenue_30d >= min_revenue)
        if max_revenue is not None:
            query = query.where(Startup.revenue_30d <= max_revenue)
        if search:
            pattern = f"%{search}%"
            query = query.where(
                (Startup.name.ilike(pattern)) | 
                (Startup.description.ilike(pattern))
            )
        
        query = query.order_by(desc(Startup.revenue_30d)).limit(limit)
        
        result = await db.execute(query)
        startups = result.scalars().all()
        
        return [s.to_dict() for s in startups]


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
    "Query startups from the database with optional filters for category, revenue range, and search terms. Returns detailed information about matching startups including revenue, category, description, and pricing.",
    {"category": str, "min_revenue": float, "max_revenue": float, "search": str, "limit": int}
)
async def query_startups_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """MCP tool wrapper for query_startups"""
    try:
        result = await query_startups(
            category=args.get("category"),
            min_revenue=args.get("min_revenue"),
            max_revenue=args.get("max_revenue"),
            search=args.get("search"),
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
