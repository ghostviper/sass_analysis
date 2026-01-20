# Product & Market Thinking Enhancement Analysis

## 目标

通过研究 marketingskills 和 agents 项目，提取产品和市场方面的专业方法论，增强 ai-template-generator skill 的策展模板生成能力，使其具备：

1. **产品思维和市场洞察**：从产品定位、竞争格局、用户价值等多维度分析
2. **市场视角补充**：当前项目已有产品维度拆解，需要补充市场分析视角
3. **专业框架应用**：引入成熟的产品/市场分析框架

---

## 已研究的 Skills 总结

### 1. Marketing Skills (4个)

#### pricing-strategy
**核心框架：**
- Van Westendorp PSM (价格敏感度测试)
- MaxDiff Analysis (最大差异分析)
- Value Metrics (价值指标定价)
- Tier Structure (分层定价策略)

**可借鉴点：**
- 价格心理学：锚定效应、对比效应
- 价值感知：如何传达产品价值
- 定价策略与市场定位的关系

#### launch-strategy
**核心框架：**
- ORB Framework (Owned/Rented/Borrowed channels)
- 5-phase launch approach
- Channel selection matrix

**可借鉴点：**
- 产品发布的渠道策略
- 不同阶段的营销重点
- 如何构建发布势能

#### free-tool-strategy
**核心框架：**
- Engineering as Marketing
- Tool types (calculators, analyzers, generators)
- SEO considerations

**可借鉴点：**
- 免费工具作为获客手段
- 工具型产品的设计思路
- 价值展示与转化路径

#### marketing-psychology
**核心内容：**
- 70+ mental models
- Buyer behavior patterns
- Cognitive biases

**可借鉴点：**
- 用户心理模型
- 决策影响因素
- 认知偏差在产品设计中的应用

### 2. Marketing Skills - Competitive & Market (3个)

#### competitor-alternatives
**核心框架：**
- 4种对比页面格式
- Centralized competitor data
- Modular content architecture

**可借鉴点：**
- 竞品分析的结构化方法
- 差异化定位的表达方式
- 诚实对比建立信任

#### marketing-ideas
**核心内容：**
- 140种营销策略
- 按类别组织（Content/SEO, Paid Ads, Community, etc.）
- 按阶段/预算/时间线分类

**可借鉴点：**
- 营销策略的系统化分类
- 不同阶段的策略选择
- 资源约束下的优先级

#### page-cro
**核心框架：**
- Value proposition clarity
- CTA optimization
- Trust signals & social proof
- Objection handling

**可借鉴点：**
- 价值主张的清晰表达
- 转化路径优化
- 用户异议的预判和处理

### 3. Startup Business Analyst Skills (3个)

#### market-sizing-analysis
**核心框架：**
- TAM/SAM/SOM 三层市场模型
- 3种计算方法：Top-Down, Bottom-Up, Value Theory
- 行业特定考量（SaaS, Marketplace, Consumer, B2B）

**可借鉴点：**
- 市场机会的量化评估
- 不同方法的三角验证
- 市场规模与产品定位的关系


#### competitive-landscape
**核心框架：**
- Porter's Five Forces (五力模型)
- Blue Ocean Strategy (蓝海战略)
- Competitive Positioning Maps (竞争定位图)
- Four Actions Framework (消除-减少-增加-创造)

**可借鉴点：**
- 系统化的竞争分析方法
- 差异化机会识别
- 可防御的竞争优势评估

#### startup-metrics-framework
**核心框架：**
- Universal metrics (MRR, ARR, Growth Rate)
- Unit economics (CAC, LTV, Payback Period)
- SaaS metrics (NDR, Magic Number, Rule of 40)
- Marketplace metrics (GMV, Take Rate, Liquidity)

**可借鉴点：**
- 量化产品成功的指标体系
- 不同商业模式的关键指标
- 按阶段追踪不同指标

---

## 当前项目的产品维度现状

### 已有的产品维度（来自 domain_knowledge.py）

1. **产品类型维度**
   - 工具型、平台型、内容型、服务型、社交型、电商型、教育型、娱乐型

2. **目标用户维度**
   - B2B、B2C、B2B2C、开发者、创作者、企业、个人

3. **商业模式维度**
   - 订阅制、一次性付费、免费增值、广告、交易佣金、企业授权

4. **技术特征维度**
   - AI驱动、无代码、API优先、开源、移动优先、Web3

5. **使用场景维度**
   - 生产力、协作、自动化、分析、创作、学习、娱乐

6. **产品成熟度维度**
   - MVP、成长期、成熟期、扩张期

### 缺失的市场维度

当前项目主要关注**产品本身的特征**，但缺少：

1. **市场机会维度**
   - 市场规模（TAM/SAM/SOM）
   - 市场增长率
   - 市场成熟度

2. **竞争格局维度**
   - 竞争强度
   - 差异化空间
   - 进入壁垒

3. **用户价值维度**
   - 解决的痛点强度
   - 价值主张清晰度
   - ROI 可量化性

4. **增长潜力维度**
   - 病毒系数
   - 网络效应
   - 扩展性

5. **商业健康度维度**
   - 单位经济模型
   - 获客效率
   - 留存质量

---

## 增强方案：引入市场驱动的策展视角

### 方案 1：扩展 Opportunity Types

**当前的 4 种机会类型：**
1. Contrast（对比型）
2. Cognitive（认知型）
3. Action（行动型）
4. Niche（细分型）

**建议新增的市场驱动机会类型：**

5. **Market-Gap（市场空白型）**
   - 识别未被满足的市场需求
   - 基于 Blue Ocean Strategy 的四行动框架
   - 示例："没有针对 X 行业的 Y 工具"

6. **Value-Arbitrage（价值套利型）**
   - 高价值但低价格的机会
   - 基于 pricing-strategy 的价值感知
   - 示例："企业级功能，个人版价格"

7. **Competitive-Weakness（竞品弱点型）**
   - 利用竞品的明显短板
   - 基于 competitive-landscape 分析
   - 示例："Notion 太慢，我们更快"

8. **Metrics-Driven（指标驱动型）**
   - 基于关键业务指标的优化
   - 基于 startup-metrics-framework
   - 示例："提升 30% 转化率的工具"

9. **Channel-Innovation（渠道创新型）**
   - 新的获客或分发渠道
   - 基于 launch-strategy 的 ORB 框架
   - 示例："通过 Chrome 扩展获客"

10. **Psychology-Leverage（心理杠杆型）**
    - 利用用户心理和认知偏差
    - 基于 marketing-psychology
    - 示例："社交证明驱动的产品"

### 方案 2：增强 curation-logic.md 框架

**当前框架：**
- 基于产品特征的匹配逻辑
- 主题判断规则
- 产品筛选标准

**建议增强：**

#### 2.1 添加市场分析层

```markdown
## Market Analysis Layer

### Market Opportunity Assessment
- **Market Size**: TAM/SAM/SOM estimation
- **Growth Rate**: Market expansion velocity
- **Maturity**: Emerging / Growing / Mature / Declining

### Competitive Landscape
- **Competition Intensity**: Low / Medium / High
- **Differentiation Space**: Clear gaps vs. crowded
- **Entry Barriers**: Network effects, switching costs, etc.

### Value Proposition Strength
- **Pain Point Severity**: How acute is the problem?
- **Solution Clarity**: How clear is the value?
- **ROI Measurability**: Can users quantify benefits?
```

#### 2.2 添加增长潜力评估

```markdown
## Growth Potential Framework

### Viral Mechanics
- **K-Factor**: Organic sharing potential
- **Network Effects**: Value increases with users
- **Referral Loops**: Built-in growth mechanisms

### Scalability
- **Unit Economics**: CAC vs LTV
- **Margin Structure**: Gross margin potential
- **Expansion Revenue**: Upsell/cross-sell opportunities

### Market Timing
- **Trend Alignment**: Riding macro trends
- **Technology Readiness**: Infrastructure maturity
- **Regulatory Environment**: Tailwinds or headwinds
```

#### 2.3 添加商业模式评估

```markdown
## Business Model Health

### Revenue Quality
- **Predictability**: Recurring vs. one-time
- **Scalability**: Linear vs. exponential
- **Defensibility**: Switching costs, lock-in

### Customer Economics
- **CAC Payback**: < 12 months ideal
- **LTV:CAC Ratio**: > 3.0 healthy
- **Retention**: NDR > 100% excellent

### Monetization Strategy
- **Pricing Power**: Premium vs. value positioning
- **Packaging**: Tier structure effectiveness
- **Expansion Path**: Land-and-expand potential
```


### 方案 3：优化 discover_opportunities.py 的 AI Prompt

**当前 Prompt 结构：**
- 基于产品数据分析
- 识别 4 种机会类型
- 输出机会描述

**建议增强的 Prompt 结构：**

```python
ENHANCED_DISCOVERY_PROMPT = """
你是一位资深的产品策展专家，同时具备深厚的市场分析和商业洞察能力。

## 分析维度

### 1. 产品维度（已有）
- 产品类型、功能、技术特征
- 目标用户、使用场景
- 商业模式、成熟度

### 2. 市场维度（新增）
- **市场机会**：评估 TAM/SAM/SOM，识别市场空白
- **竞争格局**：分析竞争强度，找出差异化空间
- **增长潜力**：评估病毒性、网络效应、扩展性

### 3. 用户价值维度（新增）
- **痛点强度**：用户问题的紧迫性和严重性
- **价值主张**：解决方案的清晰度和独特性
- **ROI 可见性**：用户能否量化收益

### 4. 商业健康度维度（新增）
- **单位经济**：CAC、LTV、Payback Period
- **留存质量**：用户粘性、复购率
- **定价策略**：价值感知与定价匹配度

## 机会类型（扩展到 10 种）

### 原有类型
1. **Contrast（对比型）**：通过对比突出差异
2. **Cognitive（认知型）**：改变用户认知
3. **Action（行动型）**：激发具体行动
4. **Niche（细分型）**：聚焦特定细分

### 新增类型
5. **Market-Gap（市场空白型）**：未被满足的需求
   - 应用 Blue Ocean Strategy 四行动框架
   - 识别"消除-减少-增加-创造"的机会
   
6. **Value-Arbitrage（价值套利型）**：高价值低价格
   - 应用 pricing-strategy 的价值感知理论
   - 找出价格与价值不匹配的机会
   
7. **Competitive-Weakness（竞品弱点型）**：竞品短板
   - 应用 Porter's Five Forces 分析
   - 识别竞品的结构性弱点
   
8. **Metrics-Driven（指标驱动型）**：关键指标优化
   - 应用 startup-metrics-framework
   - 聚焦可量化的业务指标提升
   
9. **Channel-Innovation（渠道创新型）**：新分发渠道
   - 应用 launch-strategy 的 ORB 框架
   - 识别 Owned/Rented/Borrowed 渠道机会
   
10. **Psychology-Leverage（心理杠杆型）**：认知偏差利用
    - 应用 marketing-psychology 的 mental models
    - 利用锚定、社交证明、稀缺性等心理效应

## 分析框架

### Porter's Five Forces 应用
- 新进入者威胁：进入壁垒高低
- 供应商议价能力：依赖度分析
- 买家议价能力：客户集中度
- 替代品威胁：替代方案评估
- 行业竞争：竞争强度判断

### Blue Ocean Strategy 应用
- **消除**：哪些行业标配可以去掉？
- **减少**：哪些功能可以大幅简化？
- **增加**：哪些方面可以远超行业标准？
- **创造**：哪些全新价值可以创造？

### Value Theory 应用
- 当前问题成本：时间、金钱、效率损失
- 解决方案价值：节省、收益、效率提升
- 支付意愿：价值的 10-30%
- 定价策略：锚定、对比、分层

## 输出要求

对每个识别的机会，提供：

1. **机会类型**：10 种类型之一
2. **机会描述**：清晰的策展角度
3. **市场洞察**：
   - 市场规模估算（定性）
   - 竞争格局评估
   - 增长潜力判断
4. **用户价值**：
   - 核心痛点
   - 价值主张
   - ROI 可见性
5. **商业逻辑**：
   - 单位经济可行性
   - 留存预期
   - 定价策略建议
6. **应用框架**：使用了哪些分析框架
7. **匹配产品数量**：预估符合条件的产品数量
8. **策展价值**：为什么这个角度有价值

## 示例输出

```json
{
  "opportunity_type": "Value-Arbitrage",
  "title": "企业级功能，个人版价格",
  "description": "策展那些提供企业级能力但定价亲民的工具...",
  "market_insight": {
    "market_size": "中等（SMB 市场）",
    "competition": "低（大多数企业工具定价高昂）",
    "growth_potential": "高（价格敏感的 SMB 市场快速增长）"
  },
  "user_value": {
    "pain_point": "需要企业级功能但预算有限",
    "value_proposition": "10x 价值，1/10 价格",
    "roi_visibility": "高（成本节省直接可见）"
  },
  "business_logic": {
    "unit_economics": "可行（自助服务降低 CAC）",
    "retention": "高（功能强大，切换成本高）",
    "pricing_strategy": "价值定价，对比企业版突出性价比"
  },
  "frameworks_applied": [
    "pricing-strategy: Value Metrics",
    "competitive-landscape: Positioning Map",
    "market-sizing: Bottom-Up Analysis"
  ],
  "estimated_matches": 25,
  "curation_value": "帮助预算有限的团队发现高性价比工具"
}
```

现在，基于以下产品数据，识别 5-10 个高价值的策展机会...
"""
```

### 方案 4：创建新的 Reference 文件

建议在 `backend/skills/ai-template-generator/references/` 下新增：

#### 4.1 market-analysis-frameworks.md

```markdown
# Market Analysis Frameworks

## Porter's Five Forces
[详细说明如何应用五力模型分析产品市场]

## Blue Ocean Strategy
[详细说明四行动框架的应用]

## Market Sizing (TAM/SAM/SOM)
[详细说明市场规模评估方法]

## Competitive Positioning
[详细说明竞争定位图的绘制和分析]
```

#### 4.2 business-metrics-guide.md

```markdown
# Business Metrics Guide

## SaaS Metrics
- MRR, ARR, Growth Rate
- CAC, LTV, Payback Period
- NDR, Magic Number, Rule of 40

## Marketplace Metrics
- GMV, Take Rate
- Liquidity, Fill Rate
- Supply/Demand Balance

## Consumer Metrics
- DAU/MAU, Retention Curves
- K-Factor, Viral Coefficient
- Session Frequency/Duration
```

#### 4.3 pricing-psychology.md

```markdown
# Pricing Psychology

## Cognitive Biases
- Anchoring Effect
- Price-Quality Heuristic
- Decoy Effect

## Value Perception
- Reference Pricing
- Price Framing
- Tier Structure

## Willingness to Pay
- Van Westendorp PSM
- Value Metrics
- Competitive Benchmarking
```

---

## 实施路径

### Phase 1: 扩展机会类型（1-2 天）

1. **更新 discover_opportunities.py**
   - 扩展 AI prompt，加入市场分析维度
   - 新增 6 种机会类型
   - 增强输出结构（包含市场洞察、用户价值、商业逻辑）

2. **测试新机会类型**
   - 运行发现脚本
   - 验证新类型的识别质量
   - 调整 prompt 优化结果

### Phase 2: 增强策展逻辑（2-3 天）

1. **更新 curation-logic.md**
   - 添加市场分析层
   - 添加增长潜力评估
   - 添加商业模式评估

2. **更新 generate_template.py**
   - 在模板生成时应用新框架
   - 增强产品筛选逻辑
   - 优化主题描述生成

### Phase 3: 创建参考文档（1-2 天）

1. **创建新 reference 文件**
   - market-analysis-frameworks.md
   - business-metrics-guide.md
   - pricing-psychology.md

2. **更新 SKILL.md**
   - 引用新的 reference 文件
   - 更新使用说明
   - 添加新框架的应用示例

### Phase 4: 验证和优化（1-2 天）

1. **端到端测试**
   - 发现机会 → 生成模板 → 预览产品
   - 验证市场洞察的准确性
   - 评估策展质量提升

2. **迭代优化**
   - 根据测试结果调整
   - 优化 AI prompt
   - 完善文档

---

## 预期效果

### 1. 策展视角更丰富

**之前：**
- 主要基于产品特征（"AI 工具"、"无代码平台"）
- 缺少市场和商业视角

**之后：**
- 市场驱动（"市场空白"、"竞品弱点"）
- 价值驱动（"价值套利"、"指标优化"）
- 增长驱动（"渠道创新"、"心理杠杆"）

### 2. 策展质量更专业

**之前：**
- 简单的产品分类和聚合
- 缺少深度洞察

**之后：**
- 应用成熟的商业分析框架
- 提供市场洞察和商业逻辑
- 量化评估（市场规模、竞争强度、增长潜力）

### 3. 用户价值更清晰

**之前：**
- "这些产品都是 AI 工具"
- 用户需要自己判断价值

**之后：**
- "这些工具提供企业级功能但价格亲民，适合预算有限的团队"
- 明确的价值主张和使用场景

### 4. 可操作性更强

**之前：**
- 策展主题较抽象
- 缺少行动指引

**之后：**
- 基于具体指标（"提升 30% 转化率"）
- 明确的应用场景和 ROI

---

## 关键成功因素

1. **平衡复杂度**：引入专业框架但保持易用性
2. **数据支撑**：尽可能用数据验证市场洞察
3. **迭代优化**：根据实际效果持续调整
4. **文档完善**：确保框架应用有清晰指引

---

## 下一步行动

1. **Review 本分析文档**：确认方向和优先级
2. **选择实施方案**：决定从哪个 Phase 开始
3. **开始实施**：按照路径逐步推进
4. **持续验证**：每个阶段都进行测试和优化

