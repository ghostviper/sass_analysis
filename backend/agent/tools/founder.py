"""
创始人相关工具
"""

import json
from typing import Dict, Any
from sqlalchemy import select, desc

from database.db import AsyncSessionLocal
from database.models import Startup, Founder
from .decorator import tool
from .base import _build_product_profile


async def _get_founder_products(username: str) -> Dict[str, Any]:
    """获取开发者的所有产品及其完整分析数据"""
    async with AsyncSessionLocal() as db:
        founder_result = await db.execute(
            select(Founder).where(Founder.username == username)
        )
        founder = founder_result.scalar_one_or_none()

        products_result = await db.execute(
            select(Startup)
            .where(Startup.founder_username == username)
            .order_by(desc(Startup.revenue_30d))
        )
        products = products_result.scalars().all()

        if not products and not founder:
            return {"error": f"No founder or products found for username: {username}"}

        product_profiles = [await _build_product_profile(db, p) for p in products]

        total_revenue = sum(p.revenue_30d or 0 for p in products)
        categories = list(set(p.category for p in products if p.category))

        # 分析共同特征
        common_patterns = []
        if product_profiles:
            tech_levels = [p.get("analysis", {}).get("tech_complexity") for p in product_profiles if p.get("analysis")]
            if tech_levels and all(t == "low" for t in tech_levels if t):
                common_patterns.append("low_tech_complexity")
            
            customers = [p.get("analysis", {}).get("target_customer") for p in product_profiles if p.get("analysis")]
            if customers:
                most_common = max(set(c for c in customers if c), key=lambda x: customers.count(x)) if any(customers) else None
                if most_common:
                    common_patterns.append(f"focus_{most_common}")
            
            product_driven = [p.get("analysis", {}).get("is_product_driven") for p in product_profiles if p.get("analysis")]
            if product_driven and all(pd for pd in product_driven if pd is not None):
                common_patterns.append("product_driven")

        # 构建创始人社交媒体链接
        founder_social_url = None
        founder_username_val = username  # 使用传入的 username 参数
        
        # 优先从 Startup 获取社交平台信息
        if products and products[0].founder_username:
            founder_username_val = products[0].founder_username
            platform = (products[0].founder_social_platform or "").lower()
            if platform in ['x', 'x (twitter)', 'twitter', '𝕏']:
                founder_social_url = f"https://x.com/{founder_username_val}"
            elif 'linkedin' in platform:
                founder_social_url = f"https://linkedin.com/in/{founder_username_val}"
            else:
                # 默认使用 X
                founder_social_url = f"https://x.com/{founder_username_val}"
        elif founder:
            # 如果没有产品信息，从 Founder 表获取
            platform = (founder.social_platform or "").lower()
            if platform in ['x', 'x (twitter)', 'twitter', '𝕏']:
                founder_social_url = f"https://x.com/{founder.username}"
            elif 'linkedin' in platform:
                founder_social_url = f"https://linkedin.com/in/{founder.username}"
            else:
                founder_social_url = f"https://x.com/{founder.username}"

        return {
            "founder": {
                "username": founder_username_val,
                "name": founder.name if founder else (products[0].founder_name if products else None),
                "rank": founder.rank if founder else None,
                "followers": founder.followers if founder else (products[0].founder_followers if products else None),
                "social_url": founder_social_url,  # 社交媒体链接
            },
            "products": product_profiles,
            "portfolio_insights": {
                "total_products": len(products),
                "total_monthly_revenue": total_revenue,
                "avg_revenue_per_product": round(total_revenue / len(products), 2) if products else 0,
                "categories": categories,
                "common_patterns": common_patterns,
            }
        }


@tool(
    "get_founder_products",
    "Get all products owned by a specific founder/developer with full analysis data.",
    {
        "type": "object",
        "properties": {
            "username": {"type": "string", "description": "The founder's username (e.g., 'levelsio')"}
        },
        "required": ["username"]
    }
)
async def get_founder_products_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """获取创始人的产品"""
    import time as time_module
    import asyncio as aio

    start_time = time_module.time()
    username = args.get("username", "")

    print(f"[TOOL] get_founder_products called with username='{username}'", flush=True)

    if not username:
        return {
            "content": [{"type": "text", "text": json.dumps({"error": "No username provided"}, ensure_ascii=False)}],
            "is_error": True
        }

    try:
        result = await aio.wait_for(_get_founder_products(username), timeout=30.0)
        elapsed = time_module.time() - start_time

        if "error" in result:
            return {
                "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}],
                "is_error": True
            }

        print(f"[TOOL] get_founder_products completed in {elapsed:.2f}s", flush=True)
        return {"content": [{"type": "text", "text": json.dumps(result, indent=2, ensure_ascii=False)}]}

    except Exception as e:
        print(f"[TOOL] get_founder_products failed: {e}", flush=True)
        return {
            "content": [{"type": "text", "text": json.dumps({"error": str(e)}, ensure_ascii=False)}],
            "is_error": True
        }
