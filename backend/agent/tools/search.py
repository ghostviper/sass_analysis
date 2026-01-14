"""
Web 搜索工具 - Tavily API

支持精准信息源过滤，可通过预设域名组或自定义域名列表限定搜索范围。
"""

import os
import json
import asyncio
from typing import Optional, List, Dict, Any
import httpx

from .decorator import tool

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# 预定义的可信信息源组
DOMAIN_PRESETS: Dict[str, List[str]] = {
    # 独立开发者社区 - 适合产品灵感、收入案例、独立开发经验
    "indie": [
        "indiehackers.com",
        "reddit.com/r/SideProject",
        "reddit.com/r/startups",
        "reddit.com/r/Entrepreneur",
        "reddit.com/r/SaaS",
        "producthunt.com",
    ],
    # 技术新闻 - 适合行业动态、融资新闻、产品发布
    "tech_news": [
        "news.ycombinator.com",
        "techcrunch.com",
        "theverge.com",
        "wired.com",
        "arstechnica.com",
    ],
    # 开发者社区 - 适合技术讨论、最佳实践、问题解答
    "dev_community": [
        "reddit.com/r/webdev",
        "reddit.com/r/programming",
        "reddit.com/r/javascript",
        "reddit.com/r/Python",
        "dev.to",
        "stackoverflow.com",
        "github.com",
    ],
    # 产品评测 - 适合竞品分析、用户反馈、市场定位
    "product_reviews": [
        "g2.com",
        "capterra.com",
        "trustpilot.com",
        "getapp.com",
        "softwareadvice.com",
    ],
    # AI/ML 领域 - 适合 AI 产品、模型、工具相关搜索
    "ai_ml": [
        "huggingface.co",
        "reddit.com/r/MachineLearning",
        "reddit.com/r/LocalLLaMA",
        "arxiv.org",
        "paperswithcode.com",
    ],
}


async def _tavily_search(
    query: str,
    search_depth: str = "basic",
    include_domains: Optional[List[str]] = None,
    exclude_domains: Optional[List[str]] = None,
    time_range: Optional[str] = None,
    topic: str = "general",
    max_results: int = 5
) -> Dict[str, Any]:
    """
    Search the web using Tavily API
    
    Args:
        query: 搜索查询
        search_depth: 搜索深度 (basic/advanced)
        include_domains: 限定搜索的域名列表 (最多300个)
        exclude_domains: 排除的域名列表 (最多150个)
        time_range: 时间范围 (day/week/month/year)
        topic: 搜索主题 (general/news/finance)
        max_results: 最大结果数
    """
    if not TAVILY_API_KEY:
        return {"error": "TAVILY_API_KEY not configured", "results": []}
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        payload = {
            "api_key": TAVILY_API_KEY,
            "query": query,
            "search_depth": search_depth,
            "topic": topic,
            "max_results": max_results,
            "include_answer": True,
        }
        
        if include_domains:
            payload["include_domains"] = include_domains[:300]  # API 限制
        
        if exclude_domains:
            payload["exclude_domains"] = exclude_domains[:150]  # API 限制
        
        if time_range and time_range in ("day", "week", "month", "year"):
            payload["time_range"] = time_range
        
        try:
            response = await client.post("https://api.tavily.com/search", json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"Tavily API error: {e.response.status_code}", "results": []}
        except Exception as e:
            return {"error": str(e), "results": []}


@tool(
    "web_search",
    """Search the web for information with precise source filtering.

Use domain_preset for common scenarios:
- "indie": IndieHackers, Reddit (SideProject/startups/SaaS), ProductHunt - for indie dev insights, revenue cases
- "tech_news": HackerNews, TechCrunch, TheVerge - for industry news, funding, launches
- "dev_community": Reddit dev subs, dev.to, StackOverflow, GitHub - for technical discussions
- "product_reviews": G2, Capterra, Trustpilot - for competitor analysis, user feedback
- "ai_ml": HuggingFace, Reddit ML subs, arXiv - for AI/ML products and research

Or use include_domains for custom domain filtering.""",
    {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query - be specific for better results"
            },
            "domain_preset": {
                "type": "string",
                "enum": ["indie", "tech_news", "dev_community", "product_reviews", "ai_ml"],
                "description": "Predefined trusted domain group. Choose based on query intent."
            },
            "include_domains": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Custom domains to search (overrides preset). E.g., ['reddit.com', 'indiehackers.com']"
            },
            "exclude_domains": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Domains to exclude from results. E.g., ['medium.com', 'pinterest.com']"
            },
            "time_range": {
                "type": "string",
                "enum": ["day", "week", "month", "year"],
                "description": "Limit to recent content. Use for time-sensitive queries."
            },
            "topic": {
                "type": "string",
                "enum": ["general", "news", "finance"],
                "description": "Search topic type. Use 'news' for recent events, 'finance' for financial data."
            },
            "search_depth": {
                "type": "string",
                "enum": ["basic", "advanced"],
                "description": "Search depth. 'advanced' for more thorough results. Default: basic"
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum results (1-10). Default: 5"
            }
        },
        "required": ["query"]
    }
)
async def web_search_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """Web 搜索 - 支持精准信息源过滤"""
    import time as time_module
    
    start_time = time_module.time()
    query = args.get("query", "")
    domain_preset = args.get("domain_preset")
    include_domains = args.get("include_domains")
    exclude_domains = args.get("exclude_domains")
    time_range = args.get("time_range")
    topic = args.get("topic", "general")
    search_depth = args.get("search_depth", "basic")
    max_results = min(args.get("max_results", 5), 10)
    
    # 处理域名过滤：自定义域名优先，否则使用预设
    effective_domains = None
    domain_source = None
    
    if include_domains:
        effective_domains = include_domains
        domain_source = "custom"
    elif domain_preset and domain_preset in DOMAIN_PRESETS:
        effective_domains = DOMAIN_PRESETS[domain_preset]
        domain_source = f"preset:{domain_preset}"
    
    # 日志
    log_parts = [f"query='{query[:50]}...'"]
    if domain_source:
        log_parts.append(f"domains={domain_source}")
    if time_range:
        log_parts.append(f"time={time_range}")
    print(f"[TOOL] web_search called with {', '.join(log_parts)}", flush=True)
    
    if not query:
        return {
            "content": [{"type": "text", "text": json.dumps({"error": "No query provided"}, ensure_ascii=False)}],
            "is_error": True
        }
    
    if not TAVILY_API_KEY:
        return {
            "content": [{"type": "text", "text": json.dumps({
                "error": "Web search not configured. Set TAVILY_API_KEY.",
            }, ensure_ascii=False)}],
            "is_error": True
        }
    
    try:
        result = await asyncio.wait_for(
            _tavily_search(
                query=query,
                search_depth=search_depth,
                include_domains=effective_domains,
                exclude_domains=exclude_domains,
                time_range=time_range,
                topic=topic,
                max_results=max_results
            ),
            timeout=30.0
        )
        elapsed = time_module.time() - start_time
        
        if "results" in result:
            formatted_results = []
            for r in result.get("results", []):
                formatted_results.append({
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "content": r.get("content", "")[:500],
                    "score": r.get("score", 0),
                    "published_date": r.get("published_date", ""),
                })
            
            output = {
                "answer": result.get("answer", ""),
                "results": formatted_results,
                "query": query,
                "search_time_ms": int(elapsed * 1000),
                "filters_applied": {
                    "domains": domain_source,
                    "time_range": time_range,
                    "topic": topic,
                }
            }
        else:
            output = result
        
        print(f"[TOOL] web_search completed in {elapsed:.2f}s, {len(result.get('results', []))} results", flush=True)
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
