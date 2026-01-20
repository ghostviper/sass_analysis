#!/usr/bin/env python3
"""
Template Preview Script (Standalone Version)

Preview products that match a template's filter rules using backend API.
"""

import os
import sys
import argparse
import asyncio
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
script_dir = Path(__file__).parent
skill_dir = script_dir.parent
backend_dir = skill_dir.parent.parent
env_path = backend_dir / ".env"
load_dotenv(env_path)

# Import local API client
from api_client import BackendAPIClient


async def preview_template(
    template_key: str,
    filter_rules: Dict[str, Any],
    limit: int = 10,
    api_url: str = "http://localhost:8001"
):
    """Preview products matching template"""
    
    async with BackendAPIClient(base_url=api_url) as api:
        result = await api.preview_template(filter_rules, limit=limit)
        
        products = result.get("products", [])
        total = result.get("total_matches", 0)
        
        print(f"📊 Found {total} products matching template: {template_key}")
        print()
        
        for i, product in enumerate(products, 1):
            print(f"{i}. {product['name']}")
            print(f"   Revenue: ${product['revenue_30d']:,}/mo" if product['revenue_30d'] else "   Revenue: N/A")
            print(f"   Followers: {product['founder_followers']:,}" if product['founder_followers'] else "   Followers: N/A")
            print(f"   Team: {product['team_size']}" if product['team_size'] else "   Team: N/A")
            print(f"   Category: {product['category']}" if product['category'] else "   Category: N/A")
            print(f"   Website: {product['website_url']}" if product.get('website_url') else "   Website: N/A")
            print()
        
        return total


async def main():
    parser = argparse.ArgumentParser(description="Preview template matches")
    parser.add_argument("--template-key", "-k", required=True, help="Template key to preview")
    parser.add_argument("--filter-rules", "-f", required=True, help="Filter rules JSON file")
    parser.add_argument("--limit", "-l", type=int, default=10, help="Max products to show")
    parser.add_argument("--api-url", default="http://localhost:8001", help="Backend API URL")
    
    args = parser.parse_args()
    
    # Load filter rules from file
    filter_file = Path(args.filter_rules)
    if not filter_file.exists():
        print(f"❌ Filter rules file not found: {filter_file}", file=sys.stderr)
        sys.exit(1)
    
    import json
    with open(filter_file, 'r', encoding='utf-8') as f:
        filter_rules = json.load(f)
    
    print(f"🔍 Preview template: {args.template_key}")
    print(f"🔗 API URL: {args.api_url}")
    print()
    
    try:
        await preview_template(
            template_key=args.template_key,
            filter_rules=filter_rules,
            limit=args.limit,
            api_url=args.api_url
        )
    except Exception as e:
        print(f"❌ Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
