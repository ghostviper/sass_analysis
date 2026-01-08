"""
SerpAPI Implementation

Commercial search API with multiple search engines support
Pricing: $50/month for 5000 searches
Docs: https://serpapi.com/search-api
"""

import time
import aiohttp
from typing import Optional, Dict, Any, Literal
from .base import GoogleSearchService, SearchResponse, SearchResult, SearchError
from config.search_config import get_search_config


class SerpAPISearch(GoogleSearchService):
    """SerpAPI implementation"""

    def __init__(self):
        super().__init__("serpapi")
        self.config = get_search_config()
        self.api_key = self.config.google.serpapi_key
        self.base_url = "https://serpapi.com/search"

    async def is_available(self) -> bool:
        """Check if SerpAPI is configured"""
        return self.config.google.has_serpapi

    async def search(
        self,
        query: str,
        limit: int = 10,
        engine: Literal["google", "bing", "duckduckgo"] = "google",
        **kwargs
    ) -> SearchResponse:
        """
        Search using SerpAPI

        Args:
            query: Search query
            limit: Number of results
            engine: Search engine to use (google, bing, duckduckgo)
            **kwargs: Additional parameters
                - location: Location for search (e.g., "United States")
                - gl: Country code (e.g., "us")
                - hl: Language (e.g., "en")
                - tbs: Time-based search (e.g., "qdr:d" for past day)

        Returns:
            SearchResponse with results

        Raises:
            SearchError: If API call fails
        """
        if not await self.is_available():
            raise SearchError(
                "SerpAPI not configured. Set SERPAPI_API_KEY",
                self.service_name
            )

        start_time = time.time()

        # Build request parameters
        params = {
            "api_key": self.api_key,
            "q": query,
            "num": limit,
            "engine": engine,
        }

        # Add optional parameters
        if "location" in kwargs:
            params["location"] = kwargs["location"]
        if "gl" in kwargs:
            params["gl"] = kwargs["gl"]
        if "hl" in kwargs:
            params["hl"] = kwargs["hl"]
        if "tbs" in kwargs:
            params["tbs"] = kwargs["tbs"]

        try:
            # Get proxy configuration
            proxy = None
            proxy_dict = self.config.get_proxy_dict()
            if proxy_dict:
                proxy = proxy_dict.get("https") or proxy_dict.get("http")

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.base_url,
                    params=params,
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
            organic_results = data.get("organic_results", [])

            for item in organic_results[:limit]:
                result = SearchResult(
                    title=item.get("title", ""),
                    url=item.get("link", ""),
                    snippet=item.get("snippet", ""),
                    source="google",
                    date=item.get("date"),
                    raw_data=item
                )
                results.append(result)

            search_time = time.time() - start_time
            search_info = data.get("search_information", {})
            total_results = int(search_info.get("total_results", 0))

            return SearchResponse(
                results=results,
                query=query,
                source=self.service_name,
                total_results=total_results,
                search_time=search_time,
                cached=False
            )

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
        Search within a specific site using site: operator

        Args:
            query: Search query
            site: Domain to search (e.g., "reddit.com")
            limit: Maximum results
            **kwargs: Additional parameters

        Returns:
            SearchResponse with results
        """
        site_query = f"site:{site} {query}"
        return await self.search(site_query, limit=limit, **kwargs)
