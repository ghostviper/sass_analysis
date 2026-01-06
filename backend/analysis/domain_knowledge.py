"""
Domain Knowledge - 确定性高的判断维度

提供基于行业常识、技术常识、商业常识的确定性判断，
这些判断不依赖数据计算，而是基于先验知识。
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class DomainInsight:
    """领域洞察"""
    type: str  # positive / warning / info
    title: str
    description: str
    confidence: str  # high / medium
    source: str  # 行业常识 / 技术常识 / 商业常识


class DomainKnowledge:
    """确定性判断模块"""

    # 判断规则定义
    RULES = {
        # AI依赖相关
        "ai_dependency_heavy": {
            "condition": lambda tags: tags.get("ai_dependency_level") == "heavy",
            "insight": DomainInsight(
                type="warning",
                title="核心依赖LLM API",
                description="成本不可控，受供应商定价影响；存在API变更和服务中断风险",
                confidence="high",
                source="行业常识"
            )
        },
        "ai_dependency_light": {
            "condition": lambda tags: tags.get("ai_dependency_level") == "light",
            "insight": DomainInsight(
                type="info",
                title="轻度使用AI增强",
                description="AI作为辅助功能，核心价值不依赖AI，风险可控",
                confidence="high",
                source="行业常识"
            )
        },
        "ai_dependency_none": {
            "condition": lambda tags: tags.get("ai_dependency_level") == "none",
            "insight": DomainInsight(
                type="positive",
                title="不依赖AI",
                description="无AI相关成本和供应商风险，技术栈更稳定",
                confidence="high",
                source="行业常识"
            )
        },

        # 合规要求相关
        "compliance_required": {
            "condition": lambda tags: tags.get("has_compliance_requirement") is True,
            "insight": DomainInsight(
                type="warning",
                title="需要合规认证",
                description="医疗/金融领域门槛高、认证周期长、法律风险大",
                confidence="high",
                source="行业常识"
            )
        },

        # 实时功能相关
        "realtime_required": {
            "condition": lambda tags: tags.get("has_realtime_feature") is True,
            "insight": DomainInsight(
                type="info",
                title="需要实时功能",
                description="WebSocket等实时技术复杂度较高，运维成本增加",
                confidence="high",
                source="技术常识"
            )
        },

        # 数据密集型
        "data_intensive": {
            "condition": lambda tags: tags.get("is_data_intensive") is True,
            "insight": DomainInsight(
                type="warning",
                title="数据密集型产品",
                description="需要大规模数据处理能力，基础设施成本高",
                confidence="high",
                source="技术常识"
            )
        },

        # 定价模式相关
        "pricing_subscription": {
            "condition": lambda tags: tags.get("pricing_model") == "subscription",
            "insight": DomainInsight(
                type="positive",
                title="订阅制收费",
                description="收入可预测，现金流稳定，比一次性付费更可持续",
                confidence="high",
                source="商业常识"
            )
        },
        "pricing_one_time": {
            "condition": lambda tags: tags.get("pricing_model") == "one_time",
            "insight": DomainInsight(
                type="info",
                title="一次性付费",
                description="前期收入高但缺乏持续性，需要不断获取新客户",
                confidence="high",
                source="商业常识"
            )
        },
        "pricing_usage": {
            "condition": lambda tags: tags.get("pricing_model") == "usage",
            "insight": DomainInsight(
                type="info",
                title="按量付费",
                description="收入与使用量挂钩，适合API类产品，但收入波动大",
                confidence="high",
                source="商业常识"
            )
        },

        # 目标客户相关
        "target_b2b_enterprise": {
            "condition": lambda tags: tags.get("target_customer") == "b2b_enterprise",
            "insight": DomainInsight(
                type="info",
                title="面向大企业客户",
                description="客单价高但销售周期长，需要专业销售团队，个人开发者难度大",
                confidence="high",
                source="商业常识"
            )
        },
        "target_b2b_smb": {
            "condition": lambda tags: tags.get("target_customer") == "b2b_smb",
            "insight": DomainInsight(
                type="positive",
                title="面向中小企业",
                description="决策链短，自助购买为主，适合个人开发者",
                confidence="high",
                source="商业常识"
            )
        },
        "target_b2c": {
            "condition": lambda tags: tags.get("target_customer") == "b2c",
            "insight": DomainInsight(
                type="info",
                title="面向个人消费者",
                description="用户量大但客单价低，需要大量营销投入",
                confidence="high",
                source="商业常识"
            )
        },
        "target_b2d": {
            "condition": lambda tags: tags.get("target_customer") == "b2d",
            "insight": DomainInsight(
                type="positive",
                title="面向开发者",
                description="开发者群体技术敏感，口碑传播效果好，适合技术型创始人",
                confidence="high",
                source="商业常识"
            )
        },

        # 市场类型相关
        "market_vertical": {
            "condition": lambda tags: tags.get("market_scope") == "vertical",
            "insight": DomainInsight(
                type="info",
                title="垂直细分市场",
                description="竞争相对较少，但市场天花板有限，需要深耕行业",
                confidence="high",
                source="商业常识"
            )
        },
        "market_horizontal": {
            "condition": lambda tags: tags.get("market_scope") == "horizontal",
            "insight": DomainInsight(
                type="info",
                title="通用水平市场",
                description="市场空间大但竞争激烈，需要差异化定位",
                confidence="high",
                source="商业常识"
            )
        },

        # 功能复杂度相关
        "complexity_simple": {
            "condition": lambda tags: tags.get("feature_complexity") == "simple",
            "insight": DomainInsight(
                type="positive",
                title="功能简单聚焦",
                description="开发维护成本低，易于快速迭代，适合个人开发者",
                confidence="high",
                source="技术常识"
            )
        },
        "complexity_complex": {
            "condition": lambda tags: tags.get("feature_complexity") == "complex",
            "insight": DomainInsight(
                type="warning",
                title="功能复杂",
                description="开发周期长，维护成本高，需要团队协作",
                confidence="high",
                source="技术常识"
            )
        },

        # 护城河相关
        "moat_none": {
            "condition": lambda tags: tags.get("moat_type") == "none",
            "insight": DomainInsight(
                type="warning",
                title="缺乏明显护城河",
                description="容易被复制，需要持续创新或快速占领市场",
                confidence="medium",
                source="商业常识"
            )
        },
        "moat_data": {
            "condition": lambda tags: "data" in (tags.get("moat_type") or ""),
            "insight": DomainInsight(
                type="positive",
                title="数据护城河",
                description="独特数据资产难以复制，竞争优势可持续",
                confidence="high",
                source="商业常识"
            )
        },
        "moat_network": {
            "condition": lambda tags: "network" in (tags.get("moat_type") or ""),
            "insight": DomainInsight(
                type="positive",
                title="网络效应",
                description="用户越多价值越大，形成正向循环，但冷启动困难",
                confidence="high",
                source="商业常识"
            )
        },

        # 启动成本相关
        "startup_cost_low": {
            "condition": lambda tags: tags.get("startup_cost_level") == "low",
            "insight": DomainInsight(
                type="positive",
                title="启动成本低",
                description="可以快速验证想法，失败成本可控",
                confidence="high",
                source="商业常识"
            )
        },
        "startup_cost_high": {
            "condition": lambda tags: tags.get("startup_cost_level") == "high",
            "insight": DomainInsight(
                type="warning",
                title="启动成本高",
                description="需要较大前期投入，验证周期长，风险较高",
                confidence="high",
                source="商业常识"
            )
        },

        # 产品阶段相关
        "stage_early": {
            "condition": lambda tags: tags.get("product_stage") == "early",
            "insight": DomainInsight(
                type="info",
                title="早期产品",
                description="市场验证不充分，但如果成功说明需求真实存在",
                confidence="medium",
                source="商业常识"
            )
        },
        "stage_mature": {
            "condition": lambda tags: tags.get("product_stage") == "mature",
            "insight": DomainInsight(
                type="positive",
                title="成熟产品",
                description="经过市场验证，商业模式相对稳定",
                confidence="high",
                source="商业常识"
            )
        },

        # 增长驱动相关
        "growth_product_driven": {
            "condition": lambda tags: tags.get("growth_driver") == "product_driven",
            "insight": DomainInsight(
                type="positive",
                title="产品驱动增长",
                description="不依赖创始人IP，产品本身创造价值，可复制性强",
                confidence="high",
                source="商业常识"
            )
        },
        "growth_ip_driven": {
            "condition": lambda tags: tags.get("growth_driver") == "ip_driven",
            "insight": DomainInsight(
                type="warning",
                title="IP驱动增长",
                description="依赖创始人个人影响力，复制难度大",
                confidence="high",
                source="商业常识"
            )
        },
        "growth_content_driven": {
            "condition": lambda tags: tags.get("growth_driver") == "content_driven",
            "insight": DomainInsight(
                type="info",
                title="内容驱动增长",
                description="需要持续产出优质内容，适合有内容创作能力的创始人",
                confidence="high",
                source="商业常识"
            )
        },

        # 收入层级相关
        "revenue_large": {
            "condition": lambda tags: tags.get("revenue_tier") == "large",
            "insight": DomainInsight(
                type="positive",
                title="收入验证充分",
                description="月收入>$10K，市场需求已被充分验证",
                confidence="high",
                source="商业常识"
            )
        },
        "revenue_micro": {
            "condition": lambda tags: tags.get("revenue_tier") == "micro",
            "insight": DomainInsight(
                type="info",
                title="收入较低",
                description="月收入<$500，市场验证不充分，可能是早期或需求不足",
                confidence="medium",
                source="商业常识"
            )
        },
    }

    @classmethod
    def get_insights(cls, tags: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        根据产品标签获取确定性洞察

        Args:
            tags: 产品标签字典

        Returns:
            洞察列表
        """
        insights = []

        for rule_name, rule in cls.RULES.items():
            try:
                if rule["condition"](tags):
                    insight = rule["insight"]
                    insights.append({
                        "type": insight.type,
                        "title": insight.title,
                        "description": insight.description,
                        "confidence": insight.confidence,
                        "source": insight.source,
                        "rule_name": rule_name,
                    })
            except Exception:
                # 忽略条件检查错误
                continue

        # 按类型排序：positive > info > warning
        type_order = {"positive": 0, "info": 1, "warning": 2}
        insights.sort(key=lambda x: type_order.get(x["type"], 3))

        return insights

    @classmethod
    def get_summary_points(cls, tags: Dict[str, Any], max_points: int = 5) -> List[Dict[str, str]]:
        """
        获取简洁的摘要要点（用于展示层）

        Args:
            tags: 产品标签字典
            max_points: 最大要点数量

        Returns:
            摘要要点列表
        """
        insights = cls.get_insights(tags)

        # 优先选择高置信度的洞察
        high_confidence = [i for i in insights if i["confidence"] == "high"]

        # 确保每种类型都有代表
        summary = []
        seen_types = set()

        for insight in high_confidence:
            if len(summary) >= max_points:
                break
            if insight["type"] not in seen_types or len(summary) < 3:
                summary.append({
                    "type": insight["type"],
                    "text": insight["title"]
                })
                seen_types.add(insight["type"])

        return summary

    @classmethod
    def get_risk_assessment(cls, tags: Dict[str, Any]) -> Dict[str, Any]:
        """
        获取风险评估

        Args:
            tags: 产品标签字典

        Returns:
            风险评估结果
        """
        insights = cls.get_insights(tags)

        warnings = [i for i in insights if i["type"] == "warning"]
        positives = [i for i in insights if i["type"] == "positive"]

        # 计算风险分数 (0-10, 越低越好)
        risk_score = len(warnings) * 2 - len(positives) * 0.5
        risk_score = max(0, min(10, risk_score + 5))  # 基础分5

        if risk_score <= 3:
            risk_level = "low"
            risk_label = "低风险"
        elif risk_score <= 6:
            risk_level = "medium"
            risk_label = "中等风险"
        else:
            risk_level = "high"
            risk_label = "高风险"

        return {
            "risk_score": round(risk_score, 1),
            "risk_level": risk_level,
            "risk_label": risk_label,
            "warning_count": len(warnings),
            "positive_count": len(positives),
            "key_risks": [w["title"] for w in warnings[:3]],
            "key_advantages": [p["title"] for p in positives[:3]],
        }
