"""
Skill Support API Routes

Provides data access endpoints specifically for skills to query database information
without direct database dependencies.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
from sqlalchemy import func, and_
from database.db import get_sync_session
from database.models import (
    Startup, 
    ProductSelectionAnalysis, 
    LandingPageAnalysis, 
    MotherThemeJudgment
)

router = APIRouter(prefix="/api/skill-support", tags=["skill-support"])


@router.get("/db-stats")
async def get_database_stats() -> Dict[str, Any]:
    """
    Get database statistics for template generation
    
    Returns product counts by revenue, followers, team size, etc.
    """
    with get_sync_session() as session:
        stats = {}
        
        # Total products
        stats["total_products"] = session.query(func.count(Startup.id)).scalar() or 0
        
        # Revenue distribution
        stats["revenue_distribution"] = {
            "0-2k": session.query(func.count(Startup.id)).filter(
                Startup.revenue_30d < 2000
            ).scalar() or 0,
            "2k-10k": session.query(func.count(Startup.id)).filter(
                and_(Startup.revenue_30d >= 2000, Startup.revenue_30d < 10000)
            ).scalar() or 0,
            "10k-50k": session.query(func.count(Startup.id)).filter(
                and_(Startup.revenue_30d >= 10000, Startup.revenue_30d < 50000)
            ).scalar() or 0,
            "50k+": session.query(func.count(Startup.id)).filter(
                Startup.revenue_30d >= 50000
            ).scalar() or 0,
        }
        
        # Followers distribution
        stats["followers_distribution"] = {
            "0-1k": session.query(func.count(Startup.id)).filter(
                Startup.founder_followers < 1000
            ).scalar() or 0,
            "1k-5k": session.query(func.count(Startup.id)).filter(
                and_(Startup.founder_followers >= 1000, Startup.founder_followers < 5000)
            ).scalar() or 0,
            "5k+": session.query(func.count(Startup.id)).filter(
                Startup.founder_followers >= 5000
            ).scalar() or 0,
        }
        
        # Team size distribution
        stats["team_size_distribution"] = {
            "solo": session.query(func.count(Startup.id)).filter(
                Startup.team_size == 1
            ).scalar() or 0,
            "2-3": session.query(func.count(Startup.id)).filter(
                and_(Startup.team_size >= 2, Startup.team_size <= 3)
            ).scalar() or 0,
            "4+": session.query(func.count(Startup.id)).filter(
                Startup.team_size >= 4
            ).scalar() or 0,
        }
        
        return stats


@router.post("/preview-template")
async def preview_template_matches(
    filter_rules: Dict[str, Any],
    limit: int = Query(default=10, ge=1, le=50)
) -> Dict[str, Any]:
    """
    Preview products that match template filter rules
    
    Args:
        filter_rules: Template filter rules (startup, selection, landing_page)
        limit: Maximum number of products to return
        
    Returns:
        List of matching products with basic info
    """
    with get_sync_session() as session:
        query = session.query(Startup)
        
        # Join necessary tables based on filter rules
        if "selection" in filter_rules:
            query = query.join(
                ProductSelectionAnalysis, 
                Startup.id == ProductSelectionAnalysis.startup_id
            )
        
        if "landing_page" in filter_rules:
            query = query.join(
                LandingPageAnalysis, 
                Startup.id == LandingPageAnalysis.startup_id
            )
        
        # Apply startup filters
        if "startup" in filter_rules:
            for field, value in filter_rules["startup"].items():
                if isinstance(value, dict):
                    if "min" in value:
                        query = query.filter(getattr(Startup, field) >= value["min"])
                    if "max" in value:
                        query = query.filter(getattr(Startup, field) <= value["max"])
                elif isinstance(value, list):
                    query = query.filter(getattr(Startup, field).in_(value))
        
        # Apply selection filters
        if "selection" in filter_rules:
            for field, value in filter_rules["selection"].items():
                if isinstance(value, list):
                    query = query.filter(
                        getattr(ProductSelectionAnalysis, field).in_(value)
                    )
        
        # Apply landing_page filters
        if "landing_page" in filter_rules:
            for field, value in filter_rules["landing_page"].items():
                if isinstance(value, dict):
                    if "min" in value:
                        query = query.filter(
                            getattr(LandingPageAnalysis, field) >= value["min"]
                        )
                    if "max" in value:
                        query = query.filter(
                            getattr(LandingPageAnalysis, field) <= value["max"]
                        )
                elif isinstance(value, bool):
                    query = query.filter(getattr(LandingPageAnalysis, field) == value)
        
        # Execute query
        products = query.limit(limit).all()
        
        # Format results
        results = []
        for product in products:
            results.append({
                "id": product.id,
                "name": product.name,
                "slug": product.slug,
                "description": product.description,
                "category": product.category,
                "revenue_30d": product.revenue_30d,
                "founder_followers": product.founder_followers,
                "team_size": product.team_size,
                "website_url": product.website_url
            })
        
        return {
            "total_matches": len(results),
            "products": results
        }


@router.get("/mother-theme-distribution")
async def get_mother_theme_distribution() -> Dict[str, Any]:
    """
    Get distribution of products across mother theme dimensions
    
    Returns counts and combinations of mother theme values to help AI
    discover interesting curation angles.
    
    Note: MotherThemeJudgment uses theme_key + judgment structure,
    not direct fields like success_driver.
    """
    with get_sync_session() as session:
        # Get all mother theme judgments
        judgments = session.query(MotherThemeJudgment).all()
        
        if not judgments:
            return {"error": "No mother theme data available"}
        
        # Group by theme_key and count judgment values
        distributions = {}
        
        for judgment in judgments:
            theme_key = judgment.theme_key
            judgment_value = judgment.judgment
            
            if theme_key not in distributions:
                distributions[theme_key] = {}
            
            if judgment_value:
                distributions[theme_key][judgment_value] = distributions[theme_key].get(judgment_value, 0) + 1
        
        # Find interesting combinations (contrasts)
        combinations = []
        
        # High revenue + low followers
        high_revenue_low_followers = session.query(func.count(Startup.id.distinct())).filter(
            and_(
                Startup.revenue_30d >= 10000,
                Startup.founder_followers < 1000
            )
        ).scalar() or 0
        
        if high_revenue_low_followers > 0:
            combinations.append({
                "pattern": "high_revenue_low_followers",
                "count": high_revenue_low_followers,
                "description": "高收入但低粉丝的产品"
            })
        
        # Simple features but profitable
        simple_profitable = session.query(func.count(Startup.id.distinct())).join(
            ProductSelectionAnalysis, Startup.id == ProductSelectionAnalysis.startup_id
        ).filter(
            and_(
                ProductSelectionAnalysis.feature_complexity == "simple",
                Startup.revenue_30d >= 5000
            )
        ).scalar() or 0
        
        if simple_profitable > 0:
            combinations.append({
                "pattern": "simple_features_profitable",
                "count": simple_profitable,
                "description": "功能简单但盈利的产品"
            })
        
        # No AI but profitable
        no_ai_profitable = session.query(func.count(Startup.id.distinct())).join(
            ProductSelectionAnalysis, Startup.id == ProductSelectionAnalysis.startup_id
        ).filter(
            and_(
                ProductSelectionAnalysis.ai_dependency_level.in_(["none", "light"]),
                Startup.revenue_30d >= 10000
            )
        ).scalar() or 0
        
        if no_ai_profitable > 0:
            combinations.append({
                "pattern": "no_ai_profitable",
                "count": no_ai_profitable,
                "description": "不依赖AI但盈利的产品"
            })
        
        # Vertical niche success
        vertical_success = session.query(func.count(Startup.id.distinct())).join(
            ProductSelectionAnalysis, Startup.id == ProductSelectionAnalysis.startup_id
        ).filter(
            and_(
                ProductSelectionAnalysis.market_scope == "vertical",
                Startup.revenue_30d >= 3000
            )
        ).scalar() or 0
        
        if vertical_success > 0:
            combinations.append({
                "pattern": "vertical_niche_success",
                "count": vertical_success,
                "description": "垂直细分市场成功案例"
            })
        
        # Small team high revenue
        small_team_high_revenue = session.query(func.count(Startup.id)).filter(
            and_(
                Startup.team_size <= 2,
                Startup.revenue_30d >= 10000
            )
        ).scalar() or 0
        
        if small_team_high_revenue > 0:
            combinations.append({
                "pattern": "small_team_high_revenue",
                "count": small_team_high_revenue,
                "description": "小团队高收入产品"
            })
        
        return {
            "total_products_with_themes": len(set(j.startup_id for j in judgments)),
            "total_judgments": len(judgments),
            "distributions": distributions,
            "interesting_combinations": combinations
        }


@router.get("/product-characteristics")
async def get_product_characteristics() -> Dict[str, Any]:
    """
    Get aggregated product characteristics for opportunity discovery
    
    Returns distributions of technical complexity, market scope, customer types, etc.
    """
    with get_sync_session() as session:
        analyses = session.query(ProductSelectionAnalysis).all()
        
        if not analyses:
            return {"error": "No product analysis data available"}
        
        characteristics = {
            "growth_driver": {},
            "feature_complexity": {},
            "ai_dependency_level": {},
            "startup_cost_level": {},
            "market_scope": {},
            "target_customer": {},
            "tech_complexity_level": {}
        }
        
        for analysis in analyses:
            for field in characteristics.keys():
                value = getattr(analysis, field, None)
                if value:
                    characteristics[field][value] = characteristics[field].get(value, 0) + 1
        
        return {
            "total_analyzed_products": len(analyses),
            "characteristics": characteristics
        }
