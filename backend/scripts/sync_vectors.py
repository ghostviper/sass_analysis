"""
同步数据到向量库

用法:
    python scripts/sync_vectors.py --all        # 同步所有数据
    python scripts/sync_vectors.py --products   # 只同步产品
    python scripts/sync_vectors.py --categories # 只同步赛道
    python scripts/sync_vectors.py --full       # 全量同步（清空后重建）
    python scripts/sync_vectors.py --stats      # 查看统计
"""

import asyncio
import argparse
import sys
from pathlib import Path

# 添加项目根目录到 path
sys.path.insert(0, str(Path(__file__).parent.parent))

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import select
from database.db import AsyncSessionLocal
from database.models import (
    Startup, 
    LandingPageAnalysis, 
    ProductSelectionAnalysis,
    CategoryAnalysis,
    ComprehensiveAnalysis
)
from services.vector_store import vector_store


# ============================================================================
# 产品向量化
# ============================================================================

def build_product_text(startup, landing, selection, comprehensive) -> str:
    """构建产品的向量化文本"""
    parts = [
        f"产品: {startup.name}",
    ]
    
    if startup.description:
        parts.append(f"描述: {startup.description}")
    
    if startup.category:
        parts.append(f"类目: {startup.category}")
    
    # Landing page 分析数据
    if landing:
        if landing.headline_text:
            parts.append(f"定位: {landing.headline_text}")
        
        if landing.target_audience:
            audiences = landing.target_audience if isinstance(landing.target_audience, list) else []
            if audiences:
                parts.append(f"目标用户: {', '.join(audiences[:5])}")
        
        if landing.use_cases:
            cases = landing.use_cases if isinstance(landing.use_cases, list) else []
            if cases:
                parts.append(f"使用场景: {', '.join(cases[:5])}")
        
        if landing.core_features:
            features = landing.core_features if isinstance(landing.core_features, list) else []
            if features:
                parts.append(f"核心功能: {', '.join(features[:5])}")
        
        if landing.pain_points:
            pains = landing.pain_points if isinstance(landing.pain_points, list) else []
            if pains:
                parts.append(f"解决痛点: {', '.join(pains[:3])}")
        
        if landing.value_propositions:
            props = landing.value_propositions if isinstance(landing.value_propositions, list) else []
            if props:
                parts.append(f"价值主张: {', '.join(props[:3])}")
    
    # 选品分析数据
    if selection:
        if selection.tech_complexity_level:
            parts.append(f"技术复杂度: {selection.tech_complexity_level}")
        if selection.target_customer:
            parts.append(f"目标客户: {selection.target_customer}")
        if selection.pricing_model:
            parts.append(f"定价模式: {selection.pricing_model}")
        if selection.growth_driver:
            parts.append(f"增长驱动: {selection.growth_driver}")
        if selection.ai_dependency_level:
            parts.append(f"AI依赖: {selection.ai_dependency_level}")
    
    # 综合分析摘要
    if comprehensive and comprehensive.analysis_summary:
        summary = comprehensive.analysis_summary
        if isinstance(summary, dict):
            if summary.get("one_liner"):
                parts.append(f"一句话总结: {summary['one_liner']}")
            if summary.get("strengths"):
                strengths = summary["strengths"][:2] if isinstance(strengths, list) else []
                if strengths:
                    parts.append(f"优势: {', '.join(strengths)}")
    
    return "\n".join(parts)


def build_product_metadata(startup, landing, selection, comprehensive) -> dict:
    """构建产品的元数据（用于过滤）"""
    meta = {
        "startup_id": startup.id,
        "name": startup.name,
        "slug": startup.slug,
    }
    
    if startup.category:
        meta["category"] = startup.category
    
    if startup.revenue_30d is not None:
        meta["revenue_30d"] = float(startup.revenue_30d)
    
    if selection:
        if selection.tech_complexity_level:
            meta["tech_complexity"] = selection.tech_complexity_level
        if selection.target_customer:
            meta["target_customer"] = selection.target_customer
        if selection.ai_dependency_level:
            meta["ai_dependency"] = selection.ai_dependency_level
        if selection.individual_dev_suitability is not None:
            meta["suitability_score"] = float(selection.individual_dev_suitability)
        if selection.pricing_model:
            meta["pricing_model"] = selection.pricing_model
    
    if comprehensive:
        if comprehensive.overall_recommendation is not None:
            meta["recommendation_score"] = float(comprehensive.overall_recommendation)
    
    return meta


async def load_products():
    """从数据库加载产品数据"""
    async with AsyncSessionLocal() as db:
        # 加载所有产品
        result = await db.execute(select(Startup))
        startups = {s.id: s for s in result.scalars().all()}
        
        # 加载 landing page 分析
        result = await db.execute(select(LandingPageAnalysis))
        landings = {l.startup_id: l for l in result.scalars().all()}
        
        # 加载选品分析
        result = await db.execute(select(ProductSelectionAnalysis))
        selections = {s.startup_id: s for s in result.scalars().all()}
        
        # 加载综合分析
        result = await db.execute(select(ComprehensiveAnalysis))
        comprehensives = {c.startup_id: c for c in result.scalars().all()}
        
        products = []
        for startup_id, startup in startups.items():
            landing = landings.get(startup_id)
            selection = selections.get(startup_id)
            comprehensive = comprehensives.get(startup_id)
            products.append((startup, landing, selection, comprehensive))
        
        return products


async def sync_products(full: bool = False):
    """同步产品到向量库"""
    print("\n📦 [产品] 加载数据...")
    products = await load_products()
    print(f"   找到 {len(products)} 个产品")
    
    if full:
        print("🗑️  清空现有产品向量...")
        vector_store.delete_all(namespace="products")
    
    print("🔄 生成向量...")
    
    batch_size = 20
    total_synced = 0
    
    for i in range(0, len(products), batch_size):
        batch = products[i:i + batch_size]
        
        texts = []
        items = []
        for startup, landing, selection, comprehensive in batch:
            text = build_product_text(startup, landing, selection, comprehensive)
            metadata = build_product_metadata(startup, landing, selection, comprehensive)
            texts.append(text)
            items.append({
                "id": f"product_{startup.id}",
                "metadata": metadata
            })
        
        try:
            embeddings = await vector_store.get_embeddings_batch(texts)
        except Exception as e:
            print(f"   ⚠️ Embedding 失败: {e}")
            continue
        
        vectors = []
        for item, embedding in zip(items, embeddings):
            item["values"] = embedding
            vectors.append(item)
        
        try:
            count = vector_store.upsert(vectors, namespace="products")
            total_synced += count
            print(f"   ✓ 产品已同步 {total_synced}/{len(products)}")
        except Exception as e:
            print(f"   ⚠️ 上传失败: {e}")
    
    print(f"✅ 产品同步完成，共 {total_synced} 条")
    return total_synced


# ============================================================================
# 赛道向量化
# ============================================================================

def build_category_text(category: CategoryAnalysis) -> str:
    """构建赛道的向量化文本"""
    parts = [
        f"赛道: {category.category}",
    ]
    
    if category.market_type:
        parts.append(f"市场类型: {category.market_type}")
    
    if category.market_type_reason:
        parts.append(f"市场特征: {category.market_type_reason}")
    
    if category.total_projects:
        parts.append(f"产品数量: {category.total_projects}")
    
    if category.total_revenue:
        parts.append(f"总收入: ${category.total_revenue:,.0f}")
    
    if category.median_revenue:
        parts.append(f"中位数收入: ${category.median_revenue:,.0f}")
    
    if category.gini_coefficient is not None:
        gini = category.gini_coefficient
        if gini < 0.3:
            distribution = "收入分布均匀，竞争激烈"
        elif gini < 0.5:
            distribution = "收入分布适中"
        else:
            distribution = "收入集中在头部，存在寡头"
        parts.append(f"收入分布: {distribution} (基尼系数 {gini:.2f})")
    
    if category.top10_revenue_share:
        parts.append(f"头部集中度: TOP10占比 {category.top10_revenue_share:.1f}%")
    
    return "\n".join(parts)


def build_category_metadata(category: CategoryAnalysis) -> dict:
    """构建赛道的元数据"""
    meta = {
        "category": category.category,
        "category_id": category.id,
    }
    
    if category.market_type:
        meta["market_type"] = category.market_type
    
    if category.total_projects:
        meta["total_projects"] = category.total_projects
    
    if category.total_revenue:
        meta["total_revenue"] = float(category.total_revenue)
    
    if category.median_revenue:
        meta["median_revenue"] = float(category.median_revenue)
    
    if category.gini_coefficient is not None:
        meta["gini_coefficient"] = float(category.gini_coefficient)
    
    return meta


async def load_categories():
    """从数据库加载赛道数据（每个赛道取最新一条）"""
    async with AsyncSessionLocal() as db:
        # 获取所有赛道分析，按日期降序
        result = await db.execute(
            select(CategoryAnalysis)
            .order_by(CategoryAnalysis.category, CategoryAnalysis.analysis_date.desc())
        )
        all_analyses = result.scalars().all()
        
        # 每个赛道只保留最新的
        latest = {}
        for analysis in all_analyses:
            if analysis.category not in latest:
                latest[analysis.category] = analysis
        
        return list(latest.values())


async def sync_categories(full: bool = False):
    """同步赛道到向量库"""
    print("\n📦 [赛道] 加载数据...")
    categories = await load_categories()
    print(f"   找到 {len(categories)} 个赛道")
    
    if not categories:
        print("   ⚠️ 没有赛道数据，跳过")
        return 0
    
    if full:
        print("🗑️  清空现有赛道向量...")
        vector_store.delete_all(namespace="categories")
    
    print("🔄 生成向量...")
    
    texts = []
    items = []
    for cat in categories:
        text = build_category_text(cat)
        metadata = build_category_metadata(cat)
        texts.append(text)
        items.append({
            "id": f"category_{cat.category}",
            "metadata": metadata
        })
    
    try:
        embeddings = await vector_store.get_embeddings_batch(texts)
    except Exception as e:
        print(f"   ⚠️ Embedding 失败: {e}")
        return 0
    
    vectors = []
    for item, embedding in zip(items, embeddings):
        item["values"] = embedding
        vectors.append(item)
    
    try:
        count = vector_store.upsert(vectors, namespace="categories")
        print(f"✅ 赛道同步完成，共 {count} 条")
        return count
    except Exception as e:
        print(f"   ⚠️ 上传失败: {e}")
        return 0


# ============================================================================
# 主函数
# ============================================================================

async def show_stats():
    """显示向量库统计"""
    if not vector_store.enabled:
        print("❌ 向量服务未启用")
        return
    
    stats = vector_store.stats()
    print("\n📊 向量库统计:")
    print(f"   总向量数: {stats.get('total_vector_count', 0)}")
    
    namespaces = stats.get("namespaces", {})
    if namespaces:
        for ns, info in namespaces.items():
            print(f"   - {ns}: {info.get('vector_count', 0)} 条")
    else:
        print("   (暂无数据)")


async def main():
    parser = argparse.ArgumentParser(description="同步数据到向量库")
    parser.add_argument("--all", action="store_true", help="同步所有数据")
    parser.add_argument("--products", action="store_true", help="只同步产品")
    parser.add_argument("--categories", action="store_true", help="只同步赛道")
    parser.add_argument("--full", action="store_true", help="全量同步（清空后重建）")
    parser.add_argument("--stats", action="store_true", help="查看统计信息")
    args = parser.parse_args()
    
    if not vector_store.enabled:
        print("❌ 向量服务未启用，请配置 PINECONE_API_KEY")
        return
    
    if args.stats:
        await show_stats()
        return
    
    # 默认同步所有
    sync_all = args.all or (not args.products and not args.categories)
    
    total = 0
    
    if sync_all or args.products:
        total += await sync_products(full=args.full)
    
    if sync_all or args.categories:
        total += await sync_categories(full=args.full)
    
    print(f"\n🎉 全部完成，共同步 {total} 条向量")
    await show_stats()


if __name__ == "__main__":
    asyncio.run(main())
