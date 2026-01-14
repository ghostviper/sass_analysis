---
name: market-signals
description: Identifies counter-intuitive market signals and hidden opportunities in SaaS data. Use this skill when analyzing products, categories, or market trends to find insights that aren't obvious from surface-level metrics.
---

# Market Signals Analysis

This skill helps identify non-obvious patterns and counter-intuitive signals in SaaS market data that often indicate the best opportunities.

## Counter-Intuitive Signals to Hunt

### 🎯 High-Value Signals

| Signal | What to Look For | Why It Matters |
|--------|------------------|----------------|
| **Low Followers + High Revenue** | `founder_followers < 1000` AND `revenue_30d > $5000` | Product-driven growth, not IP-dependent. Replicable without building an audience first. |
| **Short Description + High Revenue** | Description < 50 words AND `revenue_30d > $3000` | Precise positioning, clear problem-solution fit. Easy to understand = easy to sell. |
| **Small Category + High Growth** | Category products < 20 AND top products growing > 10%/mo | Blue ocean opportunity. Less competition, room to grow. |
| **Low Complexity + High Revenue** | `tech_complexity: "low"` AND `revenue_30d > $5000` | Replicable by solo developers. Execution > innovation. |
| **Low Multiple + High Growth** | `multiple < 2x` AND `growth_rate > 15%` | Undervalued. Market hasn't caught up to potential. |
| **No AI + High Revenue** | `ai_dependency: "none"` AND `revenue_30d > $10000` | Proves you don't need AI to succeed. Simpler to build and maintain. |

### ⚠️ Warning Signals

| Signal | What It Indicates |
|--------|-------------------|
| High followers + Low revenue | IP-dependent, hard to replicate |
| Many products + Low median revenue | Saturated market, race to bottom |
| High complexity + Low revenue | Over-engineered, poor market fit |
| High multiple + Declining growth | Overvalued, potential correction |

## Analysis Framework

### Step 1: Surface the Data
Query products with relevant filters to get raw data.

### Step 2: Calculate Derived Metrics

**Revenue-to-Follower Ratio**
```
ratio = revenue_30d / (founder_followers + 1)
```
- Ratio > 10: Strong product-driven signal
- Ratio 1-10: Balanced
- Ratio < 1: IP-dependent

**Category Concentration (Gini)**
- Gini < 0.3: Evenly distributed (healthy competition)
- Gini 0.3-0.6: Moderate concentration
- Gini > 0.6: Winner-take-all (risky for new entrants)

**Growth Sustainability Score**
```
sustainability = growth_rate * (1 - gini_coefficient)
```
Higher = more sustainable growth opportunity

### Step 3: Pattern Recognition

Look for clusters of products that share:
- Similar revenue ranges
- Similar complexity levels
- Different approaches to the same problem

These clusters often reveal "template" opportunities.

### Step 4: Synthesize Insights

Don't just report signals - interpret them:

❌ **Bad**: "ProductX has low followers and high revenue"

✅ **Good**: "ProductX's $8K MRR with only 200 followers suggests the product sells itself. This is a strong signal for indie developers who don't want to become influencers. The key question: what's their acquisition channel if not social media?"

### The Insight Quality Test

Before presenting any finding, verify it passes ALL three checks:

| Check | Question | If No... |
|-------|----------|----------|
| **Non-Obvious** | Would a smart person already know this? | Dig deeper or skip it |
| **Actionable** | Does this change what they should do? | Add the "so what" |
| **Specific** | Does it include numbers or comparisons? | Add concrete data |

**Examples of FAILING the test:**

```
❌ "The market is competitive" 
   → Fails: Obvious, not actionable, no specifics

❌ "This product has good growth"
   → Fails: No numbers, doesn't say why it matters

❌ "You should consider the competition"
   → Fails: Obvious advice, no insight
```

**Examples of PASSING the test:**

```
✅ "This category's Gini of 0.72 means the top 3 products own 85% of revenue. 
    New entrants have a 3% chance of reaching $5K MRR based on historical data.
    → Only enter if you have a distribution advantage."

✅ "ProductX grew 340% in 6 months with zero social presence.
    Their secret: SEO-optimized landing pages ranking for 47 long-tail keywords.
    → This is a replicable playbook for non-influencer founders."
```

### Insight Depth Requirements

Every analysis MUST include at least TWO of these insight types:

1. **Quantified Comparison**: "X is 3x higher than category median"
2. **Counter-Intuitive Finding**: "Despite Y, the data shows Z"
3. **Hidden Risk**: "What's not obvious: [specific risk with data]"
4. **Actionable Threshold**: "If X > Y, do A. Otherwise, do B."
5. **Pattern Recognition**: "Products with [trait] show [outcome] 78% of the time"

## Output Format

When presenting market signals, use this structure:

### 🔍 Key Finding
[One sentence summary of the most important insight — must be non-obvious]

### 📊 Supporting Data
| Metric | Value | Benchmark | Signal |
|--------|-------|-----------|--------|
| ... | ... | ... | 🟢/🟡/🔴 |

### 💡 Interpretation
[2-3 sentences explaining what this means and why it matters]
**Must answer**: "So what? What should they do differently because of this?"

### ⚡ Action Item
[One specific thing the user should do with this information]
**Must be concrete**: Include a specific product to study, metric to track, or decision to make

### Banned Output Patterns

Never include these in your analysis:

| Pattern | Why It's Bad | What To Do Instead |
|---------|--------------|-------------------|
| "The market is growing" | Obvious, no insight | "Market grew 47% YoY, but 80% went to top 3 players" |
| "Competition is fierce" | Vague, not actionable | "23 new entrants in 6 months, only 2 reached $1K MRR" |
| "Consider your strengths" | Generic advice | "Backend devs have 2.3x success rate in API tools category" |
| "Do more research" | Lazy cop-out | "Study [ProductX]'s pricing page — they A/B tested to this" |
| "It depends on..." | Hedge without value | "If you have <10h/week, X. If 10-20h, Y. If 20h+, Z." |

## Example Analysis

**Query**: "Find opportunities in the AI tools category"

**Response**:
```
🔍 Key Finding
The AI Tools category shows a surprising pattern: the highest-revenue products are NOT the most technically sophisticated.

📊 Supporting Data
| Product | Revenue | AI Dependency | Complexity | Followers |
|---------|---------|---------------|------------|-----------|
| [ToolA](/products/toola) | $12K | Light | Low | 450 |
| [ToolB](/products/toolb) | $8K | None | Low | 120 |
| [ToolC](/products/toolc) | $3K | Heavy | High | 5,200 |

💡 Interpretation
The top performers use AI as a feature, not the core product. ToolB doesn't even use AI - it's a simple wrapper that solves a specific workflow problem. Meanwhile, ToolC with heavy AI investment and 5K followers struggles to monetize.

⚡ Action Item
If entering AI tools: focus on a specific workflow problem first, add AI as enhancement later. Study ToolB's positioning - what problem does it solve that makes AI unnecessary?
```
