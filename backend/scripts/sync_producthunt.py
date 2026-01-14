"""
Product Hunt 数据同步脚本

支持多种同步模式，适合长期积累数据：

1. --new       抓取最新产品（遇到已有的就停止，适合每日运行）
2. --history   抓取历史产品（从断点继续往后翻页）
3. --bydate    按日期分段抓取（绕过 API 深度限制，获取更多历史数据）
4. --refresh   更新已有产品的热度数据

使用方式:
    # 每天抓新上榜的产品
    python scripts/sync_producthunt.py --new
    
    # 按日期抓取历史数据（推荐，可获取更多数据）
    python scripts/sync_producthunt.py --bydate --start 2024-01-01 --end 2024-12-31
    
    # 刷新已有产品的 votes/comments
    python scripts/sync_producthunt.py --refresh --limit 500
    
环境变量:
    PH_TOKENS=token1,token2,token3
"""

import os
import sys
import asyncio
import argparse
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Set
from urllib.parse import urlparse
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import select, desc
from database.db import AsyncSessionLocal
from database.models import Startup, ProductHuntPost
from services.producthunt import ProductHuntClient, ProductHuntDataService, ProductHuntRateLimitError, resolve_redirect_url

# 数据目录
DATA_DIR = Path(__file__).parent.parent / "data"
HISTORY_CHECKPOINT = DATA_DIR / "ph_history_checkpoint.json"
BYDATE_CHECKPOINT = DATA_DIR / "ph_bydate_checkpoint.json"


class ProductHuntSyncer:
    """Product Hunt 数据同步器"""
    
    def __init__(self, client: Optional[ProductHuntClient] = None):
        self.client = client or ProductHuntClient()
        self.service = ProductHuntDataService(self.client)
        self.stats = {"fetched": 0, "inserted": 0, "updated": 0, "skipped": 0, "errors": 0}
        self._existing_ids: Set[str] = set()
    
    async def _load_existing_ids(self):
        """加载已有的 PH ID"""
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(ProductHuntPost.ph_id))
            self._existing_ids = {row[0] for row in result.fetchall()}
        print(f"[DB] Loaded {len(self._existing_ids)} existing records")
    
    def _load_history_checkpoint(self) -> Optional[dict]:
        """加载历史抓取断点"""
        if HISTORY_CHECKPOINT.exists():
            with open(HISTORY_CHECKPOINT, "r") as f:
                return json.load(f)
        return None
    
    def _save_history_checkpoint(self, cursor: str, page: int):
        """保存历史抓取断点"""
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(HISTORY_CHECKPOINT, "w") as f:
            json.dump({"cursor": cursor, "page": page, "saved_at": datetime.utcnow().isoformat()}, f)
    
    # ========== 模式1: 抓新产品 ==========
    async def sync_new(self, max_pages: int = 10, delay: float = 1.0):
        """抓取最新产品，遇到已有的就停止"""
        print(f"\n{'='*50}\n[MODE] Sync NEW products\n{'='*50}")
        await self._load_existing_ids()
        
        cursor = None
        consecutive_existing = 0
        
        for page in range(max_pages):
            print(f"\n[Page {page+1}] Fetching latest posts...")
            result = await self.service.get_posts(first=20, after=cursor, order="NEWEST")
            edges = result.get("posts", {}).get("edges", [])
            
            if not edges:
                print("[Done] No more posts")
                break
            
            new_count = 0
            for edge in edges:
                post = edge.get("node", {})
                ph_id = str(post.get("id", ""))
                self.stats["fetched"] += 1
                
                if ph_id in self._existing_ids:
                    consecutive_existing += 1
                    self.stats["skipped"] += 1
                else:
                    if await self._save_post(post):
                        self._existing_ids.add(ph_id)
                        new_count += 1
                        consecutive_existing = 0
            
            print(f"[Page {page+1}] {new_count} new, {len(edges)-new_count} existing")
            
            # 连续遇到20条已有的就停止
            if consecutive_existing >= 20:
                print(f"[Done] Found {consecutive_existing} consecutive existing posts, stopping")
                break
            
            page_info = result.get("posts", {}).get("pageInfo", {})
            if not page_info.get("hasNextPage"):
                break
            cursor = page_info.get("endCursor")
            
            await asyncio.sleep(delay)
        
        self._print_stats()

    # ========== 模式2: 抓历史产品 ==========
    async def sync_history(self, max_pages: int = 50, delay: float = 1.5):
        """从断点继续抓取历史产品"""
        print(f"\n{'='*50}\n[MODE] Sync HISTORY products\n{'='*50}")
        await self._load_existing_ids()
        
        # 加载断点
        checkpoint = self._load_history_checkpoint()
        cursor = checkpoint.get("cursor") if checkpoint else None
        start_page = checkpoint.get("page", 0) if checkpoint else 0
        
        if cursor:
            print(f"[Resume] From page {start_page}, cursor: {cursor[:30]}...")
        else:
            print("[Start] From beginning")
        
        for page in range(start_page, start_page + max_pages):
            print(f"\n[Page {page+1}] Fetching...")
            
            try:
                # 不限制 featured，获取更多数据
                result = await self.service.get_posts(first=20, after=cursor, featured=False, order="NEWEST")
                edges = result.get("posts", {}).get("edges", [])
                page_info = result.get("posts", {}).get("pageInfo", {})
                
                print(f"[Page {page+1}] Got {len(edges)} posts, hasNextPage={page_info.get('hasNextPage')}")
                
                if not edges:
                    print("[Done] No more posts returned")
                    break
                
                new_count = 0
                for edge in edges:
                    post = edge.get("node", {})
                    ph_id = str(post.get("id", ""))
                    self.stats["fetched"] += 1
                    
                    if ph_id in self._existing_ids:
                        self.stats["skipped"] += 1
                    else:
                        if await self._save_post(post):
                            self._existing_ids.add(ph_id)
                            new_count += 1
                
                print(f"[Page {page+1}] {new_count} new, {len(edges)-new_count} skipped")
                
                # 保存断点
                cursor = page_info.get("endCursor")
                if cursor:
                    self._save_history_checkpoint(cursor, page + 1)
                
                if not page_info.get("hasNextPage"):
                    print("[Done] API says no more pages (hasNextPage=false)")
                    print("[Info] This is a Product Hunt API limitation, not all historical data is accessible")
                    break
                
                await asyncio.sleep(delay)
                
            except ProductHuntRateLimitError as e:
                print(f"\n[Rate Limited] {e}")
                print(f"[Checkpoint Saved] Run again later to continue from page {page+1}")
                break
        
        self._print_stats()
    
    # ========== 模式3: 刷新已有数据 ==========
    async def refresh_existing(self, limit: int = 100, delay: float = 0.5):
        """刷新已有产品数据，优先处理缺失 website_resolved 的记录"""
        print(f"\n{'='*50}\n[MODE] REFRESH existing products\n{'='*50}")
        
        async with AsyncSessionLocal() as db:
            # 优先获取缺失 website_resolved 的记录
            result = await db.execute(
                select(ProductHuntPost.slug)
                .where(ProductHuntPost.website_resolved.is_(None))
                .order_by(ProductHuntPost.synced_at.asc())
                .limit(limit)
            )
            slugs = [row[0] for row in result.fetchall()]
            
            # 如果不够，再补充其他旧数据
            if len(slugs) < limit:
                remaining = limit - len(slugs)
                result2 = await db.execute(
                    select(ProductHuntPost.slug)
                    .where(ProductHuntPost.website_resolved.isnot(None))
                    .order_by(ProductHuntPost.synced_at.asc())
                    .limit(remaining)
                )
                slugs.extend([row[0] for row in result2.fetchall()])
        
        print(f"[Refresh] {len(slugs)} products to update")
        
        for i, slug in enumerate(slugs):
            try:
                post = await self.service.get_post_by_slug(slug)
                if post:
                    await self._save_post(post, update_only=True)
                    self.stats["updated"] += 1
                    if (i + 1) % 10 == 0:
                        print(f"[Progress] {i+1}/{len(slugs)} updated")
                await asyncio.sleep(delay)
            except Exception as e:
                print(f"[Error] {slug}: {e}")
                self.stats["errors"] += 1
        
        self._print_stats()
    
    # ========== 模式4: 按日期分段抓取 ==========
    async def sync_by_date(self, start_date: str, end_date: str, delay: float = 1.5, force_update: bool = False):
        """
        按日期分段抓取，绕过 API 深度限制
        
        Args:
            force_update: 强制更新已存在的记录（用于补充 website 等新字段）
        """
        print(f"\n{'='*50}\n[MODE] Sync BY DATE {'(FORCE UPDATE)' if force_update else ''}\n{'='*50}")
        print(f"Date range: {start_date} to {end_date}")
        
        if not force_update:
            await self._load_existing_ids()
        
        # 解析日期
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        # 加载断点（force 模式也支持断点）
        checkpoint = self._load_bydate_checkpoint()
        resume_cursor = None
        resume_page = 0
        if checkpoint:
            resume_date = checkpoint.get("current_date")
            if resume_date:
                start = datetime.strptime(resume_date, "%Y-%m-%d")
                resume_cursor = checkpoint.get("cursor")
                resume_page = checkpoint.get("page", 0)
                if resume_cursor:
                    print(f"[Resume] From {resume_date}, page {resume_page + 1}")
                else:
                    print(f"[Resume] From {resume_date}")
        
        # 按月分段
        current = start
        is_first_month = True
        
        while current <= end:
            # 计算当月范围
            month_start = current.replace(day=1)
            if current.month == 12:
                month_end = current.replace(year=current.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                month_end = current.replace(month=current.month + 1, day=1) - timedelta(days=1)
            
            # 确保不超过 end_date
            if month_end > end:
                month_end = end
            
            print(f"\n[Month] {month_start.strftime('%Y-%m')} ({month_start.strftime('%Y-%m-%d')} to {month_end.strftime('%Y-%m-%d')})")
            
            # 第一个月使用断点的 cursor，后续月份从头开始
            start_cursor = resume_cursor if is_first_month else None
            start_page = resume_page if is_first_month else 0
            is_first_month = False
            
            # 抓取这个月的数据
            completed = await self._fetch_date_range(
                posted_after=month_start.strftime("%Y-%m-%d"),
                posted_before=(month_end + timedelta(days=1)).strftime("%Y-%m-%d"),
                max_pages=50,
                delay=delay,
                month_key=month_start.strftime("%Y-%m-%d"),
                start_cursor=start_cursor,
                start_page=start_page,
                force_update=force_update
            )
            
            if not completed:
                # 被中断了（限流或错误），断点已保存，退出
                print(f"[Paused] Will resume from current position next time")
                self._print_stats()
                return
            
            # 这个月完成，清除 cursor，保存月份进度
            self._save_bydate_checkpoint(month_end.strftime("%Y-%m-%d"), cursor=None, page=0)
            
            # 移动到下个月
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1, day=1)
            else:
                current = current.replace(month=current.month + 1, day=1)
            
            # 月间延迟
            await asyncio.sleep(2)
        
        # 完成，清除断点
        self._clear_bydate_checkpoint()
        self._print_stats()
    
    async def _fetch_date_range(
        self, 
        posted_after: str, 
        posted_before: str, 
        max_pages: int, 
        delay: float,
        month_key: str,
        start_cursor: Optional[str] = None,
        start_page: int = 0,
        force_update: bool = False
    ) -> bool:
        """
        抓取指定日期范围的数据
        
        Args:
            force_update: 强制更新已存在的记录
        
        Returns:
            True: 本月抓取完成
            False: 被中断（限流），需要下次继续
        """
        cursor = start_cursor
        
        for page in range(start_page, max_pages):
            try:
                result = await self.service.get_posts(
                    first=20, 
                    after=cursor, 
                    featured=False,
                    order="NEWEST",
                    posted_after=posted_after,
                    posted_before=posted_before
                )
                edges = result.get("posts", {}).get("edges", [])
                page_info = result.get("posts", {}).get("pageInfo", {})
                
                if not edges:
                    return True  # 没有更多数据，本月完成
                
                new_count = 0
                updated_count = 0
                for edge in edges:
                    post = edge.get("node", {})
                    ph_id = str(post.get("id", ""))
                    self.stats["fetched"] += 1
                    
                    if force_update:
                        # 强制更新模式：所有记录都保存/更新
                        if await self._save_post(post):
                            if ph_id in self._existing_ids:
                                updated_count += 1
                            else:
                                self._existing_ids.add(ph_id)
                                new_count += 1
                    else:
                        # 普通模式：跳过已存在的
                        if ph_id in self._existing_ids:
                            self.stats["skipped"] += 1
                        else:
                            if await self._save_post(post):
                                self._existing_ids.add(ph_id)
                                new_count += 1
                
                if force_update:
                    print(f"  Page {page+1}: {new_count} new, {updated_count} updated")
                else:
                    print(f"  Page {page+1}: {new_count} new, {len(edges)-new_count} skipped")
                
                # 获取下一页 cursor
                next_cursor = page_info.get("endCursor")
                
                # 每页抓完后保存断点（保存下一页的 cursor）
                if next_cursor:
                    self._save_bydate_checkpoint(month_key, cursor=next_cursor, page=page + 1)
                
                if not page_info.get("hasNextPage"):
                    return True  # 本月完成
                
                cursor = next_cursor
                await asyncio.sleep(delay)
                
            except ProductHuntRateLimitError as e:
                print(f"  [Rate Limited] {e}")
                print(f"  [Checkpoint] Saved at page {page + 1}, run again to continue")
                return False  # 被限流，下次从断点继续
            except Exception as e:
                import traceback
                print(f"  [Error] {e}")
                traceback.print_exc()
                self.stats["errors"] += 1
                return False
        
        return True  # 达到 max_pages 限制
    
    def _load_bydate_checkpoint(self) -> Optional[dict]:
        """加载按日期抓取的断点"""
        if BYDATE_CHECKPOINT.exists():
            with open(BYDATE_CHECKPOINT, "r") as f:
                return json.load(f)
        return None
    
    def _save_bydate_checkpoint(self, current_date: str, cursor: Optional[str] = None, page: int = 0):
        """
        保存按日期抓取的断点
        
        Args:
            current_date: 当前正在抓取的月份
            cursor: 当前页的 cursor（用于页内断点续抓）
            page: 当前页码
        """
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(BYDATE_CHECKPOINT, "w") as f:
            json.dump({
                "current_date": current_date,
                "cursor": cursor,
                "page": page,
                "saved_at": datetime.utcnow().isoformat()
            }, f)
    
    def _clear_bydate_checkpoint(self):
        """清除按日期抓取的断点"""
        if BYDATE_CHECKPOINT.exists():
            BYDATE_CHECKPOINT.unlink()

    async def _save_post(self, post: Dict[str, Any], update_only: bool = False) -> bool:
        """保存或更新产品，同时解析真实 URL"""
        ph_id = str(post.get("id", ""))
        if not ph_id:
            return False
        
        async with AsyncSessionLocal() as db:
            try:
                result = await db.execute(
                    select(ProductHuntPost).where(ProductHuntPost.ph_id == ph_id)
                )
                existing = result.scalar_one_or_none()
                
                data = self._parse_post(post)
                
                # 解析真实 URL
                website = data.get("website")
                if website and website.startswith("https://www.producthunt.com/r/"):
                    try:
                        resolved = await resolve_redirect_url(website)
                        if resolved and resolved != website:
                            data["website_resolved"] = resolved
                    except:
                        pass  # 解析失败不影响保存
                
                if existing:
                    for k, v in data.items():
                        if k != "ph_id":
                            setattr(existing, k, v)
                    self.stats["updated"] += 1
                elif not update_only:
                    db.add(ProductHuntPost(**data))
                    self.stats["inserted"] += 1
                else:
                    return False
                
                await db.commit()
                return True
            except Exception as e:
                await db.rollback()
                print(f"  [DB Error] {e}")
                self.stats["errors"] += 1
                return False
    
    def _parse_post(self, post: Dict[str, Any]) -> Dict[str, Any]:
        """解析 API 数据（同步版本，不解析 URL）"""
        topics = None
        if post.get("topics") and post["topics"].get("edges"):
            topics = [{"id": e["node"]["id"], "name": e["node"]["name"], "slug": e["node"]["slug"]} 
                      for e in post["topics"]["edges"]]
        
        makers = None
        if post.get("makers"):
            makers = [{"id": m.get("id"), "name": m.get("name"), "username": m.get("username"), "headline": m.get("headline")} 
                      for m in post["makers"]]
        
        # 解析创建者信息
        user = None
        if post.get("user"):
            u = post["user"]
            user = {"id": u.get("id"), "name": u.get("name"), "username": u.get("username"), "headline": u.get("headline")}
        
        # 解析媒体资源
        media = None
        if post.get("media"):
            media = [{"url": m.get("url"), "type": m.get("type")} for m in post["media"]]
        
        # 解析产品链接
        product_links = None
        if post.get("productLinks"):
            product_links = [{"url": p.get("url")} for p in post["productLinks"]]
        
        featured_at = None
        if post.get("featuredAt"):
            try:
                featured_at = datetime.fromisoformat(post["featuredAt"].replace("Z", "+00:00")).replace(tzinfo=None)
            except: pass
        
        created_at = None
        if post.get("createdAt"):
            try:
                created_at = datetime.fromisoformat(post["createdAt"].replace("Z", "+00:00")).replace(tzinfo=None)
            except: pass
        
        return {
            "ph_id": str(post.get("id", "")),
            "slug": post.get("slug", ""),
            "name": post.get("name", ""),
            "tagline": post.get("tagline"),
            "description": post.get("description"),
            "url": post.get("url"),  # PH 跟踪链接
            "website": post.get("website"),  # PH 返回的 website（可能是重定向）
            "ph_url": f"https://www.producthunt.com/posts/{post.get('slug')}",
            "thumbnail_url": post.get("thumbnail", {}).get("url") if post.get("thumbnail") else None,
            "votes_count": post.get("votesCount", 0),
            "comments_count": post.get("commentsCount", 0),
            "reviews_count": post.get("reviewsCount", 0),
            "reviews_rating": post.get("reviewsRating"),
            "featured_at": featured_at,
            "ph_created_at": created_at,
            "topics": json.dumps(topics, ensure_ascii=False) if topics else None,
            "makers": json.dumps(makers, ensure_ascii=False) if makers else None,
            "user": json.dumps(user, ensure_ascii=False) if user else None,
            "media": json.dumps(media, ensure_ascii=False) if media else None,
            "product_links": json.dumps(product_links, ensure_ascii=False) if product_links else None,
            "raw_data": json.dumps(post, ensure_ascii=False),
            "synced_at": datetime.utcnow(),
        }
    
    def _print_stats(self):
        print(f"\n{'='*50}")
        print(f"Fetched: {self.stats['fetched']}, Inserted: {self.stats['inserted']}, "
              f"Updated: {self.stats['updated']}, Skipped: {self.stats['skipped']}, Errors: {self.stats['errors']}")
        status = self.client.get_status()
        for t in status["tokens"]:
            print(f"Token {t['name']}: {t['complexity_remaining']}/{t['complexity_limit']} remaining")
        print(f"{'='*50}")
    
    def _get_wait_seconds(self) -> int:
        """计算需要等待的秒数（到最近的 reset 时间）"""
        status = self.client.get_status()
        min_wait = 900  # 默认最多等15分钟
        
        for t in status["tokens"]:
            if t.get("reset_at"):
                try:
                    reset_at = datetime.fromisoformat(t["reset_at"])
                    wait = (reset_at - datetime.utcnow()).total_seconds()
                    if 0 < wait < min_wait:
                        min_wait = int(wait) + 5  # 多等5秒确保重置
                except:
                    pass
        
        return max(60, min_wait)  # 至少等60秒


async def main():
    parser = argparse.ArgumentParser(description="Product Hunt Data Sync")
    
    # 模式选择（互斥）
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--new", action="store_true", help="Sync new products (stop when hitting existing)")
    mode.add_argument("--history", action="store_true", help="Sync history (continue from checkpoint)")
    mode.add_argument("--bydate", action="store_true", help="Sync by date range (bypass API depth limit)")
    mode.add_argument("--refresh", action="store_true", help="Refresh existing products' data")
    mode.add_argument("--test", action="store_true", help="Test API connection")
    
    # 参数
    parser.add_argument("--pages", type=int, default=50, help="Max pages (for --new/--history)")
    parser.add_argument("--limit", type=int, default=100, help="Max products (for --refresh)")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between requests")
    parser.add_argument("--start", type=str, help="Start date for --bydate (YYYY-MM-DD)")
    parser.add_argument("--end", type=str, help="End date for --bydate (YYYY-MM-DD)")
    parser.add_argument("--force", action="store_true", help="Force update existing records (for --bydate)")
    
    args = parser.parse_args()
    
    client = ProductHuntClient()
    if not client.tokens:
        print("Error: No PH tokens configured! Set PH_TOKENS in .env")
        sys.exit(1)
    
    print(f"Tokens loaded: {len(client.tokens)}")
    
    if args.test:
        from services.producthunt import test_connection
        success = await test_connection()
        sys.exit(0 if success else 1)
    
    syncer = ProductHuntSyncer(client)
    
    try:
        if args.new:
            await syncer.sync_new(max_pages=args.pages, delay=args.delay)
        elif args.history:
            await syncer.sync_history(max_pages=args.pages, delay=args.delay)
        elif args.bydate:
            if not args.start or not args.end:
                print("Error: --bydate requires --start and --end dates")
                print("Example: --bydate --start 2024-01-01 --end 2024-12-31")
                sys.exit(1)
            await syncer.sync_by_date(start_date=args.start, end_date=args.end, delay=args.delay, force_update=args.force)
        elif args.refresh:
            await syncer.refresh_existing(limit=args.limit, delay=args.delay)
    except KeyboardInterrupt:
        print("\n[Interrupted] Checkpoint saved")
        syncer._print_stats()


if __name__ == "__main__":
    asyncio.run(main())
