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
    # ============ 创业与独立开发 ============
    # 独立开发者社区 - 产品灵感、收入案例、独立开发经验
    "indie": [
        "indiehackers.com",
        "producthunt.com",
        "betalist.com",
        "microconf.com",
        "barnacl.es",  # bootstrapped startups
        # Reddit 创业相关
        "reddit.com/r/SideProject",
        "reddit.com/r/startups",
        "reddit.com/r/Entrepreneur",
        "reddit.com/r/SaaS",
        "reddit.com/r/microsaas",
        "reddit.com/r/micro_saas",
        "reddit.com/r/indiebiz",
        "reddit.com/r/indiehackers",
        "reddit.com/r/IndieDev",
        "reddit.com/r/SoloDevelopment",
        "reddit.com/r/smallbusiness",
        "reddit.com/r/EntrepreneurRideAlong",
        "reddit.com/r/nocode",
        # 其他社区
        "news.ycombinator.com",
        "lobste.rs",
    ],
    
    # 创业融资与商业 - VC、融资、商业模式
    "startup_business": [
        "techcrunch.com",
        "crunchbase.com",
        "pitchbook.com",
        "saastr.com",
        "openviewpartners.com",
        "tomtunguz.com",
        "bothsidesofthetable.com",
        "avc.com",
        "firstround.com/review",
        "a]6z.com",
        "sequoiacap.com",
        "ycombinator.com/library",
        "paulgraham.com",
    ],
    
    # ============ 技术与开发 ============
    # 技术新闻 - 行业动态、产品发布、技术趋势
    "tech_news": [
        "news.ycombinator.com",
        "techcrunch.com",
        "theverge.com",
        "wired.com",
        "arstechnica.com",
        "thenextweb.com",
        "venturebeat.com",
        "zdnet.com",
        "engadget.com",
        "gizmodo.com",
        "mashable.com",
        "cnet.com",
    ],
    
    # 开发者社区 - 技术讨论、最佳实践、问题解答
    "dev_community": [
        "dev.to",
        "stackoverflow.com",
        "github.com",
        "hashnode.dev",
        "lobste.rs",
        "news.ycombinator.com",
        # Reddit 开发相关
        "reddit.com/r/webdev",
        "reddit.com/r/programming",
        "reddit.com/r/javascript",
        "reddit.com/r/reactjs",
        "reddit.com/r/node",
        "reddit.com/r/Python",
        "reddit.com/r/golang",
        "reddit.com/r/rust",
        "reddit.com/r/typescript",
        "reddit.com/r/nextjs",
        "reddit.com/r/sveltejs",
        "reddit.com/r/vuejs",
        "reddit.com/r/django",
        "reddit.com/r/flask",
        "reddit.com/r/FastAPI",
        "reddit.com/r/FullStack",
    ],
    
    # 官方文档与教程 - 权威技术资料
    "official_docs": [
        "docs.github.com",
        "developer.mozilla.org",
        "docs.python.org",
        "nodejs.org",
        "react.dev",
        "vuejs.org",
        "svelte.dev",
        "nextjs.org",
        "vercel.com/docs",
        "docs.aws.amazon.com",
        "cloud.google.com/docs",
        "docs.microsoft.com",
        "supabase.com/docs",
        "planetscale.com/docs",
        "stripe.com/docs",
    ],
    
    # ============ AI/ML 领域 ============
    # AI/ML 综合 - AI 产品、模型、工具、研究
    "ai_ml": [
        "huggingface.co",
        "openai.com",
        "anthropic.com",
        "deepmind.com",
        "arxiv.org",
        "paperswithcode.com",
        "ai.googleblog.com",
        "openai.com/blog",
        "lilianweng.github.io",
        "jalammar.github.io",
        "distill.pub",
        # Reddit AI 相关
        "reddit.com/r/MachineLearning",
        "reddit.com/r/LocalLLaMA",
        "reddit.com/r/artificial",
        "reddit.com/r/ChatGPT",
        "reddit.com/r/ClaudeAI",
        "reddit.com/r/singularity",
        "reddit.com/r/StableDiffusion",
        "reddit.com/r/comfyui",
        "reddit.com/r/reinforcementlearning",
    ],
    
    # AI 工具与应用 - AI SaaS、工具评测
    "ai_tools": [
        "theresanaiforthat.com",
        "futuretools.io",
        "aitools.fyi",
        "toolify.ai",
        "producthunt.com",
        "reddit.com/r/ChatGPTPro",
        "reddit.com/r/OpenAI",
        "reddit.com/r/midjourney",
    ],
    
    # ============ 产品与市场 ============
    # 产品评测 - 竞品分析、用户反馈、市场定位
    "product_reviews": [
        "g2.com",
        "capterra.com",
        "trustpilot.com",
        "getapp.com",
        "softwareadvice.com",
        "trustradius.com",
        "sourceforge.net",
        "alternativeto.net",
        "slant.co",
        "saasworthy.com",
        "crozdesk.com",
    ],
    
    # 产品设计与 UX - 设计灵感、用户体验
    "design_ux": [
        "dribbble.com",
        "behance.net",
        "uxdesign.cc",
        "smashingmagazine.com",
        "nngroup.com",
        "lawsofux.com",
        "mobbin.com",
        "pageflows.com",
        "reddit.com/r/userexperience",
        "reddit.com/r/UI_Design",
        "reddit.com/r/web_design",
    ],
    
    # 营销与增长 - SEO、内容营销、增长策略
    "marketing_growth": [
        "backlinko.com",
        "neilpatel.com",
        "moz.com",
        "ahrefs.com/blog",
        "semrush.com/blog",
        "hubspot.com/blog",
        "growthhackers.com",
        "cxl.com",
        "copyblogger.com",
        "reddit.com/r/marketing",
        "reddit.com/r/SEO",
        "reddit.com/r/bigseo",
        "reddit.com/r/seogrowth",
        "reddit.com/r/content_marketing",
        "reddit.com/r/GrowthHacking",
        "reddit.com/r/digital_marketing",
        "reddit.com/r/PPC",
        "reddit.com/r/linkbuilding",
    ],
    
    # ============ 垂直领域 ============
    # 远程工作与数字游民 - 远程工具、生活方式
    "remote_nomad": [
        "nomadlist.com",
        "remoteok.com",
        "weworkremotely.com",
        "levels.fyi",
        "reddit.com/r/digitalnomad",
        "reddit.com/r/remotework",
        "reddit.com/r/WorkOnline",
    ],
    
    # 开源项目 - 开源生态、项目发现
    "opensource": [
        "github.com",
        "gitlab.com",
        "opensource.com",
        "opensourcealternative.to",
        "reddit.com/r/opensource",
        "reddit.com/r/selfhosted",
        "news.ycombinator.com",
    ],
    
    # 金融科技 - Fintech、支付、加密
    "fintech": [
        "finextra.com",
        "pymnts.com",
        "coindesk.com",
        "theblock.co",
        "decrypt.co",
        "reddit.com/r/fintech",
        "reddit.com/r/CryptoCurrency",
        "reddit.com/r/defi",
    ],
    
    # 电商与 DTC - 电商工具、品牌建设
    "ecommerce": [
        "shopify.com/blog",
        "bigcommerce.com/blog",
        "practicalecommerce.com",
        "ecommercefuel.com",
        "reddit.com/r/ecommerce",
        "reddit.com/r/shopify",
        "reddit.com/r/FulfillmentByAmazon",
        "reddit.com/r/dropship",
    ],
    
    # 游戏开发 - 游戏引擎、独立游戏
    "gamedev": [
        "gamedeveloper.com",
        "itch.io",
        "indiedb.com",
        "reddit.com/r/gamedev",
        "reddit.com/r/IndieDev",
        "reddit.com/r/Unity3D",
        "reddit.com/r/unrealengine",
        "reddit.com/r/godot",
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

Domain presets by category:

【创业与独立开发】
- "indie": IndieHackers, ProductHunt, BetaList, Reddit创业subs, HN - 独立开发经验、收入案例
- "startup_business": TechCrunch, Crunchbase, SaaStr, VC blogs - 融资、商业模式

【技术与开发】
- "tech_news": HN, TechCrunch, TheVerge, Wired, Ars - 行业动态、产品发布
- "dev_community": dev.to, SO, GitHub, Reddit dev subs - 技术讨论、最佳实践
- "official_docs": MDN, React, Next.js, Vercel, AWS docs - 官方文档

【AI/ML】
- "ai_ml": HuggingFace, OpenAI, arXiv, Reddit ML subs - AI研究、模型
- "ai_tools": TheresAnAIForThat, FutureTools, ProductHunt - AI工具发现

【产品与市场】
- "product_reviews": G2, Capterra, Trustpilot, AlternativeTo - 竞品分析、用户反馈
- "design_ux": Dribbble, Behance, NN/g, Mobbin - 设计灵感、UX
- "marketing_growth": Backlinko, Moz, Ahrefs, HubSpot - SEO、增长策略

【垂直领域】
- "remote_nomad": NomadList, RemoteOK, levels.fyi - 远程工作
- "opensource": GitHub, GitLab, r/selfhosted - 开源项目
- "fintech": Finextra, CoinDesk, TheBlock - 金融科技
- "ecommerce": Shopify blog, r/ecommerce, r/FBA - 电商
- "gamedev": GameDeveloper, itch.io, r/gamedev - 游戏开发

Or use include_domains for custom filtering.""",
    {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query - be specific for better results"
            },
            "domain_preset": {
                "type": "string",
                "enum": [
                    "indie", "startup_business",
                    "tech_news", "dev_community", "official_docs",
                    "ai_ml", "ai_tools",
                    "product_reviews", "design_ux", "marketing_growth",
                    "remote_nomad", "opensource", "fintech", "ecommerce", "gamedev"
                ],
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
