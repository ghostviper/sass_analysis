"""
Agent tools package

工具模块拆分：
- base.py: 基础工具（产品查询、赛道分析、趋势报告）
- founder.py: 创始人相关工具
- search.py: 搜索工具（Web搜索）
- semantic.py: 语义搜索工具（向量检索）
"""

from .base import (
    # 底层函数
    _build_product_profile,
    _get_startups_by_ids,
    _search_startups,
    _browse_startups,
    # 工具函数
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
)

from .founder import (
    _get_founder_products,
    get_founder_products_tool,
)

from .search import (
    web_search_tool,
)

from .semantic import (
    semantic_search_products_tool,
    find_similar_products_tool,
    semantic_search_categories_tool,
    discover_products_by_scenario_tool,
)

# 兼容旧的导入方式
from .decorator import tool, HAS_CLAUDE_SDK
