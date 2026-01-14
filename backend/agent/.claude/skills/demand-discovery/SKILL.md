---
name: demand-discovery
description: Methodology framework for pain point discovery. Automatically loaded when @demand-researcher executes searches. Provides query templates, domain presets, five-dimension analysis framework, and citation standards.
---

# Demand Discovery Methodology

This skill provides the **knowledge framework** for discovering real market demands and pain points. It defines HOW to search, WHAT to look for, and HOW to analyze findings.

> **Note**: This skill provides methodology only. Actual execution is handled by the `@demand-researcher` subagent.

## Core Principle: Evidence Over Speculation

**Your job is NOT to list possible pain points. Your job is to DISCOVER and VALIDATE real pain points with evidence.**

```
❌ SPECULATION: "AI writing tools might have these pain points:
                1. Output quality issues
                2. Pricing concerns"

✅ DISCOVERY: "Based on 47 discussions across Reddit and IndieHackers,
              the #1 pain point is 'AI-sounding output' (mentioned 23 times).
              Users specifically complain about..."
```

## Query Optimization for Tavily

Tavily is a semantic search engine. Use natural language, not keyword stuffing.

### Pain Point Discovery Queries

| Goal | Query Template | Example |
|------|---------------|---------|
| Find complaints | "What do people hate about [X]?" | "What do people hate about AI writing tools?" |
| Find gaps | "What's missing in [X] tools?" | "What's missing in project management tools?" |
| Find switches | "Why people switch from [X]" | "Why people switch from Notion" |
| Find wishes | "[X] feature request OR wishlist" | "email marketing feature request wishlist" |
| Find failures | "Why [X] startups fail" | "Why SaaS startups fail" |
| Find frustrations | "[X] frustrated OR annoying OR hate" | "CRM frustrated annoying hate" |

### Domain Preset Selection

| Research Goal | Preset | Best For |
|--------------|--------|----------|
| Indie dev opportunities | `indie` | Reddit startup subs + IndieHackers + HN |
| User complaints | `product_reviews` | G2, Capterra, Trustpilot |
| Technical pain points | `dev_community` | StackOverflow, dev.to |
| AI/ML specific | `ai_ml` | HuggingFace, Reddit ML subs |
| Marketing/SEO | `marketing_growth` | Backlinko, Moz, Ahrefs |

### Time Range Selection

| Scenario | Time Range | Why |
|----------|------------|-----|
| Verify pain point still exists | `month` | Old complaints may be solved |
| Find emerging trends | `week` | Catch new patterns early |
| Historical analysis | `year` | Understand evolution |
| Default discovery | (none) | Broader coverage |

## Analysis Framework

### Five Dimensions of Pain Point Validation

For each pain point discovered, analyze:

| Dimension | Question | Strong Signal | Weak Signal |
|-----------|----------|---------------|-------------|
| **Frequency** | How many independent mentions? | >10 mentions | <3 mentions |
| **Intensity** | How strong is the emotion? | "hate", "nightmare", "waste of time" | "would be nice", "minor issue" |
| **Recency** | Is this still a problem? | Posts from last 30 days | Posts from 1+ year ago |
| **Payment Signal** | Is there money here? | "I'd pay for", "shut up and take my money" | No price discussion |
| **Solution Gap** | Why hasn't this been solved? | Existing solutions inadequate | Good solutions exist |

### Cross-Validation Requirements

**Never conclude from a single source.** Every major finding must be validated:

```
Finding: "Users hate AI writing tools' robotic output"

Validation checklist:
□ Found in Reddit? [Yes - r/content_marketing, r/copywriting]
□ Found in IndieHackers? [Yes - 3 posts]
□ Found in product reviews? [Yes - G2 reviews for Jasper]
□ Recent? [Yes - posts from last 2 months]
□ Payment signals? [Yes - "I'd pay $50/mo for human-sounding AI"]

→ VALIDATED: Cross-platform, recent, has payment intent
```

### Evidence Strength Scale

| Level | Criteria | Confidence |
|-------|----------|------------|
| ⬤⬤⬤⬤⬤ (5/5) | 10+ mentions, multiple platforms, recent, payment signals | High - validated opportunity |
| ⬤⬤⬤⬤○ (4/5) | 5-10 mentions, 2+ platforms, recent | Good - worth pursuing |
| ⬤⬤⬤○○ (3/5) | 3-5 mentions, single platform | Moderate - needs more validation |
| ⬤⬤○○○ (2/5) | 1-3 mentions, anecdotal | Low - may be outlier |
| ⬤○○○○ (1/5) | Single mention, old | Very Low - likely not real |

## Source Citation Format

### Inline Citations (Required)

Use numbered citations inline, similar to Perplexity:

```
Users frequently complain that AI writing tools produce "robotic, generic content" [1][2].
This pain point appears in 23+ discussions across Reddit and IndieHackers [1][3][4],
with some users explicitly stating willingness to pay for better solutions [2].
```

### Source List Format (Required at End)

```
## Sources

| # | Source | Type |
|---|--------|------|
| 1 | [r/content_marketing: AI writing complaints](https://reddit.com/...) | 💬 Reddit |
| 2 | [IndieHackers: Why I quit Jasper](https://indiehackers.com/...) | 🚀 IndieHackers |
| 3 | [G2: Jasper AI Reviews](https://g2.com/...) | ⭐ Review |
| 4 | [HN: AI Writing Tools Discussion](https://news.ycombinator.com/...) | 🔶 HN |
```

### Source Type Icons

| Icon | Source Type |
|------|-------------|
| 💬 | Reddit |
| 🚀 | IndieHackers |
| 🔶 | Hacker News |
| ⭐ | Review sites (G2, Capterra) |
| 📰 | News/Blog |
| 🐦 | Twitter/X |
| 📹 | YouTube |

## Anti-Patterns

| Don't Do This | Why | Do This Instead |
|---------------|-----|-----------------|
| List possible pain points without searching | Speculation, not discovery | Search first, report findings |
| Report one source as truth | Could be outlier | Cross-validate across platforms |
| Say "users complain about X" without citation | Unverifiable claim | "Users complain about X [1][2]" |
| Skip recency check | Pain point may be solved | Add time_range filter |
| Ignore payment signals | No money = no business | Explicitly look for willingness to pay |
| Give generic advice | Not actionable | Give specific, evidence-based recommendations |
| End with "any questions?" | Low-value ending | End with decision-forcing question |

## Quality Checklist

Before delivering analysis, verify:

```
□ Did I search multiple sources (not just one)?
□ Did I use specific queries (not vague keywords)?
□ Did I validate findings across platforms?
□ Did I include frequency/intensity/recency analysis?
□ Did I look for payment signals?
□ Did I cite specific sources with URLs?
□ Did I provide analysis, not just listing?
□ Did I explain WHY this is an opportunity?
□ Did I identify the solution gap?
```
