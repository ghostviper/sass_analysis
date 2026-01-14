"""
Agent module for BuildWhat
"""

from .tools import query_startups, get_category_analysis, get_trend_report, get_leaderboard

# Import Claude Agent SDK client (optional, for backward compatibility)
try:
    from .client import SaaSAnalysisAgent
    # Alias for new name
    BuildWhatAgent = SaaSAnalysisAgent
    __all__ = [
        "query_startups",
        "get_category_analysis",
        "get_trend_report",
        "get_leaderboard",
        "BuildWhatAgent",
        "SaaSAnalysisAgent"
    ]
except ImportError:
    # Claude SDK not installed yet
    __all__ = [
        "query_startups",
        "get_category_analysis",
        "get_trend_report",
        "get_leaderboard",
    ]
