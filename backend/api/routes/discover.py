"""
Discover API Routes - 发现页 API

从数据库读取专题数据（discover_topics 和 topic_products 表）
支持双语 (i18n)

区块：
1. TopicCollections - 专题合集
2. TodayCuration - 今日策展
3. SuccessBreakdown - 爆款解剖
4. CreatorUniverse - 创作者宇宙
5. ForYouSection - 为你推荐
"""

from datetime import date, timedelta
from typing import Optional, List, Dict
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, func, desc, and_, or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload
from urllib.parse import urlparse

from database.db import get_db_session
from database.models import (
    DiscoverTopic, TopicProduct, Startup, MotherThemeJudgment, Founder,
    DailyCuration, CurationProduct, SuccessStory, StoryTimelineEvent,
    StoryKeyInsight, FeaturedCreator, UserPreference
)

router = APIRouter()

# =============================================================================
# 常量配置
# =============================================================================

# 关键标签映射（根据角色选择展示哪些标签）
KEY_TAGS_BY_ROLE = {
    'cautious_indie_dev': ['solo_feasibility', 'entry_barrier', 'primary_risk'],
    'quick_starter': ['entry_barrier', 'mvp_clarity', 'solo_feasibility'],
    'opportunity_hunter': ['opportunity_validity', 'demand_type', 'entry_barrier'],
    'anti_bubble': ['opportunity_validity', 'primary_risk', 'demand_type'],
    'product_driven_fan': ['success_driver', 'differentiation_point', 'positioning_insight'],
    'niche_hunter': ['positioning_insight', 'differentiation_point', 'demand_type'],
    'ux_differentiator': ['differentiation_point', 'positioning_insight', 'success_driver'],
    'low_risk_starter': ['entry_barrier', 'primary_risk', 'mvp_clarity'],
    'content_to_product': ['success_driver', 'demand_type', 'solo_feasibility'],
    'scenario_focused': ['positioning_insight', 'mvp_clarity', 'demand_type'],
}

# 标签显示名称映射 (双语)
LABEL_MAP = {
    'opportunity_validity': {'zh': '机会真实性', 'en': 'Opportunity Validity'},
    'demand_type': {'zh': '需求类型', 'en': 'Demand Type'},
    'solo_feasibility': {'zh': '独立可行性', 'en': 'Solo Feasibility'},
    'entry_barrier': {'zh': '入场门槛', 'en': 'Entry Barrier'},
    'primary_risk': {'zh': '主要风险', 'en': 'Primary Risk'},
    'mvp_clarity': {'zh': 'MVP清晰度', 'en': 'MVP Clarity'},
    'success_driver': {'zh': '成功驱动', 'en': 'Success Driver'},
    'positioning_insight': {'zh': '定位洞察', 'en': 'Positioning Insight'},
    'differentiation_point': {'zh': '差异化点', 'en': 'Differentiation'},
}


HIGH_FOLLOWER_THRESHOLD = 5000


def build_social_url(handle: Optional[str], platform: Optional[str], username: Optional[str]) -> Optional[str]:
    """构建创作者社交链接"""
    if handle:
        trimmed = handle.strip()
        if trimmed.startswith("http://") or trimmed.startswith("https://"):
            return trimmed
    name = None
    if handle:
        name = handle.strip()
    if name and name.startswith("@"):
        name = name[1:]
    if not name:
        name = username
    if not name:
        return None
    platform_value = (platform or "").lower()
    if "linkedin" in platform_value:
        return f"https://www.linkedin.com/in/{name}"
    if "github" in platform_value:
        return f"https://github.com/{name}"
    return f"https://x.com/{name}"


def normalize_creator_key(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    trimmed = value.strip()
    if not trimmed:
        return None
    if trimmed.startswith("http://") or trimmed.startswith("https://"):
        parsed = urlparse(trimmed)
        if parsed.path:
            trimmed = parsed.path.strip("/").split("/")[-1]
    if trimmed.startswith("@"):
        trimmed = trimmed[1:]
    trimmed = trimmed.strip()
    return trimmed.lower() if trimmed else None


def count_products_by_id(products: List[dict]) -> int:
    ids = {p.get('id') for p in products if p.get('id') is not None}
    return len(ids) if ids else len(products)


def format_followers(count: Optional[int]) -> Optional[str]:
    if not count:
        return None
    return f"{count / 1000:.0f}k" if count >= 1000 else str(count)


def extract_key_tags(judgments: dict, role: str, founder_followers: Optional[int] = None) -> List[dict]:
    """提取关键标签"""
    key_fields = KEY_TAGS_BY_ROLE.get(role, ['solo_feasibility', 'entry_barrier', 'primary_risk'])
    tags = []
    
    for field in key_fields:
        if field in judgments:
            judgment_data = judgments[field]
            value = judgment_data.get('judgment', '') if isinstance(judgment_data, dict) else str(judgment_data)
            if field == 'success_driver' and founder_followers is not None and founder_followers >= HIGH_FOLLOWER_THRESHOLD:
                value = 'IP/创作者驱动'
            label_data = LABEL_MAP.get(field, {'zh': field, 'en': field})
            tags.append({
                'key': field,
                'label': label_data['zh'],
                'label_zh': label_data['zh'],
                'label_en': label_data['en'],
                'value': value
            })
    
    return tags[:4]


# =============================================================================
# 1. TopicCollections - 专题合集
# =============================================================================

@router.get("/discover/topics")
async def get_topics():
    """获取专题列表（从数据库，支持双语）"""
    async with get_db_session() as db:
        query = (
            select(DiscoverTopic)
            .where(DiscoverTopic.is_active == True)
            .options(selectinload(DiscoverTopic.products))
            .order_by(DiscoverTopic.display_order)
        )
        result = await db.execute(query)
        db_topics = result.scalars().all()
        
        if not db_topics:
            return {'topics': []}
        
        topics = []
        for topic in db_topics:
            role = topic.curator_role or ''
            
            # 获取前3个产品作为预览
            top_products = []
            product_ids = [tp.startup_id for tp in topic.products[:3]]
            
            if product_ids:
                startup_query = select(Startup).where(Startup.id.in_(product_ids))
                startup_result = await db.execute(startup_query)
                startups = {s.id: s for s in startup_result.scalars()}
                
                for tp in topic.products[:3]:
                    startup = startups.get(tp.startup_id)
                    if startup:
                        top_products.append({
                            'name': startup.name,
                            'revenue_30d': startup.revenue_30d,
                        })
            
            topics.append({
                'id': topic.topic_key,
                'title': topic.title,
                'title_zh': topic.title_zh or topic.title,
                'title_en': topic.title_en or topic.title,
                'description': topic.description,
                'description_zh': topic.description_zh or topic.description,
                'description_en': topic.description_en or topic.description,
                'curator_role': role,
                'product_count': len(topic.products),
                'top_products': top_products,
            })
        
        return {'topics': topics}


@router.get("/discover/topics/{topic_id}")
async def get_topic_detail(
    topic_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sort: str = Query('revenue'),
):
    """获取专题详情（从数据库，支持双语）"""
    async with get_db_session() as db:
        query = (
            select(DiscoverTopic)
            .where(DiscoverTopic.topic_key == topic_id)
            .options(selectinload(DiscoverTopic.products))
        )
        result = await db.execute(query)
        topic = result.scalar_one_or_none()
        
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")
        
        role = topic.curator_role or ''
        all_product_ids = [tp.startup_id for tp in topic.products]
        
        def build_topic_response(product_count: int):
            return {
                'id': topic.topic_key,
                'title': topic.title,
                'title_zh': topic.title_zh or topic.title,
                'title_en': topic.title_en or topic.title,
                'description': topic.description,
                'description_zh': topic.description_zh or topic.description,
                'description_en': topic.description_en or topic.description,
                'curator_role': role,
                'product_count': product_count,
            }
        
        if not all_product_ids:
            return {
                'topic': build_topic_response(0),
                'products': [],
                'pagination': {'total': 0, 'page': page, 'limit': limit, 'total_pages': 0}
            }
        
        # 查询产品信息
        startup_query = select(Startup).where(Startup.id.in_(all_product_ids))
        startup_result = await db.execute(startup_query)
        startups = list(startup_result.scalars())
        
        # 排序
        if sort == 'revenue':
            startups = sorted(startups, key=lambda x: x.revenue_30d or 0, reverse=True)
        elif sort == 'name':
            startups = sorted(startups, key=lambda x: x.name or '')
        
        # 分页
        total = len(startups)
        start = (page - 1) * limit
        end = start + limit
        paginated_startups = startups[start:end]
        
        # 获取判断结果
        startup_ids = [s.id for s in paginated_startups]
        judgment_query = select(MotherThemeJudgment).where(
            MotherThemeJudgment.startup_id.in_(startup_ids)
        )
        judgment_result = await db.execute(judgment_query)
        
        judgments_by_startup = {}
        for j in judgment_result.scalars():
            if j.startup_id not in judgments_by_startup:
                judgments_by_startup[j.startup_id] = {}
            judgments_by_startup[j.startup_id][j.theme_key] = {
                'judgment': j.judgment,
                'confidence': j.confidence,
            }
        
        product_list = []
        for startup in paginated_startups:
            judgments = judgments_by_startup.get(startup.id, {})
            product_list.append({
                'id': startup.id,
                'name': startup.name,
                'slug': startup.slug,
                'category': startup.category,
                'logo_url': startup.logo_url,
                'revenue_30d': startup.revenue_30d,
                'key_tags': extract_key_tags(judgments, role, startup.founder_followers),
            })
        
        return {
            'topic': build_topic_response(total),
            'products': product_list,
            'pagination': {
                'total': total,
                'page': page,
                'limit': limit,
                'total_pages': (total + limit - 1) // limit,
            }
        }



# =============================================================================
# 2. TodayCuration - 今日策展
# =============================================================================

@router.get("/discover/curations")
async def get_curations(
    limit: int = Query(4, ge=1, le=100),
    days: int = Query(30, ge=1, le=365),
):
    """获取最近的策展内容"""
    async with get_db_session() as db:
        # 获取最近 N 天的策展
        since_date = date.today() - timedelta(days=days)
        
        query = (
            select(DailyCuration)
            .where(and_(
                DailyCuration.is_active == True,
                DailyCuration.curation_date >= since_date
            ))
            .options(selectinload(DailyCuration.products))
            .order_by(desc(DailyCuration.curation_date), DailyCuration.display_order)
            .limit(limit)
        )
        result = await db.execute(query)
        curations = result.scalars().all()
        
        # 如果没有最近的数据，获取所有活跃的策展（不限日期）
        if not curations:
            query = (
                select(DailyCuration)
                .where(DailyCuration.is_active == True)
                .options(selectinload(DailyCuration.products))
                .order_by(desc(DailyCuration.curation_date), DailyCuration.display_order)
                .limit(limit)
            )
            result = await db.execute(query)
            curations = result.scalars().all()
        
        if not curations:
            return {'curations': []}
        
        # 获取所有关联的产品信息
        all_startup_ids = []
        for c in curations:
            all_startup_ids.extend([p.startup_id for p in c.products[:3]])
        
        startups_map = {}
        if all_startup_ids:
            startup_query = select(Startup).where(Startup.id.in_(all_startup_ids))
            startup_result = await db.execute(startup_query)
            startups_map = {s.id: s for s in startup_result.scalars()}
        
        curation_list = []
        for curation in curations:
            products = []
            for cp in curation.products[:3]:
                startup = startups_map.get(cp.startup_id)
                if startup:
                    products.append({
                        'name': startup.name,
                        'slug': startup.slug,
                        'mrr': f"${startup.revenue_30d / 1000:.1f}k" if startup.revenue_30d else None,
                        'logo': startup.logo_url or '📦',
                        'highlight_zh': cp.highlight_zh,
                        'highlight_en': cp.highlight_en,
                    })
            
            curation_list.append({
                'id': curation.id,
                'title': curation.title,
                'title_zh': curation.title_zh or curation.title,
                'title_en': curation.title_en or curation.title,
                'description': curation.description,
                'description_zh': curation.description_zh or curation.description,
                'description_en': curation.description_en or curation.description,
                'tag': curation.tag,
                'tag_zh': curation.tag_zh or curation.tag,
                'tag_en': curation.tag_en or curation.tag,
                'tag_color': curation.tag_color or 'amber',
                'insight': curation.insight,
                'insight_zh': curation.insight_zh or curation.insight,
                'insight_en': curation.insight_en or curation.insight,
                'curation_type': curation.curation_type,
                'curation_date': curation.curation_date.isoformat() if curation.curation_date else None,
                'products': products,
            })
        
        return {'curations': curation_list}


# =============================================================================
# 3. SuccessBreakdown - 爆款解剖
# =============================================================================

@router.get("/discover/stories")
async def get_success_stories(
    limit: int = Query(4, ge=1, le=10),
    featured_only: bool = Query(False),
):
    """获取爆款故事列表"""
    async with get_db_session() as db:
        query = (
            select(SuccessStory)
            .where(SuccessStory.is_active == True)
            .options(
                selectinload(SuccessStory.timeline_events),
                selectinload(SuccessStory.key_insights)
            )
            .order_by(desc(SuccessStory.is_featured), SuccessStory.display_order)
            .limit(limit)
        )
        
        if featured_only:
            query = query.where(SuccessStory.is_featured == True)
        
        result = await db.execute(query)
        stories = result.scalars().all()
        
        story_list = []
        for story in stories:
            # 时间线
            timeline = sorted(story.timeline_events, key=lambda x: x.display_order)[:4]
            timeline_data = [{
                'date': e.event_date,
                'event': e.event_text,
                'event_zh': e.event_text_zh or e.event_text,
                'event_en': e.event_text_en or e.event_text,
            } for e in timeline]
            
            # 关键洞察
            insights = sorted(story.key_insights, key=lambda x: x.display_order)
            insights_data = [{
                'text': i.insight_text,
                'text_zh': i.insight_text_zh or i.insight_text,
                'text_en': i.insight_text_en or i.insight_text,
            } for i in insights]
            
            story_list.append({
                'id': story.id,
                'title': story.title,
                'title_zh': story.title_zh or story.title,
                'title_en': story.title_en or story.title,
                'subtitle': story.subtitle,
                'subtitle_zh': story.subtitle_zh or story.subtitle,
                'subtitle_en': story.subtitle_en or story.subtitle,
                'product': {
                    'name': story.product_name,
                    'logo': story.product_logo or '📊',
                    'mrr': story.product_mrr,
                    'founder': story.founder_name,
                },
                'timeline': timeline_data,
                'key_insights': insights_data,
                'gradient': story.gradient,
                'accent_color': story.accent_color,
            })
        
        return {'stories': story_list}


@router.get("/discover/stories/{story_id}")
async def get_story_detail(story_id: int):
    """获取爆款故事详情"""
    async with get_db_session() as db:
        query = (
            select(SuccessStory)
            .where(SuccessStory.id == story_id)
            .options(
                selectinload(SuccessStory.timeline_events),
                selectinload(SuccessStory.key_insights)
            )
        )
        result = await db.execute(query)
        story = result.scalar_one_or_none()
        
        if not story:
            raise HTTPException(status_code=404, detail="Story not found")
        
        return {'story': story.to_dict()}



# =============================================================================
# 4. CreatorUniverse - 创作者宇宙
# =============================================================================

@router.get("/discover/creators")
async def get_creators(
    limit: int = Query(8, ge=1, le=20),
    use_featured: bool = Query(True),
):
    """
    获取创作者列表
    
    两种模式：
    1. use_featured=True: 从 featured_creators 表获取手动策划的创作者
    2. use_featured=False: 从 startups 表聚合计算
    """
    async with get_db_session() as db:
        if use_featured:
            # 从精选创作者表获取
            query = (
                select(FeaturedCreator)
                .where(FeaturedCreator.is_featured == True)
                .order_by(FeaturedCreator.display_order)
                .limit(limit)
            )
            result = await db.execute(query)
            featured = result.scalars().all()
            
            if featured:
                # 获取关联的产品
                normalized_usernames = []
                founder_id_by_key = {}
                creator_key_by_founder_id = {}
                username_by_key = {}

                featured_founder_ids = [f.founder_id for f in featured if f.founder_id]
                username_by_id = {}
                if featured_founder_ids:
                    founders_result = await db.execute(
                        select(Founder.id, Founder.username)
                        .where(Founder.id.in_(featured_founder_ids))
                    )
                    for founder_id, username in founders_result.all():
                        username_by_id[founder_id] = username

                for f in featured:
                    if f.founder_id and f.founder_id in username_by_id:
                        key = normalize_creator_key(username_by_id[f.founder_id])
                        if key:
                            founder_id_by_key[key] = f.founder_id
                            creator_key_by_founder_id[f.founder_id] = key
                            username_by_key[key] = username_by_id[f.founder_id]
                        continue
                    key = normalize_creator_key(f.founder_username) or normalize_creator_key(f.handle)
                    if key:
                        normalized_usernames.append(key)
                normalized_usernames = list(dict.fromkeys(normalized_usernames))

                if normalized_usernames:
                    founders_query = (
                        select(Founder.id, Founder.username)
                        .where(func.lower(Founder.username).in_(normalized_usernames))
                    )
                    founders_result = await db.execute(founders_query)
                    for founder_id, username in founders_result.all():
                        key = normalize_creator_key(username)
                        if key and key not in founder_id_by_key:
                            founder_id_by_key[key] = founder_id
                            creator_key_by_founder_id[founder_id] = key
                            username_by_key[key] = username

                founder_ids = list(dict.fromkeys(founder_id_by_key.values()))
                # 兼容 founder_id 未回填的情况，始终保留 username 路径
                fallback_usernames = list(normalized_usernames)

                products_by_key = {}
                avatar_by_key = {}
                platform_by_key = {}

                if founder_ids or fallback_usernames:
                    conditions = []
                    if founder_ids:
                        conditions.append(Startup.founder_id.in_(founder_ids))
                    if fallback_usernames:
                        conditions.append(func.lower(Startup.founder_username).in_(fallback_usernames))
                    products_query = (
                        select(Startup)
                        .where(or_(*conditions))
                        .order_by(desc(Startup.revenue_30d))
                    )
                    products_result = None
                    try:
                        products_result = await db.execute(products_query)
                    except SQLAlchemyError:
                        if normalized_usernames:
                            fallback_query = (
                                select(Startup)
                                .where(func.lower(Startup.founder_username).in_(normalized_usernames))
                                .order_by(desc(Startup.revenue_30d))
                            )
                            products_result = await db.execute(fallback_query)
                    if products_result:
                        for p in products_result.scalars():
                            key = normalize_creator_key(p.founder_username) or creator_key_by_founder_id.get(p.founder_id)
                            if not key:
                                continue
                            if key not in products_by_key:
                                products_by_key[key] = []
                            products_by_key[key].append({
                                'id': p.id,
                                'name': p.name,
                                'mrr': f"${p.revenue_30d / 1000:.0f}k" if p.revenue_30d else None,
                            })
                            if p.founder_avatar_url and key not in avatar_by_key:
                                avatar_by_key[key] = p.founder_avatar_url
                            if p.founder_social_platform and key not in platform_by_key:
                                platform_by_key[key] = p.founder_social_platform
                
                creator_list = []
                for f in featured:
                    if f.founder_id and f.founder_id in creator_key_by_founder_id:
                        creator_key = creator_key_by_founder_id[f.founder_id]
                    else:
                        creator_key = normalize_creator_key(f.founder_username) or normalize_creator_key(f.handle)
                    all_products = products_by_key.get(creator_key, []) or []
                    products = all_products[:3]
                    # 统一使用 featured_creators.product_count
                    product_count = f.product_count if f.product_count is not None else 0
                    resolved_username = username_by_key.get(creator_key) or f.founder_username
                    avatar_url = avatar_by_key.get(creator_key)
                    platform = platform_by_key.get(creator_key)
                    handle = f.handle
                    if resolved_username and (not handle or not handle.startswith("http")):
                        handle = f"@{resolved_username}"
                    social_url = build_social_url(handle, platform, resolved_username)
                    creator_list.append({
                        'id': f.id,
                        'name': f.name,
                        'handle': handle,
                        'avatar': f.avatar or '🚀',
                        'avatar_url': avatar_url,
                        'bio': f.bio_zh,
                        'bio_zh': f.bio_zh,
                        'bio_en': f.bio_en,
                        'tag': f.tag,
                        'tag_zh': f.tag_zh or f.tag,
                        'tag_en': f.tag_en or f.tag,
                        'tag_color': f.tag_color or 'amber',
                        'total_mrr': f.total_mrr,
                        'followers': f.followers,
                        'social_url': social_url,
                        'social_platform': platform,
                        'products': products,
                        'product_count': product_count,
                    })
                
                return {'creators': creator_list}
        
        # 从 startups 表聚合
        # 按 founder_id 分组，避免用户名变更导致计数错误
        query = (
            select(
                Startup.founder_id.label('founder_id'),
                Founder.username.label('founder_username'),
                Founder.name.label('founder_name'),
                func.max(Startup.founder_avatar_url).label('founder_avatar_url'),
                func.max(Startup.founder_followers).label('founder_followers'),
                func.max(Startup.founder_social_platform).label('founder_social_platform'),
                func.sum(Startup.revenue_30d).label('total_revenue'),
                func.count(Startup.id).label('product_count')
            )
            .join(Founder, Startup.founder_id == Founder.id)
            .where(Startup.founder_id.isnot(None))
            .where(Startup.revenue_30d > 0)
            .group_by(
                Startup.founder_id,
                Founder.username,
                Founder.name,
            )
            .order_by(desc('total_revenue'))
            .limit(limit)
        )
        
        using_fallback = False
        try:
            result = await db.execute(query)
            rows = result.fetchall()
        except SQLAlchemyError:
            rows = []
            using_fallback = True
        if not rows:
            fallback_query = (
                select(
                    Startup.founder_username.label('founder_username'),
                    func.max(Startup.founder_name).label('founder_name'),
                    func.max(Startup.founder_avatar_url).label('founder_avatar_url'),
                    func.max(Startup.founder_followers).label('founder_followers'),
                    func.max(Startup.founder_social_platform).label('founder_social_platform'),
                    func.sum(Startup.revenue_30d).label('total_revenue'),
                    func.count(Startup.id).label('product_count')
                )
                .where(Startup.founder_username.isnot(None))
                .where(Startup.founder_username != '')
                .where(Startup.revenue_30d > 0)
                .group_by(Startup.founder_username)
                .order_by(desc('total_revenue'))
                .limit(limit)
            )
            fallback_result = await db.execute(fallback_query)
            rows = fallback_result.fetchall()
            using_fallback = True

        if not rows:
            fallback_query = (
                select(
                    Startup.founder_username.label('founder_username'),
                    func.max(Startup.founder_name).label('founder_name'),
                    func.max(Startup.founder_avatar_url).label('founder_avatar_url'),
                    func.max(Startup.founder_followers).label('founder_followers'),
                    func.max(Startup.founder_social_platform).label('founder_social_platform'),
                    func.sum(func.coalesce(Startup.revenue_30d, 0)).label('total_revenue'),
                    func.count(Startup.id).label('product_count')
                )
                .where(Startup.founder_username.isnot(None))
                .where(Startup.founder_username != '')
                .group_by(Startup.founder_username)
                .order_by(desc('total_revenue'))
                .limit(limit)
            )
            fallback_result = await db.execute(fallback_query)
            rows = fallback_result.fetchall()
            using_fallback = True
        
        if not rows:
            return {'creators': []}
        
        # 获取每个创作者的产品列表
        if using_fallback:
            usernames = []
            for r in rows:
                key = normalize_creator_key(r.founder_username)
                if key:
                    usernames.append(key)
            usernames = list(dict.fromkeys(usernames))
            products_result = await db.execute(
                select(Startup)
                .where(func.lower(Startup.founder_username).in_(usernames))
                .order_by(desc(Startup.revenue_30d))
            )
        else:
            founder_ids = [r.founder_id for r in rows if r.founder_id is not None]
            username_by_id = {r.founder_id: r.founder_username for r in rows if r.founder_id is not None}
            products_result = await db.execute(
                select(Startup)
                .where(Startup.founder_id.in_(founder_ids))
                .order_by(desc(Startup.revenue_30d))
            )
        
        products_by_key = {}
        for p in products_result.scalars():
            key = normalize_creator_key(p.founder_username)
            if not using_fallback and key is None:
                key = normalize_creator_key(username_by_id.get(p.founder_id))
            if not key:
                continue
            if key not in products_by_key:
                products_by_key[key] = []
            products_by_key[key].append({
                'id': p.id,
                'name': p.name,
                'mrr': f"${p.revenue_30d / 1000:.0f}k" if p.revenue_30d else None,
            })
        
        creator_list = []
        for row in rows:
            row_username = row.founder_username if hasattr(row, 'founder_username') else None
            row_name = row.founder_name if hasattr(row, 'founder_name') else None
            row_avatar_url = row.founder_avatar_url if hasattr(row, 'founder_avatar_url') else None
            row_followers = row.founder_followers if hasattr(row, 'founder_followers') else None
            row_social_platform = row.founder_social_platform if hasattr(row, 'founder_social_platform') else None
            row_key = normalize_creator_key(row_username)
            all_products = products_by_key.get(row_key, []) or []
            products = all_products[:3]
            total_mrr = row.total_revenue or 0
            followers = format_followers(row_followers)
            social_url = build_social_url(
                f"@{row_username}" if row_username else None,
                row_social_platform,
                row_username,
            )

            product_count = row.product_count or count_products_by_id(all_products)
            creator_list.append({
                'id': row_username,
                'name': row_name or row_username,
                'handle': f"@{row_username}" if row_username else None,
                'avatar': row_avatar_url or '??',
                'avatar_url': row_avatar_url,
                'bio': None,
                'bio_zh': None,
                'bio_en': None,
                'tag': None,
                'tag_zh': None,
                'tag_en': None,
                'tag_color': 'amber',
                'total_mrr': f"${total_mrr / 1000:.0f}k+" if total_mrr >= 1000 else f"${total_mrr:.0f}",
                'followers': followers,
                'social_url': social_url,
                'social_platform': row_social_platform,
                'products': products,
                'product_count': product_count,
            })
        
        return {'creators': creator_list}


@router.get("/discover/creators/{creator_id}")
async def get_creator_detail(creator_id: str):
    """获取创作者详情（精选创作者或按 founder_username 聚合）"""
    async with get_db_session() as db:
        creator = None
        creator_data = None
        username = None
        creator_key = None

        # 优先按精选创作者 ID 查找
        if creator_id.isdigit():
            featured_query = select(FeaturedCreator).where(FeaturedCreator.id == int(creator_id))
            featured_result = await db.execute(featured_query)
            creator = featured_result.scalar_one_or_none()

        if creator:
            if creator.founder_id:
                founder_result = await db.execute(
                    select(Founder).where(Founder.id == creator.founder_id)
                )
                founder = founder_result.scalar_one_or_none()
                username = founder.username if founder else (creator.founder_username or creator.handle)
                creator_key = normalize_creator_key(username)
            else:
                username = creator.founder_username or creator.handle
                creator_key = normalize_creator_key(creator.founder_username) or normalize_creator_key(creator.handle)
            creator_data = {
                'id': creator.id,
                'name': creator.name,
                'handle': creator.handle,
                'avatar': creator.avatar or '??',
                'bio': creator.bio_zh,
                'bio_zh': creator.bio_zh,
                'bio_en': creator.bio_en,
                'tag': creator.tag,
                'tag_zh': creator.tag_zh or creator.tag,
                'tag_en': creator.tag_en or creator.tag,
                'tag_color': creator.tag_color or 'amber',
                'total_mrr': creator.total_mrr,
                'followers': creator.followers,
                'products': [],
                'product_count': creator.product_count or 0,
            }
        else:
            # 兜底：按 founder_username 聚合
            username = creator_id.lstrip('@')
            creator_key = normalize_creator_key(username)

        products = []
        avatar_url = None
        platform = None
        followers_count = None
        founder = None
        if creator_key:
            founder_result = await db.execute(
                select(Founder).where(func.lower(Founder.username) == creator_key)
            )
            founder = founder_result.scalar_one_or_none()

        if creator_key:
            if founder:
                products_query = (
                    select(Startup)
                    .where(Startup.founder_id == founder.id)
                    .order_by(desc(Startup.revenue_30d))
                )
            else:
                products_query = (
                    select(Startup)
                    .where(func.lower(Startup.founder_username) == creator_key)
                    .order_by(desc(Startup.revenue_30d))
                )
            products_result = await db.execute(products_query)
            startups = list(products_result.scalars())

            for p in startups:
                if avatar_url is None and p.founder_avatar_url:
                    avatar_url = p.founder_avatar_url
                if platform is None and p.founder_social_platform:
                    platform = p.founder_social_platform
                if followers_count is None and p.founder_followers is not None:
                    followers_count = p.founder_followers
            if followers_count is None and founder and founder.followers is not None:
                followers_count = founder.followers
            if platform is None and founder and founder.social_platform:
                platform = founder.social_platform

            products = [{
                'name': p.name,
                'mrr': f"${p.revenue_30d / 1000:.0f}k" if p.revenue_30d else None,
            } for p in startups[:6]]

            if not creator_data:
                total_revenue = sum(p.revenue_30d or 0 for p in startups)
                display_username = founder.username if founder else username
                creator_data = {
                    'id': display_username,
                    'name': startups[0].founder_name or (founder.name if founder else None) or display_username if startups else display_username,
                    'handle': f"@{display_username}" if display_username else None,
                    'avatar': avatar_url or '??',
                    'avatar_url': avatar_url,
                    'bio': None,
                    'bio_zh': None,
                    'bio_en': None,
                    'tag': None,
                    'tag_zh': None,
                    'tag_en': None,
                    'tag_color': 'amber',
                    'total_mrr': f"${total_revenue / 1000:.0f}k+" if total_revenue >= 1000 else f"${total_revenue:.0f}",
                    'followers': format_followers(followers_count),
                    'social_url': build_social_url(f"@{display_username}", platform, display_username),
                    'social_platform': platform,
                    'products': [],
                    'product_count': len(startups),
                }

        if creator_data:
            if not creator_data.get('avatar_url'):
                creator_data['avatar_url'] = avatar_url
            if not creator_data.get('social_url'):
                creator_data['social_url'] = build_social_url(
                    creator_data.get('handle'),
                    platform,
                    founder.username if founder else username
                )
            if not creator_data.get('social_platform'):
                creator_data['social_platform'] = platform
            if not creator_data.get('followers'):
                creator_data['followers'] = format_followers(followers_count)

        if not creator_data:
            raise HTTPException(status_code=404, detail="Creator not found")

        creator_data['products'] = products
        if creator_data['product_count'] == 0:
            creator_data['product_count'] = len(products)

        return {'creator': creator_data}



# =============================================================================
# 5. ForYouSection - 为你推荐
# =============================================================================

# 推荐方向配置
RECOMMENDATION_DIRECTIONS = [
    {
        'id': 'api_tools',
        'direction_zh': 'API 工具类产品',
        'direction_en': 'API Tool Products',
        'description_zh': '技术门槛适中，市场需求稳定，适合有后端经验的开发者',
        'description_en': 'Moderate technical barrier, stable market demand, suitable for developers with backend experience',
        'examples': ['Screenshot API', 'PDF Generation API', 'Email Validation API'],
        'difficulty': 'medium',
        'potential': 'high',
        'gradient': 'from-blue-500/10 to-cyan-500/5',
        'accent_color': 'blue',
        'match_roles': ['cautious_indie_dev', 'quick_starter'],
        'match_categories': ['Developer Tools', 'API'],
    },
    {
        'id': 'dev_efficiency',
        'direction_zh': '开发者效率工具',
        'direction_en': 'Developer Efficiency Tools',
        'description_zh': '面向开发者的小工具，用户付费意愿强，口碑传播效果好',
        'description_en': 'Small tools for developers, strong willingness to pay, good word-of-mouth',
        'examples': ['Code Snippet Manager', 'API Testing Tool', 'Local Dev Environment'],
        'difficulty': 'low',
        'potential': 'medium-high',
        'gradient': 'from-violet-500/10 to-purple-500/5',
        'accent_color': 'violet',
        'match_roles': ['quick_starter', 'product_driven_fan'],
        'match_categories': ['Developer Tools', 'Productivity'],
    },
    {
        'id': 'content_creator',
        'direction_zh': '内容创作者工具',
        'direction_en': 'Content Creator Tools',
        'description_zh': '帮助内容创作者提高效率的工具，市场正在快速增长',
        'description_en': 'Tools to help content creators improve efficiency, rapidly growing market',
        'examples': ['Social Media Scheduler', 'Video Subtitle Generator', 'Content Analytics'],
        'difficulty': 'medium',
        'potential': 'high',
        'gradient': 'from-rose-500/10 to-pink-500/5',
        'accent_color': 'rose',
        'match_roles': ['content_to_product', 'opportunity_hunter'],
        'match_categories': ['Marketing', 'Social Media'],
    },
    {
        'id': 'ai_wrapper',
        'direction_zh': 'AI 应用封装',
        'direction_en': 'AI Application Wrapper',
        'description_zh': '基于大模型 API 的垂直应用，开发快但需要找准场景',
        'description_en': 'Vertical applications based on LLM APIs, fast development but need to find the right scenario',
        'examples': ['AI Writing Assistant', 'AI Image Generator', 'AI Code Review'],
        'difficulty': 'low',
        'potential': 'medium',
        'gradient': 'from-amber-500/10 to-orange-500/5',
        'accent_color': 'amber',
        'match_roles': ['quick_starter', 'scenario_focused'],
        'match_categories': ['AI', 'Productivity'],
    },
    {
        'id': 'niche_saas',
        'direction_zh': '垂直细分 SaaS',
        'direction_en': 'Vertical Niche SaaS',
        'description_zh': '针对特定行业或人群的 SaaS，竞争小但需要深入了解用户',
        'description_en': 'SaaS for specific industries or groups, less competition but requires deep user understanding',
        'examples': ['Dental Practice Management', 'Freelancer Invoice Tool', 'Gym Member Tracker'],
        'difficulty': 'medium',
        'potential': 'high',
        'gradient': 'from-emerald-500/10 to-teal-500/5',
        'accent_color': 'emerald',
        'match_roles': ['niche_hunter', 'scenario_focused'],
        'match_categories': ['SaaS', 'Business'],
    },
]

ROLE_LABELS = {
    "cautious_indie_dev": {"zh": "谨慎的独立开发者", "en": "Cautious Indie Dev"},
    "quick_starter": {"zh": "快速启动者", "en": "Quick Starter"},
    "opportunity_hunter": {"zh": "机会嗅觉型", "en": "Opportunity Hunter"},
    "anti_bubble": {"zh": "反泡沫分析者", "en": "Anti-Bubble Analyst"},
    "product_driven_fan": {"zh": "产品驱动爱好者", "en": "Product-Driven"},
    "niche_hunter": {"zh": "细分市场猎手", "en": "Niche Hunter"},
    "ux_differentiator": {"zh": "体验差异化追求者", "en": "UX Differentiator"},
    "low_risk_starter": {"zh": "低风险入门者", "en": "Low-Risk Starter"},
    "content_to_product": {"zh": "内容创作者转型", "en": "Content Creator"},
    "scenario_focused": {"zh": "场景聚焦者", "en": "Scenario Focused"},
}

SKILL_LEVEL_LABELS = {
    "beginner": {"zh": "入门", "en": "Beginner"},
    "intermediate": {"zh": "进阶", "en": "Intermediate"},
    "advanced": {"zh": "高级", "en": "Advanced"},
}


def build_why_for_you(
    direction: dict,
    preferred_roles: List[str],
    interested_categories: List[str],
    skill_level: Optional[str],
) -> Dict[str, Optional[str]]:
    """生成个性化推荐原因"""
    role_matches = [r for r in direction.get("match_roles", []) if r in preferred_roles]
    role_labels_zh = [ROLE_LABELS.get(r, {"zh": r}).get("zh", r) for r in role_matches]
    role_labels_en = [ROLE_LABELS.get(r, {"en": r}).get("en", r) for r in role_matches]

    category_matches = [c for c in direction.get("match_categories", []) if c in interested_categories]

    reasons_zh = []
    reasons_en = []

    if role_labels_zh:
        reasons_zh.append(f"匹配你的角色偏好：{', '.join(role_labels_zh)}")
        reasons_en.append(f"Matches your role preferences: {', '.join(role_labels_en)}")
    if category_matches:
        reasons_zh.append(f"符合你关注的领域：{', '.join(category_matches)}")
        reasons_en.append(f"Aligned with your categories: {', '.join(category_matches)}")

    if skill_level:
        skill = SKILL_LEVEL_LABELS.get(skill_level, {"zh": skill_level, "en": skill_level})
        reasons_zh.append(f"难度更适合你的阶段：{skill['zh']}")
        reasons_en.append(f"Difficulty fits your level: {skill['en']}")

    if not reasons_zh:
        return {"zh": None, "en": None}

    return {"zh": "；".join(reasons_zh), "en": " · ".join(reasons_en)}


@router.get("/discover/recommendations")
async def get_recommendations(
    user_id: Optional[str] = Query(None),
    limit: int = Query(3, ge=1, le=6),
):
    """
    获取个性化推荐
    
    如果有 user_id，根据用户偏好推荐
    否则返回默认推荐
    """
    async with get_db_session() as db:
        user_pref = None
        
        if user_id:
            pref_query = select(UserPreference).where(UserPreference.user_id == user_id)
            pref_result = await db.execute(pref_query)
            user_pref = pref_result.scalar_one_or_none()
        
        # 根据用户偏好排序推荐
        recommendations = RECOMMENDATION_DIRECTIONS.copy()
        
        if user_pref:
            preferred_roles = user_pref.preferred_roles or []
            interested_categories = user_pref.interested_categories or []
            skill_level = user_pref.skill_level

            def score_direction(d):
                score = 0
                for role in d.get('match_roles', []):
                    if role in preferred_roles:
                        score += 2
                for cat in d.get('match_categories', []):
                    if cat in interested_categories:
                        score += 1
                return score
            
            recommendations = sorted(recommendations, key=score_direction, reverse=True)
        else:
            preferred_roles = []
            interested_categories = []
            skill_level = None

        # 格式化输出
        result = []
        for d in recommendations[:limit]:
            why = build_why_for_you(d, preferred_roles, interested_categories, skill_level)
            result.append({
                'id': d['id'],
                'direction': d['direction_zh'],
                'direction_zh': d['direction_zh'],
                'direction_en': d['direction_en'],
                'description': d['description_zh'],
                'description_zh': d['description_zh'],
                'description_en': d['description_en'],
                'why_for_you': why['zh'],
                'why_for_you_zh': why['zh'],
                'why_for_you_en': why['en'],
                'examples': d['examples'],
                'difficulty': d['difficulty'],
                'potential': d['potential'],
                'gradient': d['gradient'],
                'accent_color': d['accent_color'],
            })
        
        return {'recommendations': result}


@router.get("/discover/user-preference")
async def get_user_preference(user_id: str):
    """获取用户偏好设置"""
    async with get_db_session() as db:
        query = select(UserPreference).where(UserPreference.user_id == user_id)
        result = await db.execute(query)
        pref = result.scalar_one_or_none()
        
        if not pref:
            return {'preference': None}
        
        return {'preference': pref.to_dict()}


@router.post("/discover/user-preference")
async def save_user_preference(
    user_id: str,
    preferred_roles: List[str] = [],
    interested_categories: List[str] = [],
    skill_level: str = 'beginner',
    goal: Optional[str] = None,
    time_commitment: Optional[str] = None,
    tech_stack: List[str] = [],
):
    """保存用户偏好设置"""
    async with get_db_session() as db:
        query = select(UserPreference).where(UserPreference.user_id == user_id)
        result = await db.execute(query)
        pref = result.scalar_one_or_none()
        
        if pref:
            pref.preferred_roles = preferred_roles
            pref.interested_categories = interested_categories
            pref.skill_level = skill_level
            pref.goal = goal
            pref.time_commitment = time_commitment
            pref.tech_stack = tech_stack
        else:
            pref = UserPreference(
                user_id=user_id,
                preferred_roles=preferred_roles,
                interested_categories=interested_categories,
                skill_level=skill_level,
                goal=goal,
                time_commitment=time_commitment,
                tech_stack=tech_stack,
            )
            db.add(pref)
        
        await db.commit()
        return {'success': True, 'preference': pref.to_dict()}
