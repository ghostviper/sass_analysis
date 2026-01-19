# BuildWhat Curation System 架构设计文档

## 一、系统定位与核心目标

### 1.1 系统定位

Curation System（策展系统）是 BuildWhat 的**内容生成引擎**，负责将结构化的产品分析数据转化为有价值的发现内容。

> **核心定位**：AI 驱动的 SaaS 机会策展空间
> **服务对象**：寻找市场机会、开发机会、寻找 niche 的开发者/创业者
> **核心价值**：帮用户发现"我可以做什么"、"哪里有机会"

### 1.2 系统目标

**不是**：
- ❌ 数据展示平台
- ❌ 产品排行榜
- ❌ "我告诉你哪个好"

**而是**：
- ✅ 给数据命名（从字段到判断句）
- ✅ 叙事 + 主题（从排序到策展）
- ✅ 帮用户发现可能感兴趣的机会

### 1.3 唯一转化目标

> **让用户忍不住点进 Ask AI**

产生的感觉应该是：
> "这个专题太对我了，我想问更多"

---

## 二、三层分析架构

### 2.1 架构总览

```
Landing Page 原始数据（已有）
        ↓
第一层：事实标签层（客观提取）
        ↓
第二层：判断母题层（AI 推断）← 当前重点
        ↓
第三层：策展生成层（专题/合集/命名）← 下一阶段
```

### 2.2 第一层：事实标签层

**定义**：AI 从 Landing Page 直接可抽取的客观事实，不含观点。

**已有数据源**：
| 数据表 | 关键字段 |
|--------|----------|
| Startup | revenue_30d, mrr, growth_rate, founder_followers, team_size |
| LandingPageAnalysis | headline_text, core_features, pricing_model, target_audience, pain_points |
| ProductSelectionAnalysis | growth_driver, tech_complexity_level, startup_cost_level |

### 2.3 第二层：判断母题层

**定义**：不是从页面直接读出，而是 AI 基于多个字段推断的判断。

**核心原则**：
- 母题 = 行业内反复出现、可复用的"判断问题模板"
- 母题不是答案，而是"制造值得被策展的张力"
- 母题必须：减少选择空间、指向行动判断、可被多次复用

### 2.4 第三层：策展生成层

**定义**：基于多个产品的判断母题结果，生成专题/合集/命名。

**输入**：多个产品的判断标签集合
**输出**：专题、合集、标题、CTA

---

## 三、母题框架设计（9个母题，三层架构）

### 3.1 框架总览

| 层级 | 核心问题 | 母题数量 |
|------|----------|----------|
| 筛选层 | 这个方向值不值得研究？ | 2 |
| 行动层 | 如果我想做，可行吗？怎么做？ | 4 |
| 归因层 | 为什么成功？哪些值得借鉴？ | 3 |

### 3.2 筛选层（2个）

#### opportunity_validity（机会真实性）
- **核心问题**：这是真实的市场机会，还是伪机会？
- **选项**：真实机会 | 存在风险 | 伪机会 | 证据不足
- **策展价值**："看起来热门但其实是坑的方向"

#### demand_type（需求类型）
- **核心问题**：用户会主动搜索还是需要教育？
- **选项**：主动搜索型 | 触发认知型 | 需教育型 | 证据不足
- **策展价值**："不需要教育市场的机会"

### 3.3 行动层（4个）

#### solo_feasibility（独立可行性）
- **核心问题**：一个人能不能做出来并维护？
- **选项**：非常适合 | 有挑战但可行 | 不适合 | 证据不足
- **策展价值**："一个人也能维护的 SaaS"

#### entry_barrier（入场门槛）
- **核心问题**：启动需要投入多少时间和资金？
- **选项**：低门槛快启动 | 中等投入 | 高门槛 | 证据不足
- **策展价值**："周末就能启动的项目"

#### primary_risk（主要风险）
- **核心问题**：如果失败，最可能死在哪个环节？
- **选项**：技术实现 | 市场验证 | 用户获取 | 变现转化 | 证据不足
- **策展价值**："最容易死在获客阶段的产品"

#### mvp_clarity（MVP清晰度）
- **核心问题**：最小可行版本是否清晰可执行？
- **选项**：清晰可执行 | 基本清晰 | 模糊 | 证据不足
- **策展价值**："MVP 最清晰的产品方向"

### 3.4 归因层（3个）

#### success_driver（成功驱动因素）
- **核心问题**：这个产品的成功主要靠什么驱动？
- **选项**：产品驱动 | IP/创作者驱动 | 内容驱动 | 渠道驱动 | 证据不足
- **策展价值**："不靠粉丝也能成功的产品"

#### positioning_insight（定位洞察）
- **核心问题**：定位策略有什么值得学习的？
- **选项**：精准垂直 | 差异化定价 | 痛点锋利 | 场景具体 | 无明显亮点 | 证据不足
- **策展价值**："定位教科书级别的产品"

#### differentiation_point（差异化点）
- **核心问题**：相比竞品的独特之处是什么？
- **选项**：功能差异化 | 体验差异化 | 人群差异化 | 定价差异化 | 无明显差异化 | 证据不足
- **策展价值**："靠体验打赢竞品的产品"

---

## 四、多角色策展系统

### 4.1 核心理解

> **不是让 AI 模拟人，而是让 AI 用不同"判断偏好"去过滤同一批分析结果**

- 不是聊天
- 不是人格扮演
- 是**结构化偏见系统**

### 4.2 角色只出现在策展阶段

```
判断母题 Agent（单产品分析）
        ↓
【生成：判断标签 + 判断理由】
        ↓
多角色策展 Agent（跨产品筛选）
        ↓
【生成：专题 / 合集 / 命名】
```

### 4.3 策展角色定义示例

#### 角色 1：谨慎的独立开发者
```python
{
    "name": "cautious_indie_dev",
    "display_name": "谨慎的独立开发者",
    "filter_rules": {
        "solo_feasibility": ["非常适合", "有挑战但可行"],
        "opportunity_validity": ["真实机会"],
        "primary_risk": {"exclude": ["技术实现"]},
    },
    "topic_templates": [
        "失败成本最低的 SaaS 方向",
        "一个人也能维护的产品",
        "不需要融资也能活的方向",
    ],
}
```

#### 角色 2：机会嗅觉型创业者
```python
{
    "name": "opportunity_hunter",
    "display_name": "机会嗅觉型创业者",
    "filter_rules": {
        "opportunity_validity": ["真实机会"],
        "demand_type": ["主动搜索型"],
        "entry_barrier": ["低门槛快启动", "中等投入"],
    },
    "topic_templates": [
        "被低估但值得认真研究的方向",
        "现在入场还不晚的机会",
    ],
}
```

#### 角色 3：反泡沫角色（建立信任）
```python
{
    "name": "anti_bubble",
    "display_name": "反泡沫角色",
    "filter_rules": {
        "opportunity_validity": ["存在风险", "伪机会"],
    },
    "topic_templates": [
        "看起来性感但风险很高的产品",
        "营销比产品强的案例",
    ],
}
```

### 4.4 策展 Agent 实现（规则驱动，Phase 2）

#### 核心逻辑

```python
# curator_agent.py

from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class TopicTemplate:
    title: str
    pattern: str  # contrast / niche / cognitive / action
    description_template: str
    cta: str = "让我帮你分析：你能不能做类似的"

# 策展角色配置
CURATOR_ROLES = {
    "cautious_indie_dev": {
        "display_name": "谨慎的独立开发者",
        "filter_rules": {
            "solo_feasibility": ["非常适合", "有挑战但可行"],
            "opportunity_validity": ["真实机会"],
            "primary_risk": {"exclude": ["技术实现"]},
        },
        "topic_templates": [
            TopicTemplate(
                title="失败成本最低的 SaaS 方向",
                pattern="action",
                description_template="这些产品技术门槛低、一个人可维护，即使失败也不会损失太多时间和金钱。",
            ),
            TopicTemplate(
                title="一个人也能维护的产品",
                pattern="niche",
                description_template="不需要团队、不需要融资，独立开发者的理想选择。",
            ),
        ],
    },
    "opportunity_hunter": {
        "display_name": "机会嗅觉型创业者",
        "filter_rules": {
            "opportunity_validity": ["真实机会"],
            "demand_type": ["主动搜索型"],
            "entry_barrier": ["低门槛快启动", "中等投入"],
        },
        "topic_templates": [
            TopicTemplate(
                title="需求明确、门槛不高的机会",
                pattern="action",
                description_template="用户会主动搜索解决方案，获客路径清晰。",
            ),
        ],
    },
    "anti_bubble": {
        "display_name": "反泡沫角色",
        "filter_rules": {
            "opportunity_validity": ["存在风险", "伪机会"],
        },
        "topic_templates": [
            TopicTemplate(
                title="看起来性感但风险很高的产品",
                pattern="cognitive",
                description_template="这些产品营销做得好，但仔细分析会发现明显的风险点。",
            ),
        ],
    },
}

def filter_products_by_rules(
    products: List[Dict], 
    filter_rules: Dict
) -> List[Dict]:
    """根据筛选规则过滤产品"""
    result = []
    for product in products:
        judgments = product.get("mother_theme_judgments", {})
        match = True
        
        for theme_key, rule in filter_rules.items():
            judgment_value = judgments.get(theme_key, {}).get("judgment")
            
            if isinstance(rule, list):
                # 包含规则：判断值必须在列表中
                if judgment_value not in rule:
                    match = False
                    break
            elif isinstance(rule, dict) and "exclude" in rule:
                # 排除规则：判断值不能在排除列表中
                if judgment_value in rule["exclude"]:
                    match = False
                    break
        
        if match:
            result.append(product)
    
    return result

def generate_topics(
    products: List[Dict],
    min_products: int = 3,
    max_products: int = 10
) -> List[Dict]:
    """生成所有符合条件的专题"""
    topics = []
    
    for role_name, role_config in CURATOR_ROLES.items():
        # 1. 按规则筛选产品
        filtered = filter_products_by_rules(
            products, 
            role_config["filter_rules"]
        )
        
        # 2. 产品数量不足则跳过
        if len(filtered) < min_products:
            continue
        
        # 3. 为每个模板生成专题
        for template in role_config["topic_templates"]:
            topics.append({
                "topic_key": f"{role_name}_{template.pattern}",
                "title": template.title,
                "description": template.description_template,
                "curator_role": role_name,
                "generation_pattern": template.pattern,
                "filter_rules": role_config["filter_rules"],
                "products": filtered[:max_products],
                "product_count": len(filtered),
                "cta_text": template.cta,
            })
    
    return topics
```

#### 离线处理架构

```
┌─────────────────────────────────────────────────────────────┐
│                    离线批处理流程                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    定时任务     ┌─────────────────────┐   │
│  │  Startups   │ ──────────────→ │ 母题判断 Agent      │   │
│  │  (新增/更新) │    (每日凌晨)   │ (LLM 批量处理)      │   │
│  └─────────────┘                 └──────────┬──────────┘   │
│                                             │              │
│                                             ↓              │
│                                  ┌─────────────────────┐   │
│                                  │ mother_theme_       │   │
│                                  │ judgments 表        │   │
│                                  └──────────┬──────────┘   │
│                                             │              │
│  ┌─────────────┐    定时任务     ┌──────────↓──────────┐   │
│  │ 策展角色    │ ──────────────→ │ 策展 Agent          │   │
│  │ 配置        │    (每日/每周)  │ (规则筛选，无LLM)   │   │
│  └─────────────┘                 └──────────┬──────────┘   │
│                                             │              │
│                                             ↓              │
│                                  ┌─────────────────────┐   │
│                                  │ discover_topics 表  │   │
│                                  └─────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    在线服务流程                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  用户请求 → API → 直接查询 discover_topics 表 → 返回专题    │
│                                                             │
│  （无 LLM 调用，响应快速）                                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### 定时任务设计

| 任务 | 频率 | 耗时预估 | 说明 |
|------|------|----------|------|
| 母题判断 | 每日凌晨 | 较长（LLM调用） | 只处理新增/更新的产品 |
| 专题生成 | 每日/每周 | 秒级（纯SQL） | 基于已有判断结果筛选 |
| 专题清理 | 每周 | 秒级 | 移除产品数不足的专题 |

#### 增量处理策略

```python
def get_products_need_judgment():
    """获取需要进行母题判断的产品"""
    return db.query("""
        SELECT s.* FROM startups s
        LEFT JOIN mother_theme_judgments m 
            ON s.id = m.startup_id
        WHERE m.id IS NULL  -- 从未判断过
           OR s.updated_at > m.created_at  -- 产品有更新
    """)
```

#### 后续扩展（Phase 4）

- 用 LLM 动态生成标题和描述
- 基于用户行为反馈调整角色权重
- 自动发现新的筛选规则组合

---

## 五、专题生成套路

### 5.1 套路一：反差型（最好用）

**原理**：用两个"本不该同时出现的判断维度"做交集

**示例组合**：
- entry_barrier = 低门槛 + positioning_insight = 精准垂直
- solo_feasibility = 非常适合 + success_driver = 产品驱动

**标题模板**：
> 「这些产品{A}，但{B}」

### 5.2 套路二：Niche 聚焦型

**原理**：在一个小用户群体中再切一刀

**示例组合**：
- target_audience = developer + demand_type = 主动搜索型

**标题模板**：
> 「专门赚{用户群}钱的"小而美"产品」

### 5.3 套路三：认知纠偏型（建立信任）

**原理**：明确告诉用户：你以为的和现实不一样

**示例组合**：
- opportunity_validity = 存在风险 + primary_risk = 用户获取

**标题模板**：
> 「这些产品不是没需求，而是{真实问题}」

### 5.4 套路四：行动导向型（强转化）

**原理**：明确回答"你现在能不能做"

**示例组合**：
- solo_feasibility = 非常适合 + mvp_clarity = 清晰可执行 + entry_barrier = 低门槛快启动

**标题模板**：
> 「如果你现在想做 SaaS，可以从这些方向开始」

---

## 六、冲突类型（驱动专题生成）

专题的本质是"冲突"，以下是可系统化的冲突类型：

| 冲突类型 | 描述 | 示例 |
|----------|------|------|
| 表象 vs 本质 | 看起来 X，实际上 Y | 看起来很简单，实际上很难增长 |
| 预期 vs 现实 | 你以为这样能成功，但现实不是 | 你以为需要 AI，但不需要 |
| 优点 vs 代价 | 这个好处背后藏着什么坑 | 低门槛意味着高竞争 |
| 可行性 vs 可持续性 | 能做出来，但能不能活下去 | 能复制，但能不能赚钱 |
| 局部最优 vs 全局失败 | 单点做对了，但整体错了 | 产品好，但获客难 |

---

## 七、数据流与工程架构

### 7.1 Agent 拆分

```
1. Landing Page 解析 Agent（已有）
   - 输入：网页 HTML
   - 输出：结构化字段（第一层）

2. 判断母题 Agent（mother_theme_test.py - 当前实现）
   - 输入：第一层字段 + 母题模板
   - 输出：每个产品的判断标签 + 理由

3. 策展 Agent（待实现）
   - 输入：多个产品的判断标签 + 角色定义 + 专题套路
   - 输出：专题/合集/标题
```

### 7.2 数据流图

```
┌─────────────────────────────────────────────────────────────┐
│                    Landing Page HTML                        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              Landing Page 解析 Agent                        │
│  输出：headline, features, pricing, cta, scores...          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              判断母题 Agent（单产品）                         │
│  输入：第一层字段 + 9个母题模板                               │
│  输出：{                                                    │
│    "opportunity_validity": "真实机会",                       │
│    "demand_type": "主动搜索型",                              │
│    "solo_feasibility": "非常适合",                          │
│    ...                                                      │
│  }                                                          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              策展 Agent（跨产品）                            │
│  输入：N个产品的判断结果 + 角色 + 套路                        │
│  输出：{                                                    │
│    "topic_title": "失败成本最低的 SaaS 方向",                │
│    "topic_description": "...",                              │
│    "products": [...],                                       │
│    "cta": "让我帮你分析：你能不能做类似的"                    │
│  }                                                          │
└─────────────────────────────────────────────────────────────┘
```


### 7.3 数据库设计（新增表）

```sql
-- 母题判断结果表
CREATE TABLE mother_theme_judgments (
    id SERIAL PRIMARY KEY,
    startup_id INTEGER NOT NULL REFERENCES startups(id),
    theme_key VARCHAR(50) NOT NULL,
    judgment VARCHAR(100),
    confidence VARCHAR(10),
    reasons JSONB,
    evidence_fields JSONB,
    uncertainties JSONB,
    prompt_version VARCHAR(20),
    model VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 专题表
CREATE TABLE discover_topics (
    id SERIAL PRIMARY KEY,
    topic_key VARCHAR(100) UNIQUE,
    title VARCHAR(200),
    description TEXT,
    curator_role VARCHAR(50),
    generation_pattern VARCHAR(50),
    filter_rules JSONB,
    product_ids JSONB,
    cta_text VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    display_order INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 专题-产品关联表
CREATE TABLE topic_products (
    id SERIAL PRIMARY KEY,
    topic_id INTEGER NOT NULL REFERENCES discover_topics(id),
    startup_id INTEGER NOT NULL REFERENCES startups(id),
    ai_label VARCHAR(200),
    counter_intuitive_point TEXT,
    display_order INTEGER
);
```

---

## 八、母题生成器（可扩展性保障）

### 8.1 母题生成公式

> **母题 = A 视角 × B 约束 × C 冲突**

### 8.2 A 类：视角（Perspective）

- 初次做 SaaS 的人
- 连续创业者
- 没时间的人（副业）
- 不擅长增长的人
- 技术强 / 市场弱的人

### 8.3 B 类：约束（Constraint）

- 时间（只能业余）
- 精力（不能 24h 维护）
- 资金（0 成本 / 低成本）
- 技能（只会前端 / 只会后端）

### 8.4 C 类：冲突（Tension）

- 表象 vs 本质
- 预期 vs 现实
- 优点 vs 代价
- 可行性 vs 可持续性

### 8.5 母题演化机制

母题库不是靠"想到多少"，而是靠"世界变化会不断制造新冲突"：

1. **数据规模变化** → 新模式出现
2. **世界变化** → 新失效方式出现
3. **用户约束变化** → 新视角出现
4. **现有母题之间的冲突** → 新母题产生

---

## 九、发现页模块设计

### 9.1 整体结构

```
发现 Discover
├─ 今日 AI 策展（每日 1-2 个，灵魂模块）
├─ 主题合集（横向滑动，差异化核心）
├─ 爆款解剖（把"抄"说清楚）
├─ 创作者宇宙（人的维度）
└─ 你可能想抄的（强转化区，个性化推荐）
```

### 9.2 模块一：今日 AI 策展

**定位**：灵魂模块，每日只推 1-2 个

**页面结构**：
1. AI 写一段"为什么这批东西值得看"
2. 展示 3-5 个产品/创作者
3. 每个卡片只展示：一句话标签 + 一个"反直觉点"
4. 底部强 CTA：👉 **"让我帮你分析：你能不能做类似的"**

### 9.3 模块二：主题合集

**产品向标签示例**：
- 「被低估的赚钱机器」
- 「一个人也能维护的 SaaS」
- 「没有融资，但活得很好」

**点击后结构**：
1. AI 解释：这个主题为什么存在
2. 列出 5-10 个对象
3. 每个对象附一个 AI 生成的"命名标签"

---

## 十、实施路线图

### Phase 1：母题判断验证（当前 ✅）

**目标**：验证 9 个母题在真实数据上的表现

**任务**：
- [x] 完成 `mother_theme_test.py` 基础框架
- [x] 定义 9 个母题模板（三层架构）
- [x] 实现 one-shot 批量判断
- [x] Prompt 优化到 v4.2
- [ ] 跑 50-100 个产品，观察判断分布
- [ ] 分析判断一致性和证据充分性

**产出**：
- 母题判断结果 JSON
- 各母题分布统计
- Prompt 调优记录

### Phase 2：策展 Agent 开发

**目标**：实现跨产品的专题生成

**任务**：
- [ ] 设计策展角色配置结构
- [ ] 实现专题生成套路（4 种）
- [ ] 开发策展 Agent
- [ ] 生成第一批专题（10-20 个）

**产出**：
- `curator_agent.py`
- 专题数据库表
- 第一批专题内容

### Phase 3：发现页 MVP

**目标**：上线最小可用的发现页

**任务**：
- [ ] 前端发现页 UI
- [ ] 今日 AI 策展模块
- [ ] 主题合集模块
- [ ] 专题详情页 + Ask AI 入口

**产出**：
- 发现页前端
- 专题 → Ask AI 转化链路

### Phase 4：母题演化系统

**目标**：让母题库可以自我进化

**任务**：
- [ ] 实现母题生成器 Agent
- [ ] 建立母题评估机制（用户行为反馈）
- [ ] 母题版本管理

---

## 十一、关键成功指标

### 11.1 母题判断质量

- 判断一致性：同一产品多次判断结果一致率 > 90%
- 证据充分性："证据不足"判断占比 < 20%
- 判断分布：每个母题的判断选项分布合理，无极端偏斜

### 11.2 专题生成质量

- 专题覆盖率：> 80% 的产品至少出现在 1 个专题中
- 专题差异性：不同专题的产品重叠率 < 30%
- 标题吸引力：人工评估标题"想点进去"的比例 > 60%

### 11.3 用户转化

- 发现页 → 专题详情页 点击率
- 专题详情页 → Ask AI 转化率
- Ask AI 对话深度（轮次）

---

## 十二、核心理念总结

### 12.1 发现系统的本质

> **发现 = AI 自动生成「可以当标题的判断句」**

### 12.2 母题的本质

> **母题 = 行业内反复出现、可复用的"判断问题模板"**
> **母题不是答案，而是"制造值得被策展的张力"**

### 12.3 多角色策展的本质

> **不同角色 = 不同"筛选器"**
> **角色不"分析产品"，角色只"组合判断"**

### 12.4 专业性的来源

> **专业性不来自你的经验，而来自"判断为什么成立"的透明度**

只要做到：有判断、有理由、有不确定性说明，BuildWhat 就是一个"可信但不权威"的认知产品。

### 12.5 可扩展性的保障

> **母题库不是靠"你想到多少"，而是靠"世界变化会不断制造新冲突"**

---

## 附录：当前实现状态

### A. mother_theme_test.py 状态

- **Prompt 版本**：v4.2
- **母题数量**：9 个（2 筛选 + 4 行动 + 3 归因）
- **验证机制**：
  - `validation_errors`：格式/解析错误（严格）
  - `validation_warnings`：业务建议（宽松）
- **一致性检查**：跨母题逻辑一致性验证

### B. 待解决问题

1. 部分产品输出 `uncertainties: null`（应为 `[]`）
2. 个别产品使用母题名称作为 evidence_fields
3. 需要更多样本验证判断分布

### C. 下一步行动

1. 扩大测试样本到 50-100 个产品
2. 统计各母题判断分布
3. 根据分布调整 hints
4. 开始设计策展 Agent
