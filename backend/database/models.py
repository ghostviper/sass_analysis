"""
SQLAlchemy models for SaaS Analysis Tool
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, Date, ForeignKey, JSON, Index
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all models"""
    pass


class Startup(Base):
    """Startup/Product information from TrustMRR"""
    __tablename__ = "startups"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True, index=True)

    # URLs
    website_url = Column(String(512), nullable=True)  # 产品官网
    logo_url = Column(String(512), nullable=True)  # Logo URL
    profile_url = Column(String(512), nullable=True)  # TrustMRR页面链接

    # Founder information
    founder_name = Column(String(255), nullable=True)
    founder_username = Column(String(255), nullable=True, index=True)
    founder_followers = Column(Integer, nullable=True)  # 粉丝数
    founder_social_platform = Column(String(50), nullable=True)  # 社交平台 (X, Twitter, LinkedIn)
    founder_avatar_url = Column(String(512), nullable=True)  # 创始人头像URL

    # Financial data
    total_revenue = Column(Float, nullable=True)  # 总收入
    mrr = Column(Float, nullable=True)  # 月经常性收入
    revenue_30d = Column(Float, nullable=True)  # 30天收入 (revenue_last_4_weeks)
    revenue_arr = Column(Float, nullable=True)  # 年经常性收入
    growth_rate = Column(Float, nullable=True)  # 增长率 (revenue_change_percent)
    profit_margin = Column(Float, nullable=True)  # 利润率

    # Sale information
    is_for_sale = Column(Boolean, default=False)
    asking_price = Column(Float, nullable=True)  # 要价
    multiple = Column(Float, nullable=True)  # 收入倍数
    buyers_interested = Column(Integer, nullable=True)  # 关注买家数

    # Company info
    founded_date = Column(String(50), nullable=True)  # 成立时间
    country = Column(String(100), nullable=True)  # 国家
    country_code = Column(String(10), nullable=True, index=True)  # 国家代码

    # Metrics
    rank = Column(Integer, nullable=True, index=True)  # 排名
    customers_count = Column(Integer, nullable=True)  # 活跃订阅数
    team_size = Column(Integer, nullable=True)

    # Status
    is_verified = Column(Boolean, default=False)
    verified_source = Column(String(50), nullable=True)  # Stripe, Paddle等

    # Metadata
    html_snapshot_path = Column(String(512), nullable=True)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Startup(name='{self.name}', revenue_30d=${self.revenue_30d})>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "description": self.description,
            "category": self.category,
            # URLs
            "website_url": self.website_url,
            "logo_url": self.logo_url,
            "profile_url": self.profile_url,
            # Founder
            "founder_name": self.founder_name,
            "founder_username": self.founder_username,
            "founder_followers": self.founder_followers,
            "founder_social_platform": self.founder_social_platform,
            "founder_avatar_url": self.founder_avatar_url,
            # Financial
            "total_revenue": self.total_revenue,
            "mrr": self.mrr,
            "revenue_30d": self.revenue_30d,
            "revenue_arr": self.revenue_arr,
            "growth_rate": self.growth_rate,
            "profit_margin": self.profit_margin,
            # Sale
            "is_for_sale": self.is_for_sale,
            "asking_price": self.asking_price,
            "multiple": self.multiple,
            "buyers_interested": self.buyers_interested,
            # Company
            "founded_date": self.founded_date,
            "country": self.country,
            "country_code": self.country_code,
            # Metrics
            "rank": self.rank,
            "customers_count": self.customers_count,
            "team_size": self.team_size,
            # Status
            "is_verified": self.is_verified,
            "verified_source": self.verified_source,
            # Metadata
            "html_snapshot_path": self.html_snapshot_path,
            "scraped_at": self.scraped_at.isoformat() if self.scraped_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class LeaderboardEntry(Base):
    """Leaderboard rankings for top 100 products"""
    __tablename__ = "leaderboard_entries"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    startup_slug = Column(String(255), nullable=False, index=True)  # Links to Startup
    rank = Column(Integer, nullable=False, index=True)
    
    # Metrics visible on leaderboard
    revenue_30d = Column(Float, nullable=True)
    growth_rate = Column(Float, nullable=True)
    multiple = Column(Float, nullable=True)
    
    # Metadata
    leaderboard_date = Column(DateTime, default=datetime.utcnow, index=True)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<LeaderboardEntry(rank={self.rank}, startup='{self.startup_slug}')>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "startup_slug": self.startup_slug,
            "rank": self.rank,
            "revenue_30d": self.revenue_30d,
            "growth_rate": self.growth_rate,
            "multiple": self.multiple,
            "leaderboard_date": self.leaderboard_date.isoformat() if self.leaderboard_date else None,
            "scraped_at": self.scraped_at.isoformat() if self.scraped_at else None,
        }


class Founder(Base):
    """Founder information from Leaderboard"""
    __tablename__ = "founders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    username = Column(String(255), unique=True, nullable=False, index=True)
    profile_url = Column(String(512), nullable=True)
    rank = Column(Integer, nullable=True, index=True)

    # Social media
    followers = Column(Integer, nullable=True)  # 粉丝数
    social_platform = Column(String(50), nullable=True)  # 社交平台

    # Metadata
    scraped_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Founder(name='{self.name}', rank={self.rank})>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "username": self.username,
            "profile_url": self.profile_url,
            "rank": self.rank,
            "followers": self.followers,
            "social_platform": self.social_platform,
            "scraped_at": self.scraped_at.isoformat() if self.scraped_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class CategoryAnalysis(Base):
    """赛道/领域分析结果表"""
    __tablename__ = "category_analysis"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String(100), nullable=False, index=True)
    analysis_date = Column(Date, nullable=False, index=True)

    # 基础统计
    total_projects = Column(Integer, default=0)
    total_revenue = Column(Float, default=0)
    avg_revenue = Column(Float, default=0)
    median_revenue = Column(Float, default=0)
    revenue_per_project = Column(Float, default=0)  # 领域单位项目收入

    # 收入分布
    top10_revenue_share = Column(Float, default=0)  # TOP10收入占比
    top50_revenue_share = Column(Float, default=0)  # TOP50收入占比
    revenue_std_dev = Column(Float, default=0)  # 收入标准差
    gini_coefficient = Column(Float, default=0)  # 基尼系数，衡量分布均匀度

    # 市场分类
    market_type = Column(String(50), nullable=True)  # red_ocean, blue_ocean, weak_demand, moderate
    market_type_reason = Column(Text, nullable=True)

    # 模板化产品分析
    template_clusters = Column(JSON, nullable=True)  # 相似产品分组

    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<CategoryAnalysis(category='{self.category}', market_type='{self.market_type}')>"

    def to_dict(self):
        return {
            "id": self.id,
            "category": self.category,
            "analysis_date": self.analysis_date.isoformat() if self.analysis_date else None,
            "total_projects": self.total_projects,
            "total_revenue": self.total_revenue,
            "avg_revenue": self.avg_revenue,
            "median_revenue": self.median_revenue,
            "revenue_per_project": self.revenue_per_project,
            "top10_revenue_share": self.top10_revenue_share,
            "top50_revenue_share": self.top50_revenue_share,
            "revenue_std_dev": self.revenue_std_dev,
            "gini_coefficient": self.gini_coefficient,
            "market_type": self.market_type,
            "market_type_reason": self.market_type_reason,
            "template_clusters": self.template_clusters,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ProductSelectionAnalysis(Base):
    """选品分析结果表"""
    __tablename__ = "product_selection_analysis"

    id = Column(Integer, primary_key=True, autoincrement=True)
    startup_id = Column(Integer, ForeignKey("startups.id"), nullable=False, unique=True, index=True)

    # ========== 原有字段 ==========
    # 产品驱动型指标
    is_product_driven = Column(Boolean, default=False)  # 产品驱动型标记
    ip_dependency_score = Column(Float, default=5.0)  # 0-10, IP依赖度，越低越好
    follower_revenue_ratio = Column(Float, default=0)  # 收入/粉丝比

    # 小而美指标
    is_small_and_beautiful = Column(Boolean, default=False)
    description_word_count = Column(Integer, default=0)
    feature_simplicity_score = Column(Float, default=5.0)  # 0-10, 功能简洁度

    # 复杂度分析
    uses_llm_api = Column(Boolean, default=False)  # 是否依赖大模型
    requires_realtime = Column(Boolean, default=False)  # 是否需要实时协作
    requires_large_data = Column(Boolean, default=False)  # 是否需要大规模数据
    requires_compliance = Column(Boolean, default=False)  # 是否需要合规（金融/医疗等）
    tech_complexity_level = Column(String(20), default="medium")  # low, medium, high
    compliance_risk_level = Column(String(20), default="low")  # low, medium, high
    maintenance_cost_level = Column(String(20), default="medium")  # low, medium, high

    # 组合分析匹配
    combo1_match = Column(Boolean, default=False)  # 低粉丝+高收入+简单描述+创立<1年
    combo2_match = Column(Boolean, default=False)  # 领域收入不高但中位数稳定
    combo3_match = Column(Boolean, default=False)  # 功能极少+定价清晰+收入持续

    # 综合评分
    individual_dev_suitability = Column(Float, default=5.0)  # 0-10, 个人开发适合度

    # 数据质量标记
    has_follower_data = Column(Boolean, default=True)
    data_quality_notes = Column(String(255), nullable=True)

    # ========== 新增标签字段 (v2) ==========

    # 【收入验证维度】
    revenue_tier = Column(String(20), nullable=True)  # micro(<$500) / small($500-2K) / medium($2K-10K) / large(>$10K)
    revenue_follower_ratio_level = Column(String(20), nullable=True)  # high(>2) / medium(0.5-2) / low(<0.5)

    # 【增长驱动维度】
    growth_driver = Column(String(20), nullable=True)  # product_driven / ip_driven / content_driven / community_driven

    # 【技术特征维度】
    ai_dependency_level = Column(String(20), nullable=True)  # none / light / heavy
    has_realtime_feature = Column(Boolean, nullable=True)  # 是否有实时功能
    is_data_intensive = Column(Boolean, nullable=True)  # 是否数据密集型
    has_compliance_requirement = Column(Boolean, nullable=True)  # 是否有合规要求

    # 【商业模式维度】
    pricing_model = Column(String(20), nullable=True)  # subscription / one_time / usage / freemium
    target_customer = Column(String(20), nullable=True)  # b2c / b2b_smb / b2b_enterprise / b2d
    market_scope = Column(String(20), nullable=True)  # horizontal / vertical

    # 【可复制性维度】
    feature_complexity = Column(String(20), nullable=True)  # simple / moderate / complex
    moat_type = Column(String(100), nullable=True)  # none / data / network / brand / tech (逗号分隔多选)
    startup_cost_level = Column(String(20), nullable=True)  # low(<$100) / medium($100-1K) / high(>$1K)

    # 【生命周期维度】
    product_stage = Column(String(20), nullable=True)  # early(<6月) / growth(6-24月) / mature(>24月)

    analyzed_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ProductSelectionAnalysis(startup_id={self.startup_id}, suitability={self.individual_dev_suitability})>"

    def to_dict(self):
        return {
            "id": self.id,
            "startup_id": self.startup_id,
            # 原有字段
            "is_product_driven": self.is_product_driven,
            "ip_dependency_score": self.ip_dependency_score,
            "follower_revenue_ratio": self.follower_revenue_ratio,
            "is_small_and_beautiful": self.is_small_and_beautiful,
            "description_word_count": self.description_word_count,
            "feature_simplicity_score": self.feature_simplicity_score,
            "uses_llm_api": self.uses_llm_api,
            "requires_realtime": self.requires_realtime,
            "requires_large_data": self.requires_large_data,
            "requires_compliance": self.requires_compliance,
            "tech_complexity_level": self.tech_complexity_level,
            "compliance_risk_level": self.compliance_risk_level,
            "maintenance_cost_level": self.maintenance_cost_level,
            "combo1_match": self.combo1_match,
            "combo2_match": self.combo2_match,
            "combo3_match": self.combo3_match,
            "individual_dev_suitability": self.individual_dev_suitability,
            "has_follower_data": self.has_follower_data,
            "data_quality_notes": self.data_quality_notes,
            # 新增标签字段 (v2)
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
            "analyzed_at": self.analyzed_at.isoformat() if self.analyzed_at else None,
        }

    def to_tags_dict(self):
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

    def to_scores_dict(self):
        """返回评分数据"""
        return {
            "individual_dev_suitability": self.individual_dev_suitability,
            "ip_dependency_score": self.ip_dependency_score,
            "feature_simplicity_score": self.feature_simplicity_score,
            "follower_revenue_ratio": self.follower_revenue_ratio,
        }


class LandingPageSnapshot(Base):
    """Landing Page快照表"""
    __tablename__ = "landing_page_snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    startup_id = Column(Integer, ForeignKey("startups.id"), nullable=False, index=True)
    url = Column(String(512), nullable=False)
    html_content = Column(Text, nullable=True)
    raw_text = Column(Text, nullable=True)
    snapshot_path = Column(String(512), nullable=True)

    # 状态
    status = Column(String(20), default="pending")  # pending, success, failed, timeout
    error_message = Column(Text, nullable=True)

    # 指标
    page_load_time_ms = Column(Integer, nullable=True)
    content_length = Column(Integer, nullable=True)

    scraped_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<LandingPageSnapshot(startup_id={self.startup_id}, status='{self.status}')>"

    def to_dict(self):
        return {
            "id": self.id,
            "startup_id": self.startup_id,
            "url": self.url,
            "snapshot_path": self.snapshot_path,
            "status": self.status,
            "error_message": self.error_message,
            "page_load_time_ms": self.page_load_time_ms,
            "content_length": self.content_length,
            "scraped_at": self.scraped_at.isoformat() if self.scraped_at else None,
        }


class LandingPageAnalysis(Base):
    """Landing Page AI分析结果表"""
    __tablename__ = "landing_page_analysis"

    id = Column(Integer, primary_key=True, autoincrement=True)
    startup_id = Column(Integer, ForeignKey("startups.id"), nullable=False, unique=True, index=True)
    snapshot_id = Column(Integer, ForeignKey("landing_page_snapshots.id"), nullable=True)

    # 用户分析
    target_audience = Column(JSON, nullable=True)  # 目标用户群体列表
    target_roles = Column(JSON, nullable=True)  # 目标角色/职位列表
    use_cases = Column(JSON, nullable=True)  # 使用场景列表

    # 功能分析
    core_features = Column(JSON, nullable=True)  # 核心功能列表
    feature_count = Column(Integer, default=0)
    value_propositions = Column(JSON, nullable=True)  # 价值主张列表

    # 痛点分析
    pain_points = Column(JSON, nullable=True)  # 痛点列表
    pain_point_sharpness = Column(Float, default=5.0)  # 0-10, 痛点锋利度
    uses_before_after = Column(Boolean, default=False)  # 是否使用新旧对比
    uses_emotional_words = Column(Boolean, default=False)  # 是否使用情绪词

    # 护城河分析
    potential_moats = Column(JSON, nullable=True)  # 潜在竞争优势列表

    # 定价分析
    pricing_model = Column(String(50), nullable=True)  # one-time, subscription, usage, hybrid
    pricing_tiers = Column(JSON, nullable=True)  # 定价层级详情
    pricing_clarity_score = Column(Float, default=5.0)  # 0-10, 定价清晰度
    has_free_tier = Column(Boolean, default=False)
    has_trial = Column(Boolean, default=False)

    # 转化分析
    cta_count = Column(Integer, default=0)  # CTA按钮数量
    cta_texts = Column(JSON, nullable=True)  # CTA文案列表
    conversion_funnel_steps = Column(Integer, default=0)  # 转化漏斗步骤数
    has_instant_value_demo = Column(Boolean, default=False)  # 是否有即时体验价值
    conversion_friendliness_score = Column(Float, default=5.0)  # 0-10, 转化友好度

    # 关键词分析
    industry_keywords = Column(JSON, nullable=True)  # 行业关键词密度
    headline_text = Column(Text, nullable=True)  # 主标题
    tagline_text = Column(Text, nullable=True)  # 副标题/标语

    # 综合评分
    positioning_clarity_score = Column(Float, default=5.0)  # 0-10, 定位清晰度
    replication_difficulty_score = Column(Float, default=5.0)  # 0-10, 复制难度
    individual_replicability_score = Column(Float, default=5.0)  # 0-10, 个人可复制性
    product_maturity_score = Column(Float, default=5.0)  # 0-10, 产品成熟度

    # 元数据
    ai_model_used = Column(String(100), nullable=True)
    ai_analysis_raw = Column(JSON, nullable=True)  # 原始AI响应
    analyzed_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<LandingPageAnalysis(startup_id={self.startup_id})>"

    def to_dict(self):
        return {
            "id": self.id,
            "startup_id": self.startup_id,
            "snapshot_id": self.snapshot_id,
            "target_audience": self.target_audience,
            "target_roles": self.target_roles,
            "use_cases": self.use_cases,
            "core_features": self.core_features,
            "feature_count": self.feature_count,
            "value_propositions": self.value_propositions,
            "pain_points": self.pain_points,
            "pain_point_sharpness": self.pain_point_sharpness,
            "uses_before_after": self.uses_before_after,
            "uses_emotional_words": self.uses_emotional_words,
            "potential_moats": self.potential_moats,
            "pricing_model": self.pricing_model,
            "pricing_tiers": self.pricing_tiers,
            "pricing_clarity_score": self.pricing_clarity_score,
            "has_free_tier": self.has_free_tier,
            "has_trial": self.has_trial,
            "cta_count": self.cta_count,
            "cta_texts": self.cta_texts,
            "conversion_funnel_steps": self.conversion_funnel_steps,
            "has_instant_value_demo": self.has_instant_value_demo,
            "conversion_friendliness_score": self.conversion_friendliness_score,
            "industry_keywords": self.industry_keywords,
            "headline_text": self.headline_text,
            "tagline_text": self.tagline_text,
            "positioning_clarity_score": self.positioning_clarity_score,
            "replication_difficulty_score": self.replication_difficulty_score,
            "individual_replicability_score": self.individual_replicability_score,
            "product_maturity_score": self.product_maturity_score,
            "ai_model_used": self.ai_model_used,
            "analyzed_at": self.analyzed_at.isoformat() if self.analyzed_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ComprehensiveAnalysis(Base):
    """产品综合分析结论表"""
    __tablename__ = "comprehensive_analysis"

    id = Column(Integer, primary_key=True, autoincrement=True)
    startup_id = Column(Integer, ForeignKey("startups.id"), nullable=False, unique=True, index=True)

    # 综合评分 (0-10)
    maturity_score = Column(Float, default=5.0)  # 产品成熟度
    positioning_clarity = Column(Float, default=5.0)  # 定位清晰度
    pain_point_sharpness = Column(Float, default=5.0)  # 痛点锋利度
    pricing_clarity = Column(Float, default=5.0)  # 定价清晰度
    conversion_friendliness = Column(Float, default=5.0)  # 转化友好度
    individual_replicability = Column(Float, default=5.0)  # 个人可复制性

    # 总体推荐
    overall_recommendation = Column(Float, default=5.0)  # 综合推荐指数 (0-10)
    analysis_summary = Column(JSON, nullable=True)  # 综合分析结论

    analyzed_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<ComprehensiveAnalysis(startup_id={self.startup_id}, recommendation={self.overall_recommendation})>"

    def to_dict(self):
        return {
            "id": self.id,
            "startup_id": self.startup_id,
            "maturity_score": self.maturity_score,
            "positioning_clarity": self.positioning_clarity,
            "pain_point_sharpness": self.pain_point_sharpness,
            "pricing_clarity": self.pricing_clarity,
            "conversion_friendliness": self.conversion_friendliness,
            "individual_replicability": self.individual_replicability,
            "overall_recommendation": self.overall_recommendation,
            "analysis_summary": self.analysis_summary,
            "analyzed_at": self.analyzed_at.isoformat() if self.analyzed_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class RevenueHistory(Base):
    """收入时序数据表 - 存储每日收入明细"""
    __tablename__ = "revenue_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    startup_id = Column(Integer, ForeignKey("startups.id"), nullable=False, index=True)

    # 时间点
    date = Column(Date, nullable=False, index=True)

    # 收入数据 (单位: 美分，与 TrustMRR 原始数据一致)
    revenue = Column(Integer, nullable=True)           # 总收入
    mrr = Column(Integer, nullable=True)               # 月度经常性收入
    charges = Column(Integer, nullable=True)           # 一次性收费
    subscription_revenue = Column(Integer, nullable=True)  # 订阅收入

    # 元数据
    scraped_at = Column(DateTime, default=datetime.utcnow)

    # 唯一约束: 同一产品同一日期只有一条记录
    __table_args__ = (
        Index('ix_revenue_history_startup_date', 'startup_id', 'date', unique=True),
    )

    def __repr__(self):
        return f"<RevenueHistory(startup_id={self.startup_id}, date={self.date}, revenue={self.revenue})>"

    def to_dict(self):
        return {
            "id": self.id,
            "startup_id": self.startup_id,
            "date": self.date.isoformat() if self.date else None,
            "revenue": self.revenue,
            "mrr": self.mrr,
            "charges": self.charges,
            "subscription_revenue": self.subscription_revenue,
            "scraped_at": self.scraped_at.isoformat() if self.scraped_at else None,
        }
