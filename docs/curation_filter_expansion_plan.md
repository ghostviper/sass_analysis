# 策展系统筛选优化与扩展计划

## 一、当前状态

### 1.1 数据基础
- 已判断产品：153 个
- 母题数量：9 个（筛选层 2 + 行动层 4 + 归因层 3）
- 每个判断包含：judgment（判断值）、confidence（置信度）、reasons（理由）

### 1.2 当前专题生成结果
| 专题 | 产品数 | 问题 |
|------|--------|------|
| 失败成本最低的 SaaS 方向 | 121 | 太多 |
| 一个人也能维护的产品 | 121 | 太多 |
| 周末就能启动的项目 | 48 | 偏多 |
| 需求明确、门槛不高的机会 | 40 | 偏多 |
| 看起来性感但风险很高的产品 | 14 | 合理 |
| 不靠粉丝也能成功的产品 | 114 | 太多 |

### 1.3 问题分析
1. 筛选条件太宽松，大部分产品都能入选
2. 没有利用 confidence 字段
3. 没有按收入/热度排序
4. 角色和专题模式较少

---

## 二、筛选逻辑优化

### 2.1 Phase 1：收紧现有规则

#### 2.1.1 增加置信度要求
```python
# 当前
filter_rules = {
    "solo_feasibility": ["非常适合", "有挑战但可行"],
}

# 优化后：支持 confidence 筛选
filter_rules = {
    "solo_feasibility": {
        "values": ["非常适合"],
        "confidence": ["high", "medium"],  # 只要高/中置信度
    },
}
```

#### 2.1.2 增加组合条件数量
```python
# 当前：2-3 个条件
# 优化后：4-5 个条件同时满足

"cautious_indie_dev": {
    "solo_feasibility": {"values": ["非常适合"], "confidence": ["high"]},
    "opportunity_validity": {"values": ["真实机会"]},
    "entry_barrier": {"values": ["低门槛快启动", "中等投入"]},
    "primary_risk": {"exclude": ["技术实现"]},
    "mvp_clarity": {"values": ["清晰可执行", "基本清晰"]},
}
```

#### 2.1.3 实现优先级排序
```python
def filter_products_by_rules(...):
    # 筛选后按收入排序
    filtered = sorted(
        filtered, 
        key=lambda x: x.get("revenue_30d") or 0, 
        reverse=True
    )
    return filtered
```

### 2.2 Phase 2：扩展筛选规则语法

支持更丰富的规则表达：

```python
filter_rules = {
    # 基础：值匹配
    "theme_key": ["value1", "value2"],
    
    # 排除规则
    "theme_key": {"exclude": ["bad_value"]},
    
    # 置信度要求
    "theme_key": {"values": ["value"], "confidence": ["high"]},
    
    # 数值比较（未来）
    "revenue_30d": {"min": 1000, "max": 10000},
    
    # OR 逻辑（未来）
    "_or": [
        {"solo_feasibility": ["非常适合"]},
        {"entry_barrier": ["低门槛快启动"]},
    ],
}
```

---

## 三、策展角色扩展

### 3.1 现有角色（5个）
| 角色 | 视角 | 专题数 |
|------|------|--------|
| cautious_indie_dev | 谨慎的独立开发者 | 2 |
| quick_starter | 快速启动者 | 1 |
| opportunity_hunter | 机会嗅觉型创业者 | 1 |
| anti_bubble | 反泡沫角色 | 1 |
| product_driven_fan | 产品驱动爱好者 | 1 |

### 3.2 新增角色计划

#### 3.2.1 风险敏感投资者 (risk_aware_investor)
```python
CuratorRole(
    name="risk_aware_investor",
    display_name="风险敏感投资者",
    filter_rules={
        "opportunity_validity": {"values": ["真实机会"], "confidence": ["high"]},
        "primary_risk": {"exclude": ["市场验证", "用户获取"]},
        "success_driver": ["产品驱动"],
    },
    topic_templates=[
        TopicTemplate(
            title="风险最可控的 SaaS 投资标的",
            pattern="action",
            description_template="这些产品市场验证充分、获客路径清晰，风险主要在执行层面。",
        ),
    ],
)
```

#### 3.2.2 细分市场猎手 (niche_hunter)
```python
CuratorRole(
    name="niche_hunter",
    display_name="细分市场猎手",
    filter_rules={
        "positioning_insight": ["精准垂直", "场景具体"],
        "differentiation_point": ["人群差异化"],
        "opportunity_validity": ["真实机会"],
    },
    topic_templates=[
        TopicTemplate(
            title="小众但精准的细分市场机会",
            pattern="niche",
            description_template="这些产品瞄准特定人群，竞争小但需求真实。",
        ),
    ],
)
```

#### 3.2.3 模仿友好型 (copycat_friendly)
```python
CuratorRole(
    name="copycat_friendly",
    display_name="可模仿学习者",
    filter_rules={
        "entry_barrier": ["低门槛快启动"],
        "mvp_clarity": ["清晰可执行"],
        "differentiation_point": {"exclude": ["技术差异化"]},
        "solo_feasibility": ["非常适合", "有挑战但可行"],
    },
    topic_templates=[
        TopicTemplate(
            title="最适合模仿学习的产品",
            pattern="action",
            description_template="这些产品模式清晰、技术门槛低，适合作为第一个 SaaS 项目练手。",
        ),
    ],
)
```

#### 3.2.4 逆向思维者 (contrarian)
```python
CuratorRole(
    name="contrarian",
    display_name="逆向思维者",
    filter_rules={
        "demand_type": ["需教育型"],  # 大家觉得难的
        "opportunity_validity": ["真实机会"],  # 但其实是真机会
        "solo_feasibility": ["非常适合", "有挑战但可行"],
    },
    topic_templates=[
        TopicTemplate(
            title="被低估的冷门机会",
            pattern="cognitive",
            description_template="这些方向看起来需要教育市场，但实际上有真实需求。",
        ),
    ],
)
```

#### 3.2.5 高收入追求者 (revenue_chaser)
```python
CuratorRole(
    name="revenue_chaser",
    display_name="高收入追求者",
    filter_rules={
        "opportunity_validity": ["真实机会"],
        "success_driver": ["产品驱动"],
        # 额外条件：revenue_30d > 5000（需要扩展筛选逻辑）
    },
    topic_templates=[
        TopicTemplate(
            title="月入 $5K+ 的独立产品",
            pattern="action",
            description_template="这些产品已经验证了商业模式，收入稳定。",
        ),
    ],
)
```

---

## 四、专题模式扩展

### 4.1 现有模式（4种）
| 模式 | 说明 | 示例 |
|------|------|------|
| action | 行动导向 | "失败成本最低的 SaaS 方向" |
| niche | 细分聚焦 | "一个人也能维护的产品" |
| cognitive | 认知纠偏 | "看起来性感但风险很高的产品" |
| contrast | 反差对比 | "不靠粉丝也能成功的产品" |

### 4.2 新增模式计划

#### 4.2.1 trending（趋势型）
```python
TopicTemplate(
    title="本周新增的低门槛机会",
    pattern="trending",
    description_template="最近一周新判断的产品中，最适合独立开发者的方向。",
)
```

#### 4.2.2 revenue_tier（收入分层）
```python
TopicTemplate(
    title="$1K-5K MRR 的独立开发者产品",
    pattern="revenue_tier",
    description_template="这个收入区间的产品，验证了市场但还有增长空间。",
)
```

#### 4.2.3 category_focus（类别聚焦）
```python
TopicTemplate(
    title="AI 工具中最适合独立开发的",
    pattern="category_focus",
    description_template="AI 赛道虽然卷，但这些细分方向门槛不高。",
)
```

#### 4.2.4 comparison（对比型）
```python
TopicTemplate(
    title="同样是写作工具，为什么有的成功有的失败？",
    pattern="comparison",
    description_template="对比分析成功和失败案例，找出关键差异。",
)
```

---

## 五、实现计划

### Phase 1：筛选优化（1-2天）
- [ ] 扩展 filter_rules 语法，支持 confidence 筛选
- [ ] 收紧现有角色的筛选条件
- [ ] 添加按收入排序逻辑
- [ ] 测试验证专题产品数降到合理范围（5-20）

### Phase 2：角色扩展（1-2天）
- [ ] 新增 5 个策展角色
- [ ] 每个角色配置 1-2 个专题模板
- [ ] 测试生成效果

### Phase 3：模式扩展（2-3天）
- [ ] 实现 revenue_tier 模式（需要收入区间筛选）
- [ ] 实现 category_focus 模式（需要类别筛选）
- [ ] 实现 trending 模式（需要时间筛选）
- [ ] 实现 comparison 模式（需要对比逻辑）

### Phase 4：动态专题（未来）
- [ ] 自动发现高频判断组合
- [ ] 基于用户行为反馈调整权重
- [ ] LLM 动态生成专题标题和描述

---

## 六、预期效果

### 优化前
- 6 个专题
- 平均每个专题 76 个产品
- 区分度低

### 优化后（预期）
- 15-20 个专题
- 平均每个专题 8-15 个产品
- 角色视角多样
- 专题之间差异明显

---

## 七、代码改动清单

### 7.1 curator.py
1. 扩展 `filter_products_by_rules()` 支持 confidence 筛选
2. 添加排序逻辑
3. 新增 5 个 CuratorRole 配置
4. 新增专题模板

### 7.2 cli.py
1. curate 命令支持 `--sort-by` 参数
2. 支持 `--category` 过滤

### 7.3 新增文件（可选）
- `curation/roles/` 目录，按角色拆分配置文件
- `curation/patterns/` 目录，按模式拆分生成逻辑
