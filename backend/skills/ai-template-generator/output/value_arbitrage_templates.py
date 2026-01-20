CurationTemplate(
    key="simple_features_big_profits",
    title_zh="简单功能大盈利",
    title_en="Simple Features, Big Profits",
    description_zh="挑战'功能越复杂越赚钱'的固有认知，筛选简单功能却实现可观营收的产品",
    description_en="Challenge the assumption that complex features drive profits by curating simple products with substantial revenue.",
    insight_zh="聚焦核心价值而非功能堆砌，精准解决单一痛点往往比大而全更有效",
    insight_en="Focus on core value over feature bloat; solving one sharp pain point often beats comprehensive solutions.",
    tag_zh="简单盈利",
    tag_en="Simple Profits",
    tag_color="emerald",
    curation_type="contrast",
    filter_rules={
        "startup": {
            "revenue_30d": {"min": 5000},
            "startup_cost_level": ["low", "medium"]
        },
        "selection": {
            "feature_complexity": ["simple"],
            "success_driver": ["product_driven"],
            "positioning_insight": {"contains": ["痛点锋利", "场景具体"]}
        },
        "mother_theme": {
            "success_driver": ["产品驱动"],
            "entry_barrier": ["低门槛快启动"],
            "mvp_clarity": ["清晰可执行"]
        }
    },
    conflict_dimensions=["complexity_revenue", "simple_profitable"],
    min_products=4,
    max_products=8,
    priority=9
),

CurationTemplate(
    key="weekend_mvp_product_driven",
    title_zh="周末MVP产品驱动",
    title_en="Weekend MVP Product Driven",
    description_zh="为想要快速验证想法的产品人精选低启动成本、产品驱动的简单项目",
    description_en="Curate low-cost, product-driven simple projects for makers wanting to validate ideas quickly.",
    insight_zh="用清晰MVP和具体定价策略快速测试市场，通过产品驱动增长避免早期营销负担",
    insight_en="Test markets quickly with clear MVPs and specific pricing; avoid early marketing burden through product-driven growth.",
    tag_zh="快速验证",
    tag_en="Quick Validation",
    tag_color="blue",
    curation_type="action",
    filter_rules={
        "startup": {
            "revenue_30d": {"min": 2000},
            "startup_cost_level": ["low"]
        },
        "selection": {
            "feature_complexity": ["simple"],
            "success_driver": ["product_driven"],
            "pricing_strategy": {"contains": ["价值错配", "个人价"]},
            "startup_cost_level": ["low"]
        },
        "mother_theme": {
            "success_driver": ["产品驱动"],
            "entry_barrier": ["低门槛快启动"],
            "mvp_clarity": ["清晰可执行"],
            "solo_feasibility": ["非常适合"]
        }
    },
    conflict_dimensions=["time_complexity", "effort_result"],
    min_products=5,
    max_products=10,
    priority=8
)