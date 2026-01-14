"""
Product Hunt API Service - 多 Token 轮询数据获取

Rate Limits:
- GraphQL 端点 (/v2/api/graphql): 6250 complexity points / 15 min per token
- 其他端点 (/v2/*): 450 requests / 15 min per token

通过多 Token 轮询策略最大化数据获取效率。
"""

import os
import asyncio
import time
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
import httpx
from enum import Enum
from urllib.parse import urlparse


class TokenStatus(Enum):
    AVAILABLE = "available"
    RATE_LIMITED = "rate_limited"
    INVALID = "invalid"


@dataclass
class TokenState:
    """单个 Token 的状态"""
    token: str
    name: str  # 标识名称，方便日志
    complexity_remaining: int = 6250
    complexity_limit: int = 6250
    reset_at: datetime = field(default_factory=datetime.utcnow)
    status: TokenStatus = TokenStatus.AVAILABLE
    total_requests: int = 0
    total_complexity_used: int = 0
    last_used: Optional[datetime] = None
    
    def is_available(self) -> bool:
        """检查 Token 是否可用"""
        if self.status == TokenStatus.INVALID:
            return False
        if self.status == TokenStatus.RATE_LIMITED:
            # 检查是否已过重置时间
            if datetime.utcnow() >= self.reset_at:
                self.status = TokenStatus.AVAILABLE
                self.complexity_remaining = self.complexity_limit
                return True
            return False
        return self.complexity_remaining > 0
    
    def update_from_headers(self, headers: Dict[str, str]):
        """从响应头更新状态"""
        if "X-Rate-Limit-Remaining" in headers:
            self.complexity_remaining = int(headers["X-Rate-Limit-Remaining"])
        if "X-Rate-Limit-Limit" in headers:
            self.complexity_limit = int(headers["X-Rate-Limit-Limit"])
        if "X-Rate-Limit-Reset" in headers:
            reset_seconds = int(headers["X-Rate-Limit-Reset"])
            self.reset_at = datetime.utcnow() + timedelta(seconds=reset_seconds)
        
        if self.complexity_remaining <= 0:
            self.status = TokenStatus.RATE_LIMITED


class ProductHuntClient:
    """
    Product Hunt API 客户端 - 支持多 Token 轮询
    
    使用方式:
    1. 在 .env 中配置多个 Token:
       PH_TOKENS=token1,token2,token3
       或
       PH_TOKEN_1=xxx
       PH_TOKEN_2=xxx
       
    2. 初始化客户端:
       client = ProductHuntClient()
       
    3. 执行查询:
       result = await client.query(graphql_query)
    """
    
    BASE_URL = "https://api.producthunt.com/v2/api/graphql"
    
    def __init__(self, tokens: Optional[List[str]] = None):
        """
        初始化客户端
        
        Args:
            tokens: Token 列表，如果不提供则从环境变量读取
        """
        self.tokens: List[TokenState] = []
        self._current_index = 0
        self._lock = asyncio.Lock()
        
        # 从参数或环境变量加载 Tokens
        if tokens:
            for i, token in enumerate(tokens):
                self.tokens.append(TokenState(token=token, name=f"token_{i+1}"))
        else:
            self._load_tokens_from_env()
        
        if not self.tokens:
            print("[ProductHunt] Warning: No tokens configured!")
    
    def _load_tokens_from_env(self):
        """从环境变量加载 Tokens"""
        # 方式1: 逗号分隔的 Token 列表
        tokens_str = os.getenv("PH_TOKENS", "")
        if tokens_str:
            for i, token in enumerate(tokens_str.split(",")):
                token = token.strip()
                if token:
                    self.tokens.append(TokenState(token=token, name=f"token_{i+1}"))
            return
        
        # 方式2: 单独的环境变量 PH_TOKEN_1, PH_TOKEN_2, ...
        i = 1
        while True:
            token = os.getenv(f"PH_TOKEN_{i}", "")
            if not token:
                # 也检查不带下划线的格式
                token = os.getenv(f"PH_TOKEN{i}", "")
            if not token:
                break
            self.tokens.append(TokenState(token=token, name=f"token_{i}"))
            i += 1
        
        # 方式3: 单个 Token
        if not self.tokens:
            single_token = os.getenv("PH_TOKEN", "")
            if single_token:
                self.tokens.append(TokenState(token=single_token, name="token_1"))
    
    def _get_next_available_token(self) -> Optional[TokenState]:
        """获取下一个可用的 Token（轮询策略）"""
        if not self.tokens:
            return None
        
        # 尝试从当前位置开始找可用的 Token
        for _ in range(len(self.tokens)):
            token_state = self.tokens[self._current_index]
            self._current_index = (self._current_index + 1) % len(self.tokens)
            
            if token_state.is_available():
                return token_state
        
        return None
    
    def _get_best_token(self) -> Optional[TokenState]:
        """获取剩余配额最多的 Token"""
        available_tokens = [t for t in self.tokens if t.is_available()]
        if not available_tokens:
            return None
        return max(available_tokens, key=lambda t: t.complexity_remaining)
    
    def get_status(self) -> Dict[str, Any]:
        """获取所有 Token 的状态"""
        return {
            "total_tokens": len(self.tokens),
            "available_tokens": sum(1 for t in self.tokens if t.is_available()),
            "tokens": [
                {
                    "name": t.name,
                    "status": t.status.value,
                    "complexity_remaining": t.complexity_remaining,
                    "complexity_limit": t.complexity_limit,
                    "reset_at": t.reset_at.isoformat() if t.reset_at else None,
                    "total_requests": t.total_requests,
                    "total_complexity_used": t.total_complexity_used,
                }
                for t in self.tokens
            ]
        }
    
    async def query(
        self,
        query: str,
        variables: Optional[Dict[str, Any]] = None,
        estimated_complexity: int = 100,
        retry_on_rate_limit: bool = True,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        执行 GraphQL 查询
        
        Args:
            query: GraphQL 查询字符串
            variables: 查询变量
            estimated_complexity: 预估复杂度（用于选择 Token）
            retry_on_rate_limit: 遇到限流时是否重试
            max_retries: 最大重试次数
            
        Returns:
            API 响应数据
            
        Raises:
            ProductHuntRateLimitError: 所有 Token 都被限流
            ProductHuntAPIError: API 调用失败
        """
        async with self._lock:
            for attempt in range(max_retries):
                # 选择 Token（优先选择配额充足的）
                token_state = self._get_best_token()
                
                if not token_state:
                    if retry_on_rate_limit:
                        # 计算最早的重置时间
                        next_reset = min(
                            (t.reset_at for t in self.tokens if t.status == TokenStatus.RATE_LIMITED),
                            default=datetime.utcnow() + timedelta(minutes=15)
                        )
                        wait_seconds = (next_reset - datetime.utcnow()).total_seconds()
                        if wait_seconds > 0 and wait_seconds < 900:  # 最多等15分钟
                            print(f"[ProductHunt] All tokens rate limited, waiting {wait_seconds:.0f}s...")
                            await asyncio.sleep(wait_seconds + 1)
                            continue
                    raise ProductHuntRateLimitError("All tokens are rate limited")
                
                try:
                    result = await self._execute_query(token_state, query, variables)
                    return result
                except ProductHuntRateLimitError:
                    if attempt < max_retries - 1:
                        continue
                    raise
        
        raise ProductHuntAPIError("Max retries exceeded")
    
    async def _execute_query(
        self,
        token_state: TokenState,
        query: str,
        variables: Optional[Dict[str, Any]] = None,
        max_network_retries: int = 3
    ) -> Dict[str, Any]:
        """执行单次查询，带网络重试"""
        headers = {
            "Authorization": f"Bearer {token_state.token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        
        # 读取代理配置
        proxy = os.getenv("HTTPS_PROXY") or os.getenv("HTTP_PROXY")
        
        last_error = None
        for attempt in range(max_network_retries):
            try:
                async with httpx.AsyncClient(
                    timeout=30.0,
                    proxy=proxy
                ) as client:
                    response = await client.post(self.BASE_URL, json=payload, headers=headers)
                    
                    # 更新 Token 状态
                    token_state.update_from_headers(dict(response.headers))
                    token_state.total_requests += 1
                    token_state.last_used = datetime.utcnow()
                    
                    if response.status_code == 429:
                        token_state.status = TokenStatus.RATE_LIMITED
                        raise ProductHuntRateLimitError(f"Token {token_state.name} rate limited")
                    
                    if response.status_code == 401:
                        token_state.status = TokenStatus.INVALID
                        raise ProductHuntAPIError(f"Token {token_state.name} is invalid")
                    
                    if response.status_code != 200:
                        raise ProductHuntAPIError(f"API error: {response.status_code} - {response.text[:200]}")
                    
                    data = response.json()
                    
                    if "errors" in data:
                        raise ProductHuntAPIError(f"GraphQL errors: {data['errors']}")
                    
                    return data.get("data", {})
                    
            except (httpx.ConnectError, httpx.ConnectTimeout, httpx.ReadTimeout) as e:
                last_error = e
                if attempt < max_network_retries - 1:
                    wait_time = (attempt + 1) * 2  # 2s, 4s, 6s
                    print(f"[ProductHunt] Network error (attempt {attempt + 1}/{max_network_retries}), retrying in {wait_time}s: {type(e).__name__}")
                    await asyncio.sleep(wait_time)
                else:
                    print(f"[ProductHunt] Network error after {max_network_retries} attempts: {e}")
        
        raise ProductHuntAPIError(f"Network error after {max_network_retries} retries: {last_error}")


class ProductHuntRateLimitError(Exception):
    """Rate limit exceeded"""
    pass


class ProductHuntAPIError(Exception):
    """General API error"""
    pass


# ============================================================================
# 数据获取服务
# ============================================================================

class ProductHuntDataService:
    """
    Product Hunt 数据获取服务
    
    提供高级数据获取方法，自动处理分页和限流。
    """
    
    def __init__(self, client: Optional[ProductHuntClient] = None):
        self.client = client or ProductHuntClient()
    
    async def get_posts(
        self,
        first: int = 20,
        after: Optional[str] = None,
        featured: bool = True,
        order: str = "VOTES",
        posted_after: Optional[str] = None,
        posted_before: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取产品列表
        
        Args:
            first: 每页数量 (max 20)
            after: 分页游标
            featured: 是否只获取精选产品
            order: 排序方式 (VOTES, NEWEST, RANKING)
            posted_after: 只获取此日期之后的产品 (ISO 格式: 2024-01-01)
            posted_before: 只获取此日期之前的产品 (ISO 格式: 2024-01-01)
        """
        query = """
        query getPosts($first: Int!, $after: String, $featured: Boolean, $order: PostsOrder, $postedAfter: DateTime, $postedBefore: DateTime) {
            posts(first: $first, after: $after, featured: $featured, order: $order, postedAfter: $postedAfter, postedBefore: $postedBefore) {
                edges {
                    cursor
                    node {
                        id
                        name
                        slug
                        tagline
                        description
                        url
                        website
                        votesCount
                        commentsCount
                        featuredAt
                        createdAt
                        thumbnail {
                            url
                        }
                        topics {
                            edges {
                                node {
                                    id
                                    name
                                    slug
                                }
                            }
                        }
                        makers {
                            id
                            name
                            username
                            profileImage
                        }
                    }
                }
                pageInfo {
                    hasNextPage
                    endCursor
                }
            }
        }
        """
        
        variables = {
            "first": min(first, 20),
            "after": after,
            "featured": featured,
            "order": order,
            "postedAfter": posted_after,
            "postedBefore": posted_before
        }
        
        return await self.client.query(query, variables)
    
    async def get_post_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        """通过 slug 获取单个产品详情"""
        query = """
        query getPost($slug: String!) {
            post(slug: $slug) {
                id
                name
                slug
                tagline
                description
                url
                website
                votesCount
                commentsCount
                reviewsCount
                reviewsRating
                featuredAt
                createdAt
                thumbnail {
                    url
                }
                media {
                    url
                    type
                }
                productLinks {
                    url
                }
                topics {
                    edges {
                        node {
                            id
                            name
                            slug
                        }
                    }
                }
                makers {
                    id
                    name
                    username
                    profileImage
                    headline
                }
                user {
                    id
                    name
                    username
                    profileImage
                    headline
                }
            }
        }
        """
        
        result = await self.client.query(query, {"slug": slug})
        return result.get("post")
    
    async def search_posts(
        self,
        query_text: str,
        first: int = 10
    ) -> List[Dict[str, Any]]:
        """搜索产品"""
        # 注意：Product Hunt API 的搜索功能有限
        # 这里使用 posts 查询配合客户端过滤
        query = """
        query searchPosts($first: Int!) {
            posts(first: $first, order: VOTES) {
                edges {
                    node {
                        id
                        name
                        slug
                        tagline
                        url
                        votesCount
                    }
                }
            }
        }
        """
        
        result = await self.client.query(query, {"first": first})
        posts = result.get("posts", {}).get("edges", [])
        
        # 客户端过滤
        query_lower = query_text.lower()
        filtered = [
            p["node"] for p in posts
            if query_lower in p["node"]["name"].lower() 
            or query_lower in (p["node"].get("tagline") or "").lower()
        ]
        
        return filtered
    
    async def get_all_posts_paginated(
        self,
        max_pages: int = 10,
        per_page: int = 20,
        delay_between_pages: float = 1.0,
        on_page: Optional[callable] = None
    ) -> List[Dict[str, Any]]:
        """
        分页获取所有产品
        
        Args:
            max_pages: 最大页数
            per_page: 每页数量
            delay_between_pages: 页间延迟（秒）
            on_page: 每页回调函数
            
        Returns:
            所有产品列表
        """
        all_posts = []
        cursor = None
        
        for page in range(max_pages):
            print(f"[ProductHunt] Fetching page {page + 1}/{max_pages}...")
            
            result = await self.get_posts(first=per_page, after=cursor)
            posts_data = result.get("posts", {})
            edges = posts_data.get("edges", [])
            
            if not edges:
                break
            
            posts = [edge["node"] for edge in edges]
            all_posts.extend(posts)
            
            if on_page:
                await on_page(page + 1, posts)
            
            page_info = posts_data.get("pageInfo", {})
            if not page_info.get("hasNextPage"):
                break
            
            cursor = page_info.get("endCursor")
            
            if delay_between_pages > 0:
                await asyncio.sleep(delay_between_pages)
        
        return all_posts


# ============================================================================
# 便捷函数
# ============================================================================

_default_client: Optional[ProductHuntClient] = None
_default_service: Optional[ProductHuntDataService] = None


def get_client() -> ProductHuntClient:
    """获取默认客户端实例"""
    global _default_client
    if _default_client is None:
        _default_client = ProductHuntClient()
    return _default_client


def get_service() -> ProductHuntDataService:
    """获取默认服务实例"""
    global _default_service
    if _default_service is None:
        _default_service = ProductHuntDataService(get_client())
    return _default_service


async def test_connection() -> bool:
    """测试 API 连接"""
    try:
        client = get_client()
        result = await client.query("query { viewer { id } }")
        print(f"[ProductHunt] Connection test successful: {result}")
        return True
    except Exception as e:
        print(f"[ProductHunt] Connection test failed: {e}")
        return False


# ============================================================================
# URL 解析工具
# ============================================================================

async def resolve_redirect_url(url: str, timeout: float = 10.0) -> Optional[str]:
    """
    解析 ProductHunt 重定向 URL，获取真实目标地址
    
    Args:
        url: PH 重定向 URL (如 https://www.producthunt.com/r/xxx)
        timeout: 请求超时时间
        
    Returns:
        真实 URL 或 None（如果解析失败）
    """
    if not url or not url.startswith("https://www.producthunt.com/r/"):
        return url  # 不是 PH 重定向链接，直接返回
    
    # 去掉 URL 中的 utm 参数，简化请求
    base_url = url.split("?")[0]
    
    # 读取代理配置
    proxy = os.getenv("HTTPS_PROXY") or os.getenv("HTTP_PROXY")
    
    try:
        async with httpx.AsyncClient(
            timeout=timeout, 
            follow_redirects=False,
            proxy=proxy,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        ) as client:
            # 先尝试 HEAD 请求
            response = await client.head(base_url)
            
            # 检查重定向响应
            if response.status_code in (301, 302, 303, 307, 308):
                location = response.headers.get("location")
                if location:
                    # 如果还是 PH 链接，可能需要再次解析
                    if location.startswith("https://www.producthunt.com/r/"):
                        return await resolve_redirect_url(location, timeout)
                    return location
            
            # HEAD 没有重定向，尝试 GET
            if response.status_code == 200:
                response = await client.get(base_url, follow_redirects=True)
                final_url = str(response.url)
                
                # 确保不返回 PH 内部链接
                if not final_url.startswith("https://www.producthunt.com/"):
                    return final_url
                    
    except httpx.TimeoutException:
        pass  # 超时静默处理
    except Exception as e:
        # 只在非超时错误时打印
        if "timeout" not in str(e).lower():
            print(f"[URL Resolve] Failed: {type(e).__name__}")
    
    return None


async def resolve_redirect_urls_batch(
    urls: List[str], 
    concurrency: int = 5,
    delay: float = 0.2
) -> Dict[str, Optional[str]]:
    """
    批量解析重定向 URL
    
    Args:
        urls: URL 列表
        concurrency: 并发数
        delay: 请求间延迟
        
    Returns:
        {原始URL: 真实URL} 映射
    """
    results = {}
    semaphore = asyncio.Semaphore(concurrency)
    
    async def resolve_one(url: str):
        async with semaphore:
            result = await resolve_redirect_url(url)
            await asyncio.sleep(delay)
            return url, result
    
    tasks = [resolve_one(url) for url in urls if url]
    for coro in asyncio.as_completed(tasks):
        original, resolved = await coro
        results[original] = resolved
    
    return results
