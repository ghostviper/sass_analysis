# Agent 架构分析：MCP Tools vs Skills vs Agents

> 基于 Claude Agent SDK 文档和 claude-cookbooks 最佳实践的分析报告
> 
> 创建日期：2026-01-14

## 目录

1. [三者的本质区别](#1-三者的本质区别)
2. [何时使用什么](#2-何时使用什么)
3. [当前架构评估](#3-当前架构评估)
4. [优化建议](#4-优化建议)
5. [架构最佳实践](#5-架构最佳实践)
6. [未来扩展方向](#6-未来扩展方向)

---

## 1. 三者的本质区别

| 维度 | MCP Tools | Skills | Agents (Subagents) |
|------|-----------|--------|-------------------|
| **本质** | 能力扩展 | 知识注入 | 任务委托 |
| **类比** | 工具箱里的工具 | 专家的知识库 | 团队里的专家 |
| **触发方式** | 显式调用 | 自动加载/按需激活 | Task 工具委托 |
| **执行上下文** | 主 Agent 内 | 主 Agent 内 | 独立上下文 |
| **状态** | 无状态 | 无状态 | 有独立对话历史 |

### 简单理解

- **MCP Tools** = 你能做什么（能力）
- **Skills** = 你知道什么（知识）
- **Agents** = 谁来做（分工）

---

## 2. 何时使用什么

### 2.1 MCP Tools（能力层）

```
✅ 适合场景：
- 数据查询和检索（get_startups_by_ids, search_startups）
- 外部 API 调用（web_search）
- 结构化数据操作（get_category_analysis）
- 需要精确参数的操作

❌ 不适合：
- 复杂的多步骤推理
- 需要专业领域知识的分析
- 需要独立上下文的复杂任务
```

**设计原则**：
- 单一职责，做一件事做好
- 无业务逻辑，只负责数据获取
- 参数明确，返回结构化数据

### 2.2 Skills（知识层）

```
✅ 适合场景：
- 领域专业知识（market-signals 的反直觉信号识别）
- 行为指导（indie-dev-advisor 的用户引导）
- 分析框架和方法论
- 输出格式和风格指南

❌ 不适合：
- 需要调用外部工具的操作
- 需要独立执行的复杂任务
- 需要多轮对话的深度分析
```

**设计原则**：
- 提供知识，不执行操作
- 每个 Skill 保持 < 5000 tokens
- 可被主 Agent 和 Subagents 共同使用

### 2.3 Agents/Subagents（执行层）

```
✅ 适合场景：
- 复杂的多步骤任务（product-researcher 的数据收集）
- 需要专业分析的任务（comparison-analyst 的对比分析）
- 需要独立上下文的任务（避免污染主对话）
- 可并行执行的任务

❌ 不适合：
- 简单的数据查询
- 快速响应的场景（有额外开销）
- 需要与用户实时交互的场景
```

**设计原则**：
- 有明确的专业分工
- 可以调用 MCP Tools
- 可以使用 Skills 的知识
- 有独立上下文，不污染主对话

---

## 3. 当前架构评估

### 3.1 架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    CLAUDE.md (主指令)                        │
│  - 核心理念、输出规范、保密规则                               │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│  MCP Tools    │    │    Skills     │    │   Subagents   │
│ (8个工具)     │    │ (2个技能)     │    │ (3个子代理)   │
├───────────────┤    ├───────────────┤    ├───────────────┤
│ get_startups  │    │ indie-dev-    │    │ product-      │
│ search_startups│   │   advisor     │    │   researcher  │
│ browse_startups│   │ market-       │    │ comparison-   │
│ get_category  │    │   signals     │    │   analyst     │
│ get_trend     │    └───────────────┘    │ opportunity-  │
│ get_leaderboard│                        │   scout       │
│ get_founder   │                         └───────────────┘
│ web_search    │
└───────────────┘
```

### 3.2 评估结果

**✅ 架构设计合理！** 分层正确：

| 组件 | 职责 | 评估 |
|------|------|------|
| MCP Tools | 数据获取 | ✅ 原子化设计，职责清晰 |
| Skills | 知识增强 | ✅ 提供指导而非执行 |
| Subagents | 复杂任务 | ✅ 专业分工明确 |
| CLAUDE.md | 总协调 | ✅ 定义委托决策树 |

### 3.3 当前组件清单

**MCP Tools (8个)**
| 工具名 | 用途 |
|--------|------|
| `get_startups_by_ids` | 通过 ID 精确查询产品 |
| `search_startups` | 通过关键词搜索产品 |
| `browse_startups` | 浏览筛选产品 |
| `get_category_analysis` | 赛道分析 |
| `get_trend_report` | 趋势报告 |
| `get_leaderboard` | 创始人排行榜 |
| `get_founder_products` | 开发者产品组合 |
| `web_search` | 联网搜索 |

**Skills (2个)**
| 技能名 | 用途 |
|--------|------|
| `indie-dev-advisor` | 帮助迷茫用户找方向 |
| `market-signals` | 识别反直觉市场信号 |

**Subagents (3个)**
| 子代理 | 用途 | 可用工具 |
|--------|------|----------|
| `product-researcher` | 数据收集 | get_startups_by_ids, search_startups, get_category_analysis |
| `comparison-analyst` | 产品对比 | get_startups_by_ids, search_startups, get_category_analysis |
| `opportunity-scout` | 机会发现 | browse_startups, get_category_analysis, get_trend_report |

---

## 4. 优化建议

### 4.1 委托决策树优化

```
用户问题
    │
    ├─ 简单查询 ("X 的收入是多少?")
    │   └─ 直接用 MCP Tools
    │
    ├─ 需要专业知识 ("这个市场有什么反直觉信号?")
    │   └─ 激活 market-signals Skill + MCP Tools
    │
    ├─ 用户迷茫 ("我不知道做什么")
    │   └─ 激活 indie-dev-advisor Skill
    │
    ├─ 复杂分析 ("对比 A 和 B")
    │   └─ 委托给 @comparison-analyst
    │
    └─ 机会发现 ("有什么蓝海机会?")
        └─ 委托给 @opportunity-scout
```

### 4.2 建议新增的 Skills

```markdown
1. pricing-strategy/SKILL.md
   - SaaS 定价模型知识
   - 价格弹性分析框架
   - 竞品定价对比方法

2. tech-stack-advisor/SKILL.md  
   - 不同产品类型的技术栈推荐
   - 复杂度评估标准
   - MVP 技术选型指南

3. growth-patterns/SKILL.md
   - 增长曲线分析
   - 用户获取渠道评估
   - 留存率基准数据
```

### 4.3 Skills 与 Subagents 协作

Skills 可以被 Subagents 使用。可以在 Subagent 的 `.md` 文件中引用 Skills：

```markdown
# 示例：opportunity-scout.md 中添加

## Available Skills
When analyzing opportunities, leverage these skills:
- **market-signals**: Use to identify counter-intuitive patterns
- **indie-dev-advisor**: Use to assess developer fit
```

---

## 5. 架构最佳实践

### 5.1 设计原则总结

```
┌─────────────────────────────────────────────────────────────┐
│                     设计原则                                 │
├─────────────────────────────────────────────────────────────┤
│ 1. MCP Tools = 原子操作                                      │
│    - 单一职责，做一件事做好                                   │
│    - 无业务逻辑，只负责数据获取                               │
│                                                             │
│ 2. Skills = 知识增强                                         │
│    - 领域专业知识                                            │
│    - 分析框架和方法论                                        │
│    - 不调用工具，只提供指导                                   │
│                                                             │
│ 3. Subagents = 任务专家                                      │
│    - 复杂多步骤任务                                          │
│    - 可以调用 MCP Tools                                      │
│    - 可以使用 Skills 的知识                                  │
│    - 有独立上下文，不污染主对话                               │
│                                                             │
│ 4. CLAUDE.md = 总指挥                                        │
│    - 定义何时用什么                                          │
│    - 协调 Tools、Skills、Subagents                           │
│    - 保持输出一致性                                          │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 文件结构规范

```
backend/agent/.claude/
├── CLAUDE.md              # 主指令文件
├── settings.json          # 权限配置
├── agents/                # 子代理定义
│   ├── product-researcher.md
│   ├── comparison-analyst.md
│   └── opportunity-scout.md
└── skills/                # 技能定义
    ├── indie-dev-advisor/
    │   └── SKILL.md
    └── market-signals/
        └── SKILL.md
```

### 5.3 Skill 文件模板

```markdown
---
name: skill-name
description: 简短描述，说明何时使用这个 Skill
---

# Skill 标题

## When to Use
触发条件列表

## Knowledge/Framework
核心知识或分析框架

## Output Format
输出格式指南

## Examples
示例响应
```

### 5.4 Subagent 文件模板

```markdown
---
name: agent-name
description: 简短描述
tools: mcp__saas__tool1, mcp__saas__tool2
---

# Agent 角色描述

## Core Principle
核心原则

## Tool Selection
工具选择指南

## Output Format
输出格式

## Language
语言匹配规则
```

---

## 6. 未来扩展方向

### 6.1 短期优化

- [ ] 添加更多领域 Skills（定价、增长、技术栈）
- [ ] 让 Subagents 显式引用 Skills
- [ ] 优化委托决策树

### 6.2 中期扩展

- [ ] 添加 Evaluator-Optimizer 模式
  - 创建 `@quality-reviewer` subagent
  - 在复杂分析后自动评估输出质量

- [ ] 添加更多 Subagents
  - `@trend-analyst` - 趋势分析专家
  - `@founder-profiler` - 创始人画像分析

### 6.3 长期考虑

- [ ] 考虑 Skills API（如果需要动态加载）
  - 目前使用文件系统 Skills
  - 如果需要动态管理，可以用 Anthropic Skills API

- [ ] 多 Agent 并行执行
  - 复杂任务拆分给多个 Subagents 并行处理
  - 结果聚合和冲突解决

---

## 参考资料

- [Claude Agent SDK 文档](https://github.com/anthropics/claude-agent-sdk-python)
- [Claude Cookbooks - Agent Patterns](https://github.com/anthropics/claude-cookbooks/tree/main/patterns/agents)
- [Claude Cookbooks - Skills](https://github.com/anthropics/claude-cookbooks/tree/main/skills)

---

> 💡 **关键洞察**：你当前的架构已经很好地遵循了最佳实践。主要的优化空间在于添加更多领域 Skills 来增强知识，以及让 Subagents 显式引用 Skills 来协作。
