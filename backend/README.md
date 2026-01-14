# SaaS 产品分析工具

从 TrustMRR 抓取 SaaS 产品数据，通过 AI 分析找到适合独立开发者复制的产品机会。

## 环境准备

**要求：Python 3.10+**

```bash
# 1. 创建并激活虚拟环境
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# 2. 安装依赖
pip install -r requirements.txt
playwright install chromium

# 3. 配置环境变量
cp .env.example .env
```

编辑 `.env` 文件：
```bash
OPENAI_API_KEY=your_api_key        # Landing Page AI分析
ANTHROPIC_API_KEY=your_api_key     # AI助手

# 代理（可选）
HTTP_PROXY=http://127.0.0.1:7890
HTTPS_PROXY=http://127.0.0.1:7890
```

---

## 每日更新流程

```bash
# 1. 抓取数据（产品信息 + 收入时序）
python main.py scrape

# 2. 赛道分析
python main.py analyze category

# 3. 选品分析
python main.py analyze product --all --save

# 4. Landing Page 分析（增量）
python main.py analyze landing --update

# 5. 综合分析（增量）
python main.py analyze comprehensive --update
```

---

## 命令说明

### scrape - 数据抓取

```bash
python main.py scrape                    # 抓取全部
python main.py scrape --max-startups 10  # 限制数量（测试）
```

### analyze category - 赛道分析

```bash
python main.py analyze category          # 分析所有赛道
```

### analyze product - 选品分析

```bash
python main.py analyze product --all --save   # 分析所有产品（推荐）
```

### analyze landing - Landing Page 分析

```bash
python main.py analyze landing --update  # 增量更新（推荐）
```

---

## API 服务

```bash
uvicorn api.main:app --port 8001 --reload
```

---

## 数据库表

| 表名 | 说明 | 更新命令 |
|------|------|----------|
| `startups` | 产品信息 | `scrape` |
| `revenue_history` | 收入时序 | `scrape` |
| `founders` | 创始人 | `scrape` |
| `leaderboard_entries` | 排行榜 | `scrape` |
| `category_analysis` | 赛道分析 | `analyze category` |
| `product_selection_analysis` | 选品分析 | `analyze product --all --save` |
| `landing_page_snapshots` | 官网快照 | `analyze landing --update` |
| `landing_page_analysis` | 官网分析 | `analyze landing --update` |
| `comprehensive_analysis` | 综合分析 | `analyze comprehensive --update` |
| `producthunt_posts` | Product Hunt 产品数据 | `sync_producthunt.py` |

---

## Product Hunt 数据同步

独立存储 Product Hunt 产品热度数据，与 TrustMRR 收入数据分开管理。

### 配置 Token

1. 访问 https://api.producthunt.com/v2/oauth/applications 创建应用
2. Redirect URI 随便填（如 `https://localhost/callback`）
3. 点击 "Generate Developer Token" 获取 Token
4. 配置到 `.env`：

```bash
# 单个 Token
PH_TOKEN=your_token_here

# 或多个 Token（提高抓取效率）
PH_TOKENS=token1,token2,token3
```

### 初始化数据库

```bash
# 新数据库
python migrations/add_producthunt_table.py

# 已有数据库添加新字段
python migrations/add_producthunt_new_fields.py
```

### 同步命令

```bash
# 测试连接
python scripts/sync_producthunt.py --test

# 抓取新产品（每天运行，遇到已有的就停止）
python scripts/sync_producthunt.py --new

# 按日期分段抓取历史数据（推荐，可绕过 API 深度限制）
python scripts/sync_producthunt.py --bydate --start 2024-01-01 --end 2024-12-31

# 抓取历史数据（简单翻页，有深度限制）
python scripts/sync_producthunt.py --history --pages 100

# 刷新已有产品的热度数据
python scripts/sync_producthunt.py --refresh --limit 500
```

### 四种模式说明

| 模式 | 用途 | 配额消耗 | 断点续抓 |
|------|------|---------|---------|
| `--new` | 每天抓新上榜产品 | 低 | 不需要 |
| `--bydate` | 按月分段抓历史（推荐） | 可控 | ✅ 自动 |
| `--history` | 简单翻页抓历史 | 可控 | ✅ 自动 |
| `--refresh` | 更新热度数据 | 低 | 不需要 |

### 数据字段说明

| 字段 | 说明 |
|------|------|
| `website` | PH API 返回的重定向链接 |
| `website_resolved` | 自动解析后的真实官网地址 |
| `user` | 产品创建者信息 (JSON) |
| `media` | 产品媒体资源 (JSON) |
| `product_links` | 产品相关链接 (JSON) |

> 抓取时会自动解析 PH 重定向 URL，获取真实官网地址存入 `website_resolved`

### 推荐用法

```bash
# 首次：按日期抓取历史数据（可获取大量数据）
python scripts/sync_producthunt.py --bydate --start 2020-01-01 --end 2025-01-01

# 每天：抓取新产品
python scripts/sync_producthunt.py --new

# 每周：刷新热度数据
python scripts/sync_producthunt.py --refresh --limit 1000
```

### 定时任务示例（cron）

```bash
# 每天早上8点抓新产品
0 8 * * * cd /path/to/backend && python scripts/sync_producthunt.py --new

# 每周日凌晨抓历史数据
0 2 * * 0 cd /path/to/backend && python scripts/sync_producthunt.py --bydate --start 2020-01-01 --end 2026-01-31
```

### 断点续抓说明

`--bydate` 模式支持**页级断点续抓**：
- 每抓完一页自动保存进度到 `data/ph_bydate_checkpoint.json`
- 中断后（限流/Ctrl+C）再次运行相同命令，自动从上次的**精确位置**继续
- 不会重复请求已抓过的页面，不浪费 API 额度

```bash
# 第一次运行，抓到 2025-06 第 23 页被限流
python scripts/sync_producthunt.py --bydate --start 2025-01-01 --end 2025-12-31
# 输出: [Rate Limited] Saved at page 23, run again to continue

# 第二次运行，自动从 2025-06 第 24 页继续
python scripts/sync_producthunt.py --bydate --start 2025-01-01 --end 2025-12-31
# 输出: [Resume] From 2025-06-01, page 24
```

**长期抓取策略**：
```bash
# 设定一个大范围，每次运行会自动从断点继续
python scripts/sync_producthunt.py --bydate --start 2020-01-01 --end 2026-12-31

# 额度用完后等 15 分钟再运行，会接着上次位置继续
# 重复运行直到全部抓完
```

### Rate Limit

- 每个 Token：6250 complexity points / 15 分钟
- 每页约消耗 100-150 points，约能抓 40-60 页
- 限流后自动等待到重置时间，然后继续
- 多 Token 配置 `PH_TOKENS=token1,token2` 可翻倍配额

---

## AI 助手配置

```bash
ANTHROPIC_API_KEY=your_api_key
```

需要 `claude-agent-sdk` 支持 `accumulate_streaming_content` 参数（2025年1月后版本）。
