"""
Google Custom Search API Implementation

Free tier: 100 queries per day
Docs: https://developers.google.com/custom-search/v1/overview
"""

import time
import aiohttp
from typing import Optional, Dict, Any
from .base import GoogleSearchService, SearchResponse, SearchResult, SearchError
from config.search_config import get_search_config


class GoogleCustomSearch(GoogleSearchService):
    """Google Custom Search API implementation"""

    def __init__(self):
        super().__init__("google_custom_search")
        self.config = get_search_config()
        self.api_key = self.config.google.custom_api_key
        self.engine_id = self.config.google.custom_engine_id
        self.base_url = "https://www.googleapis.com/customsearch/v1"

    async def is_available(self) -> bool:
        """Check if Google Custom Search is configured"""
        return self.config.google.has_custom

    async def search(
        self,
        query: str,
        limit: int = 10,
        **kwargs
    ) -> SearchResponse:
        """
        Search using Google Custom Search API

        Args:
            query: Search query
            limit: Number of results (max 10 per request)
            **kwargs: Additional parameters
                - start: Starting index (for pagination)
                - dateRestrict: Restrict by date (e.g., "d7" for last 7 days)
                - siteSearch: Restrict to specific site
                - exactTerms: Exact phrase to match

        Returns:
            SearchResponse with results

        Raises:
            SearchError: If API call fails
        """
        if not await self.is_available():
            raise SearchError(
                "Google Custom Search not configured. Set GOOGLE_CUSTOM_SEARCH_API_KEY and GOOGLE_CUSTOM_SEARCH_ENGINE_ID",
                self.service_name
            )

        start_time = time.time()

        # Build request parameters
        params = {
            "key": self.api_key,
            "cx": self.engine_id,
            "q": query,
            "num": min(limit, 10),  # API max is 10
        }

        # Add optional parameters
        if "start" in kwargs:
            params["start"] = kwargs["start"]
        if "dateRestrict" in kwargs:
            params["dateRestrict"] = kwargs["dateRestrict"]
        if "siteSearch" in kwargs:
            params["siteSearch"] = kwargs["siteSearch"]
        if "exactTerms" in kwargs:
            params["exactTerms"] = kwargs["exactTerms"]

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

            # Parse results
            results = []
            items = data.get("items", [])

            for item in items:
                result = SearchResult(
                    title=item.get("title", ""),
                    url=item.get("link", ""),
                    snippet=item.get("snippet", ""),
                    source="google",
                    raw_data=item
                )
                results.append(result)

            search_time = time.time() - start_time
            total_results = int(data.get("searchInformation", {}).get("totalResults", 0))

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
        Search within a specific site

        This uses the siteSearch parameter which is more reliable than site: operator
        """
        kwargs["siteSearch"] = site
        return await self.search(query, limit=limit, **kwargs)
