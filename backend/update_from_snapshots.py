"""
从HTML快照更新数据库字段
"""

import asyncio
from pathlib import Path
from typing import Optional
from datetime import datetime

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from database.models import Base, Startup, Founder
from crawler.html_parser import parse_html_file, parse_all_snapshots


# 数据库路径
DATABASE_PATH = Path(__file__).parent / 'data' / 'sass_analysis.db'
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"


def init_database():
    """初始化数据库，创建所有表"""
    # 确保data目录存在
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    engine = create_engine(DATABASE_URL, echo=False)
    Base.metadata.create_all(engine)
    print(f"Database initialized: {DATABASE_PATH}")
    return engine


def get_session():
    """获取数据库会话"""
    engine = init_database()
    Session = sessionmaker(bind=engine)
    return Session()


def parse_growth_rate(percent_str: str) -> Optional[float]:
    """解析增长率字符串为浮点数"""
    if not percent_str:
        return None
    # 移除 % 符号和空格
    clean = percent_str.replace('%', '').strip()
    try:
        return float(clean)
    except ValueError:
        return None


def parse_multiple(multiple_str: str) -> Optional[float]:
    """解析倍数字符串为浮点数"""
    if not multiple_str:
        return None
    # 移除 x 后缀
    clean = multiple_str.lower().replace('x', '').strip()
    try:
        return float(clean)
    except ValueError:
        return None


def update_startup_from_parsed_data(startup: Startup, data: dict) -> bool:
    """
    从解析的数据更新Startup对象

    Args:
        startup: 数据库中的Startup对象
        data: HTMLParser解析的数据字典

    Returns:
        是否有字段被更新
    """
    updated = False

    # 基本信息
    if data.get('name') and not startup.name:
        startup.name = data['name']
        updated = True

    if data.get('description') and not startup.description:
        startup.description = data['description']
        updated = True

    # URLs
    if data.get('website_url'):
        startup.website_url = data['website_url']
        updated = True

    if data.get('logo_url'):
        startup.logo_url = data['logo_url']
        updated = True

    if data.get('trustmrr_url'):
        startup.profile_url = data['trustmrr_url']
        updated = True

    # Founder信息
    if data.get('founder_name'):
        startup.founder_name = data['founder_name']
        updated = True

    if data.get('founder_username'):
        startup.founder_username = data['founder_username']
        updated = True

    if data.get('founder_followers'):
        startup.founder_followers = data['founder_followers']
        updated = True

    if data.get('founder_social_platform'):
        startup.founder_social_platform = data['founder_social_platform']
        updated = True

    # 财务数据
    if data.get('total_revenue_raw'):
        startup.total_revenue = float(data['total_revenue_raw'])
        updated = True

    if data.get('mrr_raw'):
        startup.mrr = float(data['mrr_raw'])
        updated = True

    if data.get('revenue_last_4_weeks_raw'):
        startup.revenue_30d = float(data['revenue_last_4_weeks_raw'])
        updated = True

    growth_rate = parse_growth_rate(data.get('revenue_change_percent', ''))
    if growth_rate is not None:
        startup.growth_rate = growth_rate
        updated = True

    # 出售信息
    if 'is_for_sale' in data:
        startup.is_for_sale = data['is_for_sale']
        updated = True

    if data.get('asking_price_raw'):
        startup.asking_price = float(data['asking_price_raw'])
        updated = True

    multiple = parse_multiple(data.get('revenue_multiple', ''))
    if multiple is not None:
        startup.multiple = multiple
        updated = True

    if data.get('buyers_interested'):
        startup.buyers_interested = data['buyers_interested']
        updated = True

    # 公司信息
    if data.get('founded'):
        startup.founded_date = data['founded']
        updated = True

    if data.get('country'):
        startup.country = data['country']
        updated = True

    if data.get('country_code'):
        startup.country_code = data['country_code']
        updated = True

    if data.get('category'):
        startup.category = data['category']
        updated = True

    # 排名
    if data.get('rank'):
        startup.rank = data['rank']
        updated = True

    # 订阅数
    if data.get('active_subscriptions'):
        startup.customers_count = data['active_subscriptions']
        updated = True

    # 验证状态
    if data.get('verified_source'):
        startup.is_verified = True
        startup.verified_source = data['verified_source']
        updated = True

    if updated:
        startup.updated_at = datetime.utcnow()

    return updated


def update_database_from_snapshots(snapshot_dir: str = None):
    """
    从HTML快照目录更新数据库

    Args:
        snapshot_dir: HTML快照目录路径，默认使用标准路径
    """
    if snapshot_dir is None:
        snapshot_dir = Path(__file__).parent / 'data' / 'html_snapshots'
    else:
        snapshot_dir = Path(snapshot_dir)

    if not snapshot_dir.exists():
        print(f"Error: Snapshot directory not found: {snapshot_dir}")
        return

    session = get_session()

    try:
        # 获取所有HTML文件
        html_files = list(snapshot_dir.glob('*.html'))
        print(f"Found {len(html_files)} HTML snapshots")

        updated_count = 0
        created_count = 0
        error_count = 0

        for html_file in html_files:
            slug = html_file.stem

            try:
                # 解析HTML
                data = parse_html_file(html_file)

                # 查找或创建Startup
                startup = session.query(Startup).filter_by(slug=slug).first()

                if startup:
                    # 更新现有记录
                    if update_startup_from_parsed_data(startup, data):
                        startup.html_snapshot_path = str(html_file)
                        updated_count += 1
                        print(f"  Updated: {slug}")
                    else:
                        print(f"  No changes: {slug}")
                else:
                    # 创建新记录
                    startup = Startup(
                        slug=slug,
                        name=data.get('name', slug),
                        html_snapshot_path=str(html_file)
                    )
                    update_startup_from_parsed_data(startup, data)
                    session.add(startup)
                    created_count += 1
                    print(f"  Created: {slug}")

            except Exception as e:
                print(f"  Error parsing {slug}: {e}")
                error_count += 1

        # 提交更改
        session.commit()

        print(f"\n{'='*60}")
        print(f"Summary:")
        print(f"  Updated: {updated_count}")
        print(f"  Created: {created_count}")
        print(f"  Errors: {error_count}")

    except Exception as e:
        session.rollback()
        print(f"Database error: {e}")
        raise
    finally:
        session.close()


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        snapshot_dir = sys.argv[1]
    else:
        snapshot_dir = None

    update_database_from_snapshots(snapshot_dir)
