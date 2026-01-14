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

### 🧠 推理过程（Show Your Work）

每个关键发现必须展示推理链：

```
**观察：** [原始数据是什么]
**推断：** [这个数据意味着什么，为什么重要]
**结论：** [所以应该怎么做]
```

**示例：**
```
**观察：** ProductX 创始人粉丝230人，月收入$8.5K
**推断：** 收入/粉丝比=37，是类目中位数(2.3)的16倍。收入完全不依赖个人影响力。
**结论：** 这是纯产品驱动增长的典型案例。值得研究他们的获客渠道——大概率是SEO或产品内病毒传播。
```

### 💡 Interpretation
[2-3 sentences explaining what this means and why it matters]
**Must answer**: "So what? What should they do differently because of this?"

### ⚡ Action Item
[One specific thing the user should do with this information]
**Must be concrete**: Include a specific product to study, metric to track, or decision to make

### ❓ 决策问题（Decision-Forcing Question）
[一个具体的、有决策价值的问题，帮助用户深入思考]

**好的问题示例：**
- "如果这个增长率在3个月后降到5%，你还会进入吗？"
- "你有什么独特优势能打破这个市场的集中度？"
- "在[ProductA]和[ProductB]的模式之间，哪个更符合你的资源状况？"

**禁止的问题：**
- ❌ "有什么问题吗？"
- ❌ "需要更多信息吗？"
- ❌ "你怎么看？"

### Banned Output Patterns

Never include these in your analysis:

| Pattern | Why It's Bad | What To Do Instead |
|---------|--------------|-------------------|
| "The market is growing" | Obvious, no insight | "Market grew 47% YoY, but 80% went to top 3 players" |
| "Competition is fierce" | Vague, not actionable | "23 new entrants in 6 months, only 2 reached $1K MRR" |
| "Consider your strengths" | Generic advice | "Backend devs have 2.3x success rate in API tools category" |
| "Do more research" | Lazy cop-out | "Study [ProductX]'s pricing page — they A/B tested to this" |
| "It depends on..." | Hedge without value | "If you have <10h/week, X. If 10-20h, Y. If 20h+, Z." |

## 多视角分析（When Data Supports Multiple Conclusions）

当市场信号可以有多种解读时，不要只给一个结论。展示不同视角：

### 触发条件
- 数据可以支持相反的结论
- 用户问"该不该进入"、"值不值得做"
- 存在明显的trade-off

### 输出格式

```
### 视角A：[乐观/进入/做]
> [具体建议]

**数据支撑：**
- [支持这个视角的数据1]
- [支持这个视角的数据2]

**适合你如果：** [具体条件]

---

### 视角B：[谨慎/观望/不做]
> [具体建议]

**数据支撑：**
- [支持这个视角的数据1]
- [支持这个视角的数据2]

**适合你如果：** [具体条件]

---

### 我的判断
[明确表态 + 理由]
但关键变量是 [用户需要自己判断的因素]
```

### 示例

**Query**: "AI写作工具市场还能进吗？"

❌ **单一结论（避免）：**
```
市场已经饱和，不建议进入。
```

✅ **多视角分析：**
```
### 视角A：现在进入正是时候
> 市场教育成本已经被头部玩家承担，用户知道AI写作是什么了

**数据支撑：**
- 类目搜索量同比增长340%，需求还在爆发
- 头部产品NPS只有28，用户抱怨集中在"输出太AI味"
- [ProductX]去年进入，6个月做到$12K，切入点是"学术写作"垂直场景

**适合你如果：** 你有明确的垂直场景或差异化定位

---

### 视角B：红海已成，不建议进入
> 头部3家占据67%份额，新进入者存活率极低

**数据支撑：**
- 过去12个月47个新产品，只有3个达到$5K MRR
- 获客成本从$12涨到$45，利润空间被压缩
- 头部产品开始打价格战，免费额度越给越多

**适合你如果：** 你没有独特的分发渠道或技术壁垒

---

### 我的判断
如果你没有明确的垂直切入点，选B。但如果你在某个专业领域（法律、医疗、学术）有背景，A是可行的——垂直场景的竞争强度只有通用市场的1/5。

❓ 你打算做通用AI写作还是某个垂直场景？如果是垂直，是哪个领域？
```

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

🧠 推理过程
**观察：** ToolB 零AI依赖、120粉丝，却有$8K收入；ToolC 重度AI、5200粉丝，只有$3K
**推断：** 收入和AI复杂度负相关，和粉丝数也负相关。说明这个市场奖励的是"解决具体问题"而非"技术炫技"
**结论：** AI工具市场的机会在于"AI作为隐形增强"，而非"AI作为卖点"

💡 Interpretation
The top performers use AI as a feature, not the core product. ToolB doesn't even use AI - it's a simple wrapper that solves a specific workflow problem. Meanwhile, ToolC with heavy AI investment and 5K followers struggles to monetize.

⚡ Action Item
If entering AI tools: focus on a specific workflow problem first, add AI as enhancement later. Study ToolB's positioning - what problem does it solve that makes AI unnecessary?

❓ 决策问题
你打算做的AI工具，AI是核心卖点还是隐形增强？如果是前者，你有什么理由相信你能打破这个"技术越复杂收入越低"的规律？
```
