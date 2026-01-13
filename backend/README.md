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

---

## AI 助手配置

```bash
ANTHROPIC_API_KEY=your_api_key
```

需要 `claude-agent-sdk` 支持 `accumulate_streaming_content` 参数（2025年1月后版本）。
