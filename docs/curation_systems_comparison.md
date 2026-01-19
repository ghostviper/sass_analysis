# 策展系统对比：每日AI策展 vs 主题合集

## 概览

| 维度 | 每日AI策展 (DailyCuration) | 主题合集 (DiscoverTopic) |
|------|---------------------------|-------------------------|
| **数据表** | `daily_curations` + `curation_products` | `discover_topics` + `topic_products` |
| **生成器** | `DailyCurationGenerator` | `CuratorAgent` |
| **模板定义** | `daily_templates.py` | `curator.py` (CuratorRole) |
| **更新频率** | 每日更新 | 长期稳定 |
| **产品数量** | 3-8个 | 3-15个 |
| **展示位置** | Discover 页面顶部 "今日策展" | Discover 页面 "主题合集" 区块 |

---

## 核心差异

### 1. 定位与目标

**每日AI策展 (DailyCuration)**
- **定位**：时效性内容，每日更新的"今日推荐"
- **目标**：提供新鲜感、引导用户每天回访
- **特点**：反差感强、有洞察、易传播
- **类比**：类似 Product Hunt 的 "Today's Top Products"

**主题合集 (DiscoverTopic)**
- **定位**：长期稳定的分类导航
- **目标**：帮助用户按需求/角色找到合适的产品方向
- **特点**：分类清晰、覆盖全面、持续有效
- **类比**：类似 Indie Hackers 的 "Product Categories"

---

### 2. 策展逻辑

**每日AI策展**
```python
# 基于模板的固定筛选规则
filter_rules = {
    "startup": {
        "founder_followers": {"max": 1000},
        "revenue_30d": {"min": 10000}
    },
    "mother_theme": {
        "success_driver": ["产品驱动"]
    }
}
```
- **筛选维度**：Startup 基础数据 + 母题判断 + 选品分析 + 落地页分析
- **模板类型**：反差型、认知型、行动型、利基型
- **文案风格**：有冲突感、反常识、引发思考

**主题合集**
```python
# 基于角色的筛选规则
filter_rules = {
    "solo_feasibility": ["非常适合"],
    "opportunity_validity": ["真实机会"],
    "entry_barrier": ["低门槛快启动"],
}
```
- **筛选维度**：仅基于母题判断结果
- **角色类型**：谨慎的独立开发者、快速启动者、机会嗅觉型等
- **文案风格**：实用导向、明确目标人群

---

### 3. 模板设计哲学

**每日AI策展模板示例**
```python
CurationTemplate(
    key="low_followers_high_revenue",
    title_zh="粉丝不到1000，月入过万",
    title_en="<1K Followers, $10K+ MRR",
    insight_zh="产品力 > 个人IP，专注解决问题比积累粉丝更重要",
    curation_type="contrast",  # 反差型
    conflict_dimensions=["founder_followers", "revenue_30d", "success_driver"]
)
```
- **强调冲突**：低粉丝 vs 高收入
- **提供洞察**：打破"需要粉丝才能赚钱"的认知
- **引发讨论**：反常识的案例更容易传播

**主题合集模板示例**
```python
CuratorRole(
    name="cautious_indie_dev",
    display_name_zh="谨慎的独立开发者",
    filter_rules={
        "solo_feasibility": ["非常适合"],
        "opportunity_validity": ["真实机会"],
        "entry_barrier": ["低门槛快启动"],
    },
    topic_templates=[
        TopicTemplate(
            title_zh="最适合独立开发者的产品方向",
            pattern="action",
            description_zh="这些产品一个人就能做、门槛低、风险可控",
        )
    ]
)
```
- **明确角色**：为特定人群筛选
- **实用导向**：帮助用户找到适合自己的方向
- **长期有效**：规则稳定，不需要频繁更新

---

### 4. 数据结构对比

**DailyCuration 表**
```python
class DailyCuration(Base):
    curation_key = Column(String(100))  # 包含日期：low_followers_high_revenue_2026-01-16
    title_zh / title_en
    description_zh / description_en
    insight_zh / insight_en  # ⭐ 独有：洞察文案
    tag_zh / tag_en  # ⭐ 独有：标签（如"反常识"）
    tag_color  # ⭐ 独有：标签颜色
    curation_type  # ⭐ 独有：contrast/cognitive/action/niche
    curation_date  # ⭐ 独有：策展日期
    conflict_dimensions  # ⭐ 独有：冲突维度说明
```

**DiscoverTopic 表**
```python
class DiscoverTopic(Base):
    topic_key = Column(String(100))  # 不含日期：cautious_indie_dev_action_0
    title_zh / title_en
    description_zh / description_en
    curator_role  # ⭐ 独有：策展角色
    generation_pattern  # contrast/niche/cognitive/action
    filter_rules  # 筛选规则
    cta_text_zh / cta_text_en  # CTA 文案
    display_order  # ⭐ 独有：展示顺序
    is_active  # ⭐ 独有：是否激活
```

---

### 5. 产品关联表对比

**CurationProduct (每日策展)**
```python
class CurationProduct(Base):
    curation_id
    startup_id
    highlight_zh  # "粉丝620，月入$40,052"
    highlight_en
    display_order
```
- **亮点文案**：根据冲突维度动态生成
- **示例**：低粉丝高收入 → "粉丝620，月入$40,052"

**TopicProduct (主题合集)**
```python
class TopicProduct(Base):
    topic_id
    startup_id
    ai_label  # AI 生成的标签
    counter_intuitive_point  # 反直觉点
    display_order
```
- **AI 标签**：产品的特征标签
- **反直觉点**：产品的独特之处

---

## 使用场景

### 每日AI策展适合：

1. **引导每日回访**
   - "今天又有什么新发现？"
   - 提供新鲜感和探索乐趣

2. **社交媒体传播**
   - 反差感强的内容更容易被分享
   - "粉丝不到1000，月入过万" → 引发讨论

3. **打破认知偏见**
   - "功能只有3个，月入$5K+" → 挑战"功能越多越好"
   - "最无聊的需求，最稳定的收入" → 重新定义"无聊"

4. **提供行动洞察**
   - "周末就能上线的产品" → 降低行动门槛
   - "不用AI也能月入过万" → 缓解AI焦虑

### 主题合集适合：

1. **按需求导航**
   - 用户明确知道自己想找什么
   - "我想找低风险的方向" → 进入对应主题

2. **按角色筛选**
   - "我是独立开发者" → 查看适合独立开发者的产品
   - "我有内容能力" → 查看内容驱动的产品

3. **系统性学习**
   - 一次性查看某个类别的所有案例
   - 对比同类产品的差异

4. **长期参考**
   - 规则稳定，可以收藏后反复查看
   - 不会因为日期过期而失效

---

## 生成流程对比

### 每日AI策展生成流程

```python
# 1. 定义模板（手动）
template = CurationTemplate(
    key="low_followers_high_revenue",
    filter_rules={...},
    conflict_dimensions=[...]
)

# 2. 自动筛选产品
generator = DailyCurationGenerator(db)
products = generator._filter_products(template.filter_rules)

# 3. 生成亮点文案
for product in products:
    highlight = generator._generate_highlight(product, template.filter_rules)

# 4. 写入数据库
curation = DailyCuration(...)
db.add(curation)
```

**特点**：
- 模板固定，每日执行
- 亮点文案根据冲突维度动态生成
- 包含日期，有时效性

### 主题合集生成流程

```python
# 1. 定义角色（手动）
role = CuratorRole(
    name="cautious_indie_dev",
    filter_rules={...},
    topic_templates=[...]
)

# 2. 筛选产品
filtered = filter_products_by_rules(products, role.filter_rules)

# 3. 生成专题
topic = {
    "topic_key": f"{role_name}_{pattern}_{index}",
    "title_zh": template.title_zh,
    "products": filtered[:max_products]
}

# 4. 写入数据库（可选）
discover_topic = DiscoverTopic(...)
db.add(discover_topic)
```

**特点**：
- 角色固定，按需生成
- 不包含日期，长期有效
- 可以手动调整展示顺序

---

## 数据量对比

### 每日AI策展
- **模板数量**：12个（当前）
- **每日生成**：8-12条（取决于数据匹配情况）
- **数据增长**：每天新增 8-12 条记录
- **历史数据**：保留所有历史策展，可以查看"过去的今天"

### 主题合集
- **角色数量**：10个（当前）
- **专题数量**：10-20个（一次性生成）
- **数据增长**：仅在角色/规则变化时重新生成
- **历史数据**：覆盖更新，不保留历史版本

---

## 技术实现差异

### 筛选能力

**每日AI策展**
```python
# 支持更复杂的筛选条件
filter_rules = {
    "startup": {
        "revenue_30d": {"min": 10000, "max": 50000},
        "founder_followers": {"max": 1000},
        "category": {"contains": ["developer", "api"]}
    },
    "mother_theme": {
        "success_driver": ["产品驱动"],
        "primary_risk": {"not": ["变现转化"]}  # 支持 NOT 条件
    },
    "selection": {
        "ai_dependency_level": ["none", "light"],
        "target_customer": ["b2b_smb"]
    },
    "landing_page": {
        "feature_count": {"max": 5}
    }
}
```
- 支持 4 个数据源：Startup / MotherTheme / Selection / LandingPage
- 支持范围筛选、NOT 条件、模糊匹配

**主题合集**
```python
# 仅支持母题判断筛选
filter_rules = {
    "solo_feasibility": ["非常适合"],
    "opportunity_validity": ["真实机会"],
    "entry_barrier": ["低门槛快启动"],
    "primary_risk": {"exclude": ["技术实现"]}
}
```
- 仅支持 1 个数据源：MotherTheme
- 支持 IN 和 EXCLUDE 条件

---

## 未来扩展方向

### 每日AI策展

1. **个性化推荐**
   - 根据用户偏好调整每日策展内容
   - 用户可以"喜欢/不喜欢"某个策展

2. **趋势分析**
   - "本周最受欢迎的策展"
   - "这个月的热门主题"

3. **社交功能**
   - 用户可以评论/讨论策展
   - 分享到社交媒体

4. **AI 生成文案**
   - 自动生成 insight 文案
   - 根据产品特征生成更精准的 highlight

### 主题合集

1. **动态角色**
   - 用户可以自定义筛选规则
   - "我想找：低门槛 + 高收入 + B2B"

2. **角色推荐**
   - 根据用户画像推荐合适的角色
   - "你可能感兴趣的主题"

3. **对比功能**
   - 同时查看多个主题的产品
   - 对比不同角色的筛选结果

4. **订阅功能**
   - 订阅某个主题，有新产品时通知
   - "你订阅的'独立开发者'主题有 3 个新产品"

---

## 总结

| 特性 | 每日AI策展 | 主题合集 |
|------|-----------|---------|
| **核心价值** | 新鲜感、洞察、传播 | 导航、分类、实用 |
| **更新频率** | 每日 | 按需 |
| **内容风格** | 反差、冲突、反常识 | 实用、明确、稳定 |
| **用户场景** | 探索、发现、灵感 | 搜索、筛选、学习 |
| **数据时效** | 有时效性 | 长期有效 |
| **筛选能力** | 强（4个数据源） | 中（1个数据源） |
| **传播性** | 高 | 中 |
| **实用性** | 中 | 高 |

**两者互补，不是替代关系**：
- 每日AI策展：吸引用户、提供新鲜感、引发讨论
- 主题合集：帮助用户、提供价值、长期参考

理想的产品应该同时包含两者，满足不同场景的需求。
