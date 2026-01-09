# MCP 工具使用指南

## 概述

本文档介绍了优化后的 MCP (Model Context Protocol) 工具集，用于查询和分析 SaaS 产品数据。

## 主要改进

### 1. 增强的查询能力

#### 模糊匹配
- `search`: 在产品名称和描述中进行模糊搜索（OR 逻辑）
- `name_contains`: 仅在产品名称中模糊匹配
- `description_contains`: 仅在描述中模糊匹配
- `founder_name_contains`: 按创始人名称模糊搜索

#### 组合查询
- `categories`: 支持多分类 OR 查询，例如 `["AI", "Developer Tools", "SaaS"]`
- 支持同时使用多个过滤条件进行精确定位

### 2. 丰富的过滤维度

#### 收入维度
- `min_revenue` / `max_revenue`: 收入范围过滤
- `revenue_tier`: 快速过滤 - micro(<$500) / small($500-2K) / medium($2K-10K) / large(>$10K)

#### 增长维度
- `min_growth_rate` / `max_growth_rate`: 增长率范围

#### 创始人维度
- `founder_name_contains`: 创始人名称模糊匹配
- `min_followers` / `max_followers`: 粉丝数范围

#### 技术特征
- `tech_complexity`: 技术复杂度 (low/medium/high)
- `ai_dependency`: AI 依赖程度 (none/light/heavy)
- `has_realtime_feature`: 是否有实时功能
- `is_data_intensive`: 是否数据密集型

#### 商业模式
- `target_customer`: 目标客户 (b2c/b2b_smb/b2b_enterprise/b2d)
- `pricing_model`: 定价模式 (subscription/one_time/usage/freemium)
- `market_scope`: 市场范围 (horizontal/vertical)

#### 可复制性
- `feature_complexity`: 功能复杂度 (simple/moderate/complex)
- `startup_cost_level`: 启动成本 (low/medium/high)
- `product_stage`: 产品阶段 (early/growth/mature)

#### 评分过滤
- `min_suitability`: 最低独立开发适合度 (0-10)
- `min_recommendation`: 最低综合推荐指数 (0-10)

#### 布尔标签
- `is_product_driven`: 产品驱动型
- `is_small_and_beautiful`: 小而美产品
- `is_for_sale`: 正在出售
- `is_verified`: 已验证

### 3. 灵活的排序和分页

#### 排序
- `sort_by`: revenue_30d / growth_rate / suitability / recommendation / followers
- `sort_order`: asc / desc

#### 分页
- `limit`: 每页最大结果数（默认 20，最大 100）
- `offset`: 跳过 N 个结果用于分页

### 4. 可选的数据包含

- `include_analysis`: 包含产品选品分析数据
- `include_landing_analysis`: 包含落地页分析数据
- `include_revenue_history`: 包含最近 30 天收入历史

## 工具列表

### 1. query_startups
**主要查询工具** - 使用综合过滤器、模糊匹配和组合查询来查找产品。

**使用场景：**
- 查找特定类型的产品
- 按技术特征筛选
- 按商业模式筛选
- 查找适合独立开发者的产品

**返回格式：**
```json
{
  "results": [...],
  "total": 100,
  "limit": 20,
  "offset": 0,
  "filters_applied": ["search='AI'", "min_revenue=1000"]
}
```

### 2. get_product_by_slug
**单品详情工具** - 通过 slug 获取产品的完整详细信息。

**使用场景：**
- 深入了解单个产品
- 获取完整的分析数据
- 查看收入历史（最近 90 天）

**参数：**
- `slug`: 产品 slug（URL 标识符）
- `include_all_analysis`: 是否包含所有分析数据（默认 true）

### 3. get_revenue_trends
**收入趋势分析工具** - 分析产品的收入趋势。

**使用场景：**
- 了解产品增长模式
- 评估收入稳定性
- 识别增长或下降趋势

**参数：**
- `slug` 或 `startup_id`: 产品标识
- `days`: 分析天数（默认 30）

**返回数据：**
- 统计数据（平均/最小/最大收入）
- 趋势方向（growing/declining/stable）
- 每日变化率
- 历史数据点

### 4. compare_products
**产品对比工具** - 并排比较多个产品。

**使用场景：**
- 评估相似产品
- 做出选择决策
- 分析竞争对手

**参数：**
- `slugs`: 产品 slug 列表（2-10 个）
- `comparison_fields`: 要比较的特定字段（可选）

### 5. get_category_analysis
**分类分析工具** - 获取分类的统计分析。

**使用场景：**
- 了解市场分类
- 识别热门领域
- 分析分类趋势

### 6. get_trend_report
**趋势报告工具** - 生成 SaaS 市场的综合趋势报告。

**返回数据：**
- 市场总体统计
- 按收入排名的热门分类
- 增长最快的产品
- 最佳投资机会
- 最高收入产品

### 7. find_excellent_developers
**优秀开发者查找工具** - 基于产品组合和成功指标查找优秀的独立开发者。

**使用场景：**
- 发现成功的独立开发者
- 学习产品策略
- 寻找潜在合作者/导师

**参数：**
- `min_products`: 最少产品数（默认 2）
- `min_total_revenue`: 最低总收入
- `min_avg_revenue`: 最低平均收入
- `min_followers`: 最低粉丝数
- `sort_by`: 排序依据（total_revenue/avg_revenue/product_count/followers）

### 8. get_leaderboard
**排行榜工具** - 获取创始人排行榜。

**参数：**
- `limit`: 返回的创始人数量（默认 20，最大 100）

### 9. web_search
**网络搜索工具** - 搜索关于 SaaS 产品、市场趋势等的网络信息。

**使用场景：**
- 搜索产品信息
- 查找市场趋势
- 获取社区讨论

**参数：**
- `query`: 搜索查询
- `limit`: 最大结果数（默认 10）
- `site`: 限制搜索的网站（可选，如 "reddit.com"）

## 使用示例

### 示例 1: 查找适合独立开发者的 AI 产品

```python
query_startups(
    categories=["AI", "Developer Tools"],
    tech_complexity="low",
    ai_dependency="light",
    feature_complexity="simple",
    startup_cost_level="low",
    min_suitability=7.0,
    is_product_driven=True,
    sort_by="suitability",
    limit=10
)
```

### 示例 2: 查找高增长的 B2B SaaS

```python
query_startups(
    categories=["SaaS", "Productivity"],
    target_customer="b2b_smb",
    min_growth_rate=20.0,
    min_revenue=1000,
    pricing_model="subscription",
    sort_by="growth_rate",
    limit=20
)
```

### 示例 3: 模糊搜索包含 "analytics" 的产品

```python
query_startups(
    search="analytics",
    min_revenue=500,
    include_analysis=True,
    limit=15
)
```

### 示例 4: 比较三个产品

```python
compare_products(
    slugs=["product-a", "product-b", "product-c"]
)
```

### 示例 5: 分析产品收入趋势

```python
get_revenue_trends(
    slug="my-product",
    days=60
)
```

## 数据库 Schema 更新

### ProductSelectionAnalysis 表新增字段

- `revenue_tier`: 收入层级
- `revenue_follower_ratio_level`: 收入粉丝比层级
- `growth_driver`: 增长驱动因素
- `ai_dependency_level`: AI 依赖程度
- `has_realtime_feature`: 是否有实时功能
- `is_data_intensive`: 是否数据密集型
- `has_compliance_requirement`: 是否有合规要求
- `pricing_model`: 定价模式
- `target_customer`: 目标客户
- `market_scope`: 市场范围
- `feature_complexity`: 功能复杂度
- `moat_type`: 护城河类型
- `startup_cost_level`: 启动成本层级
- `product_stage`: 产品阶段

## 性能优化建议

1. **使用精确过滤优先**: 先使用精确匹配（如 category, revenue_tier）再使用模糊搜索
2. **合理设置 limit**: 避免一次查询过多数据
3. **使用分页**: 对于大结果集使用 offset 和 limit 进行分页
4. **按需包含分析数据**: 如果不需要详细分析，设置 `include_analysis=False`
5. **使用索引字段排序**: 优先使用 revenue_30d, growth_rate 等有索引的字段排序

## 错误处理

所有工具都包含错误处理，返回格式：

```json
{
  "error": "错误描述",
  "type": "错误类型",
  "is_error": true
}
```

## 注意事项

1. 所有文本搜索都是**不区分大小写**的
2. 模糊搜索使用 SQL `ILIKE` 操作符（支持 % 通配符）
3. 多值过滤（如 categories）使用 OR 逻辑
4. 同一维度的多个过滤条件使用 AND 逻辑
5. 收入金额单位为美元
6. 评分范围为 0-10
7. 查询结果最多返回 100 条（可通过 limit 参数控制）

## 更新日志

### v2.0 (2026-01-09)
- ✅ 添加模糊匹配支持（search, name_contains, description_contains, founder_name_contains）
- ✅ 添加多分类查询支持（categories）
- ✅ 扩展过滤维度（技术、商业、可复制性）
- ✅ 添加灵活的排序和分页
- ✅ 添加新工具：get_product_by_slug, get_revenue_trends, compare_products
- ✅ 优化返回数据结构（包含 total, filters_applied）
- ✅ 更新数据库 schema 以支持新的分析维度
