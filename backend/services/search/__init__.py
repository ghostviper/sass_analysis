"""
Search Services Package

Provides unified interface for multiple search backends:
- Reddit (via MCP)
- Google Custom Search
- SerpAPI
- Tavily Search
"""

from .base import SearchService, SearchResult, SearchError
from .factory import SearchServiceFactory, web_search, search_site

__all__ = [
    "SearchService",
    "SearchResult",
    "SearchError",
    "SearchServiceFactory",
    "web_search",
    "search_site",
]
