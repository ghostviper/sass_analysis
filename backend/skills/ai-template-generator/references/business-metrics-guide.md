# Business Metrics Guide

## Purpose

This guide provides frameworks for evaluating business health and identifying metrics-driven curation opportunities.

---

## Universal Startup Metrics

### Revenue Metrics

**MRR (Monthly Recurring Revenue)**
```
MRR = Σ (Active Subscriptions × Monthly Price)
```

**ARR (Annual Recurring Revenue)**
```
ARR = MRR × 12
```

**Growth Rate**
```
MoM Growth = (This Month MRR - Last Month MRR) / Last Month MRR
YoY Growth = (This Year ARR - Last Year ARR) / Last Year ARR
```

**Benchmarks:**
- Seed: 15-20% MoM growth
- Series A: 10-15% MoM, 3-5x YoY
- Series B+: 100%+ YoY

**Curation Opportunities:**
- "Products with exceptional growth rates"
- "Tools achieving 20%+ MoM growth"
- "Solutions with 3x+ YoY growth"

---

## Unit Economics

### CAC (Customer Acquisition Cost)

**Formula:**
```
CAC = Total S&M Spend / New Customers Acquired
```

Include: Sales salaries, marketing spend, tools, overhead

**Benchmarks:**
- B2B SaaS: $200-$500 (SMB), $5K-$15K (Enterprise)
- B2C: $10-$50
- Marketplace: $20-$100

**Curation Opportunities:**
- "Products with low CAC (<$100)"
- "Tools with organic/viral acquisition"
- "Solutions with efficient go-to-market"

### LTV (Lifetime Value)

**Formula:**
```
LTV = ARPU × Gross Margin% × (1 / Churn Rate)
```

Simplified:
```
LTV = ARPU × Average Customer Lifetime × Gross Margin%
```

**Benchmarks:**
- B2B SaaS: $1,000-$10,000+
- B2C: $100-$500
- Marketplace: $500-$2,000

**Curation Opportunities:**
- "Products with high LTV (>$5K)"
- "Tools with long customer lifetime"
- "Solutions with low churn"

### LTV:CAC Ratio

**Formula:**
```
LTV:CAC = LTV / CAC
```

**Benchmarks:**
- > 3.0 = Healthy
- 1.0-3.0 = Needs improvement
- < 1.0 = Unsustainable

**Curation Opportunities:**
- "Products with LTV:CAC > 5.0"
- "Tools with exceptional unit economics"
- "Solutions with sustainable growth"

### CAC Payback Period

**Formula:**
```
CAC Payback = CAC / (ARPU × Gross Margin%)
```

**Benchmarks:**
- < 12 months = Excellent
- 12-18 months = Good
- > 24 months = Concerning

**Curation Opportunities:**
- "Products with quick payback (<12 months)"
- "Tools with fast cash recovery"
- "Solutions with efficient monetization"

---

## SaaS Metrics

### Revenue Composition

**Net New MRR:**
```
Net New MRR = New MRR + Expansion MRR - Contraction MRR - Churned MRR
```

**Components:**
- New MRR: New customers × ARPU
- Expansion MRR: Upsells and cross-sells
- Contraction MRR: Downgrades
- Churned MRR: Lost customers

**Curation Opportunities:**
- "Products with strong expansion revenue"
- "Tools with negative churn (NDR > 100%)"
- "Solutions with upsell/cross-sell"

### Retention Metrics

**Logo Retention:**
```
Logo Retention = (Customers End - New Customers) / Customers Start
```

**Dollar Retention (NDR):**
```
NDR = (ARR Start + Expansion - Contraction - Churn) / ARR Start
```

**Benchmarks:**
- NDR > 120% = Best-in-class
- NDR 100-120% = Good
- NDR < 100% = Needs work

**Curation Opportunities:**
- "Products with NDR > 120%"
- "Tools with exceptional retention"
- "Solutions with negative churn"

**Gross Retention:**
```
Gross Retention = (ARR Start - Churn - Contraction) / ARR Start
```

**Benchmarks:**
- > 90% = Excellent
- 85-90% = Good
- < 85% = Concerning

### SaaS-Specific Metrics

**Magic Number:**
```
Magic Number = Net New ARR (quarter) / S&M Spend (prior quarter)
```

**Benchmarks:**
- > 0.75 = Efficient, ready to scale
- 0.5-0.75 = Moderate efficiency
- < 0.5 = Inefficient, don't scale yet

**Curation Opportunities:**
- "Products with Magic Number > 0.75"
- "Tools ready to scale"
- "Solutions with efficient growth"

**Rule of 40:**
```
Rule of 40 = Revenue Growth Rate% + Profit Margin%
```

**Benchmarks:**
- > 40% = Excellent
- 20-40% = Acceptable
- < 20% = Needs improvement

**Example:** 50% growth + (-10%) margin = 40% ✓

**Curation Opportunities:**
- "Products achieving Rule of 40"
- "Tools balancing growth and profitability"
- "Solutions with sustainable economics"

**Quick Ratio:**
```
Quick Ratio = (New MRR + Expansion MRR) / (Churned MRR + Contraction MRR)
```

**Benchmarks:**
- > 4.0 = Healthy growth
- 2.0-4.0 = Moderate
- < 2.0 = Churn problem

**Curation Opportunities:**
- "Products with Quick Ratio > 4.0"
- "Tools with strong growth vs. churn"
- "Solutions with healthy expansion"

---

## Marketplace Metrics

### GMV (Gross Merchandise Value)

**Formula:**
```
GMV = Σ (Transaction Value)
```

**Growth Rate:**
```
GMV Growth = (Current GMV - Prior GMV) / Prior GMV
```

**Target:** 20%+ MoM early-stage

**Curation Opportunities:**
- "Marketplaces with high GMV growth"
- "Platforms with strong transaction volume"
- "Solutions with marketplace dynamics"

### Take Rate

**Formula:**
```
Take Rate = Net Revenue / GMV
```

**Typical Ranges:**
- Payment processors: 2-3%
- E-commerce marketplaces: 10-20%
- Service marketplaces: 15-25%
- High-value B2B: 5-15%

**Curation Opportunities:**
- "Marketplaces with healthy take rates"
- "Platforms with pricing power"
- "Solutions with sustainable economics"

### Marketplace Liquidity

**Metrics:**
- Time to Transaction: How long from listing to sale?
- Fill Rate: % of requests that result in transaction
- Repeat Rate: % of users who transact multiple times

**Benchmarks:**
- Fill rate > 80% = Strong liquidity
- Repeat rate > 60% = Strong retention

**Curation Opportunities:**
- "Marketplaces with high liquidity"
- "Platforms with strong fill rates"
- "Solutions with repeat transactions"

### Supply/Demand Balance

**Goal:** Balanced growth (1:1 ratio ideal)

**Warning Signs:**
- Too much supply: Low fill rates, frustrated suppliers
- Too much demand: Long wait times, frustrated customers

**Curation Opportunities:**
- "Marketplaces with balanced growth"
- "Platforms managing supply/demand well"
- "Solutions with healthy marketplace dynamics"

---

## Consumer/Mobile Metrics

### Engagement Metrics

**DAU/MAU Ratio:**
```
DAU/MAU = Daily Active Users / Monthly Active Users
```

**Benchmarks:**
- > 50% = Exceptional (daily habit)
- 20-50% = Good
- < 20% = Weak engagement

**Curation Opportunities:**
- "Products with DAU/MAU > 50%"
- "Tools with daily habit formation"
- "Solutions with high engagement"

**Session Metrics:**
- Session Frequency: Sessions per user per day/week
- Session Duration: Time spent per session

**Curation Opportunities:**
- "Products with high session frequency"
- "Tools with long session duration"
- "Solutions with sticky engagement"

### Retention Curves

**Key Milestones:**
- Day 1 Retention: % users who return next day
- Day 7 Retention: % users active 7 days after signup
- Day 30 Retention: % users active 30 days after signup

**Benchmarks (Day 30):**
- > 40% = Excellent
- 25-40% = Good
- < 25% = Weak

**Retention Curve Shape:**
- Flattening curve = Good (users becoming habitual)
- Steep decline = Poor product-market fit

**Curation Opportunities:**
- "Products with Day 30 retention > 40%"
- "Tools with flattening retention curves"
- "Solutions with strong product-market fit"

### Viral Coefficient (K-Factor)

**Formula:**
```
K-Factor = Invites per User × Invite Conversion Rate
```

**Example:** 10 invites/user × 20% conversion = 2.0 K-factor

**Benchmarks:**
- K > 1.0 = Viral growth
- K = 0.5-1.0 = Strong referrals
- K < 0.5 = Weak virality

**Curation Opportunities:**
- "Products with K-Factor > 1.0"
- "Tools with viral growth"
- "Solutions with built-in referral loops"

---

## B2B Metrics

### Sales Efficiency

**Win Rate:**
```
Win Rate = Deals Won / Total Opportunities
```

**Target:** 20-30% for new sales team, 30-40% mature

**Sales Cycle Length:**
- SMB: 30-60 days
- Mid-market: 60-120 days
- Enterprise: 120-270 days

**Curation Opportunities:**
- "Products with high win rates"
- "Tools with short sales cycles"
- "Solutions with efficient sales"

**Average Contract Value (ACV):**
```
ACV = Total Contract Value / Contract Length (years)
```

**Curation Opportunities:**
- "Products with high ACV"
- "Tools with enterprise pricing"
- "Solutions with large deal sizes"

### Pipeline Metrics

**Pipeline Coverage:**
```
Pipeline Coverage = Total Pipeline Value / Quota
```

**Target:** 3-5x coverage

**Conversion Rates by Stage:**
- Lead → Opportunity: 10-20%
- Opportunity → Demo: 50-70%
- Demo → Proposal: 30-50%
- Proposal → Close: 20-40%

**Curation Opportunities:**
- "Products with healthy pipeline"
- "Tools with high conversion rates"
- "Solutions with predictable sales"

---

## Metrics by Stage

### Pre-Seed (Product-Market Fit)

**Focus Metrics:**
1. Active users growth
2. User retention (Day 7, Day 30)
3. Core engagement (sessions, features used)
4. Qualitative feedback (NPS, interviews)

**Don't worry about:**
- Revenue (may be zero)
- CAC (not optimizing yet)
- Unit economics

**Curation Opportunities:**
- "Products with strong early retention"
- "Tools with clear product-market fit signals"
- "Solutions with engaged early users"

### Seed ($500K-$2M ARR)

**Focus Metrics:**
1. MRR growth rate (15-20% MoM)
2. CAC and LTV (establish baseline)
3. Gross retention (> 85%)
4. Core product engagement

**Start tracking:**
- Sales efficiency
- Burn rate and runway

**Curation Opportunities:**
- "Products with 15%+ MoM growth"
- "Tools establishing unit economics"
- "Solutions with strong retention"

### Series A ($2M-$10M ARR)

**Focus Metrics:**
1. ARR growth (3-5x YoY)
2. Unit economics (LTV:CAC > 3, payback < 18 months)
3. Net dollar retention (> 100%)
4. Burn multiple (< 2.0)
5. Magic number (> 0.5)

**Mature tracking:**
- Rule of 40
- Sales efficiency
- Pipeline coverage

**Curation Opportunities:**
- "Products with 3x+ YoY growth"
- "Tools with healthy unit economics"
- "Solutions ready to scale"

---

## Applying Metrics to Curation

### Metrics-Driven Opportunity Discovery

**Process:**
1. Identify key metric (CAC, LTV, NDR, etc.)
2. Find products excelling in that metric
3. Analyze common patterns
4. Create curation template

**Example:**
- Metric: LTV:CAC > 5.0
- Pattern: Product-led growth + Viral mechanics
- Template: "Products with exceptional unit economics through PLG"

### Quality Indicators

**Good Metrics-Driven Opportunities:**
- ✅ Specific metric threshold
- ✅ Measurable and verifiable
- ✅ Actionable insight
- ✅ Clear business value

**Bad Metrics-Driven Opportunities:**
- ❌ Vague metric reference
- ❌ Unverifiable claims
- ❌ No clear threshold
- ❌ Unclear business impact

---

## Summary: Metrics Quick Reference

| Business Model | Key Metrics | Healthy Benchmarks |
|----------------|-------------|-------------------|
| **B2B SaaS** | MRR Growth, LTV:CAC, NDR | 15% MoM, >3.0, >100% |
| **Marketplace** | GMV Growth, Take Rate, Liquidity | 20% MoM, 10-20%, >80% fill |
| **Consumer** | DAU/MAU, Retention, K-Factor | >20%, >25% D30, >0.5 |
| **B2B Sales** | Win Rate, ACV, Sales Cycle | >25%, High, Short |

**Use these benchmarks to identify exceptional products for curation.**

---

**Version**: 1.0
**Date**: 2026-01-20
**Purpose**: Enable metrics-driven curation opportunity discovery

