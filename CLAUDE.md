# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A full-stack SaaS product analysis tool that scrapes TrustMRR data and performs multi-dimensional AI-powered analysis to identify opportunities for indie developers.

**Stack:**
- Backend: Python 3.10+, FastAPI, SQLAlchemy, Playwright, OpenAI SDK
- Frontend: Next.js 14 (App Router), TypeScript, Tailwind CSS, Recharts
- Database: SQLite

## Development Commands

### Backend Setup

```bash
cd backend

# Create and activate virtual environment
python3.10 -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Configure environment
cp .env.example .env
# Edit .env with OPENAI_API_KEY and optional proxy settings
```

### Backend Commands

```bash
# Data collection (includes revenue time-series)
python main.py scrape                    # Scrape all products
python main.py scrape --max-startups 10  # Test with limited products

# Analysis pipeline (run in order)
python main.py analyze category          # Analyze market categories
python main.py analyze product --opportunities --save  # Find opportunities
python main.py analyze landing --update  # Incremental landing page analysis
python main.py analyze comprehensive --top --limit 50  # Generate recommendations

# API server
uvicorn api.main:app --port 8001 --reload
```

### Frontend Setup & Commands

```bash
cd frontend

# Install dependencies
npm install

# Development
npm run dev      # Start dev server (http://localhost:3000)

# Production
npm run build    # Build for production
npm start        # Start production server

# Linting
npm run lint
```

## Architecture

### Data Flow Pipeline

```
1. scrape → Crawl TrustMRR + Extract revenue time-series
   ↓
2. analyze category → Identify blue ocean/red ocean markets
   ↓
3. analyze product → Score individual dev suitability
   ↓
4. analyze landing → AI analysis of product websites
   ↓
5. analyze comprehensive → Generate final recommendations
```

### Database Schema (9 Tables)

**Core Data:**
- `startups` - Product information (name, slug, revenue, founder, etc.)
- `revenue_history` - Daily revenue time-series data (date, revenue, mrr, charges)
- `leaderboard_entries` - Historical ranking snapshots
- `founders` - Founder information

**Analysis Results:**
- `category_analysis` - Market type classification (blue_ocean, red_ocean, etc.)
- `product_selection_analysis` - Suitability scores and tags
- `landing_page_snapshots` - Scraped website HTML
- `landing_page_analysis` - AI-extracted features, pricing, positioning
- `comprehensive_analysis` - Final recommendation scores

### Frontend Architecture

- **App Router** (`src/app/`): Page-based routing
  - `/` - Dashboard overview
  - `/categories` - Market analysis
  - `/products` - Product listings
  - `/products/[slug]` - Product detail with radar charts
- **Components** (`src/components/`): Reusable UI components
- **API Integration** (`src/lib/api.ts`): Backend communication via Next.js rewrites

## Critical Implementation Details

### Revenue Time-Series Extraction

**Important:** TrustMRR loads chart data via API, not embedded in HTML.

- **Location:** `backend/crawler/chart_extractor.py`
- **Method:** Direct API call to `https://trustmrr.com/api/startup/revenue/{slug}?granularity=daily&period=4w`
- **Timing:** Called during `scrape` command, before HTML snapshot
- **Data:** Returns 28 days of daily revenue, MRR, charges, subscriptions
- **Note:** Not all products have time-series data (API may return empty array)

```python
# In acquire_scraper.py:
revenue_history = await extract_revenue_history(page, slug)
# This makes a direct API request using page.request.get()
```

### Analysis Order Dependencies

**Must run in sequence:**

1. `scrape` first - Populates `startups` and `revenue_history` tables
2. `analyze category` - Requires startup data, creates market classifications
3. `analyze product` - Requires startup data, can run independently
4. `analyze landing` - Requires startup data + website URLs, uses OpenAI API
5. `analyze comprehensive` - Requires all previous analyses

**Incremental Updates:**
- `analyze landing --update` - Only analyzes new/unanalyzed products (supports resume)
- `analyze product --opportunities --save` - Can be re-run to update scores

### Environment Configuration

**Backend `.env`:**
```bash
# Required for landing page analysis
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://...  # Optional
OPENAI_MODEL=gpt-4o-mini     # Optional

# Optional proxy
HTTP_PROXY=http://127.0.0.1:7890
HTTPS_PROXY=http://127.0.0.1:7890
```

**Frontend:** No environment variables needed (proxies to backend via `next.config.js`)

### Frontend-Backend Integration

- Backend API runs on `http://localhost:8001`
- Frontend proxies `/api/*` requests to backend via Next.js rewrites
- No CORS configuration needed
- Frontend expects backend to be running during development

### Common Patterns

**Scraping vs Update:**
- `scrape` - Visits live website, extracts time-series data (recommended)
- `update` - Parses local HTML snapshots, no time-series data (legacy)

**Analysis Flags:**
- `--save` - Persist results to database
- `--force` - Re-scrape/re-analyze even if data exists
- `--skip-analyzed` - Skip products with existing analysis
- `--update` - Incremental mode (equivalent to `--all --skip-analyzed`)

**Database Access:**
- SQLite file: `backend/data/sass_analysis.db`
- Async SQLAlchemy with `AsyncSessionLocal`
- Use `get_db_session()` context manager for queries

## Testing

**Backend:**
```bash
# Test OpenAI connection
python test_openai.py

# Test scraping (limited)
python main.py scrape --max-startups 3

# Test analysis on single product
python main.py analyze product --slug example-product --save
```

**Frontend:**
```bash
# Ensure backend is running first
npm run dev
# Visit http://localhost:3000
```

## Troubleshooting

**"No revenue history data available"**
- Normal for some products - API returns empty array
- Not an error, just means product doesn't share time-series data

**Landing page analysis fails**
- Check `OPENAI_API_KEY` in `.env`
- Test connection: `python test_openai.py`
- Check proxy settings if behind firewall

**Frontend shows no data**
- Ensure backend API is running on port 8001
- Run analysis commands to populate database
- Check browser console for API errors

**Playwright browser issues**
- Re-run: `playwright install chromium`
- Check system dependencies for headless browser
