# AI 策展模板生成器 - 需求文档

## 📋 项目概述

**目标：** 创建一个 AI 驱动的策展模板生成系统，让 AI 作为"资深产品策展专家"，根据用户输入的观察维度和指引，自动生成结构化的策展模板并入库。

**核心价值：**
- 🤖 AI 真正理解产品设计和市场商业逻辑
- 🎯 自动生成高质量、有洞察的策展模板
- 🔄 持续扩充策展主题库，无需人工编写
- 📊 基于数据验证模板的有效性

---

## 👥 用户故事

### US-1: 作为策展管理员，我想通过自然语言描述生成策展模板

**场景：**
```
输入：
- 观察维度：["AI依赖程度", "医疗健康类目", "合规要求"]
- 指引：找到轻度AI + 医疗健康 + 无合规要求的低门槛机会

输出：
- 结构化的 CurationTemplate 对象
- 包含中英文标题、描述、洞察、筛选规则
- 自动入库并可用于策展生成
```

**验收标准：**
- [ ] 支持自然语言输入观察维度和指引
- [ ] AI 能理解维度与母题/字段的映射关系
- [ ] 生成的模板符合 CurationTemplate 数据结构
- [ ] 生成的文案专业、有洞察、吸引人
- [ ] 自动保存到数据库并分配唯一 key

---

### US-2: 作为策展管理员，我想 AI 能理解产品和市场的深层逻辑

**场景：**
```
输入："找到适合前端开发者的变现机会"

AI 理解：
- 前端开发者 → 技术栈偏向视觉/交互
- 变现机会 → 需要真实收入、低门槛
- 适合 → 技术复杂度低、无需后端重度依赖

生成规则：
- tech_complexity_level: ["low", "medium"]
- requires_realtime: [False]
- solo_feasibility: ["非常适合"]
- revenue_30d: {"min": 2000}
```

**验收标准：**
- [ ] AI 能将用户画像映射到技术特征
- [ ] AI 能理解商业逻辑（变现、门槛、风险）
- [ ] AI 能推断隐含的筛选条件
- [ ] 生成的规则逻辑自洽、合理

---

### US-3: 作为策展管理员，我想预览和验证 AI 生成的模板

**场景：**
```
生成模板后：
1. 显示模板的完整信息（标题、描述、规则）
2. 显示匹配的产品数量和示例
3. 显示平均收入、分布情况
4. 允许人工审核和调整
5. 确认后正式入库
```

**验收标准：**
- [ ] 生成后先进入"待审核"状态
- [ ] 显示匹配产品的统计信息
- [ ] 支持编辑标题、描述、规则
- [ ] 支持测试不同的筛选规则
- [ ] 确认后才正式激活模板

---

### US-4: 作为策展管理员，我想批量生成多个相关模板

**场景：**
```
输入："生成所有行业 × AI 的低门槛机会"

AI 自动生成：
- AI × 医疗健康的低门槛机会
- AI × 教育培训的低门槛机会
- AI × 金融科技的低门槛机会
- AI × 营销工具的低门槛机会
- ...（共 10+ 个模板）
```

**验收标准：**
- [ ] 支持批量生成指令
- [ ] AI 能理解"所有行业"等泛化概念
- [ ] 自动生成多个相关但不重复的模板
- [ ] 批量预览和确认机制

---

### US-5: 作为策展管理员，我想 AI 能从数据中学习和优化

**场景：**
```
AI 观察到：
- "低粉丝高收入"模板点击率很高
- "功能简单高收入"模板产品匹配度好
- "AI教育"模板用户停留时间长

AI 自动：
- 生成类似的反差型模板
- 调整收入阈值以提高匹配度
- 扩展教育类的细分模板
```

**验收标准：**
- [ ] 记录每个模板的使用数据（点击、停留、分享）
- [ ] AI 能分析哪些模板表现好
- [ ] AI 能自动生成改进版本
- [ ] 支持 A/B 测试不同版本

---

## 🎯 核心功能需求

### 1. AI 专家系统设计

**1.1 知识库构建**

AI 需要理解的知识：

```python
# 领域知识
DOMAIN_KNOWLEDGE = {
    "user_personas": {
        "前端开发者": {
            "tech_skills": ["HTML/CSS", "JavaScript", "React/Vue"],
            "pain_points": ["后端复杂", "部署困难", "数据库管理"],
            "opportunities": ["视觉工具", "组件库", "设计系统"],
            "constraints": ["低后端复杂度", "无需实时系统"]
        },
        "独立开发者": {
            "constraints": ["一人可做", "低成本", "快速启动"],
            "preferences": ["SaaS", "工具类", "自动化"],
        },
        # ... 更多用户画像
    },
    
    "business_logic": {
        "变现难度": {
            "容易": ["B2B", "工具类", "主动搜索"],
            "中等": ["B2C订阅", "内容付费"],
            "困难": ["广告变现", "需教育市场"]
        },
        "竞争程度": {
            "蓝海": ["细分垂直", "新兴技术", "小众需求"],
            "红海": ["通用工具", "成熟市场", "巨头布局"]
        },
    },
    
    "market_insights": {
        "fintech": {
            "barriers": ["合规", "信任", "资金"],
            "opportunities": ["嵌入式金融", "加密工具"],
            "success_patterns": ["B2B切入", "API优先"]
        },
        # ... 更多行业
    }
}
```

**1.2 推理引擎**

AI 的推理流程：

```
用户输入 → 意图理解 → 知识检索 → 规则生成 → 文案创作 → 验证优化
```

**验收标准：**
- [ ] 知识库覆盖 10+ 个用户画像
- [ ] 知识库覆盖 15+ 个行业
- [ ] 推理过程可解释（显示推理步骤）
- [ ] 支持知识库的增量更新

---

### 2. 模板生成流程

**2.1 输入接口**

```python
class TemplateGenerationRequest:
    # 方式1：自然语言
    natural_language: str  # "找到适合前端开发者的变现机会"
    
    # 方式2：结构化输入
    dimensions: List[str]  # ["用户画像:前端开发者", "目标:变现"]
    constraints: Dict[str, Any]  # {"revenue_min": 2000, "solo": True}
    
    # 方式3：示例驱动
    example_products: List[int]  # [123, 456, 789] 产品ID
    pattern_type: str  # "找到类似的产品"
    
    # 通用参数
    language: str = "zh"  # zh/en/both
    creativity: float = 0.7  # 0-1，创意程度
    batch_size: int = 1  # 生成数量
```

**2.2 生成流程**

```
1. 意图解析
   ↓
2. 知识检索（从知识库匹配相关知识）
   ↓
3. 规则推导（生成 filter_rules）
   ↓
4. 文案创作（生成标题、描述、洞察）
   ↓
5. 数据验证（检查匹配产品数量）
   ↓
6. 质量评分（评估模板质量）
   ↓
7. 返回结果（待审核状态）
```

**验收标准：**
- [ ] 支持 3 种输入方式
- [ ] 生成时间 < 10 秒
- [ ] 生成的规则能匹配到产品
- [ ] 文案质量达到人工水平

---

### 3. 质量保证机制

**3.1 自动验证**

```python
class TemplateValidator:
    def validate(self, template: CurationTemplate) -> ValidationResult:
        checks = [
            self.check_product_count(),      # 匹配产品数量
            self.check_revenue_distribution(), # 收入分布合理性
            self.check_rule_consistency(),    # 规则逻辑一致性
            self.check_copy_quality(),        # 文案质量
            self.check_uniqueness(),          # 与现有模板的差异度
        ]
        return ValidationResult(checks)
```

**3.2 质量评分**

```python
quality_score = (
    product_match_score * 0.3 +      # 产品匹配度
    revenue_potential_score * 0.2 +   # 收入潜力
    uniqueness_score * 0.2 +          # 独特性
    copy_quality_score * 0.2 +        # 文案质量
    logic_consistency_score * 0.1     # 逻辑一致性
)
```

**验收标准：**
- [ ] 自动拒绝质量分 < 0.6 的模板
- [ ] 质量分 0.6-0.8 需要人工审核
- [ ] 质量分 > 0.8 可自动通过
- [ ] 显示详细的质量报告

---

### 4. 模板管理

**4.1 状态管理**

```python
class TemplateStatus(Enum):
    DRAFT = "draft"              # 草稿（AI刚生成）
    PENDING_REVIEW = "pending"   # 待审核
    APPROVED = "approved"        # 已批准
    ACTIVE = "active"            # 激活中（用于策展）
    PAUSED = "paused"            # 暂停
    ARCHIVED = "archived"        # 归档
```

**4.2 版本管理**

```python
class TemplateVersion:
    template_id: str
    version: int
    created_by: str  # "ai" or "human"
    changes: Dict[str, Any]
    performance_metrics: Dict[str, float]
```

**验收标准：**
- [ ] 支持模板的完整生命周期管理
- [ ] 支持版本回滚
- [ ] 记录所有修改历史
- [ ] 支持 A/B 测试不同版本

---

## �� 技术需求

### 1. AI 模型选择

**推荐方案：**
- 使用 GPT-4 或 Claude 3.5 Sonnet
- 需要强大的推理和结构化输出能力
- 支持 Function Calling / Structured Output

**Prompt 设计：**
```python
SYSTEM_PROMPT = \"\"\"
你是一位资深的产品策展专家，拥有 10 年的 SaaS 产品分析和市场研究经验。

你的专长：
1. 深刻理解产品设计、商业模式、市场定位
2. 能从数据中发现有价值的模式和洞察
3. 擅长为不同用户画像推荐合适的产品方向
4. 精通创业公司的增长策略和变现路径

你的任务：
根据用户提供的观察维度和指引，生成结构化的策展模板。

可用的数据维度：
- 母题判断：{MOTHER_THEMES}
- 产品字段：{EVIDENCE_FIELDS}
- 行业知识：{INDUSTRY_KNOWLEDGE}

输出要求：
1. filter_rules 必须基于可用字段
2. 标题要吸引人、有洞察
3. 描述要简洁、说明价值
4. 洞察要一针见血、点透本质
5. 规则要逻辑自洽、可执行
\"\"\"
```

**验收标准：**
- [ ] AI 输出符合 JSON Schema
- [ ] 推理过程可追溯
- [ ] 支持多轮对话优化
- [ ] 成本控制在合理范围

---

### 2. 数据库设计

**新增表：**

```sql
-- AI 生成的模板
CREATE TABLE ai_generated_templates (
    id SERIAL PRIMARY KEY,
    template_key VARCHAR(100) UNIQUE NOT NULL,
    
    -- 基本信息
    title_zh VARCHAR(200),
    title_en VARCHAR(200),
    description_zh TEXT,
    description_en TEXT,
    insight_zh VARCHAR(200),
    insight_en VARCHAR(200),
    tag_zh VARCHAR(50),
    tag_en VARCHAR(50),
    tag_color VARCHAR(20),
    curation_type VARCHAR(20),
    
    -- 筛选规则
    filter_rules JSONB NOT NULL,
    conflict_dimensions TEXT[],
    
    -- 生成信息
    generation_prompt TEXT,
    generation_reasoning TEXT,
    created_by VARCHAR(20) DEFAULT 'ai',
    
    -- 状态管理
    status VARCHAR(20) DEFAULT 'pending',
    quality_score FLOAT,
    validation_report JSONB,
    
    -- 性能指标
    matched_product_count INT,
    avg_revenue FLOAT,
    click_count INT DEFAULT 0,
    view_count INT DEFAULT 0,
    share_count INT DEFAULT 0,
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT NOW(),
    approved_at TIMESTAMP,
    activated_at TIMESTAMP,
    
    -- 优先级
    priority INT DEFAULT 5,
    min_products INT DEFAULT 3,
    max_products INT DEFAULT 8
);
```

**Prompt 设计示例**

验收标准：
- [ ] AI 输出符合 JSON Schema
- [ ] 推理过程可追溯
- [ ] 支持多轮对话优化
- [ ] 成本控制在合理范围

---

### 2. 数据库设计

新增表：ai_generated_templates

包含字段：
- id, template_key (唯一)
- title_zh, title_en, description_zh, description_en
- insight_zh, insight_en, tag_zh, tag_en, tag_color
- curation_type, filter_rules (JSONB), conflict_dimensions
- generation_prompt, generation_reasoning, created_by
- status, quality_score, validation_report (JSONB)
- matched_product_count, avg_revenue
- click_count, view_count, share_count
- created_at, approved_at, activated_at
- priority, min_products, max_products

新增表：template_versions

包含字段：
- id, template_id, version, changes (JSONB)
- created_by, created_at, performance_metrics (JSONB)

新增表：template_reviews

包含字段：
- id, template_id, reviewer_id
- action (approve/reject/request_changes)
- comments, created_at

---

## 📊 验收标准总结

### 功能完整性
- [ ] 支持自然语言生成模板
- [ ] 支持结构化输入生成模板
- [ ] 支持示例驱动生成模板
- [ ] 支持批量生成
- [ ] 支持预览和验证
- [ ] 支持人工审核和编辑
- [ ] 支持模板激活/暂停/归档

### AI 能力
- [ ] 理解用户画像和技术特征的映射
- [ ] 理解商业逻辑和市场规律
- [ ] 生成的规则逻辑自洽
- [ ] 生成的文案专业有洞察
- [ ] 推理过程可解释

### 质量保证
- [ ] 自动验证产品匹配度
- [ ] 自动评估模板质量
- [ ] 支持 A/B 测试
- [ ] 记录性能指标
- [ ] 支持持续优化

### 性能要求
- [ ] 单个模板生成时间 < 10 秒
- [ ] 批量生成 10 个模板 < 60 秒
- [ ] 支持并发生成
- [ ] API 响应时间 < 2 秒

---

## 🚀 实施建议

**Phase 1: MVP（Week 1-2）**
- 实现基础的自然语言生成
- 支持单个模板生成和预览
- 人工审核流程

**Phase 2: 增强（Week 3-4）**
- 添加知识库
- 支持批量生成
- 自动质量评分

**Phase 3: 优化（Week 5-6）**
- 数据驱动优化
- A/B 测试
- 持续学习
