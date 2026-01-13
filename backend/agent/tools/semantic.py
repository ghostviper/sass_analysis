"""
语义搜索工具 - 基于向量检索
"""

import json
from typing import Dict, Any

from .decorator import tool
from .base import _get_startups_by_ids

# 懒加载向量服务
_vector_store = None


def _get_vector_store():
    """懒加载向量存储服务"""
    global _vector_store
    if _vector_store is None:
        from services.vector_store import vector_store
        _vector_store = vector_store
    return _vector_store


@tool(
    "semantic_search_products",
    "Search products using natural language. Use this when the user describes what they're looking for, or when keyword search doesn't find good results.",
    {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Natural language query. E.g., 'tools for designers to manage assets'"
            },
            "limit": {"type": "integer", "description": "Maximum results. Default: 10"},
            "category": {"type": "string", "description": "Optional: filter by category"},
            "min_revenue": {"type": "number", "description": "Optional: minimum 30-day revenue"}
        },
        "required": ["query"]
    }
)
async def semantic_search_products_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """语义搜索产品"""
    import time as time_module
    
    start_time = time_module.time()
    query = args.get("query", "")
    limit = min(args.get("limit", 10), 50)
    category = args.get("category")
    min_revenue = args.get("min_revenue")
    
    print(f"[TOOL] semantic_search_products called with query='{query[:50]}...'", flush=True)
    
    if not query:
        return {
            "content": [{"type": "text", "text": json.dumps({"error": "No query provided"}, ensure_ascii=False)}],
            "is_error": True
        }
    
    vs = _get_vector_store()
    if not vs.enabled:
        return {
            "content": [{"type": "text", "text": json.dumps({
                "error": "Semantic search not configured. Set PINECONE_API_KEY.",
                "fallback": "Use search_startups tool instead."
            }, ensure_ascii=False)}],
            "is_error": True
        }
    
    try:
        # 构建过滤条件
        filter_dict = {}
        if category:
            filter_dict["category"] = {"$eq": category}
        if min_revenue:
            filter_dict["revenue_30d"] = {"$gte": min_revenue}
        
        # 执行语义搜索
        results = await vs.search(
            query=query,
            namespace="products",
            top_k=limit,
            filter=filter_dict if filter_dict else None
        )
        
        elapsed = time_module.time() - start_time
        
        # 提取 startup_ids
        startup_ids = []
        score_map = {}
        for r in results:
            sid = r["metadata"].get("startup_id")
            if sid:
                startup_ids.append(sid)
                score_map[sid] = r["score"]
        
        # 获取完整产品数据
        if startup_ids:
            products = await _get_startups_by_ids(startup_ids, include_full_profile=True)
            for p in products:
                p["similarity_score"] = round(score_map.get(p["id"], 0), 4)
            products.sort(key=lambda x: x.get("similarity_score", 0), reverse=True)
        else:
            products = []
        
        print(f"[TOOL] semantic_search_products completed in {elapsed:.2f}s, returned {len(products)} items", flush=True)
        
        return {
            "content": [{
                "type": "text",
                "text": json.dumps({
                    "query": query,
                    "results": products,
                    "count": len(products),
                    "search_time_ms": int(elapsed * 1000)
                }, indent=2, ensure_ascii=False)
            }]
        }
        
    except Exception as e:
        print(f"[TOOL] semantic_search_products failed: {e}", flush=True)
        return {
            "content": [{"type": "text", "text": json.dumps({"error": str(e)}, ensure_ascii=False)}],
            "is_error": True
        }


@tool(
    "find_similar_products",
    "Find products similar to a given product. Use for competitive analysis or 'more like this' recommendations.",
    {
        "type": "object",
        "properties": {
            "product_id": {"type": "integer", "description": "The startup ID to find similar products for"},
            "limit": {"type": "integer", "description": "Maximum results. Default: 5"}
        },
        "required": ["product_id"]
    }
)
async def find_similar_products_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """找相似产品"""
    import time as time_module
    
    start_time = time_module.time()
    product_id = args.get("product_id")
    limit = min(args.get("limit", 5), 20)
    
    print(f"[TOOL] find_similar_products called with product_id={product_id}", flush=True)
    
    if not product_id:
        return {
            "content": [{"type": "text", "text": json.dumps({"error": "No product_id provided"}, ensure_ascii=False)}],
            "is_error": True
        }
    
    vs = _get_vector_store()
    if not vs.enabled:
        return {
            "content": [{"type": "text", "text": json.dumps({"error": "Semantic search not configured."}, ensure_ascii=False)}],
            "is_error": True
        }
    
    try:
        # 获取目标产品信息
        source_products = await _get_startups_by_ids([product_id], include_full_profile=True)
        if not source_products:
            return {
                "content": [{"type": "text", "text": json.dumps({"error": f"Product {product_id} not found"}, ensure_ascii=False)}],
                "is_error": True
            }
        
        source = source_products[0]
        
        # 构建查询文本
        query_parts = [f"产品: {source['name']}"]
        if source.get("description"):
            query_parts.append(f"描述: {source['description']}")
        if source.get("category"):
            query_parts.append(f"类目: {source['category']}")
        if source.get("landing", {}).get("core_features"):
            features = source["landing"]["core_features"][:3]
            if features:
                query_parts.append(f"功能: {', '.join(features)}")
        
        query_text = "\n".join(query_parts)
        
        # 搜索相似产品
        results = await vs.search(
            query=query_text,
            namespace="products",
            top_k=limit + 1
        )
        
        # 过滤掉自己
        startup_ids = []
        score_map = {}
        for r in results:
            sid = r["metadata"].get("startup_id")
            if sid and sid != product_id:
                startup_ids.append(sid)
                score_map[sid] = r["score"]
        
        startup_ids = startup_ids[:limit]
        
        # 获取完整数据
        if startup_ids:
            products = await _get_startups_by_ids(startup_ids, include_full_profile=True)
            for p in products:
                p["similarity_score"] = round(score_map.get(p["id"], 0), 4)
            products.sort(key=lambda x: x.get("similarity_score", 0), reverse=True)
        else:
            products = []
        
        elapsed = time_module.time() - start_time
        print(f"[TOOL] find_similar_products completed in {elapsed:.2f}s, returned {len(products)} items", flush=True)
        
        return {
            "content": [{
                "type": "text",
                "text": json.dumps({
                    "source_product": {"id": source["id"], "name": source["name"]},
                    "similar_products": products,
                    "count": len(products)
                }, indent=2, ensure_ascii=False)
            }]
        }
        
    except Exception as e:
        print(f"[TOOL] find_similar_products failed: {e}", flush=True)
        return {
            "content": [{"type": "text", "text": json.dumps({"error": str(e)}, ensure_ascii=False)}],
            "is_error": True
        }


@tool(
    "semantic_search_categories",
    "Search categories/tracks using natural language. Use when user asks about market segments or industry verticals.",
    {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Natural language query. E.g., 'categories suitable for solo developers', 'AI related segments'"
            },
            "limit": {"type": "integer", "description": "Maximum results. Default: 5"}
        },
        "required": ["query"]
    }
)
async def semantic_search_categories_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """语义搜索赛道"""
    import time as time_module
    
    start_time = time_module.time()
    query = args.get("query", "")
    limit = min(args.get("limit", 5), 20)
    
    print(f"[TOOL] semantic_search_categories called with query='{query[:50]}...'", flush=True)
    
    if not query:
        return {
            "content": [{"type": "text", "text": json.dumps({"error": "No query provided"}, ensure_ascii=False)}],
            "is_error": True
        }
    
    vs = _get_vector_store()
    if not vs.enabled:
        return {
            "content": [{"type": "text", "text": json.dumps({
                "error": "Semantic search not configured.",
                "fallback": "Use get_category_analysis tool instead."
            }, ensure_ascii=False)}],
            "is_error": True
        }
    
    try:
        results = await vs.search(
            query=query,
            namespace="categories",
            top_k=limit
        )
        
        elapsed = time_module.time() - start_time
        
        # 格式化结果
        categories = []
        for r in results:
            meta = r["metadata"]
            categories.append({
                "category": meta.get("category"),
                "market_type": meta.get("market_type"),
                "total_projects": meta.get("total_projects"),
                "total_revenue": meta.get("total_revenue"),
                "median_revenue": meta.get("median_revenue"),
                "gini_coefficient": meta.get("gini_coefficient"),
                "similarity_score": round(r["score"], 4)
            })
        
        print(f"[TOOL] semantic_search_categories completed in {elapsed:.2f}s, returned {len(categories)} items", flush=True)
        
        return {
            "content": [{
                "type": "text",
                "text": json.dumps({
                    "query": query,
                    "results": categories,
                    "count": len(categories),
                    "search_time_ms": int(elapsed * 1000)
                }, indent=2, ensure_ascii=False)
            }]
        }
        
    except Exception as e:
        print(f"[TOOL] semantic_search_categories failed: {e}", flush=True)
        return {
            "content": [{"type": "text", "text": json.dumps({"error": str(e)}, ensure_ascii=False)}],
            "is_error": True
        }



@tool(
    "discover_products_by_scenario",
    "Discover products based on a scenario description. Combines semantic search with structured filters for scenario-based product discovery.",
    {
        "type": "object",
        "properties": {
            "scenario": {
                "type": "string",
                "description": "Describe the scenario or use case. E.g., 'I want to build a tool for freelancers to manage invoices'"
            },
            "target_customer": {
                "type": "string",
                "enum": ["b2c", "b2b_smb", "b2b_enterprise", "b2d"],
                "description": "Optional: target customer type"
            },
            "tech_complexity": {
                "type": "string",
                "enum": ["low", "medium", "high"],
                "description": "Optional: preferred technical complexity"
            },
            "max_revenue": {
                "type": "number",
                "description": "Optional: max revenue (to find smaller opportunities)"
            },
            "limit": {"type": "integer", "description": "Maximum results. Default: 10"}
        },
        "required": ["scenario"]
    }
)
async def discover_products_by_scenario_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """场景化产品发现"""
    import time as time_module
    
    start_time = time_module.time()
    scenario = args.get("scenario", "")
    target_customer = args.get("target_customer")
    tech_complexity = args.get("tech_complexity")
    max_revenue = args.get("max_revenue")
    limit = min(args.get("limit", 10), 30)
    
    print(f"[TOOL] discover_products_by_scenario called with scenario='{scenario[:50]}...'", flush=True)
    
    if not scenario:
        return {
            "content": [{"type": "text", "text": json.dumps({"error": "No scenario provided"}, ensure_ascii=False)}],
            "is_error": True
        }
    
    vs = _get_vector_store()
    if not vs.enabled:
        return {
            "content": [{"type": "text", "text": json.dumps({
                "error": "Semantic search not configured.",
                "fallback": "Use browse_startups or semantic_search_products instead."
            }, ensure_ascii=False)}],
            "is_error": True
        }
    
    try:
        # 构建过滤条件
        filter_dict = {}
        if target_customer:
            filter_dict["target_customer"] = {"$eq": target_customer}
        if tech_complexity:
            filter_dict["tech_complexity"] = {"$eq": tech_complexity}
        if max_revenue:
            filter_dict["revenue_30d"] = {"$lte": max_revenue}
        
        # 语义搜索
        results = await vs.search(
            query=scenario,
            namespace="products",
            top_k=limit * 2,  # 多取一些，后面过滤
            filter=filter_dict if filter_dict else None
        )
        
        # 提取 startup_ids
        startup_ids = []
        score_map = {}
        for r in results:
            sid = r["metadata"].get("startup_id")
            if sid:
                startup_ids.append(sid)
                score_map[sid] = r["score"]
        
        startup_ids = startup_ids[:limit]
        
        # 获取完整产品数据
        if startup_ids:
            products = await _get_startups_by_ids(startup_ids, include_full_profile=True)
            for p in products:
                p["relevance_score"] = round(score_map.get(p["id"], 0), 4)
            products.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        else:
            products = []
        
        elapsed = time_module.time() - start_time
        print(f"[TOOL] discover_products_by_scenario completed in {elapsed:.2f}s, returned {len(products)} items", flush=True)
        
        # 生成场景洞察
        insights = {
            "scenario": scenario,
            "filters_applied": {
                "target_customer": target_customer,
                "tech_complexity": tech_complexity,
                "max_revenue": max_revenue
            },
            "results_count": len(products),
            "search_time_ms": int(elapsed * 1000)
        }
        
        # 分析结果特征
        if products:
            categories = [p.get("category") for p in products if p.get("category")]
            if categories:
                from collections import Counter
                top_categories = Counter(categories).most_common(3)
                insights["top_categories"] = [{"name": c, "count": n} for c, n in top_categories]
            
            avg_revenue = sum(p.get("revenue_30d", 0) or 0 for p in products) / len(products)
            insights["avg_revenue"] = round(avg_revenue, 2)
        
        return {
            "content": [{
                "type": "text",
                "text": json.dumps({
                    "insights": insights,
                    "products": products
                }, indent=2, ensure_ascii=False)
            }]
        }
        
    except Exception as e:
        print(f"[TOOL] discover_products_by_scenario failed: {e}", flush=True)
        return {
            "content": [{"type": "text", "text": json.dumps({"error": str(e)}, ensure_ascii=False)}],
            "is_error": True
        }
