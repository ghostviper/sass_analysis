# Domain Knowledge for Curation Template Generation

## User Personas and Needs

### Primary Personas

#### 1. Solo Indie Hacker (独立开发者)
**Profile**:
- Technical background, can code
- Limited time (side project or early full-time)
- Budget-conscious, prefers low-cost tools
- Seeks validation before heavy investment

**Needs from curation**:
- Low barrier to entry projects
- Clear MVP guidance
- Solo-feasible opportunities
- Quick monetization paths
- Technical complexity assessment

**Valuable templates**:
- Weekend launchable projects
- No-AI profitable ideas
- High barrier but solo-doable
- Clear MVP inspiration

#### 2. First-Time Founder (首次创业者)
**Profile**:
- May or may not be technical
- Has some capital or runway
- Needs market validation
- Risk-averse, seeks proven patterns

**Needs from curation**:
- Real opportunity validation
- Market demand signals
- Monetization clarity
- Competitive differentiation insights
- Success pattern recognition

**Valuable templates**:
- Low monetization risk directions
- Vertical niche success
- Pricing innovation examples
- Boring but profitable

#### 3. Serial Entrepreneur (连续创业者)
**Profile**:
- Experienced, has launched before
- Seeks efficiency and leverage
- Interested in market gaps
- Values unique insights over basics

**Needs from curation**:
- Non-obvious opportunities
- Contrarian insights
- Market positioning strategies
- Differentiation patterns
- Scalability indicators

**Valuable templates**:
- Counter-intuitive successes
- Positioning insights
- Platform ecosystem plays
- Differentiation strategies

#### 4. Product Manager / Strategist (产品经理/策略师)
**Profile**:
- Works in company or consulting
- Researches market trends
- Needs competitive intelligence
- Values structured analysis

**Needs from curation**:
- Market pattern recognition
- Competitive positioning analysis
- Feature prioritization insights
- Pricing strategy examples
- Success factor attribution

**Valuable templates**:
- Cognitive templates (all)
- Differentiation analysis
- Pricing innovation
- Success driver patterns

## Business Logic and Market Insights

### What Makes Products Successful

#### Product-Driven Success (产品驱动)
**Characteristics**:
- Strong core value proposition
- Clear problem-solution fit
- Low customer acquisition cost relative to value
- Word-of-mouth potential
- Viral coefficient or network effects

**Indicators in data**:
- `growth_driver = "product_driven"`
- `is_product_driven = true`
- High conversion scores
- Clear value propositions
- Instant value demos

**Template opportunities**:
- Contrast with IP-driven products
- Highlight feature simplicity
- Emphasize conversion optimization

#### IP/Creator-Driven Success (IP驱动)
**Characteristics**:
- Founder has existing audience
- Personal brand is distribution channel
- Community-first approach
- Trust-based selling

**Indicators in data**:
- `growth_driver = "ip_driven"`
- High `founder_followers`
- Strong social media presence
- Personal story in positioning

**Template opportunities**:
- Contrast: low followers but high revenue
- Show when IP is necessary vs optional
- Highlight audience-building strategies

#### Content-Driven Success (内容驱动)
**Characteristics**:
- SEO and content marketing focus
- Educational approach
- Long-tail keyword targeting
- Inbound lead generation

**Indicators in data**:
- `growth_driver = "content_driven"`
- Blog/tutorial presence
- Educational positioning
- Search-friendly pain points

**Template opportunities**:
- Content strategy patterns
- SEO-friendly niches
- Educational product positioning

#### Channel-Driven Success (渠道驱动)
**Characteristics**:
- Platform ecosystem play
- Leverages existing user base
- Integration or extension model
- Distribution through platform

**Indicators in data**:
- `growth_driver = "channel_driven"`
- Platform-specific categories
- Integration features
- Marketplace presence

**Template opportunities**:
- Platform ecosystem opportunities
- Integration strategies
- Marketplace positioning

### Market Dynamics

#### Demand Types and Acquisition

**主动搜索型 (Active Search)**:
- Users actively search for solutions
- High intent, clear pain point
- SEO and SEM effective
- Lower education cost
- Examples: "PDF converter", "invoice generator"

**触发认知型 (Triggered Awareness)**:
- Latent need, recognized when seen
- Requires demonstration
- Social proof important
- Content marketing effective
- Examples: "team collaboration", "productivity tools"

**需教育型 (Education Required)**:
- New concept or paradigm
- High education cost
- Community building necessary
- Longer sales cycle
- Examples: "new workflow methodology", "novel tech approach"

#### Pricing Psychology

**One-Time Purchase**:
- Lower friction for users
- Requires higher volume
- Good for tools with finite value
- Appeals to subscription-fatigued users

**Subscription (MRR)**:
- Predictable revenue
- Requires ongoing value delivery
- Higher lifetime value potential
- Standard for SaaS

**Usage-Based**:
- Aligns cost with value
- Scales with customer growth
- Reduces entry barrier
- Good for API/infrastructure products

**Freemium**:
- Lowers acquisition cost
- Requires clear upgrade path
- Conversion rate critical
- Good for viral products

**Lifetime Deal (LTD)**:
- Cash injection for early stage
- Creates loyal user base
- Risk of support burden
- Popular on deal platforms

### Competitive Positioning

#### Differentiation Strategies

**功能差异化 (Feature Differentiation)**:
- Unique capabilities
- Technical moats
- Patent or proprietary tech
- Hard to replicate quickly

**体验差异化 (Experience Differentiation)**:
- Superior UX/UI
- Faster/simpler workflow
- Better onboarding
- Instant value delivery

**人群差异化 (Audience Differentiation)**:
- Vertical specialization
- Role-specific features
- Industry-specific workflows
- Niche community focus

**定价差异化 (Pricing Differentiation)**:
- Novel pricing model
- More affordable tier
- Value-based pricing
- Transparent pricing

#### Market Scope Strategies

**Horizontal (横向)**:
- Broad market appeal
- General-purpose tool
- Large TAM but high competition
- Requires strong differentiation

**Vertical (垂直)**:
- Industry-specific
- Deep domain expertise
- Smaller TAM but less competition
- Higher willingness to pay

### Risk Factors

#### Technical Implementation Risk
**High risk indicators**:
- `tech_complexity_level = "high"`
- `ai_dependency_level = "heavy"`
- `requires_realtime = true`
- `requires_large_data = true`
- `requires_compliance = true`

**Mitigation strategies**:
- Start with simpler version
- Use existing APIs/services
- Focus on workflow over tech
- Partner with technical co-founder

#### Market Validation Risk
**High risk indicators**:
- `demand_type = "需教育型"`
- Abstract pain points
- Unclear target audience
- No existing alternatives

**Mitigation strategies**:
- Pre-sell before building
- Build audience first
- Start with content/education
- Find early adopters

#### User Acquisition Risk
**High risk indicators**:
- `demand_type != "主动搜索型"`
- Weak potential moats
- Broad target audience
- High CAC market

**Mitigation strategies**:
- Content marketing
- Community building
- Platform partnerships
- Referral programs

#### Monetization Risk
**High risk indicators**:
- `primary_risk = "变现转化"`
- Unclear pricing model
- B2C with low willingness to pay
- Free tier without clear upgrade path

**Mitigation strategies**:
- Validate pricing early
- Clear value tiers
- Usage-based pricing
- B2B pivot if needed

## Template Generation Principles

### Contrast Creation

**Effective contrasts**:
1. **Expectation vs Reality**: "You'd think X, but actually Y"
   - Example: "High followers needed" vs "Low followers, high revenue"

2. **Conventional Wisdom vs Data**: "Everyone says X, data shows Y"
   - Example: "More features = better" vs "Simple but profitable"

3. **Perceived Difficulty vs Actual**: "Seems hard, actually doable"
   - Example: "High barrier" vs "Solo-feasible"

4. **Input vs Output**: "Low input, high output"
   - Example: "Weekend project" vs "$10k MRR"

**Weak contrasts to avoid**:
- Arbitrary combinations without insight
- Contrasts that don't challenge assumptions
- Too subtle to be interesting
- Require too much context to understand

### Insight Quality

**Strong insights**:
- Actionable: Suggests what to do differently
- Memorable: Sticky phrasing, clear takeaway
- Non-obvious: Not immediately apparent from data
- Validated: Supported by multiple examples

**Weak insights**:
- Generic: "Work hard and succeed"
- Obvious: "Good products make money"
- Vague: "Focus on quality"
- Unactionable: No clear next step

### Filter Rule Design

**Effective filters**:
- Combine 2-3 dimensions for richness
- Use ranges that reflect real distribution
- Leverage mother themes for strategic filters
- Balance specificity with product count

**Filter anti-patterns**:
- Single dimension (too simple)
- Too many dimensions (over-constrained)
- Arbitrary thresholds without rationale
- Ignoring data distribution

## Cultural and Linguistic Considerations

### Chinese Market Context

**Terminology preferences**:
- "独立开发者" over "个人开发者" (indie hacker)
- "出海" for international expansion
- "闷声发财" for quiet success
- "卷" for intense competition

**Cultural values**:
- Pragmatism over idealism
- Proven patterns over innovation
- Risk mitigation emphasis
- Community and social proof

**Content style**:
- Direct and practical
- Numbers and specifics valued
- Success stories resonate
- Avoid overly promotional tone

### English Market Context

**Terminology preferences**:
- "Indie hacker" over "solo developer"
- "Bootstrap" for self-funded
- "Product-market fit" widely understood
- "MRR" standard metric

**Cultural values**:
- Innovation and disruption
- Individual achievement
- Risk-taking celebrated
- Transparency valued

**Content style**:
- Conversational and authentic
- Story-driven
- Aspirational but realistic
- Community-oriented

## Template Naming Conventions

### Key Format
- Use snake_case
- Be descriptive but concise
- Avoid abbreviations unless standard
- Examples: `low_followers_high_revenue`, `weekend_launchable`

### Title Format (Chinese)
- 8-15 characters ideal
- Action-oriented or insight-driven
- Avoid clickbait
- Examples: "粉丝不多，也能做到 $10k+ MRR", "周末可启动的项目"

### Title Format (English)
- 3-8 words ideal
- Clear and direct
- Parallel structure when possible
- Examples: "Few followers, still $10k+ MRR", "Projects you can start this weekend"

### Tag Selection
- Single word or short phrase
- Captures essence of template
- Consistent across similar templates
- Examples: "反常识", "快速启动", "精准垂直"

### Color Coding
- Use Tailwind color names
- Consistent meaning across templates:
  - `amber`: Counter-intuitive, surprising
  - `emerald`: Growth, success patterns
  - `blue`: Actionable, practical
  - `purple`: Technical, advanced
  - `slate`: Stable, boring but profitable
  - `teal`: Niche, specialized
  - `orange`: Innovation, differentiation
  - `green`: Quick start, accessible
  - `indigo`: Developer-focused
  - `cyan`: Platform/ecosystem

## Success Metrics for Templates

### Quantitative Metrics
- **Match count**: 5-15 products ideal
- **User engagement**: Click-through rate on template
- **Conversion**: Products explored from template
- **Retention**: Users returning to template

### Qualitative Metrics
- **Insight quality**: Does it change perspective?
- **Actionability**: Can users act on it?
- **Uniqueness**: Different from existing templates?
- **Coherence**: Do matched products feel related?

### Red Flags
- No products match filters
- Too many products match (>30)
- Products don't align with theme
- Insight feels generic or obvious
- Poor bilingual quality
