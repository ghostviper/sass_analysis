# 向量检索方案设计

## 背景

当前 agent 工具的检索能力依赖 SQL 模糊匹配（LIKE），存在以下局限：
- 无法处理语义相似（"AI 写作助手" vs "内容生成工具"）
- 无法概念扩展（用户问"效率工具"，应覆盖 productivity、automation 等）
- 无法跨字段关联语义

## 目标

通过向量化实现：
1. **模糊检索** - 用户输入不精确时也能找到相关产品
2. **语义检索** - 理解用户意图，而非字面匹配
3. **数据增广** - 问某个方向/类目时，覆盖更多相关信息

## 技术选型

| 组件 | 选择 | 理由 |
|------|------|------|
| 向量数据库 | Pinecone (Serverless) | 免费层够用、SDK 简单、免运维 |
| Embedding 模型 | 可配置（默认 text-embedding-3-small） | 支持 OpenAI 兼容的第三方服务 |

### Pinecone 结构

```
Index: buildwhat (唯一索引)
├── Namespace: products     # 产品语义画像
└── Namespace: categories   # 赛道描述
```

## 向量化数据

### 1. 产品语义画像 (namespace: products)

**数据来源**：`startups` + `landing_page_analysis` + `product_selection_analysis` + `comprehensive_analysis`

**向量化文本**：
- 产品名称、描述、类目
- 定位（headline）
- 目标用户、使用场景
- 核心功能、解决痛点、价值主张
- 技术复杂度、目标客户、定价模式
- 综合分析摘要

**Metadata**（用于过滤）：
- startup_id, name, slug, category
- revenue_30d, tech_complexity, target_customer
- ai_dependency, suitability_score, pricing_model
- recommendation_score

### 2. 赛道描述 (namespace: categories)

**数据来源**：`category_analysis`

**向量化文本**：
- 赛道名称
- 市场类型、市场特征
- 产品数量、总收入、中位数收入
- 收入分布描述（基于基尼系数）
- 头部集中度

**Metadata**：
- category, category_id, market_type
- total_projects, total_revenue, median_revenue
- gini_coefficient

## Agent 工具

### 语义搜索工具

| 工具 | 说明 | 使用场景 |
|------|------|---------|
| `semantic_search_products` | 自然语言搜索产品 | "帮我找类似 Notion 的产品" |
| `find_similar_products` | 基于产品 ID 找相似产品 | 竞品分析、相似推荐 |
| `semantic_search_categories` | 自然语言搜索赛道 | "哪些赛道适合个人开发者" |
| `discover_products_by_scenario` | 场景化产品发现 | "我想做一个帮助设计师管理素材的工具" |

### 增强的工具

| 工具 | 增强内容 |
|------|---------|
| `browse_startups` | 新增 `semantic_query` 参数，支持语义过滤 |

### 工具模块结构

```
backend/agent/tools/
├── __init__.py      # 导出所有工具
├── decorator.py     # tool 装饰器
├── base.py          # 基础工具（产品查询、赛道分析）
├── founder.py       # 创始人相关工具
├── search.py        # Web 搜索工具
└── semantic.py      # 语义搜索工具
```

## 配置

`.env` 配置项：

```bash
# Pinecone
PINECONE_API_KEY=xxx
PINECONE_INDEX=buildwhat

# Embedding（支持第三方 OpenAI 兼容服务）
EMBEDDING_API_KEY=xxx          # 不设置则用 OPENAI_API_KEY
EMBEDDING_BASE_URL=xxx         # 不设置则用 OPENAI_BASE_URL
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSION=1536       # 需与 Pinecone 索引维度一致
```

## 数据同步

### 同步脚本

```bash
# 同步所有数据
python scripts/sync_vectors.py --all

# 只同步产品
python scripts/sync_vectors.py --products

# 只同步赛道
python scripts/sync_vectors.py --categories

# 全量同步（清空后重建）
python scripts/sync_vectors.py --full

# 查看统计
python scripts/sync_vectors.py --stats
```

### 同步策略

1. **初始化**：`--full --all` 全量同步
2. **增量更新**：产品/赛道数据更新后运行对应同步
3. **定期同步**：可选，每日定时任务

## 实现文件

```
backend/
├── services/
│   └── vector_store.py      # Pinecone 封装
├── scripts/
│   └── sync_vectors.py      # 数据同步脚本
└── agent/
    └── tools/
        └── semantic.py      # 语义搜索工具
```

## 预估数据量

| Namespace | 数量 | 说明 |
|-----------|------|------|
| products | ~1000 | 所有产品 |
| categories | ~50 | 所有赛道 |

Pinecone 免费层 100 万向量，完全够用。
