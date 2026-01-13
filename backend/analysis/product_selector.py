"""
Product Selector - 选品分析
"""

import logging
import re
from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, asdict
from sqlalchemy import select, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Startup, ProductSelectionAnalysis

logger = logging.getLogger(__name__)


@dataclass
class ProductScore:
    """产品选品评分"""
    startup_id: int
    name: str
    slug: str

    # 产品驱动型指标
    is_product_driven: bool
    ip_dependency_score: float  # 0-10, 越低越好
    follower_revenue_ratio: float

    # 小而美指标
    is_small_and_beautiful: bool
    description_word_count: int
    feature_simplicity_score: float

    # 复杂度分析
    uses_llm_api: bool
    requires_realtime: bool
    requires_large_data: bool
    requires_compliance: bool
    tech_complexity_level: str  # low, medium, high
    compliance_risk_level: str
    maintenance_cost_level: str

    # 组合分析匹配
    combo1_match: bool  # 低粉丝+高收入+简单描述+创立<1年
    combo2_match: bool  # 简单描述+中等收入+技术复杂度低
    combo3_match: bool  # 小而美+低复杂度+有稳定收入

    # 综合评分
    individual_dev_suitability: float  # 0-10

    # 数据质量标记
    has_follower_data: bool = True  # 是否有粉丝数据
    data_quality_notes: str = ""  # 数据质量说明

    # ========== 新增标签字段 (v2) ==========
    # 收入验证维度
    revenue_tier: str = None  # micro/small/medium/large
    revenue_follower_ratio_level: str = None  # high/medium/low

    # 增长驱动维度
    growth_driver: str = None  # product_driven/ip_driven/content_driven/community_driven

    # 技术特征维度
    ai_dependency_level: str = None  # none/light/heavy
    has_realtime_feature: bool = None
    is_data_intensive: bool = None
    has_compliance_requirement: bool = None

    # 商业模式维度
    pricing_model: str = None  # subscription/one_time/usage/freemium
    target_customer: str = None  # b2c/b2b_smb/b2b_enterprise/b2d
    market_scope: str = None  # horizontal/vertical

    # 可复制性维度
    feature_complexity: str = None  # simple/moderate/complex
    moat_type: str = None  # none/data/network/brand/tech
    startup_cost_level: str = None  # low/medium/high

    # 生命周期维度
    product_stage: str = None  # early/growth/mature

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_tags_dict(self) -> Dict[str, Any]:
        """返回纯标签数据（AI友好格式）"""
        return {
            "revenue_tier": self.revenue_tier,
            "revenue_follower_ratio_level": self.revenue_follower_ratio_level,
            "growth_driver": self.growth_driver,
            "ai_dependency_level": self.ai_dependency_level,
            "has_realtime_feature": self.has_realtime_feature,
            "is_data_intensive": self.is_data_intensive,
            "has_compliance_requirement": self.has_compliance_requirement,
            "pricing_model": self.pricing_model,
            "target_customer": self.target_customer,
            "market_scope": self.market_scope,
            "feature_complexity": self.feature_complexity,
            "moat_type": self.moat_type,
            "startup_cost_level": self.startup_cost_level,
            "product_stage": self.product_stage,
            "tech_complexity_level": self.tech_complexity_level,
            "maintenance_cost_level": self.maintenance_cost_level,
        }


class ProductSelector:
    """选品分析器 - 筛选适合个人开发者的产品"""

    # 阈值设置 (基于数据集：中位数粉丝254，中位数收入$264)
    LOW_FOLLOWER_THRESHOLD = 1000  # 低粉丝阈值（约75%产品低于此值）
    HIGH_FOLLOWER_THRESHOLD = 5000  # 高粉丝阈值（IP驱动型）
    HIGH_REVENUE_THRESHOLD = 1000  # 高收入阈值（约35%产品高于此值）
    VERY_HIGH_REVENUE_THRESHOLD = 5000  # 非常高收入阈值（约10%产品高于此值）
    SIMPLE_DESCRIPTION_WORDS = 50  # 简短描述字数上限
    YOUNG_COMPANY_MONTHS = 18  # 新公司月数（放宽到18个月）

    # 收入层级阈值
    REVENUE_TIER_MICRO = 500  # <$500
    REVENUE_TIER_SMALL = 2000  # $500-2K
    REVENUE_TIER_MEDIUM = 10000  # $2K-10K
    # >$10K = large

    # 数据缺失标记
    MISSING_FOLLOWER_PENALTY = 2.0  # 缺失粉丝数据时的评分惩罚

    # 复杂度关键词
    LLM_KEYWORDS = [
        "gpt", "ai", "chatgpt", "openai", "claude", "llm", "language model",
        "artificial intelligence", "machine learning", "deep learning",
        "neural", "nlp", "大模型", "人工智能"
    ]

    # AI轻度使用关键词（增强功能而非核心）
    AI_LIGHT_KEYWORDS = [
        "ai-powered", "ai enhanced", "smart", "intelligent", "automated",
        "auto-generate", "ai assistant", "ai helper"
    ]

    REALTIME_KEYWORDS = [
        "realtime", "real-time", "collaboration", "multiplayer", "sync",
        "live", "instant", "实时", "协作", "同步", "websocket"
    ]

    BIG_DATA_KEYWORDS = [
        "analytics", "data lake", "big data", "millions of", "enterprise",
        "warehouse", "etl", "pipeline", "数据分析", "大数据"
    ]

    COMPLIANCE_KEYWORDS = [
        "hipaa", "gdpr", "soc2", "compliance", "medical", "financial",
        "healthcare", "banking", "insurance", "legal", "合规", "医疗", "金融"
    ]

    # 商业模式关键词
    B2B_KEYWORDS = [
        "enterprise", "business", "team", "company", "organization",
        "saas", "b2b", "corporate", "professional", "agency", "企业", "团队"
    ]

    B2B_ENTERPRISE_KEYWORDS = [
        "enterprise", "fortune 500", "large organization", "corporate",
        "soc2", "sso", "audit", "compliance"
    ]

    B2C_KEYWORDS = [
        "personal", "individual", "consumer", "user", "people",
        "everyone", "anyone", "个人", "用户"
    ]

    B2D_KEYWORDS = [
        "developer", "api", "sdk", "integration", "devtool", "开发者",
        "programmer", "engineer", "code", "github"
    ]

    # 定价模式关键词
    SUBSCRIPTION_KEYWORDS = [
        "subscription", "monthly", "yearly", "annual", "per month",
        "/mo", "/month", "recurring", "订阅", "月付", "年付"
    ]

    ONE_TIME_KEYWORDS = [
        "one-time", "lifetime", "once", "永久", "一次性", "买断"
    ]

    USAGE_KEYWORDS = [
        "pay as you go", "usage-based", "per request", "per api call",
        "credits", "按量", "按次"
    ]

    FREEMIUM_KEYWORDS = [
        "free tier", "free plan", "freemium", "free forever", "免费版"
    ]

    # 垂直市场关键词
    VERTICAL_KEYWORDS = [
        "for lawyers", "for doctors", "for dentists", "for restaurants",
        "for real estate", "for photographers", "for musicians",
        "for teachers", "for coaches", "for therapists", "for accountants",
        "legal", "medical", "dental", "restaurant", "real estate",
        "photography", "music", "education", "coaching", "therapy", "accounting"
    ]

    # 内容驱动关键词
    CONTENT_KEYWORDS = [
        "blog", "newsletter", "course", "ebook", "tutorial", "guide",
        "template", "notion", "博客", "教程", "课程", "模板"
    ]

    # 社区驱动关键词
    COMMUNITY_KEYWORDS = [
        "open source", "community", "discord", "slack community",
        "github", "开源", "社区"
    ]

    # 护城河关键词
    DATA_MOAT_KEYWORDS = [
        "proprietary data", "unique dataset", "data advantage",
        "exclusive data", "data network"
    ]

    NETWORK_MOAT_KEYWORDS = [
        "marketplace", "platform", "network effect", "two-sided",
        "community", "social"
    ]

    BRAND_MOAT_KEYWORDS = [
        "trusted by", "used by", "featured in", "as seen on",
        "industry leader", "market leader"
    ]

    TECH_MOAT_KEYWORDS = [
        "patent", "proprietary technology", "unique algorithm",
        "breakthrough", "innovative technology"
    ]

    def __init__(self, db: AsyncSession):
        self.db = db

    async def analyze_product(self, startup: Startup) -> ProductScore:
        """
        分析单个产品的选品适合度

        Args:
            startup: Startup模型实例

        Returns:
            ProductScore对象
        """
        description = (startup.description or "").lower()
        description_words = len(description.split()) if description else 0

        # 粉丝-收入分析
        followers = startup.founder_followers  # 保持None以区分缺失数据
        revenue = startup.revenue_30d or 0
        has_follower_data = followers is not None

        # 如果没有粉丝数据，使用中位数估算（254）
        effective_followers = followers if has_follower_data else 254

        # 计算收入/粉丝比（衡量产品价值vs个人IP价值）
        follower_revenue_ratio = revenue / max(effective_followers, 1)

        # 产品驱动型判断：低粉丝但高收入
        # 如果没有粉丝数据，需要收入更高才能判定
        if has_follower_data:
            is_product_driven = (
                effective_followers < self.LOW_FOLLOWER_THRESHOLD and
                revenue > self.HIGH_REVENUE_THRESHOLD
            )
        else:
            # 没有粉丝数据时，只有收入非常高才认为是产品驱动
            is_product_driven = revenue > self.VERY_HIGH_REVENUE_THRESHOLD

        # IP依赖度评分（0-10，越低越好）
        if has_follower_data:
            # 粉丝越多，IP依赖度越高
            ip_dependency_score = min(10, (effective_followers / 5000) * 10)
        else:
            # 没有粉丝数据时，给一个中等偏低的默认值
            ip_dependency_score = 4.0

        # 小而美判断：描述简短 + 有一定收入
        is_small_beautiful = (
            description_words < self.SIMPLE_DESCRIPTION_WORDS and
            revenue > 500  # 降低门槛适配数据集
        )

        # 复杂度分析
        uses_llm = self._check_keywords(description, self.LLM_KEYWORDS)
        uses_llm_light = self._check_keywords(description, self.AI_LIGHT_KEYWORDS)
        requires_realtime = self._check_keywords(description, self.REALTIME_KEYWORDS)
        requires_big_data = self._check_keywords(description, self.BIG_DATA_KEYWORDS)
        requires_compliance = self._check_keywords(description, self.COMPLIANCE_KEYWORDS)

        # 计算复杂度等级
        complexity_count = sum([uses_llm, requires_realtime, requires_big_data, requires_compliance])

        if complexity_count == 0:
            tech_complexity = "low"
            maintenance_cost = "low"
        elif complexity_count == 1:
            tech_complexity = "medium"
            maintenance_cost = "medium"
        else:
            tech_complexity = "high"
            maintenance_cost = "high"

        # 合规风险等级
        compliance_risk = "high" if requires_compliance else "low"

        # 功能简洁度评分（0-10）
        feature_simplicity = 10 - min(10, complexity_count * 2.5)

        # 组合分析
        founded_months = self._calculate_company_age_months(startup.founded_date)

        # 组合1：低粉丝+高收入+简单描述+年轻公司
        # 核心逻辑：找到那些"不靠粉丝、产品本身就能赚钱"的新产品
        combo1 = (
            (has_follower_data and effective_followers < self.LOW_FOLLOWER_THRESHOLD) and
            revenue > self.HIGH_REVENUE_THRESHOLD and
            description_words < self.SIMPLE_DESCRIPTION_WORDS and
            founded_months is not None and founded_months < self.YOUNG_COMPANY_MONTHS
        )

        # 组合2：简单描述+中等收入+技术复杂度低
        # 核心逻辑：找"描述越简单、收入越不错"的产品，说明包装能力强或需求精准
        combo2 = (
            description_words < 30 and  # 非常简短的描述
            revenue > 500 and
            tech_complexity == "low"
        )

        # 组合3：小而美+低复杂度+有稳定收入
        # 核心逻辑：功能简单、不依赖复杂技术、能持续盈利
        combo3 = (
            is_small_beautiful and
            not uses_llm and
            not requires_realtime and
            revenue > 1000
        )

        # 计算综合适合度评分
        suitability = self._calculate_suitability(
            is_product_driven=is_product_driven,
            is_small_beautiful=is_small_beautiful,
            tech_complexity=tech_complexity,
            combo1=combo1,
            combo2=combo2,
            combo3=combo3,
            follower_revenue_ratio=follower_revenue_ratio,
            revenue=revenue,
            has_follower_data=has_follower_data
        )

        # 生成数据质量说明
        quality_notes = []
        if not has_follower_data:
            quality_notes.append("缺少粉丝数据，IP依赖度为估算值")
        if not startup.founded_date:
            quality_notes.append("缺少成立日期")
        if not startup.description:
            quality_notes.append("缺少产品描述")

        # ========== 计算新标签 (v2) ==========

        # 【收入验证维度】
        revenue_tier = self._calculate_revenue_tier(revenue)
        revenue_follower_ratio_level = self._calculate_revenue_follower_ratio_level(follower_revenue_ratio)

        # 【增长驱动维度】
        growth_driver = self._determine_growth_driver(
            is_product_driven, effective_followers, has_follower_data, description
        )

        # 【技术特征维度】
        ai_dependency_level = self._assess_ai_dependency(uses_llm, uses_llm_light, description)

        # 【商业模式维度】
        pricing_model = self._detect_pricing_model(description)
        target_customer = self._determine_target_customer(description)
        market_scope = self._determine_market_scope(description)

        # 【可复制性维度】
        feature_complexity = self._assess_feature_complexity(description_words, complexity_count)
        moat_type = self._identify_moat_type(description)
        startup_cost_level = self._estimate_startup_cost(
            uses_llm, requires_big_data, requires_compliance, requires_realtime
        )

        # 【生命周期维度】
        product_stage = self._determine_product_stage(founded_months)

        return ProductScore(
            startup_id=startup.id,
            name=startup.name,
            slug=startup.slug,
            is_product_driven=is_product_driven,
            ip_dependency_score=round(ip_dependency_score, 2),
            follower_revenue_ratio=round(follower_revenue_ratio, 4),
            is_small_and_beautiful=is_small_beautiful,
            description_word_count=description_words,
            feature_simplicity_score=round(feature_simplicity, 2),
            uses_llm_api=uses_llm,
            requires_realtime=requires_realtime,
            requires_large_data=requires_big_data,
            requires_compliance=requires_compliance,
            tech_complexity_level=tech_complexity,
            compliance_risk_level=compliance_risk,
            maintenance_cost_level=maintenance_cost,
            combo1_match=combo1,
            combo2_match=combo2,
            combo3_match=combo3,
            individual_dev_suitability=round(suitability, 2),
            has_follower_data=has_follower_data,
            data_quality_notes="; ".join(quality_notes) if quality_notes else "数据完整",
            # 新标签字段
            revenue_tier=revenue_tier,
            revenue_follower_ratio_level=revenue_follower_ratio_level,
            growth_driver=growth_driver,
            ai_dependency_level=ai_dependency_level,
            has_realtime_feature=requires_realtime,
            is_data_intensive=requires_big_data,
            has_compliance_requirement=requires_compliance,
            pricing_model=pricing_model,
            target_customer=target_customer,
            market_scope=market_scope,
            feature_complexity=feature_complexity,
            moat_type=moat_type,
            startup_cost_level=startup_cost_level,
            product_stage=product_stage,
        )

    def _check_keywords(self, text: str, keywords: List[str]) -> bool:
        """检查文本中是否包含关键词"""
        for kw in keywords:
            if kw.lower() in text:
                return True
        return False

    def _calculate_company_age_months(self, founded_date: str) -> Optional[int]:
        """计算公司成立月数"""
        if not founded_date:
            return None

        try:
            # 尝试解析常见日期格式
            # 格式如 "January 2024", "Jan 2024", "2024-01", "2024"
            date_str = founded_date.strip()

            # 尝试 "Month Year" 格式
            month_patterns = [
                r"(\w+)\s+(\d{4})",  # January 2024
                r"(\d{4})-(\d{2})",  # 2024-01
                r"(\d{4})"           # 2024
            ]

            for pattern in month_patterns:
                match = re.search(pattern, date_str)
                if match:
                    groups = match.groups()
                    if len(groups) == 2:
                        if groups[0].isdigit():
                            # 2024-01 格式
                            year = int(groups[0])
                            month = int(groups[1])
                        else:
                            # January 2024 格式
                            year = int(groups[1])
                            month_name = groups[0][:3].lower()
                            month_map = {
                                "jan": 1, "feb": 2, "mar": 3, "apr": 4,
                                "may": 5, "jun": 6, "jul": 7, "aug": 8,
                                "sep": 9, "oct": 10, "nov": 11, "dec": 12
                            }
                            month = month_map.get(month_name, 1)
                    else:
                        # 仅年份
                        year = int(groups[0])
                        month = 6  # 默认为年中

                    founded = datetime(year, month, 1)
                    now = datetime.now()
                    months = (now.year - founded.year) * 12 + (now.month - founded.month)
                    return max(0, months)

        except Exception:
            pass

        return None

    def _calculate_suitability(
        self,
        is_product_driven: bool,
        is_small_beautiful: bool,
        tech_complexity: str,
        combo1: bool,
        combo2: bool,
        combo3: bool,
        follower_revenue_ratio: float,
        revenue: float,
        has_follower_data: bool
    ) -> float:
        """
        计算个人开发者适合度评分

        评分逻辑：
        - 基础分5分
        - 产品驱动型（不靠IP）：+2分
        - 小而美（简单+盈利）：+1.5分
        - 技术复杂度低：+1.5分
        - 组合匹配：各+1分
        - 收入/粉丝比高：+0.5分
        - 高收入验证：+0.5分
        - 缺失粉丝数据：-1分（不确定性惩罚）
        """
        score = 5.0  # 基础分

        # 产品驱动型加分
        if is_product_driven:
            score += 2.0

        # 小而美加分
        if is_small_beautiful:
            score += 1.5

        # 复杂度影响
        if tech_complexity == "low":
            score += 1.5
        elif tech_complexity == "medium":
            score += 0.5
        else:  # high
            score -= 1.5

        # 组合匹配加分
        if combo1:
            score += 1.5  # 最理想的组合
        if combo2:
            score += 1.0  # 简单描述+收入不错
        if combo3:
            score += 1.0  # 小而美+低复杂度

        # 收入/粉丝比高说明产品本身有价值
        if follower_revenue_ratio > 2:
            score += 0.5

        # 有一定收入验证市场需求
        if revenue > 5000:
            score += 1.0
        elif revenue > 1000:
            score += 0.5

        # 缺失粉丝数据的不确定性惩罚
        if not has_follower_data:
            score -= 1.0

        return max(0, min(10, score))

    # ========== 新增标签计算方法 (v2) ==========

    def _calculate_revenue_tier(self, revenue: float) -> str:
        """计算收入层级"""
        if revenue < self.REVENUE_TIER_MICRO:
            return "micro"
        elif revenue < self.REVENUE_TIER_SMALL:
            return "small"
        elif revenue < self.REVENUE_TIER_MEDIUM:
            return "medium"
        else:
            return "large"

    def _calculate_revenue_follower_ratio_level(self, ratio: float) -> str:
        """计算收入/粉丝比等级"""
        if ratio > 2:
            return "high"
        elif ratio >= 0.5:
            return "medium"
        else:
            return "low"

    def _determine_growth_driver(
        self,
        is_product_driven: bool,
        followers: int,
        has_follower_data: bool,
        description: str
    ) -> str:
        """判断增长驱动类型"""
        # 检查内容驱动
        if self._check_keywords(description, self.CONTENT_KEYWORDS):
            return "content_driven"

        # 检查社区驱动
        if self._check_keywords(description, self.COMMUNITY_KEYWORDS):
            return "community_driven"

        # 产品驱动型
        if is_product_driven:
            return "product_driven"

        # IP驱动型（高粉丝）
        if has_follower_data and followers >= self.HIGH_FOLLOWER_THRESHOLD:
            return "ip_driven"

        # 默认为产品驱动
        return "product_driven"

    def _assess_ai_dependency(self, uses_llm: bool, uses_llm_light: bool, description: str) -> str:
        """评估AI依赖程度"""
        if not uses_llm and not uses_llm_light:
            return "none"

        # 检查是否是核心依赖（描述中AI相关词出现频率高）
        ai_heavy_indicators = ["powered by gpt", "built on", "uses openai", "llm-based", "ai-first"]
        if any(ind in description for ind in ai_heavy_indicators):
            return "heavy"

        if uses_llm:
            return "heavy"

        if uses_llm_light:
            return "light"

        return "none"

    def _detect_pricing_model(self, description: str) -> str:
        """检测定价模式"""
        if self._check_keywords(description, self.ONE_TIME_KEYWORDS):
            return "one_time"
        if self._check_keywords(description, self.USAGE_KEYWORDS):
            return "usage"
        if self._check_keywords(description, self.FREEMIUM_KEYWORDS):
            return "freemium"
        if self._check_keywords(description, self.SUBSCRIPTION_KEYWORDS):
            return "subscription"
        # 默认为订阅制（SaaS常见模式）
        return "subscription"

    def _determine_target_customer(self, description: str) -> str:
        """判断目标客户类型"""
        if self._check_keywords(description, self.B2D_KEYWORDS):
            return "b2d"
        if self._check_keywords(description, self.B2B_ENTERPRISE_KEYWORDS):
            return "b2b_enterprise"
        if self._check_keywords(description, self.B2B_KEYWORDS):
            return "b2b_smb"
        if self._check_keywords(description, self.B2C_KEYWORDS):
            return "b2c"
        # 默认为B2B SMB
        return "b2b_smb"

    def _determine_market_scope(self, description: str) -> str:
        """判断市场类型（水平/垂直）"""
        if self._check_keywords(description, self.VERTICAL_KEYWORDS):
            return "vertical"
        return "horizontal"

    def _assess_feature_complexity(self, description_words: int, complexity_count: int) -> str:
        """评估功能复杂度"""
        # 基于描述长度和技术复杂度综合判断
        if description_words < 30 and complexity_count == 0:
            return "simple"
        elif description_words > 100 or complexity_count >= 2:
            return "complex"
        else:
            return "moderate"

    def _identify_moat_type(self, description: str) -> str:
        """识别护城河类型"""
        moats = []

        if self._check_keywords(description, self.DATA_MOAT_KEYWORDS):
            moats.append("data")
        if self._check_keywords(description, self.NETWORK_MOAT_KEYWORDS):
            moats.append("network")
        if self._check_keywords(description, self.BRAND_MOAT_KEYWORDS):
            moats.append("brand")
        if self._check_keywords(description, self.TECH_MOAT_KEYWORDS):
            moats.append("tech")

        if not moats:
            return "none"

        return ",".join(moats)

    def _estimate_startup_cost(
        self,
        uses_llm: bool,
        requires_big_data: bool,
        requires_compliance: bool,
        requires_realtime: bool
    ) -> str:
        """估算启动成本"""
        cost_factors = sum([uses_llm, requires_big_data, requires_compliance, requires_realtime])

        if cost_factors == 0:
            return "low"
        elif cost_factors == 1:
            return "medium"
        else:
            return "high"

    def _determine_product_stage(self, founded_months: Optional[int]) -> str:
        """根据成立时间判断产品阶段"""
        if founded_months is None:
            return "growth"  # 默认值

        if founded_months < 6:
            return "early"
        elif founded_months < 24:
            return "growth"
        else:
            return "mature"

    async def find_opportunities(
        self,
        min_revenue: float = 0,
        max_complexity: str = "high",
        limit: int = 0,  # 0 = 无限制
        analyze_all: bool = False
    ) -> List[ProductScore]:
        """
        筛选适合个人开发者的机会产品

        Args:
            min_revenue: 最低收入门槛
            max_complexity: 最高复杂度 (low, medium, high)
            limit: 返回数量限制 (0 = 无限制)
            analyze_all: 是否分析所有产品

        Returns:
            ProductScore列表，按适合度降序排列
        """
        # 构建查询
        query = select(Startup).where(Startup.revenue_30d.isnot(None))
        
        if min_revenue > 0:
            query = query.where(Startup.revenue_30d >= min_revenue)
        
        query = query.order_by(desc(Startup.revenue_30d))
        
        # 如果不是分析全部，限制数量
        if not analyze_all and limit > 0:
            query = query.limit(limit * 3)  # 多取一些用于过滤
        
        result = await self.db.execute(query)
        startups = result.scalars().all()

        scores = []
        complexity_levels = {"low": 0, "medium": 1, "high": 2}
        max_level = complexity_levels.get(max_complexity, 2)

        for startup in startups:
            score = await self.analyze_product(startup)

            # 过滤复杂度
            product_level = complexity_levels.get(score.tech_complexity_level, 2)
            if product_level <= max_level:
                scores.append(score)

        # 按适合度排序
        scores.sort(key=lambda x: x.individual_dev_suitability, reverse=True)

        # 限制返回数量
        if limit > 0:
            return scores[:limit]
        return scores

    async def find_product_driven(
        self,
        min_revenue: float = 1000,  # 调整阈值
        max_followers: int = 1000,  # 调整阈值（75%产品<1K粉丝）
        limit: int = 30
    ) -> List[ProductScore]:
        """
        筛选产品驱动型产品（高收入低粉丝）

        这类产品的特点：
        - 收入主要来自产品价值，而非创始人IP
        - 适合复制，因为不需要先建立个人品牌
        """
        result = await self.db.execute(
            select(Startup)
            .where(Startup.revenue_30d >= min_revenue)
            .where(Startup.founder_followers.isnot(None))
            .where(Startup.founder_followers < max_followers)
            .order_by(desc(Startup.revenue_30d))
            .limit(limit * 2)  # 多取一些再筛选
        )
        startups = result.scalars().all()

        scores = []
        for startup in startups:
            score = await self.analyze_product(startup)
            if score.is_product_driven:
                scores.append(score)

        scores.sort(key=lambda x: x.individual_dev_suitability, reverse=True)
        return scores[:limit]

    async def find_small_beautiful(
        self,
        max_description_words: int = 40,  # 更严格的简短标准
        min_revenue: float = 500,
        limit: int = 30
    ) -> List[ProductScore]:
        """
        筛选小而美产品

        这类产品的特点：
        - 描述简短，说明功能聚焦
        - 有一定收入，验证需求存在
        - 技术复杂度通常较低
        """
        result = await self.db.execute(
            select(Startup)
            .where(Startup.revenue_30d >= min_revenue)
            .order_by(desc(Startup.revenue_30d))
            .limit(300)
        )
        startups = result.scalars().all()

        # 过滤描述长度并分析
        scores = []
        for startup in startups:
            desc_words = len((startup.description or "").split())
            if desc_words <= max_description_words and desc_words > 0:
                score = await self.analyze_product(startup)
                if score.is_small_and_beautiful:
                    scores.append(score)

        scores.sort(key=lambda x: x.individual_dev_suitability, reverse=True)
        return scores[:limit]

    async def save_analysis(self, score: ProductScore) -> ProductSelectionAnalysis:
        """保存选品分析结果到数据库"""
        # 检查是否已有分析
        result = await self.db.execute(
            select(ProductSelectionAnalysis)
            .where(ProductSelectionAnalysis.startup_id == score.startup_id)
        )
        existing = result.scalar_one_or_none()

        if existing:
            # 更新现有记录
            existing.is_product_driven = score.is_product_driven
            existing.ip_dependency_score = score.ip_dependency_score
            existing.follower_revenue_ratio = score.follower_revenue_ratio
            existing.is_small_and_beautiful = score.is_small_and_beautiful
            existing.description_word_count = score.description_word_count
            existing.feature_simplicity_score = score.feature_simplicity_score
            existing.uses_llm_api = score.uses_llm_api
            existing.requires_realtime = score.requires_realtime
            existing.requires_large_data = score.requires_large_data
            existing.requires_compliance = score.requires_compliance
            existing.tech_complexity_level = score.tech_complexity_level
            existing.compliance_risk_level = score.compliance_risk_level
            existing.maintenance_cost_level = score.maintenance_cost_level
            existing.combo1_match = score.combo1_match
            existing.combo2_match = score.combo2_match
            existing.combo3_match = score.combo3_match
            existing.individual_dev_suitability = score.individual_dev_suitability
            existing.has_follower_data = score.has_follower_data
            existing.data_quality_notes = score.data_quality_notes
            # 新增标签字段 (v2)
            existing.revenue_tier = score.revenue_tier
            existing.revenue_follower_ratio_level = score.revenue_follower_ratio_level
            existing.growth_driver = score.growth_driver
            existing.ai_dependency_level = score.ai_dependency_level
            existing.has_realtime_feature = score.has_realtime_feature
            existing.is_data_intensive = score.is_data_intensive
            existing.has_compliance_requirement = score.has_compliance_requirement
            existing.pricing_model = score.pricing_model
            existing.target_customer = score.target_customer
            existing.market_scope = score.market_scope
            existing.feature_complexity = score.feature_complexity
            existing.moat_type = score.moat_type
            existing.startup_cost_level = score.startup_cost_level
            existing.product_stage = score.product_stage
            existing.analyzed_at = datetime.utcnow()
            analysis = existing
        else:
            # 创建新记录
            analysis = ProductSelectionAnalysis(
                startup_id=score.startup_id,
                is_product_driven=score.is_product_driven,
                ip_dependency_score=score.ip_dependency_score,
                follower_revenue_ratio=score.follower_revenue_ratio,
                is_small_and_beautiful=score.is_small_and_beautiful,
                description_word_count=score.description_word_count,
                feature_simplicity_score=score.feature_simplicity_score,
                uses_llm_api=score.uses_llm_api,
                requires_realtime=score.requires_realtime,
                requires_large_data=score.requires_large_data,
                requires_compliance=score.requires_compliance,
                tech_complexity_level=score.tech_complexity_level,
                compliance_risk_level=score.compliance_risk_level,
                maintenance_cost_level=score.maintenance_cost_level,
                combo1_match=score.combo1_match,
                combo2_match=score.combo2_match,
                combo3_match=score.combo3_match,
                individual_dev_suitability=score.individual_dev_suitability,
                has_follower_data=score.has_follower_data,
                data_quality_notes=score.data_quality_notes,
                # 新增标签字段 (v2)
                revenue_tier=score.revenue_tier,
                revenue_follower_ratio_level=score.revenue_follower_ratio_level,
                growth_driver=score.growth_driver,
                ai_dependency_level=score.ai_dependency_level,
                has_realtime_feature=score.has_realtime_feature,
                is_data_intensive=score.is_data_intensive,
                has_compliance_requirement=score.has_compliance_requirement,
                pricing_model=score.pricing_model,
                target_customer=score.target_customer,
                market_scope=score.market_scope,
                feature_complexity=score.feature_complexity,
                moat_type=score.moat_type,
                startup_cost_level=score.startup_cost_level,
                product_stage=score.product_stage,
            )
            self.db.add(analysis)

        await self.db.commit()
        await self.db.refresh(analysis)
        return analysis
