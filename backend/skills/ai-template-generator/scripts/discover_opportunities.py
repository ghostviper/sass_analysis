#!/usr/bin/env python3
"""
Opportunity Discovery Script (Enhanced v2)

AI analyzes product data with market-driven frameworks to discover valuable
curation opportunities. Applies Porter's Five Forces, Blue Ocean Strategy,
and business metrics frameworks.

This script uses the complete market analysis framework defined in:
  references/curation-logic-v2.md (~1000+ lines)

For basic curation principles, see:
  references/curation-logic-basic.md (~400 lines)
"""

import os
import sys
import json
import argparse
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Tuple
from dotenv import load_dotenv

# Load environment variables
script_dir = Path(__file__).parent
skill_dir = script_dir.parent
backend_dir = skill_dir.parent.parent
env_path = backend_dir / ".env"
load_dotenv(env_path)

# Import local clients
from openai_client import OpenAIClient
from api_client import BackendAPIClient


# Enhanced AI Prompt with market-driven frameworks
ENHANCED_OPPORTUNITY_DISCOVERY_PROMPT = """你是一位资深的产品策展专家，同时具备深厚的市场分析和商业洞察能力。

## 分析维度

### 1. 产品维度
- 产品类型、功能、技术特征
- 目标用户、使用场景
- 商业模式、成熟度

### 2. 市场维度（新增）
- **市场机会**：评估市场规模、识别市场空白
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
   - 示例：高收入 + 低粉丝 = 产品驱动的证明

2. **Cognitive（认知型）**：改变用户认知
   - 示例：挑战"必须有大量用户才能赚钱"的假设

3. **Action（行动型）**：激发具体行动
   - 示例：提供可立即应用的策略

4. **Niche（细分型）**：聚焦特定细分
   - 示例：针对特定行业的垂直工具

### 新增类型（市场驱动）
5. **Market-Gap（市场空白型）**：未被满足的需求
   - 应用 Blue Ocean Strategy 四行动框架
   - 识别"消除-减少-增加-创造"的机会
   - 示例："没有针对 X 行业的 Y 工具"

6. **Value-Arbitrage（价值套利型）**：高价值低价格
   - 应用 pricing-strategy 的价值感知理论
   - 找出价格与价值不匹配的机会
   - 示例："企业级功能，个人版价格"

7. **Competitive-Weakness（竞品弱点型）**：竞品短板
   - 应用 Porter's Five Forces 分析
   - 识别竞品的结构性弱点
   - 示例："Notion 太慢，我们更快"

8. **Metrics-Driven（指标驱动型）**：关键指标优化
   - 应用 startup-metrics-framework
   - 聚焦可量化的业务指标提升
   - 示例："提升 30% 转化率的工具"

9. **Channel-Innovation（渠道创新型）**：新分发渠道
   - 应用 launch-strategy 的 ORB 框架
   - 识别 Owned/Rented/Borrowed 渠道机会
   - 示例："通过 Chrome 扩展获客"

10. **Psychology-Leverage（心理杠杆型）**：认知偏差利用
    - 应用 marketing-psychology 的 mental models
    - 利用锚定、社交证明、稀缺性等心理效应
    - 示例："社交证明驱动的产品"

## 分析框架应用

### Porter's Five Forces
- **新进入者威胁**：进入壁垒高低
- **供应商议价能力**：依赖度分析
- **买家议价能力**：客户集中度
- **替代品威胁**：替代方案评估
- **行业竞争**：竞争强度判断

### Blue Ocean Strategy
- **消除**：哪些行业标配可以去掉？
- **减少**：哪些功能可以大幅简化？
- **增加**：哪些方面可以远超行业标准？
- **创造**：哪些全新价值可以创造？

### Value Theory
- **当前问题成本**：时间、金钱、效率损失
- **解决方案价值**：节省、收益、效率提升
- **支付意愿**：价值的 10-30%
- **定价策略**：锚定、对比、分层

### Business Metrics
- **SaaS**: MRR, CAC, LTV, NDR, Magic Number
- **Marketplace**: GMV, Take Rate, Liquidity
- **Consumer**: DAU/MAU, K-Factor, Retention

## 数据分析

### 数据库统计
{db_stats}

### 母题分布
{mother_theme_dist}

### 产品特征分布
{product_chars}

## 任务

发现 {count} 个高价值的策展机会，优先考虑市场驱动的新类型（5-10）。

## 输出格式

请以 JSON 格式输出，每个机会包含：

```json
[
  {{
    "opportunity_id": "unique_id_in_snake_case",
    "type": "contrast|cognitive|action|niche|market_gap|value_arbitrage|competitive_weakness|metrics_driven|channel_innovation|psychology_leverage",
    "priority": 8,
    "observation": "具体的产品特征组合描述",
    "guidance": "AI应该寻找什么模式/提取什么洞察",
    
    "market_insight": {{
      "market_size": "小/中/大",
      "competition": "低/中/高",
      "growth_potential": "低/中/高",
      "reasoning": "市场洞察的理由"
    }},
    
    "user_value": {{
      "pain_point": "核心痛点描述",
      "value_proposition": "价值主张",
      "roi_visibility": "低/中/高",
      "reasoning": "用户价值的理由"
    }},
    
    "business_logic": {{
      "unit_economics": "可行/存疑/不可行",
      "retention_expectation": "低/中/高",
      "pricing_strategy": "定价策略建议",
      "reasoning": "商业逻辑的理由"
    }},
    
    "frameworks_applied": [
      "framework_name: specific_application"
    ],
    
    "expected_product_count": "5-10",
    "target_persona": "solo_indie_hacker|first_time_founder|serial_entrepreneur|product_manager",
    "key_insight": "这个模式教给我们什么",
    "curation_value": "为什么这个角度有价值"
  }}
]
```

## 质量标准

好的机会发现：
- ✅ 具体：清晰、可衡量的标准
- ✅ 有价值：提供可执行的洞察
- ✅ 数据支撑：预计5-15个产品匹配
- ✅ 惊喜感：挑战假设或揭示隐藏模式
- ✅ 相关性：服务特定用户角色需求
- ✅ 市场洞察：包含市场分析和商业逻辑
- ✅ 框架应用：明确使用了哪些分析框架

避免的机会：
- ❌ 模糊："好的产品"
- ❌ 显而易见："赚钱的产品赚钱"
- ❌ 过窄：<3个产品
- ❌ 过宽：>30个产品
- ❌ 无关：没有明确用户价值
- ❌ 缺少市场视角：只关注产品特征

请只输出 JSON 数组，不要包含其他解释。
"""


async def discover_opportunities(
    count: int = 5,
    model: str = "gpt-4o",
    api_url: str = "http://localhost:8001",
    enhanced: bool = True
) -> List[Dict[str, Any]]:
    """发现策展机会（增强版）"""
    
    # Get data from backend API
    async with BackendAPIClient(base_url=api_url) as api:
        db_stats = await api.get_db_stats()
        mother_theme_dist = await api.get_mother_theme_distribution()
        product_chars = await api.get_product_characteristics()
    
    # Format data for prompt
    db_stats_text = json.dumps(db_stats, indent=2, ensure_ascii=False)
    mother_theme_text = json.dumps(mother_theme_dist, indent=2, ensure_ascii=False)
    product_chars_text = json.dumps(product_chars, indent=2, ensure_ascii=False)
    
    # Build prompt (use enhanced version)
    prompt = ENHANCED_OPPORTUNITY_DISCOVERY_PROMPT.format(
        count=count,
        db_stats=db_stats_text,
        mother_theme_dist=mother_theme_text,
        product_chars=product_chars_text
    )
    
    # Call AI
    async with OpenAIClient(model=model) as ai:
        response = await ai.chat(
            messages=[
                {"role": "system", "content": "你是一位资深的产品策展专家，同时具备深厚的市场分析和商业洞察能力。你擅长应用 Porter's Five Forces、Blue Ocean Strategy、Value Theory 等框架来发现有价值的策展角度。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8  # Higher temperature for more creative discovery
        )
    
    # Parse JSON response
    opportunities = parse_json_response(response)
    return opportunities


def parse_json_response(response: str) -> List[Dict[str, Any]]:
    """从AI响应中解析JSON"""
    try:
        # Try direct parse
        return json.loads(response)
    except json.JSONDecodeError:
        pass
    
    # Try to extract from code block
    try:
        if "```json" in response:
            start = response.find("```json") + 7
            end = response.find("```", start)
            json_str = response[start:end].strip()
            return json.loads(json_str)
        elif "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            json_str = response[start:end].strip()
            return json.loads(json_str)
    except (json.JSONDecodeError, ValueError):
        pass
    
    # Try to find JSON array in response
    try:
        start = response.find("[")
        end = response.rfind("]") + 1
        if start >= 0 and end > start:
            json_str = response[start:end]
            return json.loads(json_str)
    except (json.JSONDecodeError, ValueError):
        pass
    
    raise ValueError("Failed to parse JSON from AI response")



def format_opportunity_output(opportunities: List[Dict[str, Any]]) -> str:
    """格式化机会输出（增强版）"""
    output = []
    output.append("=" * 80)
    output.append(f"发现 {len(opportunities)} 个策展机会（增强版 v2）")
    output.append("=" * 80)
    output.append("")
    
    for i, opp in enumerate(opportunities, 1):
        output.append(f"## 机会 {i}: {opp.get('opportunity_id', 'unknown')}")
        output.append("")
        output.append(f"**类型**: {opp.get('type', 'unknown')}")
        output.append(f"**优先级**: {opp.get('priority', 5)}/10")
        output.append(f"**目标用户**: {opp.get('target_persona', 'unknown')}")
        output.append(f"**预计产品数**: {opp.get('expected_product_count', 'unknown')}")
        output.append("")
        
        # Market Insight (新增)
        if 'market_insight' in opp:
            mi = opp['market_insight']
            output.append(f"**市场洞察**:")
            output.append(f"  - 市场规模: {mi.get('market_size', 'unknown')}")
            output.append(f"  - 竞争强度: {mi.get('competition', 'unknown')}")
            output.append(f"  - 增长潜力: {mi.get('growth_potential', 'unknown')}")
            output.append(f"  - 理由: {mi.get('reasoning', '')}")
            output.append("")
        
        # User Value (新增)
        if 'user_value' in opp:
            uv = opp['user_value']
            output.append(f"**用户价值**:")
            output.append(f"  - 核心痛点: {uv.get('pain_point', '')}")
            output.append(f"  - 价值主张: {uv.get('value_proposition', '')}")
            output.append(f"  - ROI可见性: {uv.get('roi_visibility', 'unknown')}")
            output.append(f"  - 理由: {uv.get('reasoning', '')}")
            output.append("")
        
        # Business Logic (新增)
        if 'business_logic' in opp:
            bl = opp['business_logic']
            output.append(f"**商业逻辑**:")
            output.append(f"  - 单位经济: {bl.get('unit_economics', 'unknown')}")
            output.append(f"  - 留存预期: {bl.get('retention_expectation', 'unknown')}")
            output.append(f"  - 定价策略: {bl.get('pricing_strategy', '')}")
            output.append(f"  - 理由: {bl.get('reasoning', '')}")
            output.append("")
        
        # Frameworks Applied (新增)
        if 'frameworks_applied' in opp:
            output.append(f"**应用框架**:")
            for framework in opp['frameworks_applied']:
                output.append(f"  - {framework}")
            output.append("")
        
        output.append(f"**观察维度**:")
        output.append(f"```")
        output.append(opp.get('observation', ''))
        output.append(f"```")
        output.append("")
        output.append(f"**指引**:")
        output.append(f"```")
        output.append(opp.get('guidance', ''))
        output.append(f"```")
        output.append("")
        output.append(f"**核心洞察**: {opp.get('key_insight', '')}")
        output.append("")
        output.append(f"**策展价值**: {opp.get('curation_value', '')}")
        output.append("")
        output.append("-" * 80)
        output.append("")
    
    return "\n".join(output)


def analyze_opportunity_types(opportunities: List[Dict[str, Any]]) -> Dict[str, Any]:
    """分析机会类型分布"""
    type_counts = {}
    for opp in opportunities:
        opp_type = opp.get('type', 'unknown')
        type_counts[opp_type] = type_counts.get(opp_type, 0) + 1
    
    # Categorize into old vs new types
    old_types = ['contrast', 'cognitive', 'action', 'niche']
    new_types = ['market_gap', 'value_arbitrage', 'competitive_weakness', 
                 'metrics_driven', 'channel_innovation', 'psychology_leverage']
    
    old_count = sum(type_counts.get(t, 0) for t in old_types)
    new_count = sum(type_counts.get(t, 0) for t in new_types)
    
    return {
        'type_counts': type_counts,
        'old_types_count': old_count,
        'new_types_count': new_count,
        'total': len(opportunities)
    }


async def main():
    parser = argparse.ArgumentParser(description="Discover curation opportunities using AI (Enhanced v2)")
    parser.add_argument("--count", "-c", type=int, default=5, help="Number of opportunities to discover")
    parser.add_argument("--model", "-m", help="AI model to use (default from env)")
    parser.add_argument("--output", "-o", help="Output file path (JSON)")
    parser.add_argument("--api-url", default="http://localhost:8001", help="Backend API URL")
    
    args = parser.parse_args()
    
    # Use model from env if not specified
    model = args.model or os.getenv("OPENAI_MODEL", "gpt-4o")
    
    print(f"🔍 Discovering {args.count} curation opportunities (Enhanced v2)...")
    print(f"🤖 Using model: {model}")
    print(f"🔗 API URL: {args.api_url}")
    print(f"✨ New features:")
    print(f"   - 10 opportunity types (6 new market-driven types)")
    print(f"   - Market insight analysis")
    print(f"   - User value assessment")
    print(f"   - Business logic evaluation")
    print(f"   - Framework application tracking")
    print()
    
    try:
        # Discover opportunities
        opportunities = await discover_opportunities(
            count=args.count,
            model=model,
            api_url=args.api_url,
            enhanced=True
        )
        
        # Analyze types
        type_analysis = analyze_opportunity_types(opportunities)
        
        print(f"📊 Opportunity Type Distribution:")
        print(f"   Old types (1-4): {type_analysis['old_types_count']}")
        print(f"   New types (5-10): {type_analysis['new_types_count']}")
        print(f"   Details: {json.dumps(type_analysis['type_counts'], indent=2)}")
        print()
        
        # Format output
        formatted = format_opportunity_output(opportunities)
        print(formatted)
        
        # Determine output path
        if args.output:
            # Create output directory in skill folder
            output_dir = skill_dir / "output"
            output_dir.mkdir(exist_ok=True)
            
            # Use provided filename or generate one
            if args.output.endswith('.json'):
                output_filename = args.output
            else:
                output_filename = f"{args.output}.json"
            
            output_path = output_dir / output_filename
        else:
            # Generate default filename with timestamp
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = skill_dir / "output"
            output_dir.mkdir(exist_ok=True)
            output_path = output_dir / f"opportunities_{timestamp}.json"
        
        # Save JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(opportunities, f, indent=2, ensure_ascii=False)
        
        # Also save formatted text
        text_path = output_path.with_suffix('.txt')
        text_path.write_text(formatted, encoding='utf-8')
        
        # Save analysis
        analysis_path = output_path.with_name(output_path.stem + '_analysis.json')
        with open(analysis_path, 'w', encoding='utf-8') as f:
            json.dump(type_analysis, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Opportunities saved to:")
        print(f"   JSON: {output_path.relative_to(backend_dir)}")
        print(f"   Text: {text_path.relative_to(backend_dir)}")
        print(f"   Analysis: {analysis_path.relative_to(backend_dir)}")
        
        print()
        print("✨ Discovery complete!")
        print()
        print("Next steps:")
        print("1. Review the discovered opportunities")
        print("2. Note the market insights and business logic")
        print("3. Select interesting ones to generate templates:")
        print("   python scripts/generate_template.py \\")
        print("     --observation \"<observation>\" \\")
        print("     --guidance \"<guidance>\" \\")
        print("     --count 2")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
