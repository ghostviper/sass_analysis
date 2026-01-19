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
from typing import Optional, List
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, func, desc, and_
from sqlalchemy.orm import selectinload

from database.db import get_db_session
from database.models import (
    DiscoverTopic, TopicProduct, Startup, MotherThemeJudgment,
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


def extract_key_tags(judgments: dict, role: str) -> List[dict]:
    """提取关键标签"""
    key_fields = KEY_TAGS_BY_ROLE.get(role, ['solo_feasibility', 'entry_barrier', 'primary_risk'])
    tags = []
    
    for field in key_fields:
        if field in judgments:
            judgment_data = judgments[field]
            value = judgment_data.get('judgment', '') if isinstance(judgment_data, dict) else str(judgment_data)
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
                'key_tags': extract_key_tags(judgments, role),
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
    limit: int = Query(4, ge=1, le=10),
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
                usernames = [f.founder_username for f in featured if f.founder_username]
                products_by_username = {}
                
                if usernames:
                    products_query = (
                        select(Startup)
                        .where(Startup.founder_username.in_(usernames))
                        .order_by(desc(Startup.revenue_30d))
                    )
                    products_result = await db.execute(products_query)
                    for p in products_result.scalars():
                        if p.founder_username not in products_by_username:
                            products_by_username[p.founder_username] = []
                        products_by_username[p.founder_username].append({
                            'name': p.name,
                            'mrr': f"${p.revenue_30d / 1000:.0f}k" if p.revenue_30d else None,
                        })
                
                creator_list = []
                for f in featured:
                    products = products_by_username.get(f.founder_username, [])[:3]
                    # 使用 featured_creators 表中的 product_count，如果没有则用实际查到的数量
                    product_count = f.product_count if f.product_count else len(products)
                    creator_list.append({
                        'id': f.id,
                        'name': f.name,
                        'handle': f.handle,
                        'avatar': f.avatar or '🚀',
                        'bio': f.bio_zh,
                        'bio_zh': f.bio_zh,
                        'bio_en': f.bio_en,
                        'tag': f.tag,
                        'tag_zh': f.tag_zh or f.tag,
                        'tag_en': f.tag_en or f.tag,
                        'tag_color': f.tag_color or 'amber',
                        'total_mrr': f.total_mrr,
                        'followers': f.followers,
                        'products': products,
                        'product_count': product_count,
                    })
                
                return {'creators': creator_list}
        
        # 从 startups 表聚合
        # 按 founder_username 分组，计算总收入
        query = (
            select(
                Startup.founder_username,
                Startup.founder_name,
                Startup.founder_avatar_url,
                Startup.founder_followers,
                func.sum(Startup.revenue_30d).label('total_revenue'),
                func.count(Startup.id).label('product_count')
            )
            .where(Startup.founder_username.isnot(None))
            .where(Startup.revenue_30d > 0)
            .group_by(
                Startup.founder_username,
                Startup.founder_name,
                Startup.founder_avatar_url,
                Startup.founder_followers
            )
            .order_by(desc('total_revenue'))
            .limit(limit)
        )
        
        result = await db.execute(query)
        rows = result.fetchall()
        
        if not rows:
            return {'creators': []}
        
        # 获取每个创作者的产品列表
        usernames = [r.founder_username for r in rows]
        products_query = (
            select(Startup)
            .where(Startup.founder_username.in_(usernames))
            .order_by(desc(Startup.revenue_30d))
        )
        products_result = await db.execute(products_query)
        
        products_by_username = {}
        for p in products_result.scalars():
            if p.founder_username not in products_by_username:
                products_by_username[p.founder_username] = []
            products_by_username[p.founder_username].append({
                'name': p.name,
                'mrr': f"${p.revenue_30d / 1000:.0f}k" if p.revenue_30d else None,
            })
        
        creator_list = []
        for row in rows:
            products = products_by_username.get(row.founder_username, [])[:3]
            total_mrr = row.total_revenue or 0
            
            creator_list.append({
                'id': row.founder_username,
                'name': row.founder_name or row.founder_username,
                'handle': f"@{row.founder_username}" if row.founder_username else None,
                'avatar': '🚀',
                'bio': None,
                'bio_zh': None,
                'bio_en': None,
                'tag': None,
                'tag_zh': None,
                'tag_en': None,
                'tag_color': 'amber',
                'total_mrr': f"${total_mrr / 1000:.0f}k+" if total_mrr >= 1000 else f"${total_mrr:.0f}",
                'followers': f"{row.founder_followers / 1000:.0f}k" if row.founder_followers and row.founder_followers >= 1000 else str(row.founder_followers or 0),
                'products': products,
                'product_count': row.product_count,
            })
        
        return {'creators': creator_list}



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
        
        # 格式化输出
        result = []
        for d in recommendations[:limit]:
            result.append({
                'id': d['id'],
                'direction': d['direction_zh'],
                'direction_zh': d['direction_zh'],
                'direction_en': d['direction_en'],
                'description': d['description_zh'],
                'description_zh': d['description_zh'],
                'description_en': d['description_en'],
                'why_for_you': None,  # 可以根据匹配原因生成
                'why_for_you_zh': None,
                'why_for_you_en': None,
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
