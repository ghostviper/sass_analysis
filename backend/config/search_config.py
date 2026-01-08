"""
Search Service Configuration

Centralized configuration for all search services (Google, Reddit, etc.)
"""

import os
from typing import Optional, Literal
from dataclasses import dataclass


@dataclass
class GoogleSearchConfig:
    """Google search configuration"""
    # Google Custom Search
    custom_api_key: Optional[str] = None
    custom_engine_id: Optional[str] = None

    # SerpAPI
    serpapi_key: Optional[str] = None

    # Tavily
    tavily_key: Optional[str] = None

    # Default backend to use
    backend: Literal["custom", "serpapi", "tavily"] = "custom"

    @property
    def has_custom(self) -> bool:
        """Check if Google Custom Search is configured"""
        return bool(self.custom_api_key and self.custom_engine_id)

    @property
    def has_serpapi(self) -> bool:
        """Check if SerpAPI is configured"""
        return bool(self.serpapi_key)

    @property
    def has_tavily(self) -> bool:
        """Check if Tavily is configured"""
        return bool(self.tavily_key)

    @property
    def is_configured(self) -> bool:
        """Check if at least one backend is configured"""
        return self.has_custom or self.has_serpapi or self.has_tavily

    def get_available_backends(self) -> list[str]:
        """Get list of configured backends"""
        backends = []
        if self.has_custom:
            backends.append("custom")
        if self.has_serpapi:
            backends.append("serpapi")
        if self.has_tavily:
            backends.append("tavily")
        return backends


@dataclass
class RedditConfig:
    """Reddit API configuration"""
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    user_agent: str = "SaaSAnalysis/1.0"

    @property
    def is_authenticated(self) -> bool:
        """Check if Reddit authentication is configured"""
        return bool(self.client_id and self.client_secret)

    @property
    def mode(self) -> Literal["anonymous", "authenticated"]:
        """Get Reddit access mode"""
        return "authenticated" if self.is_authenticated else "anonymous"


@dataclass
class SearchCacheConfig:
    """Search result caching configuration"""
    enabled: bool = True
    ttl: int = 3600  # Cache TTL in seconds (default: 1 hour)


class SearchConfig:
    """Main search configuration class"""

    def __init__(self):
        """Initialize configuration from environment variables"""
        # Google search config
        self.google = GoogleSearchConfig(
            custom_api_key=os.getenv("GOOGLE_CUSTOM_SEARCH_API_KEY"),
            custom_engine_id=os.getenv("GOOGLE_CUSTOM_SEARCH_ENGINE_ID"),
            serpapi_key=os.getenv("SERPAPI_API_KEY"),
            tavily_key=os.getenv("TAVILY_API_KEY"),
            backend=os.getenv("GOOGLE_SEARCH_BACKEND", "custom")
        )

        # Reddit config
        self.reddit = RedditConfig(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent=os.getenv("REDDIT_USER_AGENT", "SaaSAnalysis/1.0")
        )

        # Cache config
        self.cache = SearchCacheConfig(
            enabled=os.getenv("SEARCH_CACHE_ENABLED", "true").lower() == "true",
            ttl=int(os.getenv("SEARCH_CACHE_TTL", "3600"))
        )

        # Proxy settings (inherit from environment)
        self.http_proxy = os.getenv("HTTP_PROXY")
        self.https_proxy = os.getenv("HTTPS_PROXY")

    def get_proxy_dict(self) -> Optional[dict]:
        """Get proxy configuration as dict for aiohttp"""
        if self.http_proxy or self.https_proxy:
            return {
                "http": self.http_proxy,
                "https": self.https_proxy or self.http_proxy
            }
        return None

    def validate(self) -> tuple[bool, list[str]]:
        """
        Validate configuration and return status with warnings

        Returns:
            Tuple of (is_valid, warnings)
        """
        warnings = []

        # Check if at least one search backend is configured
        if not self.google.is_configured:
            warnings.append("No Google search backend configured. Google search will not be available.")

        # Check Reddit mode
        if not self.reddit.is_authenticated:
            warnings.append(f"Reddit running in anonymous mode (10 req/min). Configure REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET for authenticated mode (100 req/min).")

        # Check cache
        if not self.cache.enabled:
            warnings.append("Search result caching is disabled. This may increase API costs.")

        # At least Reddit MCP should work (no API key needed)
        is_valid = True

        return is_valid, warnings

    def get_status_report(self) -> dict:
        """Get detailed configuration status report"""
        return {
            "google": {
                "configured": self.google.is_configured,
                "backends": self.google.get_available_backends(),
                "default_backend": self.google.backend,
                "custom_search": self.google.has_custom,
                "serpapi": self.google.has_serpapi,
                "tavily": self.google.has_tavily,
            },
            "reddit": {
                "mode": self.reddit.mode,
                "authenticated": self.reddit.is_authenticated,
                "rate_limit": "100 req/min" if self.reddit.is_authenticated else "10 req/min"
            },
            "cache": {
                "enabled": self.cache.enabled,
                "ttl": self.cache.ttl
            },
            "proxy": {
                "http": bool(self.http_proxy),
                "https": bool(self.https_proxy)
            }
        }


# Global configuration instance
_config_instance: Optional[SearchConfig] = None


def get_search_config() -> SearchConfig:
    """Get or create global search configuration instance"""
    global _config_instance
    if _config_instance is None:
        _config_instance = SearchConfig()
    return _config_instance


def reload_search_config() -> SearchConfig:
    """Reload configuration from environment (useful for testing)"""
    global _config_instance
    _config_instance = SearchConfig()
    return _config_instance


# Convenience function for validation
def validate_search_config() -> tuple[bool, list[str]]:
    """Validate search configuration"""
    config = get_search_config()
    return config.validate()


if __name__ == "__main__":
    # Test configuration
    config = get_search_config()
    is_valid, warnings = config.validate()

    print("=== Search Configuration Status ===")
    print(f"Valid: {is_valid}")
    print(f"\nStatus Report:")
    import json
    print(json.dumps(config.get_status_report(), indent=2))

    if warnings:
        print(f"\nWarnings:")
        for warning in warnings:
            print(f"  - {warning}")
