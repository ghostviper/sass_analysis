"""
Agent tools - 兼容层

工具已拆分到 tools/ 目录下的模块中，此文件保留用于向后兼容。

模块结构:
- tools/base.py: 基础工具（产品查询、赛道分析、趋势报告）
- tools/founder.py: 创始人相关工具
- tools/search.py: Web 搜索工具
- tools/semantic.py: 语义搜索工具（向量检索）
"""

# 从新模块导入所有工具，保持向后兼容
from agent.tools import (
    # Decorator
    tool,
    HAS_CLAUDE_SDK,
    # 底层函数
    _build_product_profile,
    _get_startups_by_ids,
    _search_startups,
    _browse_startups,
    _get_founder_products,
    # 高级查询函数
    query_startups,
    get_category_analysis,
    get_trend_report,
    get_leaderboard,
    # MCP 工具
    get_startups_by_ids_tool,
    search_startups_tool,
    browse_startups_tool,
    get_category_analysis_tool,
    get_trend_report_tool,
    get_leaderboard_tool,
    get_founder_products_tool,
    web_search_tool,
    semantic_search_products_tool,
    find_similar_products_tool,
    semantic_search_categories_tool,
    discover_products_by_scenario_tool,
)

# 导出所有工具
__all__ = [
    "tool",
    "HAS_CLAUDE_SDK",
    "_build_product_profile",
    "_get_startups_by_ids",
    "_search_startups",
    "_browse_startups",
    "_get_founder_products",
    "query_startups",
    "get_category_analysis",
    "get_trend_report",
    "get_leaderboard",
    "get_startups_by_ids_tool",
    "search_startups_tool",
    "browse_startups_tool",
    "get_category_analysis_tool",
    "get_trend_report_tool",
    "get_leaderboard_tool",
    "get_founder_products_tool",
    "web_search_tool",
    "semantic_search_products_tool",
    "find_similar_products_tool",
    "semantic_search_categories_tool",
    "discover_products_by_scenario_tool",
]
