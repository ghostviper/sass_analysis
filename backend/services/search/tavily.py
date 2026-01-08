"""
Tavily Search API Implementation

AI-optimized search API designed for LLMs and AI agents
Docs: https://docs.tavily.com/
"""

import time
import aiohttp
from typing import Optional, Dict, Any, List, Literal
from .base import GoogleSearchService, SearchResponse, SearchResult, SearchError
from config.search_config import get_search_config


class TavilySearch(GoogleSearchService):
    """Tavily Search API implementation"""

    def __init__(self):
        super().__init__("tavily")
        self.config = get_search_config()
        self.api_key = self.config.google.tavily_key
        self.base_url = "https://api.tavily.com/search"

    async def is_available(self) -> bool:
        """Check if Tavily is configured"""
        return self.config.google.has_tavily

    async def search(
        self,
        query: str,
        limit: int = 10,
        search_depth: Literal["basic", "advanced"] = "basic",
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None,
        **kwargs
    ) -> SearchResponse:
        """
        Search using Tavily API

        Args:
            query: Search query
            limit: Number of results (max 20)
            search_depth: "basic" (faster) or "advanced" (more thorough)
            include_domains: List of domains to include (e.g., ["reddit.com"])
            exclude_domains: List of domains to exclude
            **kwargs: Additional parameters
                - include_answer: Include AI-generated answer (bool)
                - include_raw_content: Include raw HTML content (bool)
                - include_images: Include images (bool)

        Returns:
            SearchResponse with results

        Raises:
            SearchError: If API call fails
        """
        if not await self.is_available():
            raise SearchError(
                "Tavily not configured. Set TAVILY_API_KEY",
                self.service_name
            )

        start_time = time.time()

        # Build request body
        payload = {
            "api_key": self.api_key,
            "query": query,
            "max_results": min(limit, 20),  # API max is 20
            "search_depth": search_depth,
            "include_answer": kwargs.get("include_answer", False),
            "include_raw_content": kwargs.get("include_raw_content", False),
            "include_images": kwargs.get("include_images", False),
        }

        # Add domain filters
        if include_domains:
            payload["include_domains"] = include_domains
        if exclude_domains:
            payload["exclude_domains"] = exclude_domains

        try:
            # Get proxy configuration
            proxy = None
            proxy_dict = self.config.get_proxy_dict()
            if proxy_dict:
                proxy = proxy_dict.get("https") or proxy_dict.get("http")

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.base_url,
                    json=payload,
                    proxy=proxy,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise SearchError(
                            f"API returned status {response.status}: {error_text}",
                            self.service_name
                        )

                    data = await response.json()

            # Check for API errors
            if "error" in data:
                raise SearchError(
                    f"API error: {data['error']}",
                    self.service_name
                )

            # Parse results
            results = []
            tavily_results = data.get("results", [])

            for item in tavily_results:
                result = SearchResult(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    snippet=item.get("content", ""),
                    source="google",
                    score=int(item.get("score", 0) * 100),  # Convert 0-1 to 0-100
                    raw_data=item
                )
                results.append(result)

            search_time = time.time() - start_time

            # Tavily doesn't provide total results count
            total_results = len(results)

            # Store AI answer if available
            response_data = SearchResponse(
                results=results,
                query=query,
                source=self.service_name,
                total_results=total_results,
                search_time=search_time,
                cached=False
            )

            # Add AI answer to first result's raw_data if available
            if data.get("answer") and results:
                results[0].raw_data["ai_answer"] = data["answer"]

            return response_data

        except aiohttp.ClientError as e:
            raise SearchError(
                f"Network error: {str(e)}",
                self.service_name,
                original_error=e
            )
        except Exception as e:
            raise SearchError(
                f"Unexpected error: {str(e)}",
                self.service_name,
                original_error=e
            )

    async def search_site(
        self,
        query: str,
        site: str,
        limit: int = 10,
        **kwargs
    ) -> SearchResponse:
        """
        Search within a specific site using include_domains

        Args:
            query: Search query
            site: Domain to search (e.g., "reddit.com")
            limit: Maximum results
            **kwargs: Additional parameters

        Returns:
            SearchResponse with results
        """
        return await self.search(
            query,
            limit=limit,
            include_domains=[site],
            **kwargs
        )

    async def search_with_answer(
        self,
        query: str,
        limit: int = 5,
        **kwargs
    ) -> tuple[str, SearchResponse]:
        """
        Search and get AI-generated answer along with sources

        Args:
            query: Search query
            limit: Number of source results
            **kwargs: Additional parameters

        Returns:
            Tuple of (ai_answer, SearchResponse)
        """
        kwargs["include_answer"] = True
        response = await self.search(query, limit=limit, **kwargs)

        # Extract AI answer from first result's raw_data
        ai_answer = ""
        if response.results and "ai_answer" in response.results[0].raw_data:
            ai_answer = response.results[0].raw_data["ai_answer"]

        return ai_answer, response
