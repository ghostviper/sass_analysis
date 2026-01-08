"""
Search Service Factory

Provides factory methods to create and manage search service instances.
"""

from typing import Optional, Literal, Dict, Any
from .base import SearchService, GoogleSearchService
from .tavily import TavilySearch
from config.search_config import get_search_config


class SearchServiceFactory:
    """Factory for creating search service instances"""

    _instances: Dict[str, SearchService] = {}

    @classmethod
    def get_search_service(cls) -> GoogleSearchService:
        """
        Get Tavily search service instance

        Returns:
            TavilySearch instance

        Raises:
            ValueError: If Tavily is not configured
        """
        config = get_search_config()

        # Check if Tavily is configured
        if not config.google.has_tavily:
            raise ValueError("Tavily not configured. Set TAVILY_API_KEY")

        # Return cached instance or create new one
        cache_key = "tavily"
        if cache_key not in cls._instances:
            cls._instances[cache_key] = TavilySearch()

        return cls._instances[cache_key]

    @classmethod
    def is_available(cls) -> bool:
        """
        Check if search service is available

        Returns:
            True if Tavily is configured
        """
        config = get_search_config()
        return config.google.has_tavily

    @classmethod
    async def health_check(cls) -> Dict[str, Any]:
        """
        Perform health check on Tavily search service

        Returns:
            Dictionary with health status
        """
        try:
            service = cls.get_search_service()
            return await service.health_check()
        except Exception as e:
            return {
                "service": "tavily",
                "status": "error",
                "available": False,
                "error": str(e)
            }

    @classmethod
    def clear_cache(cls):
        """Clear cached service instances"""
        cls._instances.clear()


# Convenience functions

async def web_search(
    query: str,
    limit: int = 10,
    **kwargs
) -> Any:
    """
    Convenience function to search the web using Tavily

    Args:
        query: Search query
        limit: Number of results
        **kwargs: Additional parameters (search_depth, include_domains, etc.)

    Returns:
        SearchResponse
    """
    service = SearchServiceFactory.get_search_service()
    return await service.search(query, limit=limit, **kwargs)


async def search_site(
    query: str,
    site: str,
    limit: int = 10,
    **kwargs
) -> Any:
    """
    Convenience function to search within a specific site

    Args:
        query: Search query
        site: Domain to search (e.g., "reddit.com", "indiehackers.com")
        limit: Number of results
        **kwargs: Additional parameters

    Returns:
        SearchResponse
    """
    service = SearchServiceFactory.get_search_service()
    return await service.search_site(query, site, limit=limit, **kwargs)


if __name__ == "__main__":
    # Test factory
    import asyncio

    async def test():
        print("=== Tavily Search Service Test ===\n")

        # Check availability
        available = SearchServiceFactory.is_available()
        print(f"Tavily available: {available}\n")

        if not available:
            print("Tavily not configured. Set TAVILY_API_KEY in .env")
            return

        # Health check
        print("Running health check...")
        health = await SearchServiceFactory.health_check()

        import json
        print(json.dumps(health, indent=2))

        # Test search
        print("\nTesting web search...")
        try:
            results = await web_search("SaaS products for indie developers", limit=3)
            print(f"Found {len(results.results)} results")
            for i, result in enumerate(results.results, 1):
                print(f"{i}. {result.title}")
                print(f"   {result.url}")
        except Exception as e:
            print(f"Search failed: {e}")

    asyncio.run(test())
