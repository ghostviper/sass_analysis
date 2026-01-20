"""
SQLAlchemy models for SaaS Analysis Tool

Compatible with PostgreSQL (Supabase), MySQL, and SQLite.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, Date, ForeignKey, JSON, Index, BigInteger
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """Base class for all models"""
    pass


# ============================================================================
# User Authentication Models
# ============================================================================

class User(Base):
    """用户表 - 与 fix_auth_tables.py 迁移脚本保持一致"""
    __tablename__ = "user"
    
    id = Column(String(255), primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    email_verified = Column("emailVerified", Boolean, default=False)  # camelCase in DB
    name = Column(String(255), nullable=True)
    image = Column(String(512), nullable=True)
    
    # 扩展字段
    plan = Column(String(20), default="free")
    locale = Column(String(10), default="zh-CN")
    daily_chat_limit = Column("dailyChatLimit", Integer, default=10)
    daily_chat_used = Column("dailyChatUsed", Integer, default=0)
    
    # 时间戳 (camelCase in DB)
    created_at = Column("createdAt", DateTime, default=datetime.utcnow)
    updated_at = Column("updatedAt", DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    accounts = relationship("Account", back_populates="user", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="user")
    
    def __repr__(self):
        return f"<User(id='{self.id}', email='{self.email}')>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "emailVerified": self.email_verified,
            "name": self.name,
            "image": self.image,
            "plan": self.plan,
            "locale": self.locale,
            "dailyChatLimit": self.daily_chat_limit,
            "dailyChatUsed": self.daily_chat_used,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
        }


class Account(Base):
    """第三方账户关联表"""
    __tablename__ = "account"
    
    id = Column(String(255), primary_key=True)
    user_id = Column("userId", String(255), ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    account_id = Column("accountId", String(255), nullable=False)
    provider_id = Column("providerId", String(255), nullable=False)
    access_token = Column("accessToken", Text, nullable=True)
    refresh_token = Column("refreshToken", Text, nullable=True)
    access_token_expires_at = Column("accessTokenExpiresAt", DateTime, nullable=True)
    scope = Column(String(255), nullable=True)
    id_token = Column("idToken", Text, nullable=True)
    password = Column(String(255), nullable=True)
    created_at = Column("createdAt", DateTime, default=datetime.utcnow)
    updated_at = Column("updatedAt", DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="accounts")
    
    __table_args__ = (
        Index('ix_account_provider_account', 'providerId', 'accountId', unique=True),
    )
    
    def __repr__(self):
        return f"<Account(id='{self.id}', provider='{self.provider_id}')>"


# Session 和 Verification 表已移除
# 当前使用 JWT 无状态认证，不需要服务端会话存储
# 如需实现邮箱验证/密码重置功能，可以重新添加 Verification 表


# ============================================================================
# Business Data Models
# ============================================================================

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
    founder_id = Column(Integer, ForeignKey("founders.id"), nullable=True, index=True)
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

    founder = relationship("Founder", back_populates="startups")
    
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
            "founder_id": self.founder_id,
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

    startups = relationship("Startup", back_populates="founder")
    
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
    html_content = Column(Text, nullable=True)  # Text works for all databases
    raw_text = Column(Text, nullable=True)  # Text works for all databases
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


# ============================================================================
# Chat Session Models
# ============================================================================

class ChatSession(Base):
    """用户会话表 - 存储会话基本信息"""
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), unique=True, nullable=False, index=True)  # UUID格式的会话ID

    # 会话元信息
    title = Column(String(255), nullable=True)  # 会话标题（可从首条消息自动生成）
    summary = Column(Text, nullable=True)  # 会话摘要

    # 用户标识 - 关联 user 表
    user_id = Column(String(64), ForeignKey("user.id", ondelete="SET NULL"), nullable=True, index=True)

    # 会话配置
    enable_web_search = Column(Boolean, default=False)  # 是否启用联网搜索
    context_type = Column(String(20), nullable=True)  # database / url
    context_value = Column(Text, nullable=True)  # 关联的产品名或URL
    context_products = Column(JSON, nullable=True)  # 关联的多个产品名列表

    # 统计信息
    message_count = Column(Integer, default=0)  # 消息数量
    turn_count = Column(Integer, default=0)  # 对话轮数
    total_cost = Column(Float, default=0.0)  # 累计消耗（美元）
    total_input_tokens = Column(Integer, default=0)  # 累计输入token
    total_output_tokens = Column(Integer, default=0)  # 累计输出token

    # 状态
    is_archived = Column(Boolean, default=False)  # 是否已归档
    is_deleted = Column(Boolean, default=False)  # 是否已删除（软删除）

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_message_at = Column(DateTime, nullable=True)  # 最后一条消息时间
    
    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ChatSession(session_id='{self.session_id}', title='{self.title}')>"

    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "title": self.title,
            "summary": self.summary,
            "user_id": self.user_id,
            "enable_web_search": self.enable_web_search,
            "context_type": self.context_type,
            "context_value": self.context_value,
            "context_products": self.context_products,
            "message_count": self.message_count,
            "turn_count": self.turn_count,
            "total_cost": self.total_cost,
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "is_archived": self.is_archived,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_message_at": self.last_message_at.isoformat() if self.last_message_at else None,
        }

    def to_list_dict(self):
        """返回列表展示用的精简数据"""
        return {
            "session_id": self.session_id,
            "title": self.title,
            "message_count": self.message_count,
            "turn_count": self.turn_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_message_at": self.last_message_at.isoformat() if self.last_message_at else None,
        }


class ChatMessage(Base):
    """聊天消息表 - 存储每条消息"""
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), ForeignKey("chat_sessions.session_id", ondelete="CASCADE"), nullable=False, index=True)

    # 消息内容
    role = Column(String(20), nullable=False)  # user / assistant / system
    content = Column(Text, nullable=False)  # 消息内容

    # 消息序号
    sequence = Column(Integer, nullable=False)  # 消息在会话中的序号

    # 工具调用信息（仅assistant消息）
    tool_calls = Column(JSON, nullable=True)  # 工具调用记录 [{name, input, output, duration_ms}]

    # Token统计（仅assistant消息）
    input_tokens = Column(Integer, nullable=True)
    output_tokens = Column(Integer, nullable=True)
    cost = Column(Float, nullable=True)  # 本条消息消耗（美元）

    # 元数据
    model = Column(String(100), nullable=True)  # 使用的模型
    duration_ms = Column(Integer, nullable=True)  # 响应耗时（毫秒）
    
    # Claude Agent SDK checkpoint ID (用于多轮对话恢复)
    checkpoint_id = Column(String(64), nullable=True, index=True)  # UserMessage UUID

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages")

    # 索引
    __table_args__ = (
        Index('ix_chat_messages_session_sequence', 'session_id', 'sequence'),
    )

    def __repr__(self):
        return f"<ChatMessage(session_id='{self.session_id}', role='{self.role}', seq={self.sequence})>"

    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "role": self.role,
            "content": self.content,
            "sequence": self.sequence,
            "tool_calls": self.tool_calls,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "cost": self.cost,
            "model": self.model,
            "duration_ms": self.duration_ms,
            "checkpoint_id": self.checkpoint_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# ============================================================================
# Product Hunt Data Models
# ============================================================================

class ProductHuntPost(Base):
    """
    Product Hunt 产品数据表
    
    独立存储 PH 数据，与 Startup 表分离。
    后续可通过 name/url 匹配关联。
    """
    __tablename__ = "producthunt_posts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Product Hunt 原始 ID 和标识
    ph_id = Column(String(50), unique=True, nullable=False, index=True)  # PH 的 ID
    slug = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    tagline = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    
    # URLs
    url = Column(String(512), nullable=True)  # PH 跟踪链接（带 utm 参数）
    website = Column(String(512), nullable=True)  # PH 返回的 website（可能是重定向链接）
    website_resolved = Column(String(512), nullable=True)  # 解析后的真实官网地址
    ph_url = Column(String(512), nullable=True)  # PH 页面链接
    thumbnail_url = Column(String(512), nullable=True)
    
    # 互动指标（核心数据）
    votes_count = Column(Integer, default=0, index=True)  # 点赞数
    comments_count = Column(Integer, default=0)  # 评论数
    reviews_count = Column(Integer, default=0)  # 评价数
    reviews_rating = Column(Float, nullable=True)  # 评分
    
    # 时间信息
    featured_at = Column(DateTime, nullable=True, index=True)  # 上榜时间
    ph_created_at = Column(DateTime, nullable=True)  # PH 上创建时间
    
    # 分类信息（JSON 存储多个 topic）
    topics = Column(Text, nullable=True)  # JSON string: [{"id": "xxx", "name": "AI", "slug": "ai"}, ...]
    
    # Makers 信息（JSON 存储）
    makers = Column(Text, nullable=True)  # JSON string: [{"id": "xxx", "name": "John", "username": "john"}, ...]
    
    # 创建者信息（JSON 存储）
    user = Column(Text, nullable=True)  # JSON string: {"id": "xxx", "name": "John", "username": "john", "headline": "..."}
    
    # 媒体资源（JSON 存储）
    media = Column(Text, nullable=True)  # JSON string: [{"url": "xxx", "type": "image"}, ...]
    product_links = Column(Text, nullable=True)  # JSON string: [{"url": "xxx"}, ...]
    
    # 关联字段（可选，用于与 Startup 表关联）
    matched_startup_id = Column(Integer, ForeignKey("startups.id", ondelete="SET NULL"), nullable=True, index=True)
    match_confidence = Column(Float, nullable=True)  # 匹配置信度 0-1
    
    # 元数据
    raw_data = Column(Text, nullable=True)  # 原始 API 响应 (JSON string)
    synced_at = Column(DateTime, default=datetime.utcnow, index=True)  # 同步时间
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<ProductHuntPost(name='{self.name}', votes={self.votes_count})>"

    def to_dict(self):
        return {
            "id": self.id,
            "ph_id": self.ph_id,
            "slug": self.slug,
            "name": self.name,
            "tagline": self.tagline,
            "description": self.description,
            "url": self.url,
            "website": self.website,
            "website_resolved": self.website_resolved,
            "ph_url": self.ph_url,
            "thumbnail_url": self.thumbnail_url,
            "votes_count": self.votes_count,
            "comments_count": self.comments_count,
            "reviews_count": self.reviews_count,
            "reviews_rating": self.reviews_rating,
            "featured_at": self.featured_at.isoformat() if self.featured_at else None,
            "ph_created_at": self.ph_created_at.isoformat() if self.ph_created_at else None,
            "topics": self.topics,
            "makers": self.makers,
            "user": self.user,
            "media": self.media,
            "product_links": self.product_links,
            "matched_startup_id": self.matched_startup_id,
            "match_confidence": self.match_confidence,
            "synced_at": self.synced_at.isoformat() if self.synced_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def to_list_dict(self):
        """列表展示用的精简字典"""
        return {
            "id": self.id,
            "ph_id": self.ph_id,
            "slug": self.slug,
            "name": self.name,
            "tagline": self.tagline,
            "url": self.url,
            "website": self.website,
            "ph_url": self.ph_url,
            "thumbnail_url": self.thumbnail_url,
            "votes_count": self.votes_count,
            "comments_count": self.comments_count,
            "featured_at": self.featured_at.isoformat() if self.featured_at else None,
            "topics": self.topics,
            "matched_startup_id": self.matched_startup_id,
        }


# ============================================================================
# Curation System Models (母题判断与策展)
# ============================================================================

class MotherThemeJudgment(Base):
    """母题判断结果表"""
    __tablename__ = "mother_theme_judgments"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    startup_id = Column(Integer, ForeignKey("startups.id"), nullable=False, index=True)
    theme_key = Column(String(50), nullable=False, index=True)
    judgment = Column(String(100))
    confidence = Column(String(20))
    reasons = Column(JSON)
    evidence_fields = Column(JSON)
    uncertainties = Column(JSON)
    prompt_version = Column(String(20))
    model = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Unique constraint: one judgment per startup per theme
    __table_args__ = (
        Index('ix_judgment_startup_theme', 'startup_id', 'theme_key', unique=True),
    )
    
    # Relationship
    startup = relationship("Startup", backref="mother_theme_judgments")
    
    def to_dict(self):
        return {
            "id": self.id,
            "startup_id": self.startup_id,
            "theme_key": self.theme_key,
            "judgment": self.judgment,
            "confidence": self.confidence,
            "reasons": self.reasons,
            "evidence_fields": self.evidence_fields,
            "uncertainties": self.uncertainties,
            "prompt_version": self.prompt_version,
            "model": self.model,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class DiscoverTopic(Base):
    """发现页专题表"""
    __tablename__ = "discover_topics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    topic_key = Column(String(100), unique=True, index=True)
    title = Column(String(200), nullable=False)
    title_zh = Column(String(200))  # 中文标题
    title_en = Column(String(200))  # 英文标题
    description = Column(Text)
    description_zh = Column(Text)  # 中文描述
    description_en = Column(Text)  # 英文描述
    curator_role = Column(String(50))
    generation_pattern = Column(String(50))
    filter_rules = Column(JSON)
    cta_text = Column(String(200))
    cta_text_zh = Column(String(200))  # 中文 CTA
    cta_text_en = Column(String(200))  # 英文 CTA
    is_active = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    products = relationship("TopicProduct", back_populates="topic", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            "id": self.id,
            "topic_key": self.topic_key,
            "title": self.title,
            "title_zh": self.title_zh,
            "title_en": self.title_en,
            "description": self.description,
            "description_zh": self.description_zh,
            "description_en": self.description_en,
            "curator_role": self.curator_role,
            "generation_pattern": self.generation_pattern,
            "filter_rules": self.filter_rules,
            "cta_text": self.cta_text,
            "cta_text_zh": self.cta_text_zh,
            "cta_text_en": self.cta_text_en,
            "is_active": self.is_active,
            "display_order": self.display_order,
            "product_count": len(self.products) if self.products else 0,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class TopicProduct(Base):
    """专题-产品关联表"""
    __tablename__ = "topic_products"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    topic_id = Column(Integer, ForeignKey("discover_topics.id"), nullable=False, index=True)
    startup_id = Column(Integer, ForeignKey("startups.id"), nullable=False, index=True)
    ai_label = Column(String(200))
    counter_intuitive_point = Column(Text)
    display_order = Column(Integer, default=0)
    
    # Relationships
    topic = relationship("DiscoverTopic", back_populates="products")
    startup = relationship("Startup")
    
    def to_dict(self):
        return {
            "id": self.id,
            "topic_id": self.topic_id,
            "startup_id": self.startup_id,
            "ai_label": self.ai_label,
            "counter_intuitive_point": self.counter_intuitive_point,
            "display_order": self.display_order,
        }


# ============================================================================
# Discover Page Extended Models (每日策展、爆款故事、用户偏好)
# ============================================================================

class DailyCuration(Base):
    """每日策展表 - TodayCuration 区块"""
    __tablename__ = "daily_curations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    curation_key = Column(String(100), unique=True, nullable=False, index=True)
    
    # 双语标题
    title = Column(String(200), nullable=False)
    title_zh = Column(String(200))
    title_en = Column(String(200))
    
    # 双语描述
    description = Column(Text)
    description_zh = Column(Text)
    description_en = Column(Text)
    
    # 双语洞察
    insight = Column(String(300))
    insight_zh = Column(String(300))
    insight_en = Column(String(300))
    
    # 标签
    tag = Column(String(100))
    tag_zh = Column(String(100))
    tag_en = Column(String(100))
    tag_color = Column(String(20), default='amber')
    
    # 策展类型
    curation_type = Column(String(50))  # contrast/cognitive/action/niche
    
    # 生成规则
    filter_rules = Column(JSON)
    conflict_dimensions = Column(JSON)
    
    # 时间和状态
    curation_date = Column(Date, nullable=False, index=True)
    is_active = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)
    
    # 元数据
    ai_generated = Column(Boolean, default=True)
    generation_model = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    products = relationship("CurationProduct", back_populates="curation", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            "id": self.id,
            "curation_key": self.curation_key,
            "title": self.title,
            "title_zh": self.title_zh,
            "title_en": self.title_en,
            "description": self.description,
            "description_zh": self.description_zh,
            "description_en": self.description_en,
            "insight": self.insight,
            "insight_zh": self.insight_zh,
            "insight_en": self.insight_en,
            "tag": self.tag,
            "tag_zh": self.tag_zh,
            "tag_en": self.tag_en,
            "tag_color": self.tag_color,
            "curation_type": self.curation_type,
            "filter_rules": self.filter_rules,
            "conflict_dimensions": self.conflict_dimensions,
            "curation_date": self.curation_date.isoformat() if self.curation_date else None,
            "is_active": self.is_active,
            "display_order": self.display_order,
            "product_count": len(self.products) if self.products else 0,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class CurationProduct(Base):
    """策展-产品关联表"""
    __tablename__ = "curation_products"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    curation_id = Column(Integer, ForeignKey("daily_curations.id", ondelete="CASCADE"), nullable=False, index=True)
    startup_id = Column(Integer, ForeignKey("startups.id", ondelete="CASCADE"), nullable=False, index=True)
    
    highlight_zh = Column(String(200))
    highlight_en = Column(String(200))
    display_order = Column(Integer, default=0)
    
    # Relationships
    curation = relationship("DailyCuration", back_populates="products")
    startup = relationship("Startup")
    
    __table_args__ = (
        Index('ix_curation_product_unique', 'curation_id', 'startup_id', unique=True),
    )
    
    def to_dict(self):
        return {
            "id": self.id,
            "curation_id": self.curation_id,
            "startup_id": self.startup_id,
            "highlight_zh": self.highlight_zh,
            "highlight_en": self.highlight_en,
            "display_order": self.display_order,
        }


class SuccessStory(Base):
    """爆款故事表 - SuccessBreakdown 区块"""
    __tablename__ = "success_stories"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    startup_id = Column(Integer, ForeignKey("startups.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # 产品信息
    product_name = Column(String(200), nullable=False)
    product_logo = Column(String(20))  # emoji
    product_mrr = Column(String(50))
    founder_name = Column(String(200))
    
    # 双语标题
    title = Column(String(300), nullable=False)
    title_zh = Column(String(300))
    title_en = Column(String(300))
    
    # 双语副标题
    subtitle = Column(String(300))
    subtitle_zh = Column(String(300))
    subtitle_en = Column(String(300))
    
    # 样式
    gradient = Column(String(100), default='from-emerald-500/10 to-teal-500/5')
    accent_color = Column(String(20), default='emerald')
    
    # 状态
    is_featured = Column(Boolean, default=False, index=True)
    is_active = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    timeline_events = relationship("StoryTimelineEvent", back_populates="story", cascade="all, delete-orphan")
    key_insights = relationship("StoryKeyInsight", back_populates="story", cascade="all, delete-orphan")
    startup = relationship("Startup")
    
    def to_dict(self):
        return {
            "id": self.id,
            "startup_id": self.startup_id,
            "product_name": self.product_name,
            "product_logo": self.product_logo,
            "product_mrr": self.product_mrr,
            "founder_name": self.founder_name,
            "title": self.title,
            "title_zh": self.title_zh,
            "title_en": self.title_en,
            "subtitle": self.subtitle,
            "subtitle_zh": self.subtitle_zh,
            "subtitle_en": self.subtitle_en,
            "gradient": self.gradient,
            "accent_color": self.accent_color,
            "is_featured": self.is_featured,
            "is_active": self.is_active,
            "timeline": [e.to_dict() for e in self.timeline_events] if self.timeline_events else [],
            "key_insights": [i.to_dict() for i in self.key_insights] if self.key_insights else [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class StoryTimelineEvent(Base):
    """故事时间线事件表"""
    __tablename__ = "story_timeline_events"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    story_id = Column(Integer, ForeignKey("success_stories.id", ondelete="CASCADE"), nullable=False, index=True)
    
    event_date = Column(String(20), nullable=False)
    event_text = Column(String(500), nullable=False)
    event_text_zh = Column(String(500))
    event_text_en = Column(String(500))
    display_order = Column(Integer, default=0)
    
    # Relationships
    story = relationship("SuccessStory", back_populates="timeline_events")
    
    def to_dict(self):
        return {
            "date": self.event_date,
            "event": self.event_text,
            "event_zh": self.event_text_zh,
            "event_en": self.event_text_en,
        }


class StoryKeyInsight(Base):
    """故事关键洞察表"""
    __tablename__ = "story_key_insights"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    story_id = Column(Integer, ForeignKey("success_stories.id", ondelete="CASCADE"), nullable=False, index=True)
    
    insight_text = Column(String(300), nullable=False)
    insight_text_zh = Column(String(300))
    insight_text_en = Column(String(300))
    display_order = Column(Integer, default=0)
    
    # Relationships
    story = relationship("SuccessStory", back_populates="key_insights")
    
    def to_dict(self):
        return {
            "text": self.insight_text,
            "text_zh": self.insight_text_zh,
            "text_en": self.insight_text_en,
        }


class UserPreference(Base):
    """用户偏好表 - ForYouSection 区块"""
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), ForeignKey("user.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    
    preferred_roles = Column(JSON, default=list)
    interested_categories = Column(JSON, default=list)
    skill_level = Column(String(20), default='beginner')
    goal = Column(String(50))
    time_commitment = Column(String(20))
    tech_stack = Column(JSON, default=list)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "preferred_roles": self.preferred_roles,
            "interested_categories": self.interested_categories,
            "skill_level": self.skill_level,
            "goal": self.goal,
            "time_commitment": self.time_commitment,
            "tech_stack": self.tech_stack,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class FeaturedCreator(Base):
    """精选创作者表 - CreatorUniverse 区块"""
    __tablename__ = "featured_creators"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    name = Column(String(200), nullable=False)
    handle = Column(String(100))
    avatar = Column(String(20))  # emoji
    bio_zh = Column(String(300))
    bio_en = Column(String(300))
    
    tag = Column(String(100))
    tag_zh = Column(String(100))
    tag_en = Column(String(100))
    tag_color = Column(String(20), default='amber')
    
    total_mrr = Column(String(50))
    followers = Column(String(50))
    product_count = Column(Integer, nullable=True)  # 产品数量
    
    founder_username = Column(String(255), index=True)
    founder_id = Column(Integer, ForeignKey("founders.id"), nullable=True, index=True)
    
    is_featured = Column(Boolean, default=True, index=True)
    display_order = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    founder = relationship("Founder")
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "handle": self.handle,
            "avatar": self.avatar,
            "bio_zh": self.bio_zh,
            "bio_en": self.bio_en,
            "tag": self.tag,
            "tag_zh": self.tag_zh,
            "tag_en": self.tag_en,
            "tag_color": self.tag_color,
            "total_mrr": self.total_mrr,
            "followers": self.followers,
            "product_count": self.product_count,
            "founder_username": self.founder_username,
            "founder_id": self.founder_id,
            "is_featured": self.is_featured,
            "display_order": self.display_order,
        }
