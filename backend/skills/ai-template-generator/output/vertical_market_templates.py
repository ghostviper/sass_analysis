CurationTemplate(
    key="vertical_contrast_low_followers_high_revenue",
    title_zh="垂直小众，高效变现",
    title_en="Niche Vertical, High Revenue",
    description_zh="筛选市场投向为垂直、目标客户为B2B SMB、特征简单、成本低、MVP清晰、需求主动搜索的产品。打破‘垂直市场收入低’的认知，展示小众垂直的高效变现潜力，冲突维度包括垂直市场小 vs 高收入、低粉丝 vs 高收入。",
    description_en="Filter products with market_scope=vertical, target_customer=b2b_smb, feature_complexity=simple or moderate, startup_cost_level=low or medium, mvp_clarity=clear or basic, demand_type=active search. Break the myth that vertical markets have low revenue, showing the high monetization potential of niche verticals, with conflict dimensions including small vertical market vs high revenue and low followers vs high revenue.",
    insight_zh="垂直市场虽小，但聚焦精准痛点可实现高收入，无需大量粉丝支持。",
    insight_en="Vertical markets are small but focused on precise pain points can achieve high revenue without many followers.",
    tag_zh="垂直市场",
    tag_en="Vertical Market",
    tag_color="emerald",
    curation_type="contrast",
    filter_rules={
        "startup": {
            "revenue_30d": {"min": 5000},
            "founder_followers": {"max": 1000}
        },
        "selection": {
            "market_scope": ["vertical"],
            "target_customer": ["b2b_smb"],
            "feature_complexity": ["simple", "moderate"],
            "startup_cost_level": ["low", "medium"]
        },
        "mother_theme": {
            "mvp_clarity": ["清晰可执行", "基本清晰"],
            "demand_type": ["主动搜索型", "触发认知型"]
        }
    },
    conflict_dimensions=["market_scope_vertical", "revenue_high", "followers_low"],
    min_products=3,
    max_products=8,
    priority=9
),
CurationTemplate(
    key="vertical_cognitive_blue_ocean",
    title_zh="垂直蓝海，认知新篇",
    title_en="Vertical Blue Ocean, New Perspective",
    description_zh="基于市场投向为垂直、目标客户为B2B SMB、特征简单、成本低、MVP清晰、需求主动搜索的产品。提供新视角，垂直市场渗透不足但充满机会，转变‘垂直市场难入’的认知，聚焦定位和定价洞察。",
    description_en="Based on products with market_scope=vertical, target_customer=b2b_smb, feature_complexity=simple or moderate, startup_cost_level=low or medium, mvp_clarity=clear or basic, demand_type=active search. Provide a new perspective that vertical markets are under-penetrated but full of opportunities, shifting the mindset that vertical markets are hard to enter, focusing on positioning and pricing insights.",
    insight_zh="垂直市场未充分开发，聚焦精准痛点可快速启动，是B2B SMB的蓝海战略。",
    insight_en="Vertical markets are under-penetrated but focused precise pain points can start quickly, a blue ocean strategy for B2B SMB.",
    tag_zh="蓝海战略",
    tag_en="Blue Ocean",
    tag_color="blue",
    curation_type="cognitive",
    filter_rules={
        "selection": {
            "market_scope": ["vertical"],
            "target_customer": ["b2b_smb"],
            "feature_complexity": ["simple", "moderate"],
            "startup_cost_level": ["low", "medium"]
        },
        "mother_theme": {
            "mvp_clarity": ["清晰可执行", "基本清晰"],
            "demand_type": ["主动搜索型", "触发认知型"]
        }
    },
    conflict_dimensions=[],
    min_products=5,
    max_products=15,
    priority=7
)