# MCP 工具优化总结

## 优化目标

根据数据库 schema 的更新（增加了新字段），优化 MCP 工具的封装，使查询工具在查询方面的维度更加丰富，支持模糊匹配、组合查询等功能，便于 AI 理解当前语境来进行更好的查询。

## 主要改进

### 1. 查询功能增强 (query_startups)

#### 新增模糊匹配能力
- **通用搜索** (`search`): 在产品名称和描述中同时搜索
- **精确字段搜索**:
  - `name_contains`: 仅在产品名称中搜索
  - `description_contains`: 仅在描述中搜索
  - `founder_name_contains`: 按创始人名称搜索
- 所有搜索都使用 SQL `ILIKE` 实现不区分大小写的模糊匹配

#### 新增组合查询能力
- **多分类查询** (`categories`): 支持传入分类列表，使用 OR 逻辑
  - 例如: `["AI", "Developer Tools", "SaaS"]`
- **范围过滤**:
  - 收入范围: `min_revenue`, `max_revenue`
  - 增长率范围: `min_growth_rate`, `max_growth_rate`
  - 粉丝数范围: `min_followers`, `max_followers`

#### 新增过滤维度

基于 `ProductSelectionAnalysis` 表的新字段：

**技术维度**:
- `tech_complexity`: low/medium/high
- `ai_dependency`: none/light/heavy
- `has_realtime_feature`: 布尔值
- `is_data_intensive`: 布尔值

**商业模式维度**:
- `target_customer`: b2c/b2b_smb/b2b_enterprise/b2d
- `pricing_model`: subscription/one_time/usage/freemium
- `market_scope`: horizontal/vertical

**可复制性维度**:
- `feature_complexity`: simple/moderate/complex
- `startup_cost_level`: low/medium/high
- `product_stage`: early/growth/mature

**快速过滤**:
- `revenue_tier`: micro/small/medium/large（替代手动设置 min/max）

**评分过滤**:
- `min_suitability`: 独立开发适合度 (0-10)
- `min_recommendation`: 综合推荐指数 (0-10)

**布尔标签**:
- `is_product_driven`: 产品驱动型
- `is_small_and_beautiful`: 小而美
- `is_for_sale`: 正在出售
- `is_verified`: 已验证

#### 灵活的排序和分页
- **排序字段** (`sort_by`): revenue_30d, growth_rate, suitability, recommendation, followers
- **排序方向** (`sort_order`): asc, desc
- **分页参数**: `limit` (最大100), `offset`

#### 增强的返回数据
```json
{
  "results": [...],           // 产品列表
  "total": 1234,              // 总匹配数
  "limit": 20,                // 当前限制
  "offset": 0,                // 当前偏移
  "filters_applied": [...]    // 应用的过滤器列表
}
```

#### 可选数据包含
- `include_analysis`: 包含选品分析数据
- `include_landing_analysis`: 包含落地页分析数据
- `include_revenue_history`: 包含最近30天收入历史

### 2. 新增工具函数

#### get_product_by_slug
- 通过 slug 获取单个产品的完整详细信息
- 包含所有分析数据和最近90天收入历史
- 适合深入了解特定产品

#### get_revenue_trends
- 分析产品的收入趋势
- 返回统计数据（平均/最小/最大）
- 计算趋势方向（growing/declining/stable）
- 提供每日变化率

#### compare_products
- 并排比较2-10个产品
- 自动提取关键指标进行对比
- 包含技术特征、商业模式、评分等

### 3. 优化现有工具

#### get_category_analysis
- 保持原有功能
- 返回分类统计和 Top 5 产品

#### get_trend_report
- 保持原有功能
- 提供市场总体趋势

#### find_excellent_developers
- 保持原有功能
- 查找优秀的独立开发者

#### get_leaderboard
- 保持原有功能
- 返回创始人排行榜

#### web_search
- 保持原有功能
- 网络搜索集成

## 技术实现细节

### 查询优化
1. **条件 JOIN**: 只在需要时才 JOIN 分析表
2. **索引利用**: 优先使用有索引的字段进行过滤和排序
3. **分页支持**: 使用 OFFSET/LIMIT 实现高效分页
4. **模糊搜索**: 使用 ILIKE 实现不区分大小写的模糊匹配

### 数据结构优化
1. **分离标签和评分**: 
   - `to_tags_dict()`: 返回纯标签数据
   - `to_scores_dict()`: 返回评分数据
2. **按需加载**: 通过参数控制是否包含额外数据
3. **错误处理**: 统一的错误返回格式

### AI 友好设计
1. **清晰的参数命名**: 使用语义化的参数名
2. **详细的文档**: 每个工具都有详细的使用说明
3. **灵活的组合**: 支持多种过滤条件的自由组合
4. **反馈机制**: 返回 `filters_applied` 让 AI 了解实际应用的过滤器

## 使用场景示例

### 场景 1: 查找适合独立开发者的简单 AI 产品
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

### 场景 2: 查找高增长的 B2B SaaS
```python
query_startups(
    target_customer="b2b_smb",
    pricing_model="subscription",
    min_growth_rate=20.0,
    min_revenue=1000,
    sort_by="growth_rate",
    limit=20
)
```

### 场景 3: 模糊搜索 "analytics" 相关产品
```python
query_startups(
    search="analytics",
    min_revenue=500,
    include_analysis=True,
    limit=15
)
```

### 场景 4: 比较三个竞品
```python
compare_products(
    slugs=["product-a", "product-b", "product-c"]
)
```

### 场景 5: 分析产品收入趋势
```python
get_revenue_trends(
    slug="my-product",
    days=60
)
```

## 性能考虑

1. **查询限制**: 单次查询最多返回 100 条结果
2. **索引优化**: 主要过滤字段都有索引
3. **条件 JOIN**: 避免不必要的表连接
4. **按需加载**: 通过参数控制数据加载量

## 测试

创建了 `test_tools.py` 测试脚本，包含 10 个测试用例：
1. 基础查询
2. 模糊搜索
3. 多分类查询
4. 复杂组合过滤
5. 收入范围过滤
6. 分类分析
7. 趋势报告
8. 优秀开发者查找
9. 分页功能
10. 排序功能

运行测试：
```bash
cd backend
python test_tools.py
```

## 文档

创建了详细的使用指南：
- `TOOLS_GUIDE.md`: 完整的工具使用文档
- `OPTIMIZATION_SUMMARY.md`: 本优化总结文档

## 兼容性

- ✅ 向后兼容：所有原有参数仍然支持
- ✅ 渐进增强：新参数都是可选的
- ✅ 数据库兼容：支持 PostgreSQL, MySQL, SQLite

## 下一步建议

1. **性能监控**: 添加查询性能日志
2. **缓存机制**: 对热门查询添加缓存
3. **全文搜索**: 考虑使用 PostgreSQL 的全文搜索功能
4. **聚合查询**: 添加更多统计和聚合功能
5. **导出功能**: 支持查询结果导出为 CSV/JSON

## 总结

本次优化大幅提升了 MCP 工具的查询能力：
- ✅ 支持模糊匹配和组合查询
- ✅ 新增 20+ 个过滤维度
- ✅ 灵活的排序和分页
- ✅ 新增 3 个实用工具函数
- ✅ AI 友好的设计和文档
- ✅ 完整的测试覆盖

这些改进使得 AI 能够更好地理解用户意图，执行更精确的查询，提供更有价值的分析结果。
