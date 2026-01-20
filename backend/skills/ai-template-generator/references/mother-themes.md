# Mother Themes Reference

Complete definitions of all 9 mother themes used in the curation system.

## Overview

Mother themes are organized in 3 layers:
1. **Screening Layer** (筛选层): Is this opportunity worth pursuing?
2. **Action Layer** (行动层): If I want to do it, is it feasible? How?
3. **Attribution Layer** (归因层): Why did it succeed? What can I learn?

## Screening Layer (筛选层)

### 1. Opportunity Validity (机会真实性)

**Purpose**: Distinguish real market opportunities from pseudo-opportunities

**Options**:
- 真实机会 (Real opportunity)
- 存在风险 (Has risks)
- 伪机会 (Pseudo-opportunity)
- 证据不足/无法判断 (Insufficient evidence)

**Real Opportunity Indicators**:
- Specific, quantifiable pain points (e.g., "spend 5 hours/week doing X")
- Clear target audience (e.g., "Shopify store owners" not "e-commerce sellers")
- CTAs point to concrete actions
- Value propositions describe specific outcomes

**Pseudo-Opportunity Indicators** (2+ means pseudo):
- Abstract pain points (e.g., "improve efficiency")
- All value propositions are aspirational without concrete features
- Vague CTAs (e.g., "start your journey")
- Overly broad target audience (e.g., "everyone")

**Template Usage**:
- Filter for "真实机会" in action/cognitive templates
- Contrast "真实机会" vs "伪机会" for educational templates
- Combine with demand_type for acquisition strategy templates

### 2. Demand Type (需求类型)

**Purpose**: Understand how users discover and acquire this product

**Options**:
- 主动搜索型 (Active search)
- 触发认知型 (Triggered awareness)
- 需教育型 (Requires education)
- 证据不足/无法判断 (Insufficient evidence)

**Active Search Indicators**:
- Pain points users would actively search for (e.g., "PDF to Word", "invoice management")
- Clear before/after demonstration
- Problem-focused positioning

**Triggered Awareness Indicators**:
- Latent needs users recognize when shown (e.g., "team collaboration inefficiency")
- Solution-focused positioning
- Requires demonstration of value

**Requires Education Indicators**:
- New concepts or paradigms users don't know exist
- Novel approaches to familiar problems
- Requires significant context to understand value

**Template Usage**:
- "主动搜索型" for low-risk, SEO-friendly opportunities
- Contrast high revenue with "需教育型" to show exceptions
- Combine with entry_barrier for feasibility assessment

## Action Layer (行动层)

### 3. Solo Feasibility (独立可行性)

**Purpose**: Can one person build and maintain this product?

**Options**:
- 非常适合 (Very suitable)
- 有挑战但可行 (Challenging but feasible)
- 不适合 (Not suitable)
- 证据不足/无法判断 (Insufficient evidence)

**Very Suitable Indicators**:
- tech_complexity_level = low/medium
- feature_complexity = simple/moderate
- team_size <= 2
- No heavy AI or real-time data dependencies

**Challenging But Feasible Indicators**:
- tech_complexity_level = medium
- Moderate feature complexity
- Requires specific domain knowledge
- Can be phased or simplified

**Not Suitable Indicators**:
- tech_complexity_level = high
- Requires real-time systems + big data
- requires_compliance = true
- Needs large team coordination

**Template Usage**:
- Core filter for indie hacker templates
- Contrast with entry_barrier for "hard but doable" themes
- Combine with mvp_clarity for actionable templates

### 4. Entry Barrier (入场门槛)

**Purpose**: Time and capital investment needed to start

**Options**:
- 低门槛快启动 (Low barrier, quick start)
- 中等投入 (Medium investment)
- 高门槛 (High barrier)
- 证据不足/无法判断 (Insufficient evidence)

**Low Barrier Indicators**:
- startup_cost_level = low
- feature_count <= 5
- Core features simple and clear
- MVP achievable in 2 weeks

**Medium Investment Indicators**:
- startup_cost_level = medium
- Moderate feature_count
- 1-2 months to MVP
- Some specialized knowledge needed

**High Barrier Indicators**:
- startup_cost_level = high
- ai_dependency_level = heavy
- requires_compliance = true
- Needs significant initial data

**Template Usage**:
- "低门槛快启动" for weekend project templates
- Contrast high barrier with solo success for moat templates
- Combine with primary_risk for risk assessment

### 5. Primary Risk (主要风险)

**Purpose**: If this direction fails, what's the most likely cause?

**Options**:
- 技术实现 (Technical implementation)
- 市场验证 (Market validation)
- 用户获取 (User acquisition)
- 变现转化 (Monetization)
- 证据不足/无法判断 (Insufficient evidence)

**Technical Implementation Risk**:
- tech_complexity_level = high
- ai_dependency_level = heavy
- requires_realtime = true
- Complex infrastructure needs

**Market Validation Risk**:
- demand_type = 需教育型
- Abstract pain points
- Unclear target audience
- Novel concept without precedent

**User Acquisition Risk**:
- Weak potential moats
- demand_type != 主动搜索型
- Overly broad target_audience
- High CAC market

**Monetization Risk**:
- has_free_tier = true but unclear pricing_tiers
- Unclear pricing_model
- target_customer = b2c without clear pay points
- Low willingness to pay indicators

**Template Usage**:
- Filter out specific risks for risk-averse templates
- Highlight products that overcome typical risks
- Educational templates about risk mitigation

### 6. MVP Clarity (MVP清晰度)

**Purpose**: Is the minimum viable product clearly defined?

**Options**:
- 清晰可执行 (Clear and actionable)
- 基本清晰 (Basically clear)
- 模糊 (Vague)
- 证据不足/无法判断 (Insufficient evidence)

**Clear and Actionable Indicators**:
- core_features has 1-3 clear functions
- has_instant_value_demo = true
- value_propositions focus on single value point
- Headline clearly states what it does

**Basically Clear Indicators**:
- core_features identifiable but numerous (4-8)
- value_propositions have multiple directions
- Some ambiguity in scope

**Vague Indicators**:
- Too many or too abstract core_features
- Scattered value_propositions
- Overly broad headline_text
- Unclear what to build first

**Template Usage**:
- Essential for action-oriented templates
- "清晰可执行" for quick-start templates
- Contrast with success for "figure it out" themes

## Attribution Layer (归因层)

### 7. Success Driver (成功驱动因素)

**Purpose**: What primarily drives this product's success?

**Options**:
- 产品驱动 (Product-driven)
- IP/创作者驱动 (IP/Creator-driven)
- 内容驱动 (Content-driven)
- 渠道驱动 (Channel-driven)
- 证据不足/无法判断 (Insufficient evidence)

**Product-Driven Indicators**:
- growth_driver = product_driven
- is_product_driven = true
- Product features/experience are core selling point
- Low dependency on founder brand

**IP/Creator-Driven Indicators**:
- growth_driver = ip_driven
- High founder_followers
- Product strongly tied to founder personal brand
- Community-first approach

**Content-Driven Indicators**:
- growth_driver = content_driven
- Obvious blog/tutorial/course content
- SEO-focused approach
- Educational positioning

**Channel-Driven Indicators**:
- Relies on specific platform (Shopify app, Chrome extension, Notion integration)
- Inferred from description or core_features
- Marketplace distribution

**Template Usage**:
- Core contrast dimension (product vs IP)
- Filter for replicable patterns (product-driven)
- Identify distribution strategies

### 8. Positioning Insight (定位洞察)

**Purpose**: What's noteworthy about this product's positioning strategy?

**Options**:
- 精准垂直 (Precise vertical)
- 差异化定价 (Differentiated pricing)
- 痛点锋利 (Sharp pain point)
- 场景具体 (Specific scenario)
- 无明显亮点 (No obvious highlight)
- 证据不足/无法判断 (Insufficient evidence)

**Precise Vertical Indicators**:
- Very specific target_audience (e.g., "Shopify store owners" not "e-commerce sellers")
- market_scope = vertical
- Industry-specific features

**Differentiated Pricing Indicators**:
- Innovative pricing_model (usage-based, one-time, lifetime deal)
- Pricing is part of value proposition
- Transparent or unique pricing structure

**Sharp Pain Point Indicators**:
- Very specific pain_points with numbers/scenarios
- uses_before_after = true
- Quantifiable problem description

**Specific Scenario Indicators**:
- Clear, concrete use_cases
- headline_text describes usage scenario
- Workflow-focused positioning

**Template Usage**:
- Cognitive templates highlighting strategies
- Educational content about positioning
- Pattern recognition for founders

### 9. Differentiation Point (差异化点)

**Purpose**: How does this product stand out from competitors?

**Options**:
- 功能差异化 (Feature differentiation)
- 体验差异化 (Experience differentiation)
- 人群差异化 (Audience differentiation)
- 定价差异化 (Pricing differentiation)
- 无明显差异化 (No obvious differentiation)
- 证据不足/无法判断 (Insufficient evidence)

**Feature Differentiation Indicators**:
- potential_moats include tech/feature-related barriers
- core_features describe unique capabilities
- Patent or proprietary technology

**Experience Differentiation Indicators**:
- has_instant_value_demo = true
- value_propositions emphasize simplicity/speed/ease
- Superior UX/UI focus
- Faster workflow

**Audience Differentiation Indicators**:
- Very segmented target_audience
- market_scope = vertical
- Role or industry-specific features

**Pricing Differentiation Indicators**:
- pricing_model is non-standard subscription
- One-time purchase, usage-based, or lifetime deal
- Significantly different price point

**No Obvious Differentiation Indicators**:
- None of the above satisfied
- Highly similar to existing products
- Commodity positioning

**Template Usage**:
- Identify unique angles for templates
- Educational content about differentiation
- Contrast templates (differentiated vs commodity)

## Cross-Theme Patterns

### High-Value Combinations

**Product-Driven + Low Followers**:
- Proves product quality over personal brand
- Replicable for indie hackers
- Template: "Low followers, high revenue"

**Low Barrier + Clear MVP + Real Opportunity**:
- Ideal for quick starts
- Low-risk validation
- Template: "Weekend launchable"

**High Barrier + Solo Feasible**:
- Technical moat opportunity
- Less competition
- Template: "High barrier but solo-doable"

**Active Search + Real Opportunity + Low Monetization Risk**:
- Easiest path to revenue
- Clear demand signals
- Template: "Easy monetization"

**Precise Vertical + Real Opportunity**:
- Niche domination potential
- Higher willingness to pay
- Template: "Vertical niche success"

### Anti-Patterns to Avoid

**Education Required + High Barrier**:
- Double risk (market + execution)
- Avoid unless strong evidence

**Vague MVP + High Entry Barrier**:
- Unclear execution path
- High failure risk

**Pseudo-Opportunity + Any Success Metrics**:
- Likely unsustainable
- Avoid in templates

**No Differentiation + Broad Audience**:
- Commodity market
- Low template value

## Template Filter Strategy

### Using Mother Themes in Filters

**Exact Match**:
```python
"mother_theme": {
    "success_driver": ["产品驱动"]
}
```

**Multiple Options**:
```python
"mother_theme": {
    "entry_barrier": ["低门槛快启动", "中等投入"]
}
```

**Exclusion**:
```python
"mother_theme": {
    "primary_risk": {"not": ["变现转化"]}
}
```

**Combination**:
```python
"mother_theme": {
    "opportunity_validity": ["真实机会"],
    "demand_type": ["主动搜索型"],
    "solo_feasibility": ["非常适合"]
}
```

### Strategic Filter Design

**For Contrast Templates**:
- Use opposing themes (low X + high Y)
- Highlight unexpected combinations
- Example: Low followers + Product-driven + High revenue

**For Cognitive Templates**:
- Focus on positioning/differentiation themes
- Combine with success patterns
- Example: Precise vertical + Real opportunity

**For Action Templates**:
- Emphasize feasibility themes
- Reduce risk factors
- Example: Low barrier + Clear MVP + Low risk

**For Niche Templates**:
- Use specific audience/channel themes
- Narrow scope deliberately
- Example: Channel-driven + Specific category

## Mother Theme Evolution

### When to Add New Themes

Consider adding themes when:
- Recurring patterns not captured by existing themes
- New market dynamics emerge
- User feedback indicates missing dimensions
- Data shows unexplored correlations

### Theme Validation Criteria

New themes should:
- Provide unique strategic insight
- Be inferrable from available data
- Have clear option definitions
- Support actionable decisions
- Not overlap significantly with existing themes

### Maintaining Theme Quality

Regular review:
- Are all options being used?
- Do judgments align with product success?
- Are there ambiguous cases?
- Do themes need refinement?