"""
验证逻辑

包含母题判断结果的验证和跨母题一致性检查。
"""

from typing import Any, Dict, List, Optional
from .config import REQUIRED_FIELDS, CONFIDENCE_CHOICES, EVIDENCE_FIELDS


def validate_judgment(
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
            errors.append("uncertainties 不能为 null，应为空数组 []")

    # judgment 选项校验
    options = theme.get("options", [])
    if options and result.get("judgment") not in options:
        errors.append(f"judgment 不在允许范围: {result.get('judgment')}")

    # confidence 校验
    if "confidence" in result and result.get("confidence") not in CONFIDENCE_CHOICES:
        errors.append(f"confidence 不在允许范围: {result.get('confidence')}")

    # reasons 类型校验
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

    # evidence_fields 引用缺失字段
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
    driver = judgments.get("success_driver", {}).get("judgment")

    # IP驱动产品通常不是好的独立开发机会
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
        if result.get("validation_errors") and result.get("confidence") == "高":
            warnings.append(
                f"一致性警告: {key} 存在格式错误但置信度为'高'，建议降级"
            )

    return warnings


def needs_fallback(result: Dict[str, Any]) -> bool:
    """判断是否需要回退到单独判断"""
    if not isinstance(result, dict):
        return True
    if result.get("error"):
        return True
    if result.get("validation_errors"):
        return True
    return False
