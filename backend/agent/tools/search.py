"""
Web 搜索工具 - Tavily API
"""

import os
import json
import asyncio
from typing import Optional, List, Dict, Any
import httpx

from .decorator import tool

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


async def _tavily_search(
    query: str,
    search_depth: str = "basic",
    include_domains: Optional[List[str]] = None,
    max_results: int = 5
) -> Dict[str, Any]:
    """Search the web using Tavily API"""
    if not TAVILY_API_KEY:
        return {"error": "TAVILY_API_KEY not configured", "results": []}
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        payload = {
            "api_key": TAVILY_API_KEY,
            "query": query,
            "search_depth": search_depth,
            "max_results": max_results,
            "include_answer": True,
        }
        
        if include_domains:
            payload["include_domains"] = include_domains
        
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
    "Search the web for information about products, market trends, community discussions, reviews, and recent news.",
    {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query"},
            "search_depth": {
                "type": "string",
                "enum": ["basic", "advanced"],
                "description": "Search depth. Default: basic"
            },
            "include_domains": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Limit to specific domains. E.g., ['reddit.com', 'indiehackers.com']"
            },
            "max_results": {"type": "integer", "description": "Maximum results. Default: 5"}
        },
        "required": ["query"]
    }
)
async def web_search_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """Web 搜索"""
    import time as time_module
    
    start_time = time_module.time()
    query = args.get("query", "")
    search_depth = args.get("search_depth", "basic")
    include_domains = args.get("include_domains")
    max_results = min(args.get("max_results", 5), 10)
    
    print(f"[TOOL] web_search called with query='{query[:50]}...'", flush=True)
    
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
            _tavily_search(query, search_depth, include_domains, max_results),
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
                    "score": r.get("score", 0)
                })
            
            output = {
                "answer": result.get("answer", ""),
                "results": formatted_results,
                "query": query,
                "search_time_ms": int(elapsed * 1000)
            }
        else:
            output = result
        
        print(f"[TOOL] web_search completed in {elapsed:.2f}s", flush=True)
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
