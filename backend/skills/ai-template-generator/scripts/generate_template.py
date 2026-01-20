#!/usr/bin/env python3
"""
AI Template Generator Script (Standalone Version)

Generates CurationTemplate objects using AI based on observation dimensions and guidance.
This version is completely independent and uses HTTP APIs instead of direct imports.
"""

import os
import sys
import json
import argparse
import asyncio
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from backend/.env
script_dir = Path(__file__).parent
skill_dir = script_dir.parent
backend_dir = skill_dir.parent.parent
env_path = backend_dir / ".env"
load_dotenv(env_path)

# Import local clients (within skill scope)
from openai_client import OpenAIClient
from api_client import BackendAPIClient


# AI Prompt for template generation
TEMPLATE_GENERATION_PROMPT = """你是一位资深的产品策展专家，深刻理解产品设计、市场商业逻辑和用户心理。同时你也是一位优秀的文案撰写者，擅长创作吸睛、犀利、有趣的内容。

## 任务
基于以下观察维度和指引，生成 {count} 个结构化的策展模板（CurationTemplate）。

## 观察维度
{observation}

## 指引
{guidance}

## 数据库统计信息
{db_stats}

## 文案撰写要求（重要！）

### Title（标题）- 卡片顶部，最醒目
**字数限制**：中文 6-12 字，英文 3-6 words
**风格要求**：
- ✅ 简洁有力，制造反差或悬念
- ✅ 使用具体数字增强冲击力（如"月入5万"）
- ✅ 避免术语，接地气
- ❌ 不要平铺直叙或过长

**案例**：
- ❌ 差：垂直市场的B2B SMB产品
- ✅ 好：小众垂直，月入5万
- ❌ 差：简单功能但是盈利的产品  
- ✅ 好：功能极简，收入惊人

### Description（描述）- 标题下方，2行截断
**字数限制**：中文 30-60 字，英文 20-40 words
**风格要求**：
- ✅ 第一句用具体数字说明筛选标准
- ✅ 第二句说明核心价值或反差点
- ✅ 语言通顺，易于理解
- ❌ 不要堆砌技术术语

**案例**：
- ❌ 差：筛选market_scope=vertical、target_customer=b2b_smb...
- ✅ 好：月收入5000+美元，创始人粉丝不到1000，专注垂直细分市场的B2B产品。打破"小众=低收入"的刻板印象。

### Insight（洞察）- 底部高亮区域，像金句
**字数限制**：中文 15-30 字，英文 10-20 words
**风格要求**：
- ✅ 简短有力，一句话说清
- ✅ 可执行，给出明确方向
- ✅ 像金句一样易于传播
- ❌ 不要空洞或鸡汤

**案例**：
- ❌ 差：垂直市场虽小，但聚焦精准痛点可实现高收入，无需大量粉丝支持。
- ✅ 好：小众不等于低收入，精准痛点胜过万千粉丝
- ❌ 差：聚焦核心价值而非功能堆砌，精准解决单一痛点往往比大而全更有效。
- ✅ 好：做好一件事，胜过做十件平庸事

## 模板类型说明

### 1. 反差型 (contrast)
- 打破常规认知，创造"啊哈"时刻
- 高优先级 (8-10)
- 明确的冲突维度（2个以上）
- 反直觉的洞察
- 示例："粉丝不多，也能做到 $10k+ MRR"

### 2. 认知型 (cognitive)
- 提供新视角，转变心智模型
- 中高优先级 (6-8)
- 聚焦定位、定价或市场洞察
- 教育价值
- 示例："用定价做差异化的产品"

### 3. 行动型 (action)
- 指导具体行动，降低决策瘫痪
- 高优先级 (7-9)
- 可执行的标准（低门槛、清晰MVP）
- 风险降低导向
- 示例:"周末可启动的项目"

### 4. 利基型 (niche)
- 服务特定人群或市场
- 较低优先级 (3-5)
- 针对特定角色或平台
- 需要专业知识
- 示例:"做自己也愿意付费的开发者工具"

## 筛选规则语法

### startup 表字段
```python
"startup": {{
    "revenue_30d": {{"min": 5000, "max": 50000}},
    "founder_followers": {{"max": 1000}},
    "team_size": {{"max": 2}},
    "category": {{"contains": ["developer", "api"]}}
}}
```

### selection 表字段
```python
"selection": {{
    "growth_driver": ["product_driven"],
    "feature_complexity": ["simple", "moderate"],
    "startup_cost_level": ["low"],
    "ai_dependency_level": ["none", "light"],
    "target_customer": ["b2b_smb"],
    "market_scope": ["vertical"]
}}
```

### mother_theme 表字段
```python
"mother_theme": {{
    "success_driver": ["产品驱动"],
    "demand_type": ["主动搜索型"],
    "entry_barrier": ["低门槛快启动"],
    "mvp_clarity": ["清晰可执行"],
    "solo_feasibility": ["非常适合"],
    "primary_risk": {{"not": ["变现转化"]}}
}}
```

### landing_page 表字段
```python
"landing_page": {{
    "feature_count": {{"max": 5}},
    "has_instant_value_demo": true,
    "conversion_friendliness_score": {{"min": 7.0}}
}}
```


## 输出格式

请以 Python 代码格式输出，每个模板使用 CurationTemplate 构造：

```python
CurationTemplate(
    key="template_key_in_snake_case",
    title_zh="中文标题（8-15字）",
    title_en="English Title (3-8 words)",
    description_zh="中文描述，说明筛选逻辑和价值",
    description_en="English description explaining filter logic and value.",
    insight_zh="中文洞察（可执行的要点）",
    insight_en="English insight (actionable takeaway).",
    tag_zh="标签",
    tag_en="Tag",
    tag_color="tailwind_color",  # amber/emerald/blue/purple/slate/teal/orange/green/indigo/cyan
    curation_type="contrast",  # contrast/cognitive/action/niche
    filter_rules={{
        "startup": {{
            "revenue_30d": {{"min": 5000}}
        }},
        "selection": {{
            "feature_complexity": ["simple"]
        }},
        "mother_theme": {{
            "mvp_clarity": ["清晰可执行"]
        }}
    }},
    conflict_dimensions=["field1", "field2"],  # 产生反差的维度
    min_products=3,
    max_products=8,
    priority=8  # 1-10，数字越大优先级越高
),
```

## 质量标准

好的模板应该：
- ✅ 提供独特洞察，不是数据的简单呈现
- ✅ 匹配 5-15 个产品（不太窄，不太宽）
- ✅ 有清晰、吸引人的双语标题和洞察
- ✅ 筛选规则与主题一致
- ✅ 为特定用户角色或用例创造价值

避免的模板：
- ❌ 与现有模板过于相似
- ❌ 匹配太少（<3）或太多（>30）产品
- ❌ 洞察模糊或泛泛而谈
- ❌ 筛选规则组合缺乏明确理由
- ❌ 双语质量差或机翻感强

请只输出 Python 代码，不要包含其他解释。
"""


async def generate_templates(
    observation: str,
    guidance: str,
    count: int = 3,
    model: str = "gpt-4o",
    api_url: str = "http://localhost:8001"
) -> str:
    """使用AI生成模板"""
    
    # Get database statistics from backend API
    async with BackendAPIClient(base_url=api_url) as api:
        db_stats = await api.get_db_stats()
    
    # Format statistics
    stats_text = json.dumps(db_stats, indent=2, ensure_ascii=False)
    
    # Build prompt
    prompt = TEMPLATE_GENERATION_PROMPT.format(
        count=count,
        observation=observation,
        guidance=guidance,
        db_stats=stats_text
    )
    
    # Call AI
    async with OpenAIClient(model=model) as ai:
        response = await ai.chat(
            messages=[
                {"role": "system", "content": "你是一位资深的产品策展专家，擅长发现产品模式并创建有价值的策展主题。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
    
    return response


def extract_python_code(response: str) -> str:
    """从AI响应中提取Python代码"""
    # Try to extract code block
    if "```python" in response:
        start = response.find("```python") + 9
        end = response.find("```", start)
        return response[start:end].strip()
    elif "```" in response:
        start = response.find("```") + 3
        end = response.find("```", start)
        return response[start:end].strip()
    
    # If no code block markers, return entire response
    return response.strip()


async def main():
    parser = argparse.ArgumentParser(description="Generate curation templates using AI")
    parser.add_argument("--observation", "-o", required=True, help="Observation dimensions")
    parser.add_argument("--guidance", "-g", required=True, help="Generation guidance")
    parser.add_argument("--count", "-c", type=int, default=3, help="Number of templates to generate")
    parser.add_argument("--model", "-m", help="AI model to use (default from env)")
    parser.add_argument("--output", "-f", help="Output file path (relative to skill/output/)")
    parser.add_argument("--api-url", default="http://localhost:8001", help="Backend API URL")
    
    args = parser.parse_args()
    
    # Use model from env if not specified
    model = args.model or os.getenv("OPENAI_MODEL", "gpt-4o")
    
    print(f"🤖 Generating {args.count} templates...")
    print(f"📊 Observation: {args.observation}")
    print(f"💡 Guidance: {args.guidance}")
    print(f"🔗 API URL: {args.api_url}")
    print()
    
    try:
        # Generate templates
        response = await generate_templates(
            observation=args.observation,
            guidance=args.guidance,
            count=args.count,
            model=model,
            api_url=args.api_url
        )
        
        # Extract code
        code = extract_python_code(response)
        
        # Determine output path
        if args.output:
            # Create output directory in skill folder
            output_dir = skill_dir / "output"
            output_dir.mkdir(exist_ok=True)
            
            # Use provided filename or generate one
            if args.output.endswith('.py'):
                output_filename = args.output
            else:
                output_filename = f"{args.output}.py"
            
            output_path = output_dir / output_filename
        else:
            # Generate default filename with timestamp
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = skill_dir / "output"
            output_dir.mkdir(exist_ok=True)
            output_path = output_dir / f"templates_{timestamp}.py"
        
        # Save to file
        output_path.write_text(code, encoding="utf-8")
        print(f"✅ Templates saved to: {output_path.relative_to(backend_dir)}")
        
        print()
        print("✨ Generation complete!")
        print()
        print("Next steps:")
        print(f"1. Review the generated templates: {output_path.relative_to(backend_dir)}")
        print(f"2. Validate with: python scripts/validate_template.py --template-file {output_path.relative_to(backend_dir)}")
        print("3. Preview matches with: python scripts/preview_template.py --template-key <key>")
        print("4. Add to backend/curation/daily_templates.py")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
