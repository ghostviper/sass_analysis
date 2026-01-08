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
    # 新增过滤参数
    tech_complexity: Optional[str] = None,  # low, medium, high
    ai_dependency: Optional[str] = None,  # none, light, heavy
    target_customer: Optional[str] = None,  # b2c, b2b_smb, b2b_enterprise, b2d
    product_stage: Optional[str] = None,  # early, growth, mature
    min_suitability: Optional[float] = None,  # 最低独立开发适合度
    include_analysis: bool = True,  # 是否包含分析数据
) -> List[Dict[str, Any]]:
    """
    Query startups from the database with optional filters including new analysis dimensions.

    Args:
        category: Filter by category (e.g., "AI", "SaaS", "Fintech")
        min_revenue: Minimum 30-day revenue
        max_revenue: Maximum 30-day revenue
        search: Search term for name/description
        limit: Maximum number of results
        tech_complexity: Filter by technical complexity (low/medium/high)
        ai_dependency: Filter by AI dependency level (none/light/heavy)
        target_customer: Filter by target customer type (b2c/b2b_smb/b2b_enterprise/b2d)
        product_stage: Filter by product lifecycle stage (early/growth/mature)
        min_suitability: Minimum individual developer suitability score (0-10)
        include_analysis: Include comprehensive analysis data in results

    Returns:
        List of startup dictionaries with their data and optional analysis
    """
    from database.models import ProductSelectionAnalysis, LandingPageAnalysis, ComprehensiveAnalysis

    async with AsyncSessionLocal() as db:
        query = select(Startup)

        # 基础过滤
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

        # 新增分析维度过滤
        if any([tech_complexity, ai_dependency, target_customer, product_stage, min_suitability]):
            query = query.join(ProductSelectionAnalysis, Startup.id == ProductSelectionAnalysis.startup_id)

            if tech_complexity:
                query = query.where(ProductSelectionAnalysis.tech_complexity_level == tech_complexity)
            if ai_dependency:
                query = query.where(ProductSelectionAnalysis.ai_dependency_level == ai_dependency)
            if target_customer:
                query = query.where(ProductSelectionAnalysis.target_customer == target_customer)
            if product_stage:
                query = query.where(ProductSelectionAnalysis.product_stage == product_stage)
            if min_suitability is not None:
                query = query.where(ProductSelectionAnalysis.individual_dev_suitability >= min_suitability)

        query = query.order_by(desc(Startup.revenue_30d)).limit(limit)

        result = await db.execute(query)
        startups = result.scalars().all()

        # 构建返回数据
        results = []
        for s in startups:
            data = s.to_dict()

            # 如果需要包含分析数据
            if include_analysis:
                # 获取产品选品分析
                selection_result = await db.execute(
                    select(ProductSelectionAnalysis).where(ProductSelectionAnalysis.startup_id == s.id)
                )
                selection = selection_result.scalar_one_or_none()
                if selection:
                    data['selection_analysis'] = {
                        'individual_dev_suitability': selection.individual_dev_suitability,
                        'tech_complexity_level': selection.tech_complexity_level,
                        'ai_dependency_level': selection.ai_dependency_level,
                        'target_customer': selection.target_customer,
                        'product_stage': selection.product_stage,
                        'feature_complexity': selection.feature_complexity,
                        'startup_cost_level': selection.startup_cost_level,
                        'is_product_driven': selection.is_product_driven,
                        'is_small_and_beautiful': selection.is_small_and_beautiful,
                    }

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

            results.append(data)

        return results


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
    "Query startups from the database with comprehensive filters including category, revenue range, search terms, technical complexity, AI dependency, target customer type, product stage, and developer suitability. Returns detailed information about matching startups including revenue, analysis scores, and product characteristics. Use this to find products suitable for indie developers or specific technical requirements.",
    {
        "category": str,
        "min_revenue": float,
        "max_revenue": float,
        "search": str,
        "limit": int,
        "tech_complexity": str,  # low, medium, high
        "ai_dependency": str,  # none, light, heavy
        "target_customer": str,  # b2c, b2b_smb, b2b_enterprise, b2d
        "product_stage": str,  # early, growth, mature
        "min_suitability": float,  # 0-10
        "include_analysis": bool
    }
)
async def query_startups_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """MCP tool wrapper for query_startups with enhanced filtering"""
    try:
        result = await query_startups(
            category=args.get("category"),
            min_revenue=args.get("min_revenue"),
            max_revenue=args.get("max_revenue"),
            search=args.get("search"),
            limit=min(args.get("limit", 20), 100),  # Cap at 100
            tech_complexity=args.get("tech_complexity"),
            ai_dependency=args.get("ai_dependency"),
            target_customer=args.get("target_customer"),
            product_stage=args.get("product_stage"),
            min_suitability=args.get("min_suitability"),
            include_analysis=args.get("include_analysis", True)
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
