"""
Base classes for search services

Defines common interfaces and data structures for all search backends.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime


@dataclass
class SearchResult:
    """Unified search result structure"""
    title: str
    url: str
    snippet: str
    source: str  # "reddit", "google", "indiehackers", "producthunt"

    # Optional fields
    date: Optional[str] = None
    author: Optional[str] = None
    score: Optional[int] = None  # Reddit upvotes, relevance score, etc.
    comments_count: Optional[int] = None  # For Reddit/forum posts

    # Raw data from the source (for debugging/advanced use)
    raw_data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "title": self.title,
            "url": self.url,
            "snippet": self.snippet,
            "source": self.source,
            "date": self.date,
            "author": self.author,
            "score": self.score,
            "comments_count": self.comments_count,
        }


@dataclass
class SearchResponse:
    """Search response with metadata"""
    results: List[SearchResult]
    query: str
    source: str
    total_results: int
    search_time: float  # Time taken in seconds
    cached: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "results": [r.to_dict() for r in self.results],
            "query": self.query,
            "source": self.source,
            "total_results": self.total_results,
            "search_time": self.search_time,
            "cached": self.cached,
        }


class SearchError(Exception):
    """Base exception for search errors"""
    def __init__(self, message: str, service: str, original_error: Optional[Exception] = None):
        self.message = message
        self.service = service
        self.original_error = original_error
        super().__init__(f"[{service}] {message}")


class SearchService(ABC):
    """
    Abstract base class for search services

    All search backends must implement this interface.
    """

    def __init__(self, service_name: str):
        self.service_name = service_name

    @abstractmethod
    async def search(
        self,
        query: str,
        limit: int = 10,
        **kwargs
    ) -> SearchResponse:
        """
        Perform a search query

        Args:
            query: Search query string
            limit: Maximum number of results to return
            **kwargs: Additional service-specific parameters

        Returns:
            SearchResponse with results

        Raises:
            SearchError: If search fails
        """
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        """
        Check if the search service is available and configured

        Returns:
            True if service is ready to use
        """
        pass

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the service

        Returns:
            Dictionary with health status
        """
        try:
            available = await self.is_available()
            return {
                "service": self.service_name,
                "status": "healthy" if available else "unavailable",
                "available": available,
            }
        except Exception as e:
            return {
                "service": self.service_name,
                "status": "error",
                "available": False,
                "error": str(e),
            }


class GoogleSearchService(SearchService):
    """Base class for Google-based search services"""

    def __init__(self, service_name: str):
        super().__init__(service_name)

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
            site: Domain to search (e.g., "reddit.com", "indiehackers.com")
            limit: Maximum results
            **kwargs: Additional parameters

        Returns:
            SearchResponse with results
        """
        site_query = f"site:{site} {query}"
        return await self.search(site_query, limit=limit, **kwargs)


class RedditSearchService(SearchService):
    """Base class for Reddit search services"""

    def __init__(self, service_name: str = "reddit"):
        super().__init__(service_name)

    @abstractmethod
    async def browse_subreddit(
        self,
        subreddit: str,
        sort: Literal["hot", "new", "top", "rising"] = "hot",
        time_filter: Literal["hour", "day", "week", "month", "year", "all"] = "week",
        limit: int = 10,
    ) -> SearchResponse:
        """
        Browse posts from a specific subreddit

        Args:
            subreddit: Subreddit name (without r/)
            sort: Sort method
            time_filter: Time filter for 'top' sort
            limit: Maximum results

        Returns:
            SearchResponse with posts
        """
        pass

    @abstractmethod
    async def get_post_details(
        self,
        post_id: str,
        subreddit: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get detailed information about a specific post

        Args:
            post_id: Reddit post ID
            subreddit: Optional subreddit name

        Returns:
            Dictionary with post details and comments
        """
        pass
