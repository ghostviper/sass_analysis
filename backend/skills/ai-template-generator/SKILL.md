---
name: AI Template Generator
description: This skill should be used when the user asks to "generate curation templates", "create new curation templates with AI", "expand curation themes", "analyze products for template ideas", or mentions AI-powered template generation for the curation system. Provides comprehensive guidance for using AI to generate structured CurationTemplate objects based on product analysis and market insights.
version: 0.2.0
---

# AI Template Generator Skill

## Architecture

This skill is **completely independent** and self-contained:

- ✅ **No external code dependencies**: All logic is within the skill folder
- ✅ **API-based data access**: Uses HTTP APIs instead of direct database imports
- ✅ **Standalone OpenAI client**: Independent implementation without external service dependencies
- ✅ **Portable**: Can be moved or deployed independently

### Components

1. **`scripts/openai_client.py`**: Standalone OpenAI API client
2. **`scripts/api_client.py`**: Backend API client for data queries
3. **`scripts/generate_template.py`**: Main template generation script
4. **`scripts/validate_template.py`**: Template validation script
5. **`scripts/preview_template.py`**: Product preview script

### Backend API Requirements

The skill requires these backend API endpoints (already implemented in `backend/api/routes/skill_support.py`):

- `GET /api/skill-support/db-stats`: Get database statistics
- `POST /api/skill-support/preview-template`: Preview matching products

**Start the backend server before using scripts:**
```bash
cd backend
python run_server.py
```

## Purpose

This skill enables AI-powered generation of curation templates for the daily curation system. It transforms product analysis insights and market observations into structured `CurationTemplate` objects that can be used to discover and curate products with specific characteristics, creating valuable themed collections for users.

The AI acts as a senior product curation expert who understands:
- Product design patterns and business models
- Market dynamics and competitive positioning
- User psychology and decision-making factors
- What makes products successful or unique

## When to Use This Skill

Use this skill when:
- Expanding the curation template library with new themes
- Discovering patterns in successful products that warrant new templates
- Creating specialized templates for niche markets or specific user personas
- Analyzing product data to identify underserved curation angles
- Validating or refining existing template ideas

## Core Workflow

### 0. Discover Opportunities (NEW - AI-Powered)

**Let AI automatically discover valuable curation angles** based on data analysis:

```bash
backend\venv\Scripts\python.exe backend/skills/ai-template-generator/scripts/discover_opportunities.py \
  --count 5 \
  --output opportunities
```

**Parameters**:
- `--count` / `-c`: Number of opportunities to discover (default: 5)
- `--model` / `-m`: AI model to use (default: from OPENAI_MODEL env)
- `--output` / `-o`: Output filename (without extension, saved to `skill/output/`)
- `--api-url`: Backend API URL (default: http://localhost:8001)

**Output Location**: All files are saved to `backend/skills/ai-template-generator/output/`:
- `opportunities.json` - Structured opportunity data
- `opportunities.txt` - Human-readable formatted text
- `opportunities_analysis.json` - Type distribution analysis

If no `--output` is specified, files are named with timestamp: `opportunities_20260120_143022.json`

The script will:
1. Analyze mother theme distributions
2. Identify interesting product characteristic combinations
3. Apply curation logic principles (see `references/curation-logic-v2.md`)
4. Generate observation/guidance pairs with rationale
5. Output structured opportunities ready for template generation

**Output includes**:
- Opportunity type (10 types: contrast/cognitive/action/niche + 6 market-driven types)
- Priority score (1-10)
- Target user persona
- Expected product count
- Observation and guidance text
- Market insight, user value, business logic
- Framework application tracking

### 1. Understand Template Structure

Templates follow the `CurationTemplate` dataclass structure defined in `backend/curation/daily_templates.py`:

```python
@dataclass
class CurationTemplate:
    key: str                          # Unique identifier (snake_case)
    title_zh: str                     # Chinese title
    title_en: str                     # English title
    description_zh: str               # Chinese description
    description_en: str               # English description
    insight_zh: str                   # Chinese insight/takeaway
    insight_en: str                   # English insight/takeaway
    tag_zh: str                       # Chinese tag
    tag_en: str                       # English tag
    tag_color: str                    # Tailwind color name
    curation_type: str                # contrast/cognitive/action/niche
    filter_rules: Dict[str, Any]      # Filtering criteria
    conflict_dimensions: List[str]    # Dimensions creating contrast
    min_products: int = 3             # Minimum products needed
    max_products: int = 8             # Maximum products to show
    priority: int = 5                 # Priority 1-10 (higher = more important)
```

### 2. Generate Templates Using AI Script

**Prerequisites**: Backend server must be running on `http://localhost:8001`

Use the main generation script with observation dimensions and guidance:

```bash
backend\venv\Scripts\python.exe backend/skills/ai-template-generator/scripts/generate_template.py \
  --observation "低粉丝但高收入的产品" \
  --guidance "寻找产品驱动而非IP驱动的案例" \
  --count 2 \
  --output vertical_market_templates
```

**Parameters**:
- `--observation` / `-o`: Observation dimensions (required)
- `--guidance` / `-g`: Generation guidance (required)
- `--count` / `-c`: Number of templates to generate (default: 3)
- `--model` / `-m`: AI model to use (default: from OPENAI_MODEL env)
- `--output` / `-f`: Output filename (without .py extension, saved to `skill/output/`)
- `--api-url`: Backend API URL (default: http://localhost:8001)

**Output Location**: All files are saved to `backend/skills/ai-template-generator/output/`:
- `vertical_market_templates.py` - Generated Python code with CurationTemplate objects

If no `--output` is specified, files are named with timestamp: `templates_20260120_143022.py`

The script will:
1. Query backend API for database statistics
2. Apply copywriting guidelines (see `references/copywriting-guidelines.md`)
3. Use AI to generate structured templates with engaging, grounded copy
4. Output templates in Python code format ready for integration

**Copywriting Quality**: The AI follows strict guidelines to ensure:
- **Title**: 6-12 chars (CN) / 3-6 words (EN), punchy and attention-grabbing
- **Description**: 30-60 chars (CN) / 20-40 words (EN), clear value proposition
- **Insight**: 15-30 chars (CN) / 10-20 words (EN), actionable golden nugget

See `references/copywriting-guidelines.md` for detailed examples and best practices.

**Note**: The script uses standalone clients (`openai_client.py` and `api_client.py`) that don't depend on external backend code.

### 3. Validate Generated Templates

Before integrating templates, validate them:

```bash
backend\venv\Scripts\python.exe backend/skills/ai-template-generator/scripts/validate_template.py \
  --template-file generated_templates.py
```

Validation checks:
- All required fields present
- Filter rules reference valid database fields
- Conflict dimensions align with filter rules
- Priority and product count ranges are reasonable
- Bilingual content is complete

### 4. Preview Matching Products

**Prerequisites**: Backend server must be running

Test templates against the database to see which products match:

```bash
# First, save filter rules to a JSON file
echo '{"startup": {"revenue_30d": {"min": 10000}, "founder_followers": {"max": 1000}}}' > filter_rules.json

# Then preview
backend\venv\Scripts\python.exe backend/skills/ai-template-generator/scripts/preview_template.py \
  --template-key "low_followers_high_revenue" \
  --filter-rules filter_rules.json \
  --limit 10 \
  --api-url "http://localhost:8001"
```

**Parameters**:
- `--template-key` / `-k`: Template key name (required)
- `--filter-rules` / `-f`: JSON file with filter rules (required)
- `--limit` / `-l`: Max products to show (default: 10)
- `--api-url`: Backend API URL (default: http://localhost:8001)

This helps verify that:
- Templates match the intended products
- Filter rules are neither too strict nor too loose
- The resulting collection is valuable and coherent
- Filter rules are neither too strict nor too loose
- The resulting collection is valuable and coherent

## Copywriting Quality Standards

### Why Copywriting Matters

Template copy appears in the discover page curation cards and must:
- **Grab attention** in a crowded feed
- **Communicate value** quickly and clearly
- **Inspire action** without hype or misleading claims
- **Feel authentic** and grounded in real data

Poor copy = users scroll past. Great copy = users click and engage.

### The Three Text Fields

#### 1. Title (标题)
**Display**: Card top, most prominent, bold font
**Character limits**: 6-12 chars (CN) / 3-6 words (EN)
**Purpose**: Stop the scroll, create curiosity

**Good examples**:
- ✅ "小众垂直，月入5万" (specific number, clear contrast)
- ✅ "功能极简，收入惊人" (punchy, intriguing)
- ✅ "$50K/mo from Tiny Niches" (concrete, surprising)

**Bad examples**:
- ❌ "垂直市场的B2B SMB产品" (boring, jargon-heavy)
- ❌ "简单功能但是盈利的产品" (wordy, no punch)
- ❌ "Vertical Market Products" (generic, no hook)

#### 2. Description (描述)
**Display**: Below title, 2-line truncation (line-clamp-2)
**Character limits**: 30-60 chars (CN) / 20-40 words (EN)
**Purpose**: Explain the curation logic and value

**Good examples**:
- ✅ "月收入5000+美元，创始人粉丝不到1000，专注垂直细分市场的B2B产品。打破'小众=低收入'的刻板印象。"
  - First sentence: concrete numbers + filter criteria
  - Second sentence: value proposition
  
**Bad examples**:
- ❌ "筛选market_scope=vertical、target_customer=b2b_smb、feature_complexity=simple..."
  - Technical jargon, not user-friendly

#### 3. Insight (洞察)
**Display**: Bottom of card, highlighted box with icon
**Character limits**: 15-30 chars (CN) / 10-20 words (EN)
**Purpose**: Deliver actionable golden nugget

**Good examples**:
- ✅ "小众不等于低收入，精准痛点胜过万千粉丝" (memorable, actionable)
- ✅ "做好一件事，胜过做十件平庸事" (quotable, clear direction)
- ✅ "Product value beats personal brand" (concise, powerful)

**Bad examples**:
- ❌ "垂直市场虽小，但聚焦精准痛点可实现高收入，无需大量粉丝支持。" (too long, wordy)
- ❌ "聚焦核心价值而非功能堆砌" (vague, no specific action)

### Copywriting Checklist

Before finalizing templates, verify:

**Title**:
- [ ] Within character limits (6-12 CN / 3-6 EN)
- [ ] Uses concrete numbers or vivid adjectives
- [ ] Creates curiosity or surprise
- [ ] Avoids jargon and technical terms
- [ ] Both CN and EN versions feel natural (not literal translations)

**Description**:
- [ ] Within character limits (30-60 CN / 20-40 EN)
- [ ] First sentence states filter criteria with numbers
- [ ] Second sentence explains value or breaks misconception
- [ ] Fits in 2 lines without awkward truncation
- [ ] Language is conversational and clear

**Insight**:
- [ ] Within character limits (15-30 CN / 10-20 EN)
- [ ] Provides actionable takeaway
- [ ] Memorable and quotable
- [ ] Not generic or cliché
- [ ] Feels like a golden nugget, not filler

**Overall**:
- [ ] No repetition between title/description/insight
- [ ] Grounded in data, not hype
- [ ] Authentic voice, not marketing-speak
- [ ] Bilingual quality (both languages strong)

For detailed guidelines and more examples, see `references/copywriting-guidelines.md`.

## Template Types and Characteristics

### Contrast Templates (反差型)
**Purpose**: Break conventional wisdom, create "aha" moments

**Characteristics**:
- High priority (8-10)
- Clear conflict between 2+ dimensions
- Counter-intuitive insights
- Examples: "Few followers, high revenue", "Simple features, profitable"

**Filter strategy**: Combine opposing characteristics (low X + high Y)

### Cognitive Templates (认知型)
**Purpose**: Provide new perspectives, shift mental models

**Characteristics**:
- Medium-high priority (6-8)
- Focus on positioning, pricing, or market insights
- Educational value
- Examples: "Pricing innovation", "Vertical niche success"

**Filter strategy**: Highlight specific success patterns or approaches

### Action Templates (行动型)
**Purpose**: Guide concrete actions, reduce decision paralysis

**Characteristics**:
- High priority (7-9)
- Actionable criteria (low barrier, clear MVP)
- Risk-reduction focus
- Examples: "Weekend launchable", "Low monetization risk"

**Filter strategy**: Emphasize feasibility and execution clarity

### Niche Templates (利基型)
**Purpose**: Serve specific audiences or markets

**Characteristics**:
- Lower priority (3-5)
- Targeted at specific personas or platforms
- Specialized knowledge required
- Examples: "Dev tools", "Platform ecosystem"

**Filter strategy**: Category or customer type filters

## Filter Rules Reference

Templates use three types of filters:

### Startup Filters
```python
"startup": {
    "revenue_30d": {"min": 5000, "max": 50000},
    "founder_followers": {"min": 100, "max": 1000},
    "team_size": {"max": 2},
    "category": {"contains": ["developer", "api"]}
}
```

### Selection Analysis Filters
```python
"selection": {
    "feature_complexity": ["simple", "moderate"],
    "startup_cost_level": ["low"],
    "ai_dependency_level": ["none", "light"],
    "target_customer": ["b2b_smb"],
    "market_scope": ["vertical"]
}
```

### Mother Theme Filters
```python
"mother_theme": {
    "success_driver": ["产品驱动"],
    "demand_type": ["主动搜索型"],
    "entry_barrier": ["低门槛快启动"],
    "mvp_clarity": ["清晰可执行"],
    "solo_feasibility": ["非常适合"],
    "primary_risk": {"not": ["变现转化"]}
}
```

### Landing Page Filters
```python
"landing_page": {
    "feature_count": {"max": 5},
    "has_instant_value_demo": true,
    "conversion_friendliness_score": {"min": 7.0}
}
```

## Best Practices

### Template Design
1. **Start with insight**: What unique perspective does this template provide?
2. **Define conflict**: For contrast templates, identify 2-3 conflicting dimensions
3. **Be specific**: Vague filters produce generic collections
4. **Test with data**: Always preview matching products before finalizing
5. **Bilingual quality**: Ensure both Chinese and English content are natural and compelling

### Filter Rules
1. **Combine dimensions**: Use 2-3 filter types for richer targeting
2. **Avoid over-filtering**: Aim for 5-15 matching products
3. **Use ranges wisely**: Min/max values should reflect real product distribution
4. **Leverage mother themes**: They provide high-level strategic filters
5. **Consider edge cases**: Test with extreme values

### Priority Assignment
- **10**: Core contrast themes with broad appeal
- **8-9**: High-value action or contrast templates
- **6-7**: Cognitive templates and specialized contrasts
- **4-5**: Niche templates for specific audiences
- **1-3**: Experimental or very narrow templates

## Additional Resources

### Reference Files

For detailed information, consult:
- **`references/copywriting-guidelines.md`** - Complete copywriting guide with examples and checklist
- **`references/domain-knowledge.md`** - User personas, business logic, market insights
- **`references/mother-themes.md`** - Complete mother theme definitions and usage
- **`references/database-schema.md`** - Database tables and field definitions
- **`references/curation-logic-basic.md`** - Quick reference for basic curation principles (~400 lines)
- **`references/curation-logic-v2.md`** - Complete market analysis framework for AI discovery (~1000+ lines)

**Note on Curation Logic Versions:**
- **Basic version**: Quick reference for core principles, product-centric patterns
- **v2 (Enhanced)**: Complete framework with Porter's Five Forces, Blue Ocean Strategy, Value Theory, Market Sizing, and Startup Metrics. Used by `discover_opportunities.py` script for market-driven discovery

### Example Files

Working examples in `examples/`:
- **`example-requests.md`** - Sample template generation requests
- **`example-templates.py`** - Generated template examples with annotations

### Scripts

Utility scripts in `scripts/`:
- **`discover_opportunities.py`** - AI-powered opportunity discovery (Enhanced v2)
- **`generate_template.py`** - Main AI-powered template generation with copywriting
- **`validate_template.py`** - Template validation and quality checks
- **`preview_template.py`** - Preview products matching template filters

### Output Directory

All generated files are saved to `backend/skills/ai-template-generator/output/`:
- Opportunity files: `opportunities_*.json`, `opportunities_*.txt`, `opportunities_*_analysis.json`
- Template files: `templates_*.py`, `*_templates.py`
- Files are named with timestamps if no custom name provided
- This keeps the workspace root clean and organized

## Integration Workflow

After generating and validating templates:

1. **Review generated code**: Check Python syntax and structure
2. **Add to daily_templates.py**: Insert into appropriate template list
3. **Update ALL_TEMPLATES**: Ensure new templates are included in the master list
4. **Test in curation**: Run daily curation generation to verify
5. **Monitor performance**: Track which templates produce valuable collections

## Common Patterns

### Finding Underserved Niches
```bash
# Analyze products with specific characteristics
python scripts/generate_template.py \
  --observation "高技术门槛但小团队成功的产品" \
  --guidance "寻找技术壁垒成为护城河的案例"
```

### Expanding Existing Themes
```bash
# Create variations of successful templates
python scripts/generate_template.py \
  --observation "类似'低粉丝高收入'但针对B2B市场" \
  --guidance "强调企业客户的付费意愿"
```

### Seasonal or Trend-Based Templates
```bash
# Generate templates for current trends
python scripts/generate_template.py \
  --observation "2024年AI工具中不依赖大模型的产品" \
  --guidance "传统技术解决新问题的案例"
```

## Quality Criteria

Good templates should:
- ✅ Provide unique insights not obvious from raw data
- ✅ Match 5-15 products (not too narrow, not too broad)
- ✅ Have clear, compelling bilingual titles and insights
- ✅ Use filter rules that align with the stated theme
- ✅ Create value for specific user personas or use cases

Avoid templates that:
- ❌ Are too similar to existing templates
- ❌ Match too few (<3) or too many (>30) products
- ❌ Have vague or generic insights
- ❌ Use arbitrary filter combinations without clear rationale
- ❌ Lack bilingual quality or have machine-translation feel

## Troubleshooting

### Template matches no products
- Check filter rules are not too restrictive
- Verify field names match database schema
- Review value ranges against actual data distribution

### Template matches too many products
- Add more specific filters
- Narrow value ranges
- Combine multiple filter dimensions

### AI generates invalid filter rules
- Check `references/database-schema.md` for valid fields
- Provide more specific guidance in generation prompt
- Validate output before integration

### Bilingual content quality issues
- Provide cultural context in generation prompt
- Review and refine AI output manually
- Ensure insights resonate in both languages
