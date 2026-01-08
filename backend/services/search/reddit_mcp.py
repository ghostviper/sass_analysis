"""
Reddit MCP Integration

Wraps Reddit MCP Buddy functionality into our SearchService interface.
Note: This is a placeholder - actual Reddit search will be handled via MCP tools in agent/tools.py
"""

import time
from typing import Optional, Dict, Any, Literal, List
from .base import RedditSearchService, SearchResponse, SearchResult, SearchError
from config.search_config import get_search_config


class RedditMCPSearch(RedditSearchService):
    """
    Reddit search via MCP Buddy

    Note: This class provides a Python interface, but actual Reddit search
    is handled by the MCP server (reddit-mcp-buddy) via Claude Agent SDK.

    The MCP tools are registered in agent/tools.py and called by the AI agent.
    This class is mainly for direct API usage and testing.
    """

    def __init__(self):
        super().__init__("reddit_mcp")
        self.config = get_search_config()

    async def is_available(self) -> bool:
        """
        Check if Reddit MCP is available

        Reddit MCP Buddy works in anonymous mode without configuration,
        so it's always available.
        """
        return True

    async def search(
        self,
        query: str,
        limit: int = 10,
        subreddit: Optional[str] = None,
        sort: Literal["relevance", "hot", "top", "new", "comments"] = "relevance",
        time_filter: Literal["hour", "day", "week", "month", "year", "all"] = "all",
        **kwargs
    ) -> SearchResponse:
        """
        Search Reddit

        Note: This method is a placeholder. Actual Reddit search is performed
        via MCP tools in the agent. Use this for direct API testing only.

        Args:
            query: Search query
            limit: Number of results
            subreddit: Optional subreddit to search in
            sort: Sort method
            time_filter: Time filter
            **kwargs: Additional parameters

        Returns:
            SearchResponse with results

        Raises:
            SearchError: If search fails
        """
        raise NotImplementedError(
            "Reddit search should be performed via MCP tools in the agent. "
            "Use the 'search_reddit' tool in agent/tools.py instead."
        )

    async def browse_subreddit(
        self,
        subreddit: str,
        sort: Literal["hot", "new", "top", "rising"] = "hot",
        time_filter: Literal["hour", "day", "week", "month", "year", "all"] = "week",
        limit: int = 10,
    ) -> SearchResponse:
        """
        Browse posts from a specific subreddit

        Note: This method is a placeholder. Use MCP tools in the agent instead.
        """
        raise NotImplementedError(
            "Reddit browsing should be performed via MCP tools in the agent. "
            "Use the 'browse_subreddit' tool in agent/tools.py instead."
        )

    async def get_post_details(
        self,
        post_id: str,
        subreddit: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get detailed information about a specific post

        Note: This method is a placeholder. Use MCP tools in the agent instead.
        """
        raise NotImplementedError(
            "Reddit post details should be fetched via MCP tools in the agent. "
            "Use the 'get_reddit_post' tool in agent/tools.py instead."
        )

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on Reddit MCP

        Returns:
            Dictionary with health status
        """
        return {
            "service": self.service_name,
            "status": "healthy",
            "available": True,
            "mode": self.config.reddit.mode,
            "rate_limit": "100 req/min" if self.config.reddit.is_authenticated else "10 req/min",
            "note": "Reddit search is handled via MCP tools in the agent"
        }


# Helper functions for formatting Reddit data (used by MCP tools)

def format_reddit_post(post_data: Dict[str, Any]) -> SearchResult:
    """
    Format Reddit post data into SearchResult

    Args:
        post_data: Raw post data from Reddit API

    Returns:
        SearchResult object
    """
    subreddit = post_data.get("subreddit", "")
    post_id = post_data.get("id", "")

    return SearchResult(
        title=post_data.get("title", ""),
        url=f"https://reddit.com{post_data.get('permalink', '')}",
        snippet=post_data.get("selftext", "")[:300],  # First 300 chars
        source="reddit",
        date=post_data.get("created_utc"),
        author=post_data.get("author", ""),
        score=post_data.get("score", 0),
        comments_count=post_data.get("num_comments", 0),
        raw_data={
            "subreddit": subreddit,
            "post_id": post_id,
            "upvote_ratio": post_data.get("upvote_ratio", 0),
            "is_self": post_data.get("is_self", False),
            "link_flair_text": post_data.get("link_flair_text"),
        }
    )


def format_reddit_search_results(
    results: List[Dict[str, Any]],
    query: str,
    search_time: float = 0.0
) -> SearchResponse:
    """
    Format Reddit search results into SearchResponse

    Args:
        results: List of Reddit post data
        query: Original search query
        search_time: Time taken for search

    Returns:
        SearchResponse object
    """
    formatted_results = [format_reddit_post(post) for post in results]

    return SearchResponse(
        results=formatted_results,
        query=query,
        source="reddit_mcp",
        total_results=len(formatted_results),
        search_time=search_time,
        cached=False
    )
