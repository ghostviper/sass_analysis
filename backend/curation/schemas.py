"""
策展系统数据结构定义
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum


class ThemeLayer(str, Enum):
    """母题层级"""
    SCREENING = "screening"
    ACTION = "action"
    ATTRIBUTION = "attribution"


class Confidence(str, Enum):
    """置信度"""
    HIGH = "高"
    MEDIUM = "中"
    LOW = "低"


@dataclass
class ThemeJudgment:
    """单个母题的判断结果"""
    judgment: str
    confidence: str
    reasons: List[str]
    evidence_fields: List[str]
    uncertainties: List[str] = field(default_factory=list)
    validation_errors: Optional[List[str]] = None
    validation_warnings: Optional[List[str]] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ThemeJudgment":
        return cls(
            judgment=data.get("judgment", ""),
            confidence=data.get("confidence", ""),
            reasons=data.get("reasons", []),
            evidence_fields=data.get("evidence_fields", []),
            uncertainties=data.get("uncertainties", []),
            validation_errors=data.get("validation_errors"),
            validation_warnings=data.get("validation_warnings"),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "judgment": self.judgment,
            "confidence": self.confidence,
            "reasons": self.reasons,
            "evidence_fields": self.evidence_fields,
            "uncertainties": self.uncertainties,
        }
        if self.validation_errors:
            result["validation_errors"] = self.validation_errors
        if self.validation_warnings:
            result["validation_warnings"] = self.validation_warnings
        return result


@dataclass
class ProductJudgments:
    """产品的所有母题判断结果"""
    startup_id: int
    startup_name: str
    judgments: Dict[str, ThemeJudgment]
    consistency_warnings: Optional[List[str]] = None
    
    def get_judgment(self, theme_key: str) -> Optional[str]:
        """获取指定母题的判断结果"""
        if theme_key in self.judgments:
            return self.judgments[theme_key].judgment
        return None


@dataclass
class TopicTemplate:
    """专题模板"""
    title: str
    pattern: str  # contrast / niche / cognitive / action
    description_template: str
    cta: str = "让我帮你分析：你能不能做类似的"


@dataclass
class CuratorRole:
    """策展角色配置"""
    name: str
    display_name: str
    filter_rules: Dict[str, Any]
    topic_templates: List[TopicTemplate]


@dataclass
class GeneratedTopic:
    """生成的专题"""
    topic_key: str
    title: str
    description: str
    curator_role: str
    generation_pattern: str
    filter_rules: Dict[str, Any]
    product_ids: List[int]
    product_count: int
    cta_text: str
