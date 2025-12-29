#!/usr/bin/env python
"""
SaaS Analysis Tool - 统一命令行入口

Usage:
    python main.py scrape   # 执行网页抓取
    python main.py update   # 从HTML快照更新数据库
    python main.py sync     # 同步founders和leaderboard表
    python main.py analyze  # 数据分析命令组
"""

import asyncio
import argparse
import sys
import json
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from logging_config import setup_logging, get_logger
from data_sync import DataSyncManager, sync_leaderboard_from_startups


logger = get_logger(__name__)


async def cmd_scrape(args):
    """执行网页抓取"""
    from crawler.run import run_crawler

    print(f"\n开始执行网页抓取...")
    print(f"目标: {'全部可用' if args.max_startups == 0 else f'最多 {args.max_startups} 个'} startup")

    await run_crawler(
        max_startups=args.max_startups,
        scrape_leaderboard=not args.skip_leaderboard
    )

    print("抓取完成")


async def cmd_update(args):
    """从HTML快照更新数据库"""
    manager = DataSyncManager()

    snapshot_dir = Path(args.dir) if args.dir else None
    print(f"\n从快照更新数据库...")

    stats = await manager.update_from_snapshots(snapshot_dir)

    print(f"\n更新完成:")
    print(f"  总文件: {stats.get('total', 0)}")
    print(f"  更新: {stats.get('updated', 0)}")
    print(f"  新建: {stats.get('created', 0)}")
    print(f"  Founders: {stats.get('founders_synced', 0)}")
    if stats.get('errors', 0) > 0:
        print(f"  错误: {stats.get('errors', 0)}")


async def cmd_sync(args):
    """同步founders和leaderboard表"""
    manager = DataSyncManager()

    print("\n同步数据表...")

    # 同步founders
    print("  同步founders表...")
    founder_count = await manager.sync_founders_from_startups()

    # 同步leaderboard
    print("  同步leaderboard表...")
    leaderboard_count = await sync_leaderboard_from_startups()

    print(f"\n同步完成:")
    print(f"  Founders: {founder_count}")
    print(f"  Leaderboard: {leaderboard_count}")


async def cmd_analyze_category(args):
    """赛道分析命令"""
    from database.db import get_db_session
    from analysis.category_analyzer import CategoryAnalyzer

    async with get_db_session() as db:
        analyzer = CategoryAnalyzer(db)

        if args.name:
            # 分析单个赛道
            print(f"\n分析赛道: {args.name}")
            analysis = await analyzer.analyze_category(args.name)

            # 保存到数据库
            await analyzer.save_analysis(analysis)

            print(f"\n{'-'*50}")
            print(f"赛道: {analysis.category}")
            print(f"项目数: {analysis.total_projects}")
            print(f"总收入: ${analysis.total_revenue:,.0f}")
            print(f"平均收入: ${analysis.avg_revenue:,.0f}")
            print(f"中位数收入: ${analysis.median_revenue:,.0f}")
            print(f"单项目收入: ${analysis.revenue_per_project:,.0f}")
            print(f"TOP10占比: {analysis.top10_revenue_share:.1f}%")
            print(f"市场类型: {analysis.market_type}")
            print(f"原因: {analysis.market_type_reason}")
            print(f"\n[已保存到数据库]")

            # 模板化产品
            if args.templates:
                templates = await analyzer.find_template_products(args.name)
                if templates:
                    print(f"\n模板化产品分组:")
                    for t in templates:
                        print(f"  {t['pattern']}: {t['count']}个产品")
        else:
            # 分析所有赛道
            print("\n分析所有赛道...")
            analyses = await analyzer.analyze_all_categories()

            print(f"\n{'赛道':<25} {'项目数':>8} {'总收入':>12} {'单项目收入':>12} {'市场类型':>12}")
            print("-" * 75)

            for a in analyses[:args.limit]:
                print(f"{a.category:<25} {a.total_projects:>8} ${a.total_revenue:>10,.0f} ${a.revenue_per_project:>10,.0f} {a.market_type:>12}")
                # 保存每个赛道分析到数据库
                await analyzer.save_analysis(a)

            print(f"\n共 {len(analyses)} 个赛道 [已保存到数据库]")


async def cmd_analyze_product(args):
    """选品分析命令"""
    from database.db import get_db_session
    from sqlalchemy import select
    from database.models import Startup
    from analysis.product_selector import ProductSelector

    async with get_db_session() as db:
        selector = ProductSelector(db)

        if args.slug:
            # 分析单个产品
            result = await db.execute(
                select(Startup).where(Startup.slug == args.slug)
            )
            startup = result.scalar_one_or_none()

            if not startup:
                print(f"产品 '{args.slug}' 未找到")
                return

            score = await selector.analyze_product(startup)

            print(f"\n产品选品分析: {score.name}")
            print("-" * 50)
            print(f"产品驱动型: {'是' if score.is_product_driven else '否'}")
            print(f"IP依赖度: {score.ip_dependency_score:.1f}/10")
            print(f"小而美: {'是' if score.is_small_and_beautiful else '否'}")
            print(f"描述字数: {score.description_word_count}")
            print(f"技术复杂度: {score.tech_complexity_level}")
            print(f"依赖LLM: {'是' if score.uses_llm_api else '否'}")
            print(f"需要合规: {'是' if score.requires_compliance else '否'}")
            print(f"\n组合匹配:")
            print(f"  组合1 (低粉丝+高收入+简单+年轻): {'匹配' if score.combo1_match else '不匹配'}")
            print(f"  组合3 (简单+有收入+低复杂度): {'匹配' if score.combo3_match else '不匹配'}")
            print(f"\n个人开发适合度: {score.individual_dev_suitability:.1f}/10")

            # 保存分析
            if args.save:
                await selector.save_analysis(score)
                print("\n分析结果已保存到数据库")

        elif args.opportunities:
            # 筛选机会产品
            print(f"\n筛选适合个人开发者的机会产品...")
            opportunities = await selector.find_opportunities(
                min_revenue=args.min_revenue,
                max_complexity=args.max_complexity,
                limit=args.limit
            )

            print(f"\n{'名称':<30} {'收入':>10} {'复杂度':>8} {'适合度':>8} {'数据质量':<12}")
            print("-" * 75)

            for o in opportunities:
                quality = "完整" if o.has_follower_data else "缺粉丝数据"
                print(f"{o.name[:28]:<30} ${o.follower_revenue_ratio*1000:>8,.0f} {o.tech_complexity_level:>8} {o.individual_dev_suitability:>8.1f} {quality:<12}")

            print(f"\n共找到 {len(opportunities)} 个机会产品")

            # 保存所有分析结果
            if args.save:
                print(f"\n保存分析结果到数据库...")
                saved = 0
                for o in opportunities:
                    await selector.save_analysis(o)
                    saved += 1
                print(f"已保存 {saved} 个产品的选品分析")

        else:
            # 默认显示帮助
            print("请使用 --slug 指定产品或使用 --opportunities 筛选机会产品")


async def cmd_analyze_landing(args):
    """Landing Page分析命令"""
    from database.db import get_db_session
    from sqlalchemy import select
    from database.models import Startup
    from analysis.landing_analyzer import LandingPageAnalyzer
    from services.openai_service import OpenAIService

    async with get_db_session() as db:
        try:
            openai_service = OpenAIService()
        except ValueError as e:
            print(f"错误: OpenAI服务未配置 - {e}")
            print("请在.env文件中设置 OPENAI_API_KEY")
            return

        analyzer = LandingPageAnalyzer(db, openai_service)

        try:
            if args.slug:
                # 分析单个产品
                result = await db.execute(
                    select(Startup).where(Startup.slug == args.slug)
                )
                startup = result.scalar_one_or_none()

                if not startup:
                    print(f"产品 '{args.slug}' 未找到")
                    return

                if not startup.website_url:
                    print(f"产品 '{startup.name}' 没有官网URL")
                    return

                print(f"\n分析Landing Page: {startup.name}")
                print(f"URL: {startup.website_url}")
                print("正在爬取和分析，请稍候...")

                analysis = await analyzer.analyze_startup(
                    startup_id=startup.id,
                    force_rescrape=args.force
                )

                if not analysis:
                    print("分析失败")
                    return

                print(f"\n{'='*50}")
                print(f"Landing Page分析结果")
                print(f"{'='*50}")
                print(f"\n目标用户: {', '.join(analysis.target_audience or [])}")
                print(f"目标角色: {', '.join(analysis.target_roles or [])}")
                print(f"核心功能: {', '.join(analysis.core_features or [])}")
                print(f"功能数量: {analysis.feature_count}")
                print(f"\n定价模型: {analysis.pricing_model}")
                print(f"有免费层: {'是' if analysis.has_free_tier else '否'}")
                print(f"有试用: {'是' if analysis.has_trial else '否'}")
                print(f"\nCTA数量: {analysis.cta_count}")
                print(f"转化步骤: {analysis.conversion_funnel_steps}")
                print(f"\n评分:")
                print(f"  定位清晰度: {analysis.positioning_clarity_score:.1f}/10")
                print(f"  痛点锋利度: {analysis.pain_point_sharpness:.1f}/10")
                print(f"  定价清晰度: {analysis.pricing_clarity_score:.1f}/10")
                print(f"  转化友好度: {analysis.conversion_friendliness_score:.1f}/10")
                print(f"  个人可复制性: {analysis.individual_replicability_score:.1f}/10")
                print(f"  产品成熟度: {analysis.product_maturity_score:.1f}/10")

            elif args.batch or getattr(args, 'all', False) or getattr(args, 'update', False):
                # 批量分析
                from database.models import LandingPageAnalysis
                from sqlalchemy import func

                # --update 模式等同于 --all --skip-analyzed
                is_update_mode = getattr(args, 'update', False)
                is_all_mode = getattr(args, 'all', False) or is_update_mode
                skip_analyzed = args.skip_analyzed or is_update_mode

                # 先统计总数
                total_with_url_query = select(func.count(Startup.id)).where(Startup.website_url.isnot(None))
                total_with_url = (await db.execute(total_with_url_query)).scalar()

                # 统计已分析数量
                analyzed_count_query = select(func.count(LandingPageAnalysis.id))
                analyzed_count = (await db.execute(analyzed_count_query)).scalar()

                # 构建查询
                query = select(Startup.id).where(Startup.website_url.isnot(None))

                # 跳过已分析的
                if skip_analyzed:
                    analyzed_ids = select(LandingPageAnalysis.startup_id)
                    query = query.where(Startup.id.notin_(analyzed_ids))

                # 按收入排序（用coalesce处理NULL，SQLite不支持NULLS LAST）
                query = query.order_by(func.coalesce(Startup.revenue_30d, 0).desc())

                # --all/--update 分析所有，否则用 --limit
                if not is_all_mode:
                    query = query.limit(args.limit)

                result = await db.execute(query)
                startup_ids = [row[0] for row in result.all()]

                if not startup_ids:
                    print("没有需要分析的产品")
                    if skip_analyzed:
                        print(f"(已分析: {analyzed_count}/{total_with_url}，所有有URL的产品都已分析过)")
                        print("如需重新分析请去掉 --skip-analyzed 或 --update")
                else:
                    if is_update_mode:
                        mode_name = "增量更新"
                    elif is_all_mode:
                        mode_name = "全量分析"
                    else:
                        mode_name = f"前{args.limit}个"

                    skip_info = f"(已跳过 {analyzed_count} 个已分析产品)" if skip_analyzed and analyzed_count > 0 else ""

                    print(f"\n{'='*50}")
                    print(f"Landing Page 分析 - {mode_name}")
                    print(f"{'='*50}")
                    print(f"有URL的产品总数: {total_with_url}")
                    print(f"已分析数量: {analyzed_count}")
                    print(f"待分析数量: {len(startup_ids)} {skip_info}")
                    print(f"预计耗时: {len(startup_ids) * (args.delay + 10) / 60:.1f} 分钟")
                    print(f"{'='*50}\n")

                    stats = await analyzer.batch_analyze(startup_ids, delay_between=args.delay)

                    print(f"\n批量分析完成:")
                    print(f"  成功: {stats['success']}")
                    print(f"  失败: {stats['failed']}")
                    print(f"  跳过: {stats.get('skipped', 0)}")

            else:
                print("请使用 --slug 指定产品或使用 --batch/--all 批量分析")
        finally:
            # 确保关闭OpenAI客户端连接
            await analyzer.close()


async def cmd_analyze_comprehensive(args):
    """综合分析命令"""
    from database.db import get_db_session
    from sqlalchemy import select
    from database.models import Startup
    from analysis.comprehensive import ComprehensiveAnalyzer

    async with get_db_session() as db:
        analyzer = ComprehensiveAnalyzer(db)

        if args.slug:
            # 分析单个产品
            result = await db.execute(
                select(Startup).where(Startup.slug == args.slug)
            )
            startup = result.scalar_one_or_none()

            if not startup:
                print(f"产品 '{args.slug}' 未找到")
                return

            print(f"\n生成综合分析报告: {startup.name}")
            analysis = await analyzer.analyze_startup(startup.id)

            if not analysis:
                print("分析失败")
                return

            summary = analysis.analysis_summary or {}

            print(f"\n{'='*60}")
            print(f"综合分析报告: {startup.name}")
            print(f"{'='*60}")
            print(f"\n收入: ${startup.revenue_30d:,.0f}/月")
            print(f"分类: {startup.category}")

            print(f"\n综合评分:")
            print(f"  产品成熟度: {analysis.maturity_score:.1f}/10")
            print(f"  定位清晰度: {analysis.positioning_clarity:.1f}/10")
            print(f"  痛点锋利度: {analysis.pain_point_sharpness:.1f}/10")
            print(f"  定价清晰度: {analysis.pricing_clarity:.1f}/10")
            print(f"  转化友好度: {analysis.conversion_friendliness:.1f}/10")
            print(f"  个人可复制性: {analysis.individual_replicability:.1f}/10")
            print(f"\n  综合推荐指数: {analysis.overall_recommendation:.1f}/10")

            if summary.get('strengths'):
                print(f"\n优势:")
                for s in summary['strengths']:
                    print(f"  + {s}")

            if summary.get('risks'):
                print(f"\n风险:")
                for r in summary['risks']:
                    print(f"  - {r}")

            if summary.get('recommendations'):
                print(f"\n建议:")
                for r in summary['recommendations']:
                    print(f"  * {r}")

            if args.export:
                # 导出JSON
                export_path = Path(args.export)
                export_path.write_text(json.dumps(analysis.to_dict(), indent=2, ensure_ascii=False))
                print(f"\n已导出到: {export_path}")

        elif args.top:
            # 获取TOP推荐
            print(f"\n获取综合推荐TOP{args.limit}...")
            recommendations = await analyzer.get_top_recommendations(args.limit)

            print(f"\n{'排名':>4} {'名称':<30} {'收入':>10} {'推荐指数':>8}")
            print("-" * 60)

            for i, rec in enumerate(recommendations, 1):
                startup = rec['startup']
                analysis = rec['analysis']
                print(f"{i:>4} {startup['name'][:28]:<30} ${startup.get('revenue_30d', 0):>8,.0f} {analysis['overall_recommendation']:>8.1f}")

        else:
            print("请使用 --slug 指定产品或使用 --top 获取推荐列表")


def main():
    """主入口"""
    parser = argparse.ArgumentParser(
        description="SaaS Analysis Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py scrape              # 完整抓取 (无限制)
  python main.py scrape --max-startups 10  # 限制抓取数量 (测试用)
  python main.py update              # 从快照更新数据库
  python main.py sync                # 同步founders和leaderboard表

  # 分析命令
  python main.py analyze category                    # 分析所有赛道
  python main.py analyze category --name "SaaS"      # 分析单个赛道
  python main.py analyze product --opportunities     # 筛选机会产品
  python main.py analyze product --slug xxx          # 分析单个产品
  python main.py analyze landing --slug xxx          # 分析单个Landing Page
  python main.py analyze landing --update            # 增量更新（只分析新增/未分析的）
  python main.py analyze landing --all               # 全量分析所有产品
  python main.py analyze comprehensive --slug xxx    # 综合分析
  python main.py analyze comprehensive --top         # 获取TOP推荐
        """
    )

    subparsers = parser.add_subparsers(dest='command', required=True, help='可用命令')

    # scrape 命令
    scrape_parser = subparsers.add_parser('scrape', help='执行网页抓取')
    scrape_parser.add_argument('--max-startups', type=int, default=0,
                               help='最大抓取数量 (0 = 无限制，抓取全部)')
    scrape_parser.add_argument('--skip-leaderboard', action='store_true',
                               help='跳过排行榜抓取')

    # update 命令
    update_parser = subparsers.add_parser('update', help='从HTML快照更新数据库')
    update_parser.add_argument('--dir', type=str, default=None,
                               help='HTML快照目录路径')

    # sync 命令
    sync_parser = subparsers.add_parser('sync', help='同步founders和leaderboard表')

    # analyze 命令组
    analyze_parser = subparsers.add_parser('analyze', help='数据分析命令')
    analyze_subparsers = analyze_parser.add_subparsers(dest='analyze_type', required=True)

    # analyze category
    cat_parser = analyze_subparsers.add_parser('category', help='赛道/领域分析')
    cat_parser.add_argument('--name', type=str, help='赛道名称 (不指定则分析全部)')
    cat_parser.add_argument('--templates', action='store_true', help='显示模板化产品')
    cat_parser.add_argument('--limit', type=int, default=50, help='显示数量限制')

    # analyze product
    prod_parser = analyze_subparsers.add_parser('product', help='选品分析')
    prod_parser.add_argument('--slug', type=str, help='产品slug')
    prod_parser.add_argument('--opportunities', action='store_true', help='筛选机会产品')
    prod_parser.add_argument('--min-revenue', type=float, default=3000, help='最低收入')
    prod_parser.add_argument('--max-complexity', type=str, default='medium',
                             choices=['low', 'medium', 'high'], help='最高复杂度')
    prod_parser.add_argument('--limit', type=int, default=20, help='结果数量限制')
    prod_parser.add_argument('--save', action='store_true', help='保存分析结果')

    # analyze landing
    landing_parser = analyze_subparsers.add_parser('landing', help='Landing Page分析')
    landing_parser.add_argument('--slug', type=str, help='产品slug')
    landing_parser.add_argument('--batch', action='store_true', help='批量分析（按收入排序）')
    landing_parser.add_argument('--all', action='store_true', help='分析所有有URL的产品')
    landing_parser.add_argument('--update', action='store_true', help='增量更新模式（只分析新增/未分析的产品）')
    landing_parser.add_argument('--limit', type=int, default=10, help='批量分析数量（--all/--update时忽略）')
    landing_parser.add_argument('--delay', type=float, default=3.0, help='批量分析间隔(秒)')
    landing_parser.add_argument('--force', action='store_true', help='强制重新爬取')
    landing_parser.add_argument('--skip-analyzed', action='store_true', help='跳过已分析的产品')

    # analyze comprehensive
    comp_parser = analyze_subparsers.add_parser('comprehensive', help='综合分析')
    comp_parser.add_argument('--slug', type=str, help='产品slug')
    comp_parser.add_argument('--top', action='store_true', help='获取TOP推荐列表')
    comp_parser.add_argument('--limit', type=int, default=20, help='结果数量限制')
    comp_parser.add_argument('--export', type=str, help='导出JSON文件路径')

    args = parser.parse_args()

    # 设置日志
    setup_logging()

    # 命令映射
    commands = {
        'scrape': cmd_scrape,
        'update': cmd_update,
        'sync': cmd_sync,
    }

    # analyze子命令映射
    analyze_commands = {
        'category': cmd_analyze_category,
        'product': cmd_analyze_product,
        'landing': cmd_analyze_landing,
        'comprehensive': cmd_analyze_comprehensive,
    }

    # 执行命令
    try:
        if args.command == 'analyze':
            asyncio.run(analyze_commands[args.analyze_type](args))
        else:
            asyncio.run(commands[args.command](args))
    except KeyboardInterrupt:
        print("\n操作已取消")
        sys.exit(1)
    except Exception as e:
        logger.error(f"执行失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
