# SaaS 产品分析工具

从 TrustMRR 抓取 SaaS 产品数据，通过 AI 分析找到适合独立开发者复制的产品机会。

## 环境准备

**要求：Python 3.10+**

### Windows

```bash
# 1. 创建虚拟环境
py -3.10 -m venv venv

# 2. 激活虚拟环境
venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt
playwright install chromium

# 4. 配置环境变量
copy .env.example .env
```

### Mac/Linux

```bash
# 1. 创建虚拟环境
python3.10 -m venv venv

# 2. 激活虚拟环境
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt
playwright install chromium

# 4. 配置环境变量
cp .env.example .env
```

编辑 `.env` 文件：
```bash
OPENAI_API_KEY=your_api_key        # 必填，用于Landing Page AI分析
OPENAI_BASE_URL=https://...        # 可选，自定义API地址
OPENAI_MODEL=gpt-4o-mini           # 可选，默认模型

# 代理（可选）
HTTP_PROXY=http://127.0.0.1:7890
HTTPS_PROXY=http://127.0.0.1:7890
```

---

## 数据流程概览

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           数据采集与分析流程                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  阶段1: 数据抓取 (scrape)                                                │
│  ├── 访问 TrustMRR 产品页面                                              │
│  ├── 提取收入时序数据 (dailyRevenue)                                     │
│  ├── 保存 HTML 快照                                                      │
│  ├── 解析产品完整信息                                                    │
│  └── 入库: startups + revenue_history + leaderboard_entries            │
│                                                                         │
│  阶段2: 赛道分析 (analyze category)                                      │
│  └── 分析市场类型，识别蓝海/红海                                          │
│                                                                         │
│  阶段3: 选品分析 (analyze product)                                       │
│  └── 评估产品复杂度、IP依赖度、个人开发适合度                              │
│                                                                         │
│  阶段4: Landing Page 分析 (analyze landing)                              │
│  └── AI 分析产品官网，提取定位、功能、定价等                               │
│                                                                         │
│  阶段5: 综合分析 (analyze comprehensive)                                 │
│  └── 汇总所有维度，生成推荐列表                                           │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 每日更新流程

### 完整更新（推荐）

```bash
# 1. 抓取数据（包含产品信息 + 收入时序数据）
python main.py scrape

# 2. 赛道分析
python main.py analyze category

# 3. 选品分析
python main.py analyze product --opportunities --limit 500 --save

# 4. Landing Page 分析（增量，只分析新增产品）
python main.py analyze landing --update

# 5. 综合分析（可选）
python main.py analyze comprehensive --top --limit 50
```

### 快速测试

```bash
# 只抓取少量产品测试
python main.py scrape --max-startups 5
```

---

## 命令详解

### scrape - 数据抓取

抓取 TrustMRR 网站数据，一次性完成：
- 产品基本信息（名称、描述、分类、创始人等）
- 财务数据（收入、MRR、增长率等）
- **收入时序数据**（每日收入明细，用于图表展示）
- 排行榜数据

```bash
python main.py scrape                    # 抓取全部产品
python main.py scrape --max-startups 10  # 限制数量（测试用）
python main.py scrape --skip-leaderboard # 跳过排行榜
```

> **注意**：`scrape` 命令已整合数据解析，无需单独执行 `update` 命令。

### analyze category - 赛道分析

分析各赛道的市场竞争情况。

```bash
python main.py analyze category                # 分析所有赛道
python main.py analyze category --name "AI"    # 分析指定赛道
python main.py analyze category --templates    # 显示模板化产品
```

### analyze product - 选品分析

评估产品的个人开发适合度。

```bash
# 筛选机会产品并保存
python main.py analyze product --opportunities --limit 100 --save

# 按条件筛选
python main.py analyze product --opportunities \
    --min-revenue 1000 \
    --max-complexity low \
    --limit 50 \
    --save

# 分析单个产品
python main.py analyze product --slug product-name --save
```

### analyze landing - Landing Page 分析

使用 AI 分析产品官网，提取定位、功能、定价等信息。

```bash
# 增量更新（推荐）- 只分析新增/未分析的产品
python main.py analyze landing --update

# 分析单个产品
python main.py analyze landing --slug product-name

# 强制重新分析（重新爬取官网）
python main.py analyze landing --slug product-name --force

# 批量分析前N个高收入产品
python main.py analyze landing --batch --limit 50 --skip-analyzed
```

### analyze comprehensive - 综合分析

汇总所有分析维度，生成推荐列表。

```bash
# 获取TOP推荐列表
python main.py analyze comprehensive --top --limit 30

# 分析单个产品并导出
python main.py analyze comprehensive --slug product-name --export report.json
```

---

## 辅助命令

```bash
# 同步创始人和排行榜数据（通常不需要单独执行）
python main.py sync

# 从HTML快照更新数据库（用于修复数据，通常不需要）
python main.py update
```

---

## 数据库表结构

| 表名 | 说明 | 更新时机 |
|------|------|----------|
| `startups` | 产品基本信息 | scrape |
| `revenue_history` | 收入时序数据（每日） | scrape |
| `leaderboard_entries` | 排行榜历史记录 | scrape |
| `founders` | 创始人信息 | scrape |
| `category_analysis` | 赛道分析结果 | analyze category |
| `product_selection_analysis` | 选品分析结果 | analyze product |
| `landing_page_snapshots` | 官网快照 | analyze landing |
| `landing_page_analysis` | 官网AI分析结果 | analyze landing |
| `comprehensive_analysis` | 综合分析结果 | analyze comprehensive |

---

## 分析维度说明

### 赛道分析 - 市场类型

| 类型 | 含义 | 建议 |
|-----|------|-----|
| `blue_ocean` | 竞争少，多数产品盈利 | 优先考虑 |
| `emerging` | 新兴市场，早期机会 | 值得关注 |
| `moderate` | 中等竞争 | 需要差异化 |
| `concentrated` | 头部集中 | 新手慎入 |
| `red_ocean` | 竞争激烈 | 避开 |
| `weak_demand` | 需求不足 | 避开 |

### 选品分析 - 组合匹配

| 组合 | 条件 | 说明 |
|-----|------|-----|
| 组合1 | 低粉丝 + 高收入 + 简短描述 + 成立<18月 | 产品驱动型，最优 |
| 组合2 | 简短描述 + 有收入 + 低复杂度 | 包装能力强或需求精准 |
| 组合3 | 小而美 + 不依赖AI + 收入>$1K | 功能简单，易复制 |

### 综合分析 - 评分维度

| 维度 | 说明 |
|-----|------|
| 个人可复制性 | 独立开发者能否复制 |
| 定位清晰度 | 产品定位是否清晰 |
| 痛点锋利度 | 解决的痛点是否明确 |
| 定价清晰度 | 定价是否透明易懂 |
| 转化友好度 | 用户转化路径是否顺畅 |
| 产品成熟度 | 产品完善程度 |

---

## API 服务

```bash
# 启动API服务
uvicorn api.main:app --port 8001 --reload

# 访问文档
# http://localhost:8001/docs
```

主要接口：
- `GET /api/startups` - 产品列表
- `GET /api/analysis/category/` - 赛道分析
- `GET /api/analysis/product/opportunities` - 机会产品
- `GET /api/analysis/landing/{slug}` - Landing Page分析

---

## 项目结构

```
backend/
├── main.py                  # CLI入口
├── crawler/                 # 爬虫模块
│   ├── acquire_scraper.py   # 产品页面爬虫
│   ├── leaderboard_scraper.py # 排行榜爬虫
│   ├── chart_extractor.py   # 收入时序数据提取
│   ├── html_extractor.py    # HTML清洗
│   ├── html_parser.py       # HTML解析
│   └── run.py               # 爬虫入口
├── analysis/                # 分析模块
│   ├── category_analyzer.py # 赛道分析
│   ├── product_selector.py  # 选品分析
│   ├── landing_analyzer.py  # Landing Page分析
│   └── comprehensive.py     # 综合分析
├── database/                # 数据库
│   ├── models.py            # 数据模型
│   └── db.py                # 数据库连接
├── api/                     # REST API
└── data/                    # 数据文件
    ├── sass_analysis.db     # SQLite数据库
    └── html_snapshots/      # HTML快照
```

---

## 常见问题

**Q: OpenAI 连接失败？**
```bash
# 检查连接
python test_openai.py

# 如需代理，在 .env 中配置
HTTPS_PROXY=http://127.0.0.1:7890
```

**Q: Landing Page 分析中断了怎么办？**
```bash
# 支持断点续传，使用增量更新模式继续
python main.py analyze landing --update
```

**Q: 如何重新分析单个产品？**
```bash
# 强制重新爬取并分析
python main.py analyze landing --slug xxx --force
```

**Q: scrape 和 update 有什么区别？**
- `scrape`：访问网站抓取最新数据，包含收入时序数据
- `update`：从本地 HTML 快照解析数据（不包含时序数据）
- **推荐使用 `scrape`**，它已整合完整的数据采集和解析流程

---

## AI 助手

项目集成了基于 Claude Agent SDK 的智能分析助手，支持流式对话和工具调用。

### 配置

在 `.env` 中配置：

```bash
ANTHROPIC_API_KEY=your_api_key       # 必填，Anthropic API Key
ANTHROPIC_BASE_URL=https://...       # 可选，自定义 API 地址
CLAUDE_MODEL=claude-sonnet-4-5       # 可选，默认模型
```

### Claude Agent SDK 版本要求

**重要**：流式输出功能依赖 `accumulate_streaming_content` 参数，该功能由 [PR #274](https://github.com/anthropics/claude-agent-sdk-python/pull/274) 引入。

请确保安装的 `claude-agent-sdk` 版本包含此功能（2025年1月后的版本）。

```bash
# 安装最新版本
pip install claude-agent-sdk --upgrade

# 或指定版本（如果有兼容性问题）
pip install claude-agent-sdk>=0.x.x
```

**关键配置**（在 `agent/client.py` 中）：

```python
options = ClaudeAgentOptions(
    include_partial_messages=True,
    accumulate_streaming_content=True,  # 必须设置为 True，否则流式输出会退化为阻塞式
    ...
)
```

如果前端出现"文本一次性返回而非逐字流式显示"的问题，请检查：
1. SDK 版本是否支持 `accumulate_streaming_content` 参数
2. 该参数是否设置为 `True`

### 功能

- **产品分析**：查询数据库中的产品数据，分析单个产品或批量对比
- **赛道分析**：分析市场类目，识别蓝海市场和机会
- **趋势报告**：生成行业趋势报告，洞察市场动态
- **多轮对话**：支持上下文连续对话，通过 `session_id` 恢复会话
- **子代理委托**：支持将复杂任务委托给专业子代理（对比分析师、机会发现者等）
