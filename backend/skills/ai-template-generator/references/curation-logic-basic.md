# Curation Logic and Discovery Principles

## Purpose

This document defines the logical framework AI should follow when discovering new curation opportunities and generating observation/guidance pairs.

## Core Principles

### 1. Value-Driven Discovery

Every curation template must provide **clear value** to at least one user persona:

- **Solo Indie Hacker**: Actionable, low-barrier opportunities
- **First-Time Founder**: Risk-reduction, validation patterns
- **Serial Entrepreneur**: Non-obvious insights, market gaps
- **Product Manager**: Competitive intelligence, success patterns

### 2. Data-Driven Insights

Templates should be based on **actual patterns** in the data, not hypothetical scenarios:

- Minimum 3-5 products should match the filters
- Patterns should be statistically significant
- Avoid over-fitting to outliers

### 3. Contrast and Surprise

The most valuable templates create **"aha moments"** by revealing:

- Counter-intuitive patterns (low X + high Y)
- Hidden opportunities (underserved niches)
- Success factors (what actually works)
- Risk mitigation (what to avoid)

## Discovery Process

### Step 1: Analyze Mother Theme Distributions

Look for **imbalances and clusters** in mother theme data:

```
Example patterns to discover:
- Many "产品驱动" but few "IP驱动" → Opportunity for product-first strategies
- High "真实机会" + "主动搜索型" → Validated demand patterns
- "非常适合" solo + "低门槛" → Weekend project opportunities
```

### Step 2: Find Interesting Combinations

Identify **multi-dimensional patterns** that create contrast:

**Contrast Patterns** (反差型):
- High technical complexity + Small team + High revenue
- Low followers + High revenue + Product-driven
- Simple features + High pricing + B2B
- No AI + High revenue + Tech category

**Cognitive Patterns** (认知型):
- Vertical market + High willingness to pay
- Pricing innovation + Differentiation
- Content-driven + B2B SaaS
- Platform ecosystem + Low CAC

**Action Patterns** (行动型):
- Low barrier + Clear MVP + Solo feasible
- Active search + Real opportunity + Low monetization risk
- Simple complexity + Low cost + Quick launch

**Niche Patterns** (利基型):
- Specific customer type + Vertical market
- Platform-specific + Channel-driven
- Developer tools + B2D + Technical

### Step 3: Validate Product Count

Check if the pattern matches enough products:

```python
Ideal range: 5-15 products
Minimum: 3 products
Maximum: 30 products (too broad)
```

### Step 4: Extract Insight

Formulate the **actionable takeaway**:

- What does this pattern teach us?
- What should builders do differently?
- What assumption does it challenge?
- What risk does it mitigate?

## Observation Generation Rules

### Format

```
观察维度: [具体的产品特征组合]
```

### Guidelines

1. **Be Specific**: "高技术门槛但小团队成功" > "成功的产品"
2. **Multi-Dimensional**: Combine 2-3 characteristics
3. **Measurable**: Use quantifiable criteria when possible
4. **Relevant**: Align with user personas' needs

### Examples

**Good Observations**:
- "低粉丝（<1000）但高收入（$10k+）的产品驱动案例"
- "功能简单（≤5个核心功能）但定价较高（$50+/月）的B2B工具"
- "不依赖AI技术但在AI品类中成功的产品"
- "周末可启动（低门槛+清晰MVP）且已验证需求的项目"

**Bad Observations**:
- "好的产品" (too vague)
- "赚钱的SaaS" (not specific enough)
- "创新的想法" (not measurable)

## Guidance Generation Rules

### Format

```
指引: [AI应该寻找什么模式/提取什么洞察]
```

### Guidelines

1. **Explain the Why**: Why is this pattern interesting?
2. **Suggest the Insight**: What should AI look for?
3. **Provide Context**: What makes this valuable?
4. **Be Directive**: Tell AI what to emphasize

### Examples

**Good Guidance**:
- "寻找产品驱动而非IP驱动的案例，证明产品力能直接变现"
- "强调定价策略作为差异化手段，而非功能堆砌"
- "展示传统技术解决新问题的案例，挑战AI必需的假设"
- "提取快速验证的方法论，降低启动门槛"

**Bad Guidance**:
- "找一些好的产品" (not directive)
- "看看有什么" (no clear goal)
- "随便生成" (no logic)

## Discovery Strategies

### Strategy 1: Contrast Mining

Find **opposing characteristics** that coexist:

```
High X + Low Y patterns:
- High revenue + Low followers
- High complexity + Small team
- High barrier + Solo feasible
- High price + Simple features

Low X + High Y patterns:
- Low cost + High revenue
- Low features + High satisfaction
- Low marketing + High growth
```

### Strategy 2: Niche Identification

Find **underserved segments**:

```
Vertical markets:
- Healthcare + B2B + Compliance
- Education + B2C + Subscription
- Finance + B2B + API-first

Customer types:
- Developers (B2D)
- Creators (B2C)
- SMB owners (B2B)
- Enterprise (B2B)
```

### Strategy 3: Success Factor Analysis

Identify **what actually works**:

```
Growth drivers:
- Product-driven success patterns
- Content-driven acquisition
- Platform ecosystem leverage
- IP/Creator-driven growth

Positioning strategies:
- Vertical specialization
- Pricing innovation
- Experience differentiation
- Feature differentiation
```

### Strategy 4: Risk Mitigation

Find **lower-risk paths**:

```
Low-risk combinations:
- Active search + Real opportunity
- Clear MVP + Solo feasible
- Low barrier + Product-driven
- Simple features + B2B
```

## Template Type Selection

### Contrast (反差型) - Priority 8-10

**When to use**:
- Pattern challenges common assumptions
- Creates "aha moment"
- 2+ conflicting dimensions
- Broad appeal

**Example**:
- Observation: "低粉丝但高收入的产品"
- Guidance: "证明产品力能直接变现，挑战'需要大量粉丝才能赚钱'的假设"

### Cognitive (认知型) - Priority 6-8

**When to use**:
- Provides new perspective
- Educational value
- Positioning/pricing insights
- Market understanding

**Example**:
- Observation: "通过创新定价模式成功的产品"
- Guidance: "展示定价作为产品差异化的一部分，而非事后考虑"

### Action (行动型) - Priority 7-9

**When to use**:
- Reduces decision paralysis
- Clear execution path
- Risk mitigation focus
- Practical guidance

**Example**:
- Observation: "周末可启动的项目"
- Guidance: "提取快速验证方法论，降低启动门槛和心理负担"

### Niche (利基型) - Priority 3-5

**When to use**:
- Specific audience
- Specialized knowledge
- Platform/vertical focus
- Smaller TAM

**Example**:
- Observation: "开发者工具中的B2D产品"
- Guidance: "展示开发者为开发者构建的成功模式"

## Quality Criteria

### Good Opportunity Discovery

✅ **Specific**: Clear, measurable criteria
✅ **Valuable**: Provides actionable insight
✅ **Data-backed**: 5-15 products match
✅ **Surprising**: Challenges assumptions or reveals hidden patterns
✅ **Relevant**: Serves specific user persona needs

### Bad Opportunity Discovery

❌ **Vague**: "好的产品"
❌ **Obvious**: "赚钱的产品赚钱"
❌ **Too narrow**: <3 products match
❌ **Too broad**: >30 products match
❌ **Irrelevant**: No clear user value

## Example Discovery Workflow

### Input: Mother Theme Distribution Data

```json
{
  "success_driver": {
    "产品驱动": 450,
    "IP驱动": 120,
    "内容驱动": 80,
    "渠道驱动": 60
  },
  "entry_barrier": {
    "低门槛快启动": 300,
    "中等投入": 250,
    "高门槛": 100
  }
}
```

### Analysis

1. **Pattern**: 产品驱动 (450) >> IP驱动 (120)
   - Insight: Product-first strategies are more common
   - Opportunity: Highlight product-driven success without large following

2. **Pattern**: 高门槛 (100) exists with solo feasibility
   - Insight: High barriers don't always mean impossible for small teams
   - Opportunity: Show technical moats as advantage, not obstacle

### Output: Observation/Guidance Pairs

```
Pair 1 (Contrast):
Observation: "低粉丝（<1000）但高收入（$10k+）的产品驱动案例"
Guidance: "寻找产品驱动而非IP驱动的案例，证明产品力能直接变现，挑战'需要大量粉丝才能赚钱'的假设"

Pair 2 (Contrast):
Observation: "高技术门槛但小团队（≤2人）成功的产品"
Guidance: "展示技术壁垒成为护城河而非障碍，证明复杂技术也能被小团队驾驭"

Pair 3 (Action):
Observation: "低门槛+清晰MVP+独立可行的项目"
Guidance: "提取快速启动方法论，帮助独立开发者在周末验证想法"
```

## Continuous Discovery

### Monitoring Metrics

Track which templates are most valuable:

1. **User engagement**: Click-through rates
2. **Product exploration**: Products viewed from template
3. **Template reuse**: How often users return
4. **Feedback**: Direct user input

### Iteration Signals

Generate new templates when:

1. **New data patterns emerge**: Fresh product data reveals new combinations
2. **Existing templates saturate**: Too many products match
3. **User requests**: Specific needs identified
4. **Market shifts**: New trends or categories emerge

### Deprecation Signals

Remove templates when:

1. **Too few matches**: <3 products consistently
2. **Low engagement**: Users don't find it valuable
3. **Outdated**: Pattern no longer relevant
4. **Redundant**: Overlaps too much with other templates
