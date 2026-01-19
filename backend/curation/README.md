# Curation 策展系统模块

基于母题判断的 SaaS 产品策展系统，用于 BuildWhat 发现页内容生成。

## 模块结构

```
curation/
├── __init__.py      # 模块入口
├── config.py        # 母题定义、证据字段配置
├── schemas.py       # 数据结构定义
├── evidence.py      # 证据数据构建
├── prompts.py       # Prompt 模板
├── validators.py    # 验证逻辑、一致性检查
├── judge.py         # MotherThemeJudge 核心类
├── curator.py       # 策展 Agent、角色配置
└── cli.py           # 命令行工具
```

## 快速开始

```bash
cd backend

# 1. 运行母题判断
.\venv\Scripts\python.exe -m curation.cli judge --limit 10

# 2. 基于判断结果生成专题
.\venv\Scripts\python.exe -m curation.cli curate
```

## 命令行参数

### judge 命令（母题判断）
```bash
.\venv\Scripts\python.exe -m curation.cli judge [OPTIONS]

--limit N          处理产品数量，默认 10
--all              处理所有产品（忽略 limit）
--delay N          请求间隔秒数，默认 2.0
--min-revenue N    最小收入过滤
--fallback         启用回退机制（单个判断失败时重试）
```

### curate 命令（专题生成）
```bash
.\venv\Scripts\python.exe -m curation.cli curate [OPTIONS]

--min-products N   专题最小产品数，默认 3
--max-products N   专题最大产品数，默认 10
```

## 输出文件

- `backend/data/mother_theme_test_results.json` - 母题判断结果
- `backend/data/generated_topics.json` - 生成的专题

## 母题框架（9个，三层架构）

### 筛选层（2个）
- `opportunity_validity` - 机会真实性
- `demand_type` - 需求类型

### 行动层（4个）
- `solo_feasibility` - 独立可行性
- `entry_barrier` - 入场门槛
- `primary_risk` - 主要风险
- `mvp_clarity` - MVP清晰度

### 归因层（3个）
- `success_driver` - 成功驱动因素
- `positioning_insight` - 定位洞察
- `differentiation_point` - 差异化点

## 代码使用示例

```python
from curation import MotherThemeJudge, CuratorAgent, MOTHER_THEMES
from services.openai_service import OpenAIService

# 母题判断
async with OpenAIService() as openai:
    judge = MotherThemeJudge(openai)
    results = await judge.judge_all_themes(startup, analysis)

# 专题生成
curator = CuratorAgent()
topics = curator.generate(products_with_judgments)
```
