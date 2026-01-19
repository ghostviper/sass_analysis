"""
Prompt 模板

包含母题判断所需的 System Prompt 和 User Prompt 模板。
"""

from typing import Any, Dict, List
from .config import EVIDENCE_FIELDS, MOTHER_THEMES


# =============================================================================
# System Prompt
# =============================================================================

MOTHER_THEME_SYSTEM_PROMPT = """你是一位资深SaaS产品分析师。

判断风格：务实、重证据、不被营销话术迷惑。
输出格式：仅输出 JSON，不要任何解释文字。"""


# =============================================================================
# Prompt 构建函数
# =============================================================================

def build_one_shot_prompt(context: str, themes: List[Dict[str, Any]]) -> str:
    """构建结构化的 one-shot prompt，支持三层架构"""

    # 按层级组织母题
    screening = [t for t in themes if t.get("layer") == "screening"]
    action = [t for t in themes if t.get("layer") == "action"]
    attribution = [t for t in themes if t.get("layer") == "attribution"]

    def format_theme_block(theme_list: List[Dict[str, Any]], layer_name: str) -> str:
        lines = [f"\n### {layer_name}"]
        for t in theme_list:
            options_str = " / ".join(f'"{opt}"' for opt in t.get("options", []))
            hint_first_line = t.get("hint", "").split("\n")[0]
            lines.append(
                f"  {t['key']} ({t['name']}):\n"
                f"    选项: {options_str}\n"
                f"    提示: {hint_first_line}"
            )
        return "\n".join(lines)

    themes_block = (
        format_theme_block(screening, "筛选层 - 值不值得研究？") +
        format_theme_block(action, "行动层 - 能不能做？怎么做？") +
        format_theme_block(attribution, "归因层 - 为什么成功？可学什么？")
    )

    valid_fields = ", ".join(EVIDENCE_FIELDS)
    theme_keys = [t["key"] for t in themes]
    example_output = ",\n    ".join(f'"{k}": {{ ... }}' for k in theme_keys)

    return f"""## 产品数据（以下字段可作为 evidence_fields 引用）
{context}

## 任务
对以上产品完成 {len(themes)} 个母题判断，分三个层级：
- 筛选层（2个）：判断这个方向值不值得研究
- 行动层（4个）：判断如果要做，可行性和风险
- 归因层（3个）：分析成功因素和可借鉴点

## 母题定义（judgment 必须完整匹配选项）
{themes_block}

## 输出格式
```json
{{
  "judgments": {{
    {example_output}
  }}
}}
```

每个母题的结构：
```json
{{
  "judgment": "选项之一",
  "confidence": "高/中/低",
  "reasons": ["理由1", "理由2"],
  "evidence_fields": ["字段1", "字段2"],
  "uncertainties": []
}}
```

## 严格约束（违反会导致解析失败）

1. evidence_fields 只能使用「产品数据」中的字段名：
   {valid_fields}

   ❌ 错误示例: "evidence_fields": ["demand_type", "opportunity_validity"]
      （这些是母题名，不是字段名！）
   ✅ 正确示例: "evidence_fields": ["pain_points", "revenue_30d", "target_audience"]

2. uncertainties 必须是数组，不能是 null：
   ❌ 错误: "uncertainties": null
   ✅ 正确: "uncertainties": []  或  "uncertainties": ["某个不确定因素"]

3. judgment 必须完整匹配选项，例如：
   ✅ 正确: "证据不足/无法判断"
   ❌ 错误: "证据不足"

4. confidence: 只能是 "高"、"中"、"低"

5. reasons: 1-3 条，每条简洁有力

仅输出 JSON。"""



def build_single_theme_prompt(context: str, theme: Dict[str, Any]) -> str:
    """构建单母题判断 Prompt"""
    options_list = theme.get("options", [])
    options_str = " / ".join(f'"{opt}"' for opt in options_list)
    hint = theme.get("hint", "")
    layer = theme.get("layer", "")
    layer_desc = {
        "screening": "筛选层 - 判断这个方向值不值得研究",
        "action": "行动层 - 判断如果要做的可行性",
        "attribution": "归因层 - 分析成功因素和可借鉴点",
    }.get(layer, "")
    valid_fields = ", ".join(EVIDENCE_FIELDS)

    return f"""## 产品数据（以下字段可作为 evidence_fields 引用）
{context}

## 任务
完成单个母题判断：{theme['name']} ({theme['key']})
所属层级：{layer_desc}

## 选项（judgment 必须完整匹配）
{options_str}

## 判断规则
{hint}

## 输出格式
```json
{{
  "judgment": "选项之一",
  "confidence": "高/中/低",
  "reasons": ["理由1", "理由2"],
  "evidence_fields": ["字段1", "字段2"],
  "uncertainties": []
}}
```

## 严格约束（违反会导致解析失败）

1. evidence_fields 只能使用「产品数据」中的字段名：
   {valid_fields}
   ❌ 母题名不是字段名！

2. uncertainties 必须是数组，不能是 null：
   ❌ 错误: "uncertainties": null
   ✅ 正确: "uncertainties": []

3. judgment 必须完整匹配选项

4. confidence: 只能是 "高"、"中"、"低"

5. reasons: 1-3 条

仅输出 JSON。"""
