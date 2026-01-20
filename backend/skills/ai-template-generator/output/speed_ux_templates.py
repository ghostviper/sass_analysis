CurationTemplate(
    key="lightweight_wins",
    title_zh="轻量即速度",
    title_en="Lightweight Wins",
    description_zh="筛选以“轻量体验”为差异化、特性复杂度为简单或中等、AI依赖低或无、定位清晰、且产品驱动增长的产品。围绕速度与轻量体验的结构性空白，强调用更少特性更快交付可感知价值。",
    description_en="Filters products where lightweight experience is the differentiation, feature complexity is simple or moderate, AI dependency is none or light, positioning is sharp or concrete, and success is product-driven. Targets the structural gap in speed/lightweight experience by showing fewer features can deliver faster perceived value.",
    insight_zh="以“少即是多”的MVP验证速度：先做可秒懂的价值演示，再决定是否加功能。",
    insight_en="Validate speed with an MVP mindset: ship a demo that shows value in seconds, then decide what to add.",
    tag_zh="速度与轻量",
    tag_en="Speed & Lightweight",
    tag_color="emerald",
    curation_type="contrast",
    filter_rules={
        "startup": {
            "revenue_30d": {"min": 2000},
            "founder_followers": {"max": 1000},
            "team_size": {"max": 2}
        },
        "selection": {
            "feature_complexity": ["simple", "moderate"],
            "ai_dependency_level": ["none", "light"],
            "growth_driver": ["product_driven"]
        },
        "landing_page": {
            "feature_count": {"max": 5},
            "has_instant_value_demo": True,
            "conversion_friendliness_score": {"min": 7.0}
        }
    },
    conflict_dimensions=["feature_count vs perceived_speed", "lightweight vs complex_competitors"],
    min_products=5,
    max_products=12,
    priority=9
),
CurationTemplate(
    key="simple_outperforms_complex",
    title_zh="简单战胜复杂",
    title_en="Simple Outperforms Complex",
    description_zh="筛选以体验差异化为主、特性复杂度简单、AI依赖低或无、定位锋利或场景具体、且产品驱动增长的中高收入产品。反直觉洞察：功能更少的产品也能获得更高收入。",
    description_en="Filters higher-revenue products with experience differentiation, simple complexity, none/light AI reliance, sharp positioning, and product-driven growth. Counterintuitive: fewer features can drive higher revenue.",
    insight_zh="优先打磨“一件事做到极致”的体验闭环，用清晰价值替代功能堆叠。",
    insight_en="Polish a single, excellent experience loop; trade feature bloat for clear, delivered value.",
    tag_zh="体验差异化",
    tag_en="Experience Differentiation",
    tag_color="blue",
    curation_type="contrast",
    filter_rules={
        "startup": {
            "revenue_30d": {"min": 10000},
            "founder_followers": {"max": 1000},
            "team_size": {"max": 2}
        },
        "selection": {
            "feature_complexity": ["simple"],
            "ai_dependency_level": ["none", "light"],
            "growth_driver": ["product_driven"]
        },
        "landing_page": {
            "feature_count": {"max": 5},
            "has_instant_value_demo": True,
            "conversion_friendliness_score": {"min": 7.0}
        }
    },
    conflict_dimensions=["feature_count vs revenue_level", "simplicity_vs_complexity"],
    min_products=5,
    max_products=10,
    priority=8
)