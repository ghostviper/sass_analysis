"""
Backend API Client for AI Template Generator Skill

Provides methods to query backend API endpoints instead of direct database access.
"""

import os
import httpx
from typing import Dict, Any, Optional


class BackendAPIClient:
    """Client for backend skill support API"""
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: int = 30
    ):
        # Default to localhost if not specified
        self.base_url = (
            base_url or 
            os.getenv("BACKEND_API_URL", "http://localhost:8001")
        ).rstrip("/")
        
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            headers={"Content-Type": "application/json"}
        )
    
    async def get_db_stats(self) -> Dict[str, Any]:
        """
        Get database statistics
        
        Returns:
            Dictionary with product counts by revenue, followers, team size, etc.
        """
        url = f"{self.base_url}/api/skill-support/db-stats"
        
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise Exception(f"API error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")
    
    async def preview_template(
        self,
        filter_rules: Dict[str, Any],
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Preview products matching template filter rules
        
        Args:
            filter_rules: Template filter rules
            limit: Maximum number of products to return
            
        Returns:
            Dictionary with total_matches and products list
        """
        url = f"{self.base_url}/api/skill-support/preview-template"
        
        try:
            response = await self.client.post(
                url,
                json=filter_rules,
                params={"limit": limit}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise Exception(f"API error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    
    async def get_mother_theme_distribution(self) -> Dict[str, Any]:
        """
        Get mother theme distribution and interesting combinations
        
        Returns:
            Dictionary with theme distributions and pattern combinations
        """
        url = f"{self.base_url}/api/skill-support/mother-theme-distribution"
        
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise Exception(f"API error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")
    
    async def get_product_characteristics(self) -> Dict[str, Any]:
        """
        Get product characteristics distribution
        
        Returns:
            Dictionary with technical and market characteristics
        """
        url = f"{self.base_url}/api/skill-support/product-characteristics"
        
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise Exception(f"API error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")
