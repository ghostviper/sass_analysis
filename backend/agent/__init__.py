"""
Agent module for SaaS Analysis
"""

from .tools import query_startups, get_category_analysis, get_trend_report, get_leaderboard
from .prompts import SYSTEM_PROMPT

# Import Claude Agent SDK client (optional, for backward compatibility)
try:
    from .client import SaaSAnalysisAgent
    __all__ = [
        "query_startups",
        "get_category_analysis",
        "get_trend_report",
        "get_leaderboard",
        "SYSTEM_PROMPT",
        "SaaSAnalysisAgent"
    ]
except ImportError:
    # Claude SDK not installed yet
    __all__ = [
        "query_startups",
        "get_category_analysis",
        "get_trend_report",
        "get_leaderboard",
        "SYSTEM_PROMPT"
    ]
