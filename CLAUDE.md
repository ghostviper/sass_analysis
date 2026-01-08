# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A full-stack SaaS product analysis tool that scrapes TrustMRR data and performs multi-dimensional AI-powered analysis to identify opportunities for indie developers.

**Stack:**
- Backend: Python 3.10+, FastAPI, SQLAlchemy, Playwright, OpenAI SDK
- Frontend: Next.js 14 (App Router), TypeScript, Tailwind CSS, Recharts
- Database: MySQL (recommended) or SQLite (development)

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
# Claude Agent SDK - Required
ANTHROPIC_API_KEY=sk-ant-...

# Claude Model Configuration - 4 model environment variables
ANTHROPIC_MODEL=claude-sonnet-4-5-20250929
ANTHROPIC_DEFAULT_SONNET_MODEL=claude-sonnet-4-5-20250929
ANTHROPIC_DEFAULT_HAIKU_MODEL=claude-sonnet-4-5-20250929
ANTHROPIC_DEFAULT_OPUS_MODEL=claude-opus-4-5-20251101

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
- PostgreSQL/Supabase (recommended): `postgresql://user:password@host:port/database`
- MySQL: `mysql://user:password@host:port/database`
- SQLite (development): `backend/data/sass_analysis.db`
- Async SQLAlchemy with `AsyncSessionLocal`
- Use `get_db_session()` context manager for queries

**Supabase Setup (Recommended):**
```bash
# 1. Local Supabase (using Docker)
# Install Supabase CLI: https://supabase.com/docs/guides/cli
supabase start

# Default local connection:
# Host: localhost
# Port: 54322
# User: postgres
# Password: postgres
# Database: postgres

# 2. Update backend/.env
DATABASE_URL=postgresql://postgres:postgres@localhost:54322/postgres

# 3. Migrate data from SQLite (optional)
cd backend
python scripts/migrate_sqlite_to_postgres.py
```

**MySQL Setup:**
```bash
# 1. Create MySQL database
mysql -u root -p
CREATE DATABASE sass_analysis CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'sass_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON sass_analysis.* TO 'sass_user'@'localhost';
FLUSH PRIVILEGES;

# 2. Update backend/.env
DATABASE_URL=mysql://sass_user:your_password@localhost:3306/sass_analysis

# 3. Migrate data from SQLite (optional)
cd backend
python scripts/migrate_sqlite_to_mysql.py
```

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

## Web Search Feature

### Overview

The application supports web search functionality powered by Tavily AI, allowing users to search for information about products, market trends, indie hacker discussions, and community insights from sources like Reddit, IndieHackers, Product Hunt, and the general web.

### Architecture

**Search Services** (`backend/services/search/`):
- `base.py` - Abstract base classes and data structures
- `tavily.py` - Tavily Search API (AI-optimized search)
- `factory.py` - Service factory and health checks

**Agent Tools** (`backend/agent/tools.py`):
- `web_search_tool` - Web search with optional site filtering

### Configuration

Add to `backend/.env`:

```bash
# Tavily Search (Required)
TAVILY_API_KEY=your_tavily_key

# Optional: Proxy settings
HTTP_PROXY=http://127.0.0.1:7890
HTTPS_PROXY=http://127.0.0.1:7890
```

### Setup Instructions

**1. Get Tavily API Key:**

```bash
# 1. Visit https://tavily.com/
# 2. Sign up and get API Key
# 3. Add to backend/.env:
TAVILY_API_KEY=your_key
```

**2. Install Dependencies:**
```bash
cd backend
pip install aiohttp
```

**3. Test Configuration:**
```bash
cd backend
python -m services.search.factory
```

### Usage

**Frontend:**
1. Navigate to `/assistant` page
2. Click "联网搜索" (Web Search) button to enable web search
3. Ask questions like:
   - "搜索Reddit上关于独立开发者的讨论"
   - "在IndieHackers上查找成功案例"
   - "Product Hunt上有哪些热门的SaaS产品"
   - "查找关于[产品名]的社区反馈"

**Agent Tool:**

The AI agent automatically uses the web search tool when enabled:

- `web_search(query, limit, site)` - Search the web with optional site restriction (e.g., "reddit.com", "indiehackers.com", "producthunt.com")

### How It Works

1. **User enables web search** by clicking the toggle button
2. **Frontend sends** `enable_web_search: true` to `/api/chat/stream`
3. **AI agent** receives web search capability in system prompt
4. **Agent calls** `web_search_tool` with appropriate query
5. **Backend** uses Tavily to search across the web
6. **Results** are formatted and returned with source links
7. **AI synthesizes** findings and presents to user

### Tavily Search

**Tavily** is an AI-optimized search API designed for LLMs and AI agents:

- **Best for**: AI agents, semantic search, community discussions
- **Pros**:
  - AI-generated answers and summaries
  - Relevance scoring optimized for LLMs
  - Supports site-specific searches
  - Fast and reliable
- **Cons**: Requires API key (paid service)
- **Rate**: Based on your Tavily plan
- **Docs**: https://docs.tavily.com/

### Testing

**Test search service:**
```bash
cd backend
python -m services.search.factory
```

**Test via frontend:**
1. Start backend: `uvicorn api.main:app --port 8001 --reload`
2. Start frontend: `npm run dev`
3. Visit http://localhost:3000/assistant
4. Enable web search and ask questions

### Troubleshooting

**"Tavily search not configured"**
- Set `TAVILY_API_KEY` in `backend/.env`
- Run `python -m services.search.factory` to verify configuration

**Search returns empty results**
- Check API key validity at https://tavily.com/
- Verify proxy settings if behind firewall
- Check your Tavily plan rate limits

**Import errors**
- Ensure `aiohttp` is installed: `pip install aiohttp`
- Check Python path includes backend directory

**Agent doesn't call search tool**
- Verify web search is enabled in the frontend
- Check agent tools are registered in `agent/client.py`
- Try more explicit prompts: "请搜索相关信息"

### Rate Limits

- **Tavily**: Based on your plan (check https://tavily.com/pricing)

### Future Enhancements

- [ ] Search result caching (Redis/SQLite)
- [ ] Sentiment analysis on community discussions
- [ ] Trend tracking across sources
- [ ] Search history and bookmarks
- [ ] More specialized search modes (news, academic, etc.)

## Chat API Streaming Events (V2)

### Overview

The chat API uses Server-Sent Events (SSE) for real-time streaming responses. The V2 event format is based on content blocks, providing fine-grained control over different output types.

### Event Types

| Type | Layer | Description |
|------|-------|-------------|
| `block_start` | varies | A content block is starting |
| `block_delta` | varies | Incremental content for a block |
| `block_end` | varies | A content block has completed |
| `tool_start` | process | Tool execution is starting |
| `tool_end` | process | Tool execution completed |
| `status` | debug | System status update |
| `done` | primary | Stream completed |
| `error` | primary | Error occurred |

### Output Layers

- **primary**: Final output content (text responses) - displayed to users
- **process**: Intermediate processing (thinking, tool calls) - collapsible/hidden by default
- **debug**: Debug information - not shown to users

### Block Types

- **thinking**: Claude's reasoning process (layer: process)
- **text**: Final text response (layer: primary)
- **tool_use**: Tool invocation (layer: process)
- **tool_result**: Tool execution result (layer: process)

### Event Format

```json
{
  "type": "block_delta",
  "layer": "primary",
  "block_id": "block_0",
  "block_type": "text",
  "content": "Hello, how can I help you today?"
}
```

### Frontend Implementation

The frontend parses events in `streamFromBackend()`:

1. **block_start**: Initialize content block tracking
2. **block_delta**: Accumulate content based on `block_type`
   - `thinking` → Collapsible thinking panel
   - `text` (layer: primary) → Main response display
3. **block_end**: Finalize content block
4. **tool_start/tool_end**: Update tool execution timeline

### Backend Implementation

The backend (`agent/client.py`) converts Claude Agent SDK events to V2 format:

- `content_block_start` → `block_start`
- `content_block_delta` → `block_delta`
- `content_block_stop` → `block_end`

## Redis Session Storage

### Overview

Chat sessions are stored in Redis for real-time operations, with asynchronous persistence to SQLite for durability. This architecture provides:

- **Low latency**: Redis handles all real-time read/write operations
- **Durability**: SQLite provides persistent storage
- **Graceful fallback**: Automatically falls back to SQLite if Redis is unavailable

### Architecture

```
Frontend ─> Backend API ─> Redis (primary) ─> SQLite (sync)
                              │
                         SyncWorker (background)
```

**Components**:
- `services/redis_client.py` - Connection pool and basic operations
- `services/session_store.py` - Session and message CRUD with fallback
- `services/sync_worker.py` - Background sync task
- `config/redis_config.py` - Configuration management

### Configuration

Add to `backend/.env`:

```bash
# Redis connection URL
REDIS_URL=redis://localhost:6379/0

# Enable/disable Redis (if disabled, falls back to SQLite)
REDIS_ENABLED=true

# Optional password
# REDIS_PASSWORD=your_password

# Connection settings
REDIS_MAX_CONNECTIONS=20
REDIS_SESSION_TTL=604800      # 7 days
REDIS_MESSAGE_TTL=604800      # 7 days

# Sync settings
SYNC_INTERVAL_SECONDS=60      # How often to sync
SYNC_ON_DONE=true             # Sync immediately after stream
REDIS_FALLBACK_ON_ERROR=true  # Fall back to SQLite on error
```

### Data Flow

1. **Chat request**: Messages saved to Redis immediately
2. **Stream completion**: Session marked for sync
3. **SyncWorker**: Periodically syncs dirty sessions to SQLite
4. **Fallback**: If Redis unavailable, direct SQLite access

### Redis Keys

| Key Pattern | Type | Description |
|-------------|------|-------------|
| `chat:session:{id}` | Hash | Session metadata |
| `chat:message:{session}:{id}` | Hash | Individual message |
| `chat:messages:{session}` | Sorted Set | Message index by sequence |
| `chat:sessions:list:{scope}` | Sorted Set | Session list by update time |
| `chat:dirty_sessions` | Set | Sessions needing sync |

### Testing

```bash
# Test Redis connection
cd backend
python -c "import asyncio; from services.redis_client import RedisClient; print(asyncio.run(RedisClient.health_check()))"

# Check sync worker status
# (via API endpoint or logs)
```

### Troubleshooting

**Redis connection fails**
- Check Redis is running: `redis-cli ping`
- Verify `REDIS_URL` in `.env`
- Check firewall/network settings

**Sessions not persisting**
- Check `SYNC_ON_DONE=true` in config
- Verify SyncWorker is running (check logs)
- Check SQLite file permissions

**Fallback mode active**
- Redis is unavailable or disabled
- Check `REDIS_ENABLED=true` in config
- Application continues working with SQLite
