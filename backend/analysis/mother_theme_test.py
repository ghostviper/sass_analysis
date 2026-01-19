"""
母题判断测试脚本

用讨论稿中的判断母题对落地页分析结果做批量验证，
产出可用于后续多角色策展的判断矩阵。

使用方法：
    cd backend
    python -m analysis.mother_theme_test

输出：
    backend/data/mother_theme_test_results.json
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from database.db import get_db_session
from database.models import LandingPageAnalysis, Startup, ProductSelectionAnalysis, CategoryAnalysis
from services.openai_service import OpenAIService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OUTPUT_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR.mkdir(exist_ok=True)

# =============================================================================
# 配置
# =============================================================================

PROMPT_VERSION = "v4.2"  # 强化 uncertainties 和 evidence_fields 约束
ONE_SHOT_MODE = True
CONFIDENCE_CHOICES = ["高", "中", "低"]
FALLBACK_ON_INVALID = False
ENFORCE_CONSISTENCY = True

REQUIRED_FIELDS = ["judgment", "confidence", "reasons", "evidence_fields", "uncertainties"]

# =============================================================================
# 证据字段定义
# =============================================================================

# LandingPageAnalysis 字段
LANDING_PAGE_FIELDS = [
    "headline_text", "tagline_text", "core_features", "feature_count",
    "value_propositions", "target_audience", "pain_points", "use_cases",
    "pricing_model", "pricing_tiers", "has_free_tier", "has_trial",
    "cta_count", "cta_texts", "conversion_funnel_steps",
    "has_instant_value_demo", "conversion_friendliness_score",
    "potential_moats", "uses_before_after", "uses_emotional_words",
    "positioning_clarity_score", "replication_difficulty_score",
    "individual_replicability_score", "pain_point_sharpness",
]

# ProductSelectionAnalysis 字段
SELECTION_ANALYSIS_FIELDS = [
    "growth_driver", "is_product_driven", "ip_dependency_score",
    "follower_revenue_ratio", "tech_complexity_level", "feature_complexity",
    "ai_dependency_level", "startup_cost_level", "market_scope",
    "target_customer", "requires_realtime", "requires_large_data",
    "requires_compliance",
]

# Startup 基础字段
STARTUP_FIELDS = [
    "revenue_30d", "category", "description", "founder_followers", "team_size",
]

# CategoryAnalysis 字段
CATEGORY_FIELDS = ["market_type"]

# 合并所有证据字段
EVIDENCE_FIELDS = LANDING_PAGE_FIELDS + SELECTION_ANALYSIS_FIELDS + STARTUP_FIELDS + CATEGORY_FIELDS

# 特定母题的证据字段约束（用于验证）
PRICING_EVIDENCE_FIELDS = {"pricing_model", "pricing_tiers", "has_free_tier", "has_trial"}
FEASIBILITY_FIELDS = {"tech_complexity_level", "feature_complexity", "team_size", "ai_dependency_level", "requires_realtime"}
RISK_FIELDS = {"tech_complexity_level", "ai_dependency_level", "requires_realtime", "potential_moats", "target_audience"}
SUCCESS_DRIVER_FIELDS = {"growth_driver", "is_product_driven", "founder_followers", "description", "core_features"}
POSITIONING_FIELDS = {"target_audience", "market_scope", "pricing_model", "pain_points", "use_cases", "uses_before_after"}

# =============================================================================
# System Prompt - 简洁版
# =============================================================================

MOTHER_THEME_SYSTEM_PROMPT = """你是一位资深SaaS产品分析师。

判断风格：务实、重证据、不被营销话术迷惑。
输出格式：仅输出 JSON，不要任何解释文字。"""

# =============================================================================
# 母题定义 - 三层架构
# =============================================================================

# 筛选层：回答"这个方向值不值得研究？"（2个母题）
SCREENING_THEMES: List[Dict[str, Any]] = [
    {
        "key": "opportunity_validity",
        "name": "机会真实性",
        "layer": "screening",
        "options": ["真实机会", "存在风险", "伪机会", "证据不足/无法判断"],
        "hint": """判断这是真实的市场机会还是伪机会。
真实机会特征：pain_points具体可量化（如"每周花5小时做X"）、target_audience明确指向特定人群（如"Shopify店主"而非"电商卖家"）、cta_texts指向具体行动
伪机会特征（满足2个即判定）：pain_points抽象泛化（如"提高效率"）、value_propositions全是愿景无具体功能、cta_texts模糊（如"开始旅程"）、target_audience过宽（如"所有人"）""",
    },
    {
        "key": "demand_type",
        "name": "需求类型",
        "layer": "screening",
        "options": ["主动搜索型", "触发认知型", "需教育型", "证据不足/无法判断"],
        "hint": """判断用户获取这个产品的方式。
主动搜索型：pain_points描述的是用户会主动搜索的问题（如"PDF转Word"、"发票管理"）
触发认知型：pain_points是潜在需求，看到才意识到需要（如"团队协作效率低"）
需教育型：产品解决的问题用户通常不知道存在（如新概念、新范式）
关键证据：pain_points是否是用户会搜索的关键词、uses_before_after是否清晰""",
    },
]

# 行动层：回答"如果我想做，可行吗？怎么做？"（4个母题）
ACTION_THEMES: List[Dict[str, Any]] = [
    {
        "key": "solo_feasibility",
        "name": "独立可行性",
        "layer": "action",
        "options": ["非常适合", "有挑战但可行", "不适合", "证据不足/无法判断"],
        "hint": """判断一个人能否把这个产品做出来并维护。
非常适合：tech_complexity_level=low/medium、feature_complexity=simple/moderate、team_size<=2、不依赖重度AI或实时数据
有挑战但可行：tech_complexity_level=medium、功能复杂度中等、或需要特定领域知识
不适合：tech_complexity_level=high、或需要实时系统+大数据、或requires_compliance=true""",
    },
    {
        "key": "entry_barrier",
        "name": "入场门槛",
        "layer": "action",
        "options": ["低门槛快启动", "中等投入", "高门槛", "证据不足/无法判断"],
        "hint": """判断启动这个项目需要的时间和资金投入。
低门槛快启动：startup_cost_level=low、feature_count较少（<=5）、核心功能简单明确（2周内可出MVP）
中等投入：startup_cost_level=medium、feature_count中等、需要一定开发周期（1-2月出MVP）
高门槛：startup_cost_level=high、或ai_dependency_level=heavy、或requires_compliance=true、或需要大量初始数据""",
    },
    {
        "key": "primary_risk",
        "name": "主要风险",
        "layer": "action",
        "options": ["技术实现", "市场验证", "用户获取", "变现转化", "证据不足/无法判断"],
        "hint": """判断如果做这个方向失败，最可能死在哪个环节。
技术实现：tech_complexity_level=high、ai_dependency_level=heavy、或requires_realtime=true
市场验证：demand_type=需教育型、或pain_points抽象不具体
用户获取：potential_moats较弱、demand_type!=主动搜索型、target_audience过宽
变现转化：has_free_tier=true但pricing_tiers不清晰、pricing_model不明确、target_customer=b2c且无明确付费点""",
    },
    {
        "key": "mvp_clarity",
        "name": "MVP清晰度",
        "layer": "action",
        "options": ["清晰可执行", "基本清晰", "模糊", "证据不足/无法判断"],
        "hint": """判断这个产品的最小可行版本是否清晰。
清晰可执行：core_features有明确的1-3个核心功能、has_instant_value_demo=true、value_propositions聚焦单一价值点
基本清晰：core_features可识别但数量较多（4-8个）、或value_propositions有多个方向
模糊：core_features过多或过于抽象、value_propositions分散、headline_text过于宽泛""",
    },
]

# 归因层：回答"为什么成功？哪些值得借鉴？"（3个母题）
ATTRIBUTION_THEMES: List[Dict[str, Any]] = [
    {
        "key": "success_driver",
        "name": "成功驱动因素",
        "layer": "attribution",
        "options": ["产品驱动", "IP/创作者驱动", "内容驱动", "渠道驱动", "证据不足/无法判断"],
        "hint": """判断这个产品的成功主要靠什么驱动。
产品驱动：growth_driver=product_driven、或is_product_driven=true、或产品本身功能/体验是核心卖点
IP/创作者驱动：growth_driver=ip_driven、或founder_followers较高、或产品与创始人个人品牌强绑定
内容驱动：growth_driver=content_driven、或有明显博客/教程/课程内容、或通过内容获取用户
渠道驱动：依托特定平台（如Shopify app, Chrome extension, Notion integration），从description或core_features推断""",
    },
    {
        "key": "positioning_insight",
        "name": "定位洞察",
        "layer": "attribution",
        "options": ["精准垂直", "差异化定价", "痛点锋利", "场景具体", "无明显亮点", "证据不足/无法判断"],
        "hint": """判断这个产品的定位策略有什么值得学习的地方。
精准垂直：target_audience非常具体（如"Shopify店主"而非"电商卖家"）、或market_scope=vertical
差异化定价：pricing_model有创新（usage-based/一次性买断/lifetime deal等）
痛点锋利：pain_points描述非常具体的问题（有数字、有场景）、或uses_before_after=true
场景具体：use_cases明确且具体、或headline_text直接描述使用场景""",
    },
    {
        "key": "differentiation_point",
        "name": "差异化点",
        "layer": "attribution",
        "options": ["功能差异化", "体验差异化", "人群差异化", "定价差异化", "无明显差异化", "证据不足/无法判断"],
        "hint": """判断这个产品相比竞品的独特之处。
功能差异化：potential_moats包含技术/功能相关壁垒、或core_features中有独特功能描述
体验差异化：has_instant_value_demo=true、或value_propositions强调简单/快速/易用
人群差异化：target_audience非常细分、market_scope=vertical
定价差异化：pricing_model非主流订阅模式（如一次性买断、按用量付费）
无明显差异化：以上都不满足，与同类产品高度相似""",
    },
]

# 合并所有母题
MOTHER_THEMES: List[Dict[str, Any]] = SCREENING_THEMES + ACTION_THEMES + ATTRIBUTION_THEMES

# 母题分层映射
THEME_LAYERS = {
    "screening": [t["key"] for t in SCREENING_THEMES],
    "action": [t["key"] for t in ACTION_THEMES],
    "attribution": [t["key"] for t in ATTRIBUTION_THEMES],
}


# =============================================================================
# 工具函数
# =============================================================================

def _value_present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip() != ""
    if isinstance(value, list):
        return len(value) > 0
    return True


def _trim_list(values: Any, limit: int = 6) -> Any:
    if isinstance(values, list):
        return values[:limit]
    return values


def build_evidence_availability(
    startup: Startup,
    analysis: LandingPageAnalysis,
    selection: Optional[ProductSelectionAnalysis] = None,
    category_analysis: Optional[CategoryAnalysis] = None,
) -> Dict[str, bool]:
    """构建证据字段可用性映射"""
    availability = {
        # LandingPageAnalysis 字段
        "headline_text": _value_present(analysis.headline_text),
        "tagline_text": _value_present(analysis.tagline_text),
        "core_features": _value_present(analysis.core_features),
        "feature_count": analysis.feature_count is not None,
        "value_propositions": _value_present(analysis.value_propositions),
        "target_audience": _value_present(analysis.target_audience),
        "pain_points": _value_present(analysis.pain_points),
        "use_cases": _value_present(analysis.use_cases),
        "pricing_model": _value_present(analysis.pricing_model),
        "pricing_tiers": _value_present(analysis.pricing_tiers),
        "has_free_tier": analysis.has_free_tier is not None,
        "has_trial": analysis.has_trial is not None,
        "cta_count": analysis.cta_count is not None,
        "cta_texts": _value_present(analysis.cta_texts),
        "conversion_funnel_steps": analysis.conversion_funnel_steps is not None,
        "has_instant_value_demo": analysis.has_instant_value_demo is not None,
        "conversion_friendliness_score": analysis.conversion_friendliness_score is not None,
        "potential_moats": _value_present(analysis.potential_moats),
        "uses_before_after": analysis.uses_before_after is not None,
        "uses_emotional_words": analysis.uses_emotional_words is not None,
        "positioning_clarity_score": analysis.positioning_clarity_score is not None,
        "replication_difficulty_score": analysis.replication_difficulty_score is not None,
        "individual_replicability_score": analysis.individual_replicability_score is not None,
        "pain_point_sharpness": analysis.pain_point_sharpness is not None,
        # Startup 字段
        "revenue_30d": startup.revenue_30d is not None,
        "category": _value_present(startup.category),
        "description": _value_present(startup.description),
        "founder_followers": startup.founder_followers is not None,
        "team_size": startup.team_size is not None,
    }

    # ProductSelectionAnalysis 字段
    if selection:
        availability.update({
            "growth_driver": _value_present(selection.growth_driver),
            "is_product_driven": selection.is_product_driven is not None,
            "ip_dependency_score": selection.ip_dependency_score is not None,
            "follower_revenue_ratio": selection.follower_revenue_ratio is not None,
            "tech_complexity_level": _value_present(selection.tech_complexity_level),
            "feature_complexity": _value_present(selection.feature_complexity),
            "ai_dependency_level": _value_present(selection.ai_dependency_level),
            "startup_cost_level": _value_present(selection.startup_cost_level),
            "market_scope": _value_present(selection.market_scope),
            "target_customer": _value_present(selection.target_customer),
            "requires_realtime": selection.requires_realtime is not None,
            "requires_large_data": selection.requires_large_data is not None,
            "requires_compliance": selection.requires_compliance is not None,
        })
    else:
        # 没有 selection 数据时，标记为不可用
        for field in SELECTION_ANALYSIS_FIELDS:
            availability[field] = False

    # CategoryAnalysis 字段
    if category_analysis:
        availability["market_type"] = _value_present(category_analysis.market_type)
    else:
        availability["market_type"] = False

    return availability


def build_context(
    startup: Startup,
    analysis: LandingPageAnalysis,
    selection: Optional[ProductSelectionAnalysis] = None,
    category_analysis: Optional[CategoryAnalysis] = None,
    evidence_availability: Optional[Dict[str, bool]] = None,
) -> str:
    """构建产品数据 JSON，包含所有可用证据字段"""
    if evidence_availability is None:
        evidence_availability = build_evidence_availability(
            startup, analysis, selection, category_analysis
        )

    payload = {
        # === LandingPageAnalysis 字段 ===
        "headline_text": analysis.headline_text,
        "tagline_text": analysis.tagline_text,
        "core_features": _trim_list(analysis.core_features),
        "feature_count": analysis.feature_count,
        "value_propositions": _trim_list(analysis.value_propositions),
        "target_audience": _trim_list(analysis.target_audience),
        "pain_points": _trim_list(analysis.pain_points),
        "use_cases": _trim_list(analysis.use_cases),
        "pricing_model": analysis.pricing_model,
        "pricing_tiers": _trim_list(analysis.pricing_tiers, limit=3),
        "has_free_tier": analysis.has_free_tier,
        "has_trial": analysis.has_trial,
        "cta_count": analysis.cta_count,
        "cta_texts": _trim_list(analysis.cta_texts),
        "conversion_funnel_steps": analysis.conversion_funnel_steps,
        "has_instant_value_demo": analysis.has_instant_value_demo,
        "conversion_friendliness_score": analysis.conversion_friendliness_score,
        "potential_moats": _trim_list(analysis.potential_moats),
        "uses_before_after": analysis.uses_before_after,
        "uses_emotional_words": analysis.uses_emotional_words,
        "positioning_clarity_score": analysis.positioning_clarity_score,
        "replication_difficulty_score": analysis.replication_difficulty_score,
        "individual_replicability_score": analysis.individual_replicability_score,
        "pain_point_sharpness": analysis.pain_point_sharpness,
        # === Startup 字段 ===
        "revenue_30d": startup.revenue_30d,
        "category": startup.category,
        "description": startup.description,
        "founder_followers": startup.founder_followers,
        "team_size": startup.team_size,
    }

    # === ProductSelectionAnalysis 字段 ===
    if selection:
        payload.update({
            "growth_driver": selection.growth_driver,
            "is_product_driven": selection.is_product_driven,
            "ip_dependency_score": selection.ip_dependency_score,
            "follower_revenue_ratio": selection.follower_revenue_ratio,
            "tech_complexity_level": selection.tech_complexity_level,
            "feature_complexity": selection.feature_complexity,
            "ai_dependency_level": selection.ai_dependency_level,
            "startup_cost_level": selection.startup_cost_level,
            "market_scope": selection.market_scope,
            "target_customer": selection.target_customer,
            "requires_realtime": selection.requires_realtime,
            "requires_large_data": selection.requires_large_data,
            "requires_compliance": selection.requires_compliance,
        })

    # === CategoryAnalysis 字段 ===
    if category_analysis:
        payload["market_type"] = category_analysis.market_type

    return json.dumps(payload, ensure_ascii=False, indent=2, default=str)


# =============================================================================
# Prompt 构建 - 结构化版本
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
            # 取 hint 的第一行作为简要提示
            hint_first_line = t.get("hint", "").split("\n")[0]
            lines.append(f"  {t['key']} ({t['name']}):\n    选项: {options_str}\n    提示: {hint_first_line}")
        return "\n".join(lines)

    themes_block = (
        format_theme_block(screening, "筛选层 - 值不值得研究？") +
        format_theme_block(action, "行动层 - 能不能做？怎么做？") +
        format_theme_block(attribution, "归因层 - 为什么成功？可学什么？")
    )

    # 合法字段名列表
    valid_fields = ", ".join(EVIDENCE_FIELDS)

    # 生成示例 keys
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


def build_theme_prompt(context: str, theme: Dict[str, Any]) -> str:
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


# =============================================================================
# 跨母题一致性检查（三层架构版）
# =============================================================================

def check_cross_theme_consistency(judgments: Dict[str, Dict[str, Any]]) -> List[str]:
    """检查跨母题判断的一致性，基于三层架构（2+4+3=9个母题）"""
    warnings = []

    # 获取各母题判断
    opportunity = judgments.get("opportunity_validity", {}).get("judgment")
    demand = judgments.get("demand_type", {}).get("judgment")
    solo = judgments.get("solo_feasibility", {}).get("judgment")
    barrier = judgments.get("entry_barrier", {}).get("judgment")
    risk = judgments.get("primary_risk", {}).get("judgment")
    mvp = judgments.get("mvp_clarity", {}).get("judgment")
    driver = judgments.get("success_driver", {}).get("judgment")
    positioning = judgments.get("positioning_insight", {}).get("judgment")
    diff = judgments.get("differentiation_point", {}).get("judgment")

    # === 规则1: 筛选层与行动层的一致性 ===

    # 伪机会不应该有高可行性
    if opportunity == "伪机会" and solo == "非常适合":
        warnings.append(
            "一致性警告: opportunity_validity='伪机会' 但 solo_feasibility='非常适合'，存在矛盾"
        )

    # 需教育型市场通常意味着用户获取或市场验证风险
    if demand == "需教育型" and risk not in ["用户获取", "市场验证", "证据不足/无法判断"]:
        warnings.append(
            f"一致性警告: demand_type='需教育型' 但 primary_risk='{risk}'，建议复核风险判断"
        )

    # === 规则2: 行动层内部一致性 ===

    # 不适合独立开发但低门槛是矛盾的
    if solo == "不适合" and barrier == "低门槛快启动":
        warnings.append(
            "一致性警告: solo_feasibility='不适合' 但 entry_barrier='低门槛快启动'，存在矛盾"
        )

    # MVP模糊但说低门槛需要复核
    if mvp == "模糊" and barrier == "低门槛快启动":
        warnings.append(
            "一致性警告: mvp_clarity='模糊' 但 entry_barrier='低门槛快启动'，MVP不清晰难以快速启动"
        )

    # 技术风险高但说低门槛需要复核
    if risk == "技术实现" and barrier == "低门槛快启动":
        warnings.append(
            "一致性警告: primary_risk='技术实现' 但 entry_barrier='低门槛快启动'，技术风险高通常门槛不低"
        )

    # === 规则3: 归因层与行动层的一致性 ===

    # IP驱动产品通常不是好的独立开发机会（除非你有粉丝）
    if driver == "IP/创作者驱动" and solo == "非常适合":
        warnings.append(
            "一致性提醒: success_driver='IP/创作者驱动' 但 solo_feasibility='非常适合'，需考虑是否有足够影响力"
        )

    # === 规则4: 过于乐观警告 ===
    optimistic_count = 0
    if opportunity == "真实机会":
        optimistic_count += 1
    if solo == "非常适合":
        optimistic_count += 1
    if barrier == "低门槛快启动":
        optimistic_count += 1
    if mvp == "清晰可执行":
        optimistic_count += 1

    if optimistic_count >= 4:
        warnings.append(
            f"一致性警告: {optimistic_count}/4 个关键判断都是最乐观选项，请复核是否过于乐观"
        )

    # === 规则5: 存在严格验证错误时应该更保守 ===
    for key, result in judgments.items():
        if key.startswith("_"):
            continue
        # 只有严格错误才触发警告，业务警告不触发
        if result.get("validation_errors") and result.get("confidence") == "高":
            warnings.append(
                f"一致性警告: {key} 存在格式错误但置信度为'高'，建议降级"
            )

    return warnings


# =============================================================================
# 母题判断器
# =============================================================================

class MotherThemeJudge:
    """母题判断器 - 支持三层架构"""

    def __init__(self, openai_service: OpenAIService):
        self.openai = openai_service

    async def judge_theme(
        self,
        theme: Dict[str, Any],
        startup: Startup,
        analysis: LandingPageAnalysis,
        selection: Optional[ProductSelectionAnalysis] = None,
        category_analysis: Optional[CategoryAnalysis] = None,
    ) -> Dict[str, Any]:
        evidence_availability = build_evidence_availability(
            startup, analysis, selection, category_analysis
        )
        context = build_context(
            startup, analysis, selection, category_analysis,
            evidence_availability=evidence_availability
        )
        prompt = build_theme_prompt(context, theme)
        result = await self._call_ai(prompt)
        validated = self._validate(theme, result, evidence_availability=evidence_availability)
        validated["_meta"] = {
            "theme": theme["key"],
            "layer": theme.get("layer", "unknown"),
            "prompt_version": PROMPT_VERSION,
            "model": self.openai.default_model,
        }
        return validated

    async def _call_ai(self, prompt: str, attempts: int = 2, retry_delay: float = 1.0) -> Dict[str, Any]:
        """调用 AI 并解析结果"""
        last_error: Optional[str] = None
        for attempt in range(attempts):
            try:
                response = await self.openai.chat(
                    messages=[
                        {"role": "system", "content": MOTHER_THEME_SYSTEM_PROMPT},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.3,
                )
                return self._parse_json(response)
            except Exception as exc:
                last_error = str(exc)
                logger.error(f"AI 调用失败（第 {attempt + 1} 次）: {exc}")
                if attempt < attempts - 1:
                    await asyncio.sleep(retry_delay)
        return {"error": last_error or "unknown_error"}

    @staticmethod
    def _parse_json(content: str) -> Dict[str, Any]:
        """解析 AI 响应中的 JSON"""
        if isinstance(content, dict):
            return content
        if not isinstance(content, str):
            return {"error": "响应不是字符串", "raw_response": content}

        def _attempt_parse(text: str) -> Optional[Dict[str, Any]]:
            try:
                parsed = json.loads(text)
            except json.JSONDecodeError:
                return None
            return parsed if isinstance(parsed, dict) else None

        def _extract_braced(text: str) -> Optional[str]:
            start = text.find("{")
            end = text.rfind("}")
            if start == -1 or end == -1 or end <= start:
                return None
            return text[start : end + 1]

        # 直接解析
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass

        # 尝试从 markdown 代码块提取
        if "```json" in content:
            start = content.find("```json") + 7
            end = content.find("```", start)
            if end == -1:
                end = len(content)
            candidate = content[start:end].strip()
            parsed = _attempt_parse(candidate)
            if parsed is not None:
                return parsed

        if "```" in content:
            start = content.find("```") + 3
            end = content.find("```", start)
            if end == -1:
                end = len(content)
            candidate = content[start:end].strip()
            parsed = _attempt_parse(candidate)
            if parsed is not None:
                return parsed

        # 尝试提取花括号内容
        braced = _extract_braced(content)
        if braced:
            parsed = _attempt_parse(braced)
            if parsed is not None:
                return parsed

        return {"error": "JSON 解析失败", "raw_response": content}


    @staticmethod
    def _validate(
        theme: Dict[str, Any],
        result: Dict[str, Any],
        evidence_availability: Optional[Dict[str, bool]] = None,
    ) -> Dict[str, Any]:
        """校验输出格式和证据引用
        
        验证分两类：
        1. 严格错误 (validation_errors): 格式/解析错误，必须修复
        2. 业务警告 (validation_warnings): 业务规则建议，仅供参考
        """
        if not isinstance(result, dict):
            return {"error": "结果非 dict", "raw_response": result}
        if "error" in result:
            return result

        errors = []      # 严格错误：格式/解析问题
        warnings = []    # 业务警告：建议性规则

        # ========== 严格验证：格式/解析错误 ==========

        # 必填字段校验
        for field in REQUIRED_FIELDS:
            if field not in result:
                errors.append(f"缺少必填字段: {field}")
            elif field == "uncertainties" and result.get(field) is None:
                # uncertainties 不能是 null，必须是数组（可以为空数组）
                errors.append("uncertainties 不能为 null，应为空数组 []")

        # judgment 选项校验
        options = theme.get("options", [])
        if options and result.get("judgment") not in options:
            errors.append(f"judgment 不在允许范围: {result.get('judgment')}")

        # confidence 校验
        if "confidence" in result and result.get("confidence") not in CONFIDENCE_CHOICES:
            errors.append(f"confidence 不在允许范围: {result.get('confidence')}")

        # reasons 类型校验（只检查类型，不检查数量）
        if "reasons" in result:
            reasons = result.get("reasons")
            if not isinstance(reasons, list):
                errors.append("reasons 必须是数组")

        # uncertainties 类型校验
        if "uncertainties" in result:
            uncertainties = result.get("uncertainties")
            if uncertainties is not None and not isinstance(uncertainties, list):
                errors.append("uncertainties 必须是数组")

        # evidence_fields 类型和字段名校验
        evidence_fields = result.get("evidence_fields")
        if not isinstance(evidence_fields, list):
            errors.append("evidence_fields 必须是数组")
        elif evidence_fields:
            invalid_fields = [f for f in evidence_fields if f not in EVIDENCE_FIELDS]
            if invalid_fields:
                errors.append(f"evidence_fields 包含未知字段: {invalid_fields}")

        # ========== 业务警告：建议性规则（不阻塞） ==========

        # reasons 数量建议
        if isinstance(result.get("reasons"), list) and len(result.get("reasons", [])) > 3:
            warnings.append("reasons 超过 3 条，建议精简")

        # evidence_fields 引用缺失字段（字段值为 null）
        if isinstance(evidence_fields, list) and evidence_availability:
            missing = [f for f in evidence_fields if evidence_availability.get(f) is False]
            if missing:
                warnings.append(f"evidence_fields 引用了值为 null 的字段: {missing}")

        # 证据不足时的置信度建议
        if result.get("judgment") == "证据不足/无法判断" and result.get("confidence") != "低":
            warnings.append("证据不足时建议置信度降为低")

        # 构建结果
        normalized = {field: result.get(field) for field in REQUIRED_FIELDS}
        
        if errors:
            normalized["validation_errors"] = errors
        if warnings:
            normalized["validation_warnings"] = warnings
            
        return normalized

    @staticmethod
    def _needs_fallback(result: Dict[str, Any]) -> bool:
        if not isinstance(result, dict):
            return True
        if result.get("error"):
            return True
        # 只有严格错误才需要 fallback，警告不需要
        if result.get("validation_errors"):
            return True
        return False

    async def judge_all_themes_once(
        self,
        themes: List[Dict[str, Any]],
        startup: Startup,
        analysis: LandingPageAnalysis,
        selection: Optional[ProductSelectionAnalysis] = None,
        category_analysis: Optional[CategoryAnalysis] = None,
        fallback_on_invalid: bool = FALLBACK_ON_INVALID,
    ) -> Dict[str, Dict[str, Any]]:
        """一次请求返回全部母题的判断结果（支持三层架构）"""
        evidence_availability = build_evidence_availability(
            startup, analysis, selection, category_analysis
        )
        context = build_context(
            startup, analysis, selection, category_analysis,
            evidence_availability=evidence_availability
        )
        prompt = build_one_shot_prompt(context, themes)
        result = await self._call_ai(prompt)

        if not isinstance(result, dict) or "judgments" not in result:
            if fallback_on_invalid:
                output: Dict[str, Dict[str, Any]] = {}
                for theme in themes:
                    fallback_result = await self.judge_theme(
                        theme, startup, analysis, selection, category_analysis
                    )
                    fallback_result.setdefault("_meta", {})
                    fallback_result["_meta"]["fallback"] = "single_theme"
                    output[theme["key"]] = fallback_result
                return output
            return {"_error": {"error": "缺少 judgments 字段", "raw_response": result}}

        judgments_raw = result.get("judgments", {})
        output: Dict[str, Dict[str, Any]] = {}
        for theme in themes:
            if theme["key"] not in judgments_raw:
                validated = {"error": "缺少该母题结果"}
            else:
                t_res = judgments_raw.get(theme["key"], {})
                validated = self._validate(theme, t_res, evidence_availability=evidence_availability)
            if fallback_on_invalid and self._needs_fallback(validated):
                fallback_result = await self.judge_theme(
                    theme, startup, analysis, selection, category_analysis
                )
                fallback_result.setdefault("_meta", {})
                fallback_result["_meta"]["fallback"] = "single_theme"
                validated = fallback_result
            else:
                validated["_meta"] = {
                    "theme": theme["key"],
                    "layer": theme.get("layer", "unknown"),
                    "prompt_version": PROMPT_VERSION,
                    "model": self.openai.default_model,
                }
            output[theme["key"]] = validated
        return output


# =============================================================================
# 测试运行
# =============================================================================

async def get_test_products(
    db,
    limit: int = 20,
    min_revenue: Optional[float] = None,
) -> List[Tuple[Startup, LandingPageAnalysis]]:
    """获取有完整 landing page 分析的产品"""
    query = (
        select(Startup, LandingPageAnalysis)
        .join(LandingPageAnalysis, Startup.id == LandingPageAnalysis.startup_id)
        .where(LandingPageAnalysis.core_features.isnot(None))
    )

    if min_revenue is not None:
        query = query.where(Startup.revenue_30d >= min_revenue)

    query = query.order_by(Startup.revenue_30d.desc().nullslast())
    query = query.limit(limit)

    result = await db.execute(query)
    return result.all()


async def get_selection_analysis(db, startup_id: int) -> Optional[ProductSelectionAnalysis]:
    """获取产品的 ProductSelectionAnalysis"""
    query = select(ProductSelectionAnalysis).where(
        ProductSelectionAnalysis.startup_id == startup_id
    )
    result = await db.execute(query)
    row = result.first()
    return row[0] if row else None


async def get_category_analysis(db, category: str) -> Optional[CategoryAnalysis]:
    """获取类别的 CategoryAnalysis"""
    if not category:
        return None
    query = select(CategoryAnalysis).where(CategoryAnalysis.category == category)
    result = await db.execute(query)
    row = result.first()
    return row[0] if row else None


async def run_test(
    limit: int = 20,
    delay: float = 2.0,
    min_revenue: Optional[float] = None,
    one_shot: bool = ONE_SHOT_MODE,
    fallback_on_invalid: bool = FALLBACK_ON_INVALID,
) -> None:
    """运行母题判断测试"""
    logger.info(
        "开始母题判断测试，样本数量: %s, min_revenue: %s, one_shot: %s",
        limit, min_revenue, one_shot,
    )

    results: List[Dict[str, Any]] = []
    model_name = "unknown"

    async with get_db_session() as db:
        products = await get_test_products(db, limit, min_revenue=min_revenue)
        logger.info(f"获取到 {len(products)} 个产品")

        if not products:
            logger.error("没有找到符合条件的产品")
            return

        async with OpenAIService() as openai:
            judge = MotherThemeJudge(openai)
            model_name = openai.default_model

            for i, (startup, analysis) in enumerate(products):
                logger.info(f"[{i + 1}/{len(products)}] 分析: {startup.name}")

                # 获取补充数据
                selection = await get_selection_analysis(db, startup.id)
                category_analysis = await get_category_analysis(db, startup.category)

                product_result: Dict[str, Any] = {
                    "id": startup.id,
                    "name": startup.name,
                    "slug": startup.slug,
                    "category": startup.category,
                    "description": startup.description,
                    "revenue_30d": startup.revenue_30d,
                    "website_url": startup.website_url,
                    "has_selection_analysis": selection is not None,
                    "has_category_analysis": category_analysis is not None,
                    "landing_page_summary": {
                        "headline": analysis.headline_text,
                        "tagline": analysis.tagline_text,
                        "core_features": analysis.core_features,
                        "feature_count": analysis.feature_count,
                        "target_audience": analysis.target_audience,
                        "pain_points": analysis.pain_points,
                        "pricing_model": analysis.pricing_model,
                        "cta_texts": analysis.cta_texts,
                    },
                    "judgments": {},
                }

                if one_shot:
                    try:
                        theme_results = await judge.judge_all_themes_once(
                            MOTHER_THEMES, startup, analysis,
                            selection=selection,
                            category_analysis=category_analysis,
                            fallback_on_invalid=fallback_on_invalid,
                        )
                        if "_error" in theme_results:
                            product_result["judgments"] = {"_error": theme_results["_error"]}
                            logger.error(f"  - 请求失败: {theme_results['_error']}")
                        else:
                            product_result["judgments"] = theme_results
                            if ENFORCE_CONSISTENCY:
                                warnings = check_cross_theme_consistency(theme_results)
                                if warnings:
                                    product_result["consistency_warnings"] = warnings
                                    for w in warnings:
                                        logger.warning(f"  {w}")
                            for theme in MOTHER_THEMES:
                                t_res = theme_results.get(theme["key"], {})
                                logger.info(
                                    f"  - {theme['name']}: {t_res.get('judgment', 'N/A')} "
                                    f"(置信度: {t_res.get('confidence', 'N/A')})"
                                )
                    except Exception as exc:
                        product_result["judgments"] = {"_error": {"error": str(exc)}}
                        logger.error(f"  - 判断失败: {exc}")
                else:
                    for theme in MOTHER_THEMES:
                        try:
                            theme_result = await judge.judge_theme(
                                theme, startup, analysis,
                                selection=selection,
                                category_analysis=category_analysis,
                            )
                            product_result["judgments"][theme["key"]] = theme_result
                            logger.info(
                                f"  - {theme['name']}: {theme_result.get('judgment', 'N/A')} "
                                f"(置信度: {theme_result.get('confidence', 'N/A')})"
                            )
                        except Exception as exc:
                            product_result["judgments"][theme["key"]] = {"error": str(exc)}
                            logger.error(f"  - {theme['name']} 判断失败: {exc}")
                        await asyncio.sleep(delay / 2)

                results.append(product_result)
                if i < len(products) - 1:
                    await asyncio.sleep(delay)

    # 保存结果
    output_file = OUTPUT_DIR / "mother_theme_test_results.json"
    payload = {
        "test_time": datetime.now().isoformat(),
        "sample_count": len(results),
        "mother_themes_tested": [t["key"] for t in MOTHER_THEMES],
        "prompt_version": PROMPT_VERSION,
        "model": model_name,
        "config": {
            "limit": limit,
            "delay": delay,
            "min_revenue": min_revenue,
            "one_shot": one_shot,
            "fallback_on_invalid": fallback_on_invalid,
        },
        "results": results,
    }
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    logger.info(f"测试完成，结果已保存到: {output_file}")

    # 打印摘要
    print("\n" + "=" * 60)
    print("测试结果摘要")
    print("=" * 60)

    summary: Dict[str, Dict[str, int]] = {}
    for theme in MOTHER_THEMES:
        summary[theme["key"]] = {}
    for result in results:
        for theme in MOTHER_THEMES:
            j = result["judgments"].get(theme["key"], {}).get("judgment", "error")
            summary[theme["key"]][j] = summary[theme["key"]].get(j, 0) + 1

    for theme in MOTHER_THEMES:
        print(f"\n{theme['name']} ({theme['key']}) 分布:")
        for k, v in summary[theme["key"]].items():
            print(f"  {k}: {v}")

    print(f"\n详细结果请查看: {output_file}")


if __name__ == "__main__":
    asyncio.run(run_test(limit=10, delay=2.0, min_revenue=None))
