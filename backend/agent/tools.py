"""
Agent tools for querying and analyzing SaaS data
"""

import os
from typing import Optional, List, Dict, Any
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
import json
import httpx

from database.db import AsyncSessionLocal
from database.models import Startup, Founder

# Tavily API for web search
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

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
    ids: Optional[List[int]] = None,
    slugs: Optional[List[str]] = None,
    category: Optional[str] = None,
    min_revenue: Optional[float] = None,
    max_revenue: Optional[float] = None,
    search: Optional[str] = None,
    limit: int = 20,
) -> List[Dict[str, Any]]:
    """
    Query startups from the database with optional filters.
    
    Args:
        ids: List of startup IDs to query (exact match, highest priority)
        slugs: List of startup slugs to query (exact match)
        category: Filter by category (e.g., "AI", "SaaS", "Fintech")
        min_revenue: Minimum 30-day revenue
        max_revenue: Maximum 30-day revenue
        search: Search term for name/description (fuzzy match)
        limit: Maximum number of results
        
    Returns:
        List of startup dictionaries with their data
    """
    async with AsyncSessionLocal() as db:
        query = select(Startup)
        
        # 处理 ids 参数 - 可能是字符串 '[]' 或真正的列表
        if ids:
            # 如果是字符串，尝试解析
            if isinstance(ids, str):
                try:
                    ids = json.loads(ids) if ids.strip() not in ('', '[]') else None
                except:
                    ids = None
            # 确保是非空列表
            if ids and isinstance(ids, list) and len(ids) > 0:
                query = query.where(Startup.id.in_(ids))
                query = query.limit(limit)
                result = await db.execute(query)
                startups = result.scalars().all()
                return [s.to_dict() for s in startups]
        
        # 处理 slugs 参数
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
                return [s.to_dict() for s in startups]
        
        # 如果有 search 参数，优先使用模糊搜索，不要加其他限制条件
        # 这样可以避免因为 category 或 revenue 限制导致搜不到
        if search:
            pattern = f"%{search}%"
            query = query.where(
                (Startup.name.ilike(pattern)) | 
                (Startup.description.ilike(pattern)) |
                (Startup.slug.ilike(pattern))  # 也搜索 slug
            )
        else:
            # 只有在没有 search 时才应用其他过滤条件
            if category:
                query = query.where(Startup.category == category)
            if min_revenue is not None and min_revenue > 0:
                query = query.where(Startup.revenue_30d >= min_revenue)
            if max_revenue is not None:
                query = query.where(Startup.revenue_30d <= max_revenue)
        
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
# 原子化的底层查询函数
# ============================================================================

async def _get_startups_by_ids(ids: List[int]) -> List[Dict[str, Any]]:
    """通过 ID 列表精确查询产品"""
    async with AsyncSessionLocal() as db:
        query = select(Startup).where(Startup.id.in_(ids))
        result = await db.execute(query)
        startups = result.scalars().all()
        return [s.to_dict() for s in startups]


async def _search_startups(keyword: str, limit: int = 20) -> List[Dict[str, Any]]:
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
        return [s.to_dict() for s in startups]


async def _browse_startups(
    category: Optional[str] = None,
    min_revenue: Optional[float] = None,
    max_revenue: Optional[float] = None,
    limit: int = 20
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
        return [s.to_dict() for s in startups]


# ============================================================================
# MCP Tools - 原子化工具定义
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
    """通过 ID 查询产品 - 最精确的方式"""
    import time as time_module
    import asyncio as aio
    
    start_time = time_module.time()
    ids = args.get("ids", [])
    
    # 处理可能的字符串格式
    if isinstance(ids, str):
        try:
            ids = json.loads(ids)
        except:
            ids = []
    
    print(f"[TOOL] get_startups_by_ids called with ids={ids}", flush=True)
    
    if not ids:
        return {
            "content": [{"type": "text", "text": json.dumps({"error": "No IDs provided", "type": "invalid_input"}, ensure_ascii=False)}],
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
            "keyword": {
                "type": "string",
                "description": "Search keyword for product name or description"
            },
            "limit": {
                "type": "integer",
                "description": "Maximum results. Default: 20"
            }
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
    
    print(f"[TOOL] search_startups called with keyword='{keyword}', limit={limit}", flush=True)
    
    if not keyword:
        return {
            "content": [{"type": "text", "text": json.dumps({"error": "No keyword provided", "type": "invalid_input"}, ensure_ascii=False)}],
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
    "Browse startups with filters. Use this when exploring products by category or revenue range.",
    {
        "type": "object",
        "properties": {
            "category": {
                "type": "string",
                "description": "Filter by category (e.g., 'AI', 'SaaS', 'Fintech')"
            },
            "min_revenue": {
                "type": "number",
                "description": "Minimum 30-day revenue"
            },
            "max_revenue": {
                "type": "number",
                "description": "Maximum 30-day revenue"
            },
            "limit": {
                "type": "integer",
                "description": "Maximum results. Default: 20"
            }
        }
    }
)
async def browse_startups_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """浏览筛选产品"""
    import time as time_module
    import asyncio as aio
    
    start_time = time_module.time()
    print(f"[TOOL] browse_startups called with args={args}", flush=True)
    
    try:
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


# ============================================================================
# Web Search Tool (Tavily API)
# ============================================================================

async def _tavily_search(
    query: str,
    search_depth: str = "basic",
    include_domains: Optional[List[str]] = None,
    max_results: int = 5
) -> Dict[str, Any]:
    """
    Search the web using Tavily API.
    
    Args:
        query: Search query
        search_depth: "basic" or "advanced" (advanced is slower but more thorough)
        include_domains: Limit search to specific domains (e.g., ["reddit.com", "indiehackers.com"])
        max_results: Maximum number of results to return
        
    Returns:
        Search results with title, url, content, and score
    """
    if not TAVILY_API_KEY:
        return {"error": "TAVILY_API_KEY not configured", "results": []}
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        payload = {
            "api_key": TAVILY_API_KEY,
            "query": query,
            "search_depth": search_depth,
            "max_results": max_results,
            "include_answer": True,  # Get AI-generated answer summary
        }
        
        if include_domains:
            payload["include_domains"] = include_domains
        
        try:
            response = await client.post(
                "https://api.tavily.com/search",
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"Tavily API error: {e.response.status_code}", "results": []}
        except Exception as e:
            return {"error": str(e), "results": []}


@tool(
    "web_search",
    "Search the web for information about products, market trends, community discussions, reviews, and recent news. Use this when you need real-time information beyond the database.",
    {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query. Be specific and include relevant keywords."
            },
            "search_depth": {
                "type": "string",
                "enum": ["basic", "advanced"],
                "description": "Search depth. 'basic' is faster, 'advanced' is more thorough. Default: basic"
            },
            "include_domains": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Limit search to specific domains. E.g., ['reddit.com', 'indiehackers.com', 'producthunt.com']"
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of results. Default: 5, Max: 10"
            }
        },
        "required": ["query"]
    }
)
async def web_search_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """Search the web using Tavily API"""
    import time as time_module
    import asyncio as aio
    
    start_time = time_module.time()
    query = args.get("query", "")
    search_depth = args.get("search_depth", "basic")
    include_domains = args.get("include_domains")
    max_results = min(args.get("max_results", 5), 10)
    
    print(f"[TOOL] web_search called with query='{query[:50]}...', depth={search_depth}", flush=True)
    
    if not query:
        return {
            "content": [{"type": "text", "text": json.dumps({"error": "No query provided"}, ensure_ascii=False)}],
            "is_error": True
        }
    
    if not TAVILY_API_KEY:
        return {
            "content": [{"type": "text", "text": json.dumps({
                "error": "Web search is not configured. Please set TAVILY_API_KEY in environment variables.",
                "hint": "Get your API key from https://tavily.com"
            }, ensure_ascii=False)}],
            "is_error": True
        }
    
    try:
        result = await aio.wait_for(
            _tavily_search(query, search_depth, include_domains, max_results),
            timeout=30.0
        )
        elapsed = time_module.time() - start_time
        
        # Format results for better readability
        if "results" in result:
            formatted_results = []
            for r in result.get("results", []):
                formatted_results.append({
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "content": r.get("content", "")[:500],  # Truncate long content
                    "score": r.get("score", 0)
                })
            
            output = {
                "answer": result.get("answer", ""),  # AI-generated summary
                "results": formatted_results,
                "query": query,
                "search_time_ms": int(elapsed * 1000)
            }
        else:
            output = result
        
        print(f"[TOOL] web_search completed in {elapsed:.2f}s, returned {len(result.get('results', []))} results", flush=True)
        return {"content": [{"type": "text", "text": json.dumps(output, indent=2, ensure_ascii=False)}]}
        
    except asyncio.TimeoutError:
        return {
            "content": [{"type": "text", "text": json.dumps({"error": "Search timed out"}, ensure_ascii=False)}],
            "is_error": True
        }
    except Exception as e:
        print(f"[TOOL] web_search failed: {e}", flush=True)
        return {
            "content": [{"type": "text", "text": json.dumps({"error": str(e)}, ensure_ascii=False)}],
            "is_error": True
        }
