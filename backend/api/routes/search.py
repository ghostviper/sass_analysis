"""
Search API test endpoints

Provides test endpoints for verifying search functionality.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from services.search.factory import SearchServiceFactory, web_search, search_site

router = APIRouter()


class SearchTestRequest(BaseModel):
    query: str
    limit: int = 5
    site: Optional[str] = None


@router.get("/search/status")
async def search_status():
    """
    Get search services status and configuration

    Returns:
        Configuration status for all search backends
    """
    from config.search_config import get_search_config

    config = get_search_config()
    is_valid, warnings = config.validate()

    return {
        "valid": is_valid,
        "warnings": warnings,
        "status": config.get_status_report(),
        "available": SearchServiceFactory.is_available(),
    }


@router.get("/search/health")
async def search_health():
    """
    Perform health check on search service

    Returns:
        Health status
    """
    health = await SearchServiceFactory.health_check()
    return health


@router.post("/search/test")
async def test_search(request: SearchTestRequest):
    """
    Test web search functionality

    Args:
        request: Search request with query, limit, and optional site

    Returns:
        Search results
    """
    try:
        if request.site:
            results = await search_site(
                query=request.query,
                site=request.site,
                limit=request.limit
            )
        else:
            results = await web_search(
                query=request.query,
                limit=request.limit
            )

        return {
            "success": True,
            "query": request.query,
            "site": request.site,
            "results": results.results if hasattr(results, 'results') else results,
            "count": len(results.results) if hasattr(results, 'results') else len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search/test-reddit")
async def test_reddit_search(request: SearchTestRequest):
    """
    Test Reddit search via site:reddit.com

    Args:
        request: Search request

    Returns:
        Reddit search results
    """
    try:
        results = await search_site(
            query=request.query,
            site="reddit.com",
            limit=request.limit
        )

        return {
            "success": True,
            "query": request.query,
            "channel": "reddit",
            "results": results.results if hasattr(results, 'results') else results,
            "count": len(results.results) if hasattr(results, 'results') else len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search/test-indiehackers")
async def test_indiehackers_search(request: SearchTestRequest):
    """
    Test IndieHackers search via site:indiehackers.com

    Args:
        request: Search request

    Returns:
        IndieHackers search results
    """
    try:
        results = await search_site(
            query=request.query,
            site="indiehackers.com",
            limit=request.limit
        )

        return {
            "success": True,
            "query": request.query,
            "channel": "indiehackers",
            "results": results.results if hasattr(results, 'results') else results,
            "count": len(results.results) if hasattr(results, 'results') else len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search/test-producthunt")
async def test_producthunt_search(request: SearchTestRequest):
    """
    Test Product Hunt search via site:producthunt.com

    Args:
        request: Search request

    Returns:
        Product Hunt search results
    """
    try:
        results = await search_site(
            query=request.query,
            site="producthunt.com",
            limit=request.limit
        )

        return {
            "success": True,
            "query": request.query,
            "channel": "producthunt",
            "results": results.results if hasattr(results, 'results') else results,
            "count": len(results.results) if hasattr(results, 'results') else len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
