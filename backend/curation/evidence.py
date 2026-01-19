"""
证据数据构建

负责从数据库模型构建用于母题判断的上下文数据。
"""

import json
from typing import Any, Dict, Optional

from database.models import (
    Startup,
    LandingPageAnalysis,
    ProductSelectionAnalysis,
    CategoryAnalysis,
)
from .config import SELECTION_ANALYSIS_FIELDS


def _value_present(value: Any) -> bool:
    """检查值是否有效（非空）"""
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip() != ""
    if isinstance(value, list):
        return len(value) > 0
    return True


def _trim_list(values: Any, limit: int = 6) -> Any:
    """截断列表长度"""
    if isinstance(values, list):
        return values[:limit]
    return values


def build_evidence_availability(
    startup: Startup,
    analysis: LandingPageAnalysis,
    selection: Optional[ProductSelectionAnalysis] = None,
    category_analysis: Optional[CategoryAnalysis] = None,
) -> Dict[str, bool]:
    """构建证据字段可用性映射"""
    availability = {
        # LandingPageAnalysis 字段
        "headline_text": _value_present(analysis.headline_text),
        "tagline_text": _value_present(analysis.tagline_text),
        "core_features": _value_present(analysis.core_features),
        "feature_count": analysis.feature_count is not None,
        "value_propositions": _value_present(analysis.value_propositions),
        "target_audience": _value_present(analysis.target_audience),
        "pain_points": _value_present(analysis.pain_points),
        "use_cases": _value_present(analysis.use_cases),
        "pricing_model": _value_present(analysis.pricing_model),
        "pricing_tiers": _value_present(analysis.pricing_tiers),
        "has_free_tier": analysis.has_free_tier is not None,
        "has_trial": analysis.has_trial is not None,
        "cta_count": analysis.cta_count is not None,
        "cta_texts": _value_present(analysis.cta_texts),
        "conversion_funnel_steps": analysis.conversion_funnel_steps is not None,
        "has_instant_value_demo": analysis.has_instant_value_demo is not None,
        "conversion_friendliness_score": analysis.conversion_friendliness_score is not None,
        "potential_moats": _value_present(analysis.potential_moats),
        "uses_before_after": analysis.uses_before_after is not None,
        "uses_emotional_words": analysis.uses_emotional_words is not None,
        "positioning_clarity_score": analysis.positioning_clarity_score is not None,
        "replication_difficulty_score": analysis.replication_difficulty_score is not None,
        "individual_replicability_score": analysis.individual_replicability_score is not None,
        "pain_point_sharpness": analysis.pain_point_sharpness is not None,
        # Startup 字段
        "revenue_30d": startup.revenue_30d is not None,
        "category": _value_present(startup.category),
        "description": _value_present(startup.description),
        "founder_followers": startup.founder_followers is not None,
        "team_size": startup.team_size is not None,
    }

    # ProductSelectionAnalysis 字段
    if selection:
        availability.update({
            "growth_driver": _value_present(selection.growth_driver),
            "is_product_driven": selection.is_product_driven is not None,
            "ip_dependency_score": selection.ip_dependency_score is not None,
            "follower_revenue_ratio": selection.follower_revenue_ratio is not None,
            "tech_complexity_level": _value_present(selection.tech_complexity_level),
            "feature_complexity": _value_present(selection.feature_complexity),
            "ai_dependency_level": _value_present(selection.ai_dependency_level),
            "startup_cost_level": _value_present(selection.startup_cost_level),
            "market_scope": _value_present(selection.market_scope),
            "target_customer": _value_present(selection.target_customer),
            "requires_realtime": selection.requires_realtime is not None,
            "requires_large_data": selection.requires_large_data is not None,
            "requires_compliance": selection.requires_compliance is not None,
        })
    else:
        for field in SELECTION_ANALYSIS_FIELDS:
            availability[field] = False

    # CategoryAnalysis 字段
    if category_analysis:
        availability["market_type"] = _value_present(category_analysis.market_type)
    else:
        availability["market_type"] = False

    return availability



def build_context(
    startup: Startup,
    analysis: LandingPageAnalysis,
    selection: Optional[ProductSelectionAnalysis] = None,
    category_analysis: Optional[CategoryAnalysis] = None,
    evidence_availability: Optional[Dict[str, bool]] = None,
) -> str:
    """构建产品数据 JSON，包含所有可用证据字段"""
    if evidence_availability is None:
        evidence_availability = build_evidence_availability(
            startup, analysis, selection, category_analysis
        )

    payload = {
        # === LandingPageAnalysis 字段 ===
        "headline_text": analysis.headline_text,
        "tagline_text": analysis.tagline_text,
        "core_features": _trim_list(analysis.core_features),
        "feature_count": analysis.feature_count,
        "value_propositions": _trim_list(analysis.value_propositions),
        "target_audience": _trim_list(analysis.target_audience),
        "pain_points": _trim_list(analysis.pain_points),
        "use_cases": _trim_list(analysis.use_cases),
        "pricing_model": analysis.pricing_model,
        "pricing_tiers": _trim_list(analysis.pricing_tiers, limit=3),
        "has_free_tier": analysis.has_free_tier,
        "has_trial": analysis.has_trial,
        "cta_count": analysis.cta_count,
        "cta_texts": _trim_list(analysis.cta_texts),
        "conversion_funnel_steps": analysis.conversion_funnel_steps,
        "has_instant_value_demo": analysis.has_instant_value_demo,
        "conversion_friendliness_score": analysis.conversion_friendliness_score,
        "potential_moats": _trim_list(analysis.potential_moats),
        "uses_before_after": analysis.uses_before_after,
        "uses_emotional_words": analysis.uses_emotional_words,
        "positioning_clarity_score": analysis.positioning_clarity_score,
        "replication_difficulty_score": analysis.replication_difficulty_score,
        "individual_replicability_score": analysis.individual_replicability_score,
        "pain_point_sharpness": analysis.pain_point_sharpness,
        # === Startup 字段 ===
        "revenue_30d": startup.revenue_30d,
        "category": startup.category,
        "description": startup.description,
        "founder_followers": startup.founder_followers,
        "team_size": startup.team_size,
    }

    # === ProductSelectionAnalysis 字段 ===
    if selection:
        payload.update({
            "growth_driver": selection.growth_driver,
            "is_product_driven": selection.is_product_driven,
            "ip_dependency_score": selection.ip_dependency_score,
            "follower_revenue_ratio": selection.follower_revenue_ratio,
            "tech_complexity_level": selection.tech_complexity_level,
            "feature_complexity": selection.feature_complexity,
            "ai_dependency_level": selection.ai_dependency_level,
            "startup_cost_level": selection.startup_cost_level,
            "market_scope": selection.market_scope,
            "target_customer": selection.target_customer,
            "requires_realtime": selection.requires_realtime,
            "requires_large_data": selection.requires_large_data,
            "requires_compliance": selection.requires_compliance,
        })

    # === CategoryAnalysis 字段 ===
    if category_analysis:
        payload["market_type"] = category_analysis.market_type

    return json.dumps(payload, ensure_ascii=False, indent=2, default=str)
