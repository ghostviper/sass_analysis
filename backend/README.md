# SaaS 产品分析工具

从 TrustMRR 抓取 SaaS 产品数据，通过 AI 分析找到适合独立开发者复制的产品机会。

## 环境准备

```bash
# 1. 创建虚拟环境
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# 2. 安装依赖
pip install -r requirements.txt
playwright install chromium

# 3. 配置环境变量
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

## 使用流程

### 第一步：抓取数据（首次使用）

```bash
python main.py scrape          # 抓取TrustMRR网站数据
python main.py update          # 解析HTML更新数据库
python main.py sync            # 同步创始人信息
```

### 第二步：运行分析

```bash
# 1. 赛道分析 - 找蓝海市场
python main.py analyze category

# 2. 选品分析 - 找机会产品并保存
python main.py analyze product --opportunities --limit 300 --save

# 3. Landing Page分析 - AI分析产品官网
python main.py analyze landing --update    # 增量更新（推荐，只分析新增产品）
python main.py analyze landing --all       # 全量分析所有产品

# 4. 综合分析 - 生成推荐列表
python main.py analyze comprehensive --top --limit 50
```

### 第三步：查看结果

```bash
# 启动API服务
uvicorn api.main:app --port 8001 --reload

# 打开浏览器访问
# http://localhost:8001/docs
```

---

## 常用命令速查

### 赛道分析
```bash
python main.py analyze category                    # 分析所有赛道
python main.py analyze category --name "AI"        # 分析指定赛道
```

### 选品分析
```bash
# 筛选机会产品
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

### Landing Page 分析
```bash
# 增量更新模式（推荐）- 只分析新增/未分析的产品
python main.py analyze landing --update

# 全量分析所有产品
python main.py analyze landing --all

# 全量分析但跳过已分析的（等同于 --update）
python main.py analyze landing --all --skip-analyzed

# 只分析前N个高收入产品
python main.py analyze landing --batch --limit 50 --skip-analyzed

# 分析单个产品
python main.py analyze landing --slug product-name

# 强制重新分析（重新爬取官网）
python main.py analyze landing --slug product-name --force
```

### 综合分析
```bash
# 获取TOP推荐列表
python main.py analyze comprehensive --top --limit 30

# 分析单个产品并导出
python main.py analyze comprehensive --slug product-name --export report.json
```

---

## 数据库维护

```bash
# 重建分析表（保留原始数据）
python rebuild_analysis_tables.py

# 检查数据质量
python data_audit.py

# 测试OpenAI连接
python test_openai.py
```

---

## 分析维度说明

### 赛道分析 - 市场类型

| 类型 | 含义 | 建议 |
|-----|------|-----|
| `blue_ocean` | 竞争少，多数产品盈利 | ⭐ 优先考虑 |
| `emerging` | 新兴市场，早期机会 | ⭐ 值得关注 |
| `moderate` | 中等竞争 | 需要差异化 |
| `concentrated` | 头部集中 | 新手慎入 |
| `red_ocean` | 竞争激烈 | 避开 |
| `weak_demand` | 需求不足 | 避开 |

### 选品分析 - 三个组合

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

## API 接口

启动服务后访问 `http://localhost:8001/docs` 查看完整文档。

主要接口：
- `GET /api/startups` - 产品列表
- `GET /api/analysis/category/` - 赛道分析
- `GET /api/analysis/product/opportunities` - 机会产品
- `GET /api/analysis/landing/{slug}` - Landing Page分析
- `POST /api/analysis/landing/scrape/{slug}` - 触发分析

---

## 项目结构

```
backend/
├── main.py              # CLI入口
├── analysis/            # 分析模块
│   ├── category_analyzer.py   # 赛道分析
│   ├── product_selector.py    # 选品分析
│   ├── landing_analyzer.py    # Landing Page分析
│   └── comprehensive.py       # 综合分析
├── crawler/             # 爬虫模块
├── database/            # 数据库
├── api/                 # REST API
└── data/                # 数据文件
    └── sass_analysis.db     # SQLite数据库
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

**Q: 分析中断了怎么办？**
```bash
# Landing Page分析支持断点续传，使用增量更新模式继续
python main.py analyze landing --update
```

**Q: 如何重新分析？**
```bash
# 重建分析表
python rebuild_analysis_tables.py

# 或强制重新分析单个产品
python main.py analyze landing --slug xxx --force
```

## TODO
agent定位是面向分析的助手，目标是通过和AI对话洞察分析：指定的产品（库里面的产品、用户提出的产品（通过链   
  接）总结性报告、哪些地方做的好（技术、市场、产品本身、定位等等））、行业趋势分析（报告、探索性分析、通过结合收录的数   
  据和外部检索途径分析）、个人职业向探索（我适合做什么、我该做什么？有哪些机会，主要帮助个人开发寻找和探索适合自己的产   
  品方向和思路）
