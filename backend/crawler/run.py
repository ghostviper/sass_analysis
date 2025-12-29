"""
Main crawler runner - orchestrates all scrapers and saves to database
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from database.db import init_db, AsyncSessionLocal
from database.models import Startup, Founder, LeaderboardEntry
from crawler.browser import BrowserManager
from crawler.acquire_scraper import AcquireScraper
from crawler.leaderboard_scraper import LeaderboardScraper


async def save_startups(startups: list):
    """Save scraped startups to database"""
    async with AsyncSessionLocal() as session:
        for data in startups:
            # Check if startup already exists
            result = await session.execute(
                select(Startup).where(Startup.slug == data["slug"])
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                # Update existing record
                for key, value in data.items():
                    if key != "scraped_at" and value is not None:
                        setattr(existing, key, value)
                print(f"  Updated: {data['slug']}")
            else:
                # Create new record
                startup = Startup(
                    name=data["name"],
                    slug=data["slug"],
                    description=data.get("description"),
                    category=data.get("category"),
                    founder_name=data.get("founder_name"),
                    founder_username=data.get("founder_username"),
                    revenue_30d=data.get("revenue_30d"),
                    revenue_arr=data.get("revenue_arr"),
                    asking_price=data.get("asking_price"),
                    multiple=data.get("multiple"),
                    growth_rate=data.get("growth_rate"),
                    profit_margin=data.get("profit_margin"),
                    customers_count=data.get("customers_count"),
                    team_size=data.get("team_size"),
                    founded_date=data.get("founded_date"),
                    is_for_sale=data.get("is_for_sale", True),
                    is_verified=data.get("is_verified", False),
                    profile_url=data.get("profile_url"),
                    html_snapshot_path=data.get("html_snapshot_path"),
                )
                session.add(startup)
                print(f"  Created: {data['slug']}")
        
        await session.commit()
        print(f"\nSaved {len(startups)} startups to database")


async def save_leaderboard_entries(entries: list):
    """Save leaderboard entries to database"""
    async with AsyncSessionLocal() as session:
        for data in entries:
            # Create new leaderboard entry (we keep historical records)
            entry = LeaderboardEntry(
                startup_slug=data["startup_slug"],
                rank=data["rank"],
                revenue_30d=data.get("revenue_30d"),
                growth_rate=data.get("growth_rate"),
                multiple=data.get("multiple"),
            )
            session.add(entry)
            print(f"  Rank #{data['rank']}: {data['startup_slug']}")
        
        await session.commit()
        print(f"\nSaved {len(entries)} leaderboard entries to database")


async def save_founders(founders: list):
    """Save scraped founders to database"""
    async with AsyncSessionLocal() as session:
        for data in founders:
            # Check if founder already exists
            result = await session.execute(
                select(Founder).where(Founder.username == data["username"])
            )
            existing = result.scalar_one_or_none()

            if existing:
                # Update existing record
                existing.name = data.get("name", existing.name)
                if data.get("rank"):
                    existing.rank = data["rank"]
                if data.get("profile_url"):
                    existing.profile_url = data["profile_url"]
                if data.get("followers"):
                    existing.followers = data["followers"]
                if data.get("social_platform"):
                    existing.social_platform = data["social_platform"]
            else:
                # Create new record
                founder = Founder(
                    name=data.get("name", data["username"]),
                    username=data["username"],
                    profile_url=data.get("profile_url"),
                    rank=data.get("rank"),
                    followers=data.get("followers"),
                    social_platform=data.get("social_platform"),
                )
                session.add(founder)

        await session.commit()
        print(f"Saved {len(founders)} founders to database")


def extract_founders_from_startups(startups: list) -> list:
    """
    从startup数据中提取唯一的founder列表

    Args:
        startups: startup数据列表

    Returns:
        去重后的founder数据列表
    """
    founders = {}
    for startup in startups:
        username = startup.get('founder_username')
        if username and username not in founders:
            founders[username] = {
                'name': startup.get('founder_name') or username,
                'username': username,
                'profile_url': f"https://trustmrr.com/founder/{username}",
                'rank': None,
                'followers': startup.get('founder_followers'),
                'social_platform': startup.get('founder_social_platform'),
            }
    return list(founders.values())


async def run_crawler(max_startups: int = 0, scrape_leaderboard: bool = True):
    """Run all scrapers and save data

    Args:
        max_startups: Maximum startups to scrape (0 = no limit, scrape all available)
        scrape_leaderboard: Whether to scrape the leaderboard
    """
    print("=" * 60)
    print("TrustMRR Data Crawler")
    print("=" * 60)

    # Initialize database
    await init_db()

    # Initialize browser
    browser = BrowserManager()
    await browser.start()

    try:
        # Scrape Acquire page with full details and HTML snapshots
        print("\n[1/2] Scraping Acquire page (all startups with details)...")
        print(f"Target: {'all available' if max_startups == 0 else max_startups} startups")
        acquire_scraper = AcquireScraper(browser)
        startups = await acquire_scraper.scrape(max_items=max_startups)
        
        if startups:
            print(f"\nSaving {len(startups)} startups to database...")
            await save_startups(startups)

            # Extract and save founders from startup data
            founders = extract_founders_from_startups(startups)
            if founders:
                print(f"\nExtracting {len(founders)} unique founders...")
                await save_founders(founders)

        # Scrape Leaderboard (top 100 products)
        if scrape_leaderboard:
            print("\n[2/2] Scraping Leaderboard (top 100 products)...")
            leaderboard_scraper = LeaderboardScraper(browser)
            leaderboard_entries = await leaderboard_scraper.scrape(max_items=100)
            
            if leaderboard_entries:
                print(f"\nSaving {len(leaderboard_entries)} leaderboard entries to database...")
                await save_leaderboard_entries(leaderboard_entries)
        else:
            leaderboard_entries = []
        
        print("\n" + "=" * 60)
        print("Crawling complete!")
        print(f"  - Startups scraped: {len(startups)}")
        if scrape_leaderboard:
            print(f"  - Leaderboard entries: {len(leaderboard_entries)}")
        print(f"  - HTML snapshots saved to: {acquire_scraper.HTML_SNAPSHOT_DIR}")
        print("=" * 60)
        
    finally:
        await browser.stop()


def main():
    """Entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="TrustMRR Data Crawler")
    parser.add_argument("--max-startups", type=int, default=0, help="Max startups to scrape (0 = no limit)")
    parser.add_argument("--skip-leaderboard", action="store_true", help="Skip leaderboard scraping")
    parser.add_argument("--test", action="store_true", help="Run in test mode (fewer items)")
    
    args = parser.parse_args()
    
    if args.test:
        print("\n*** TEST MODE: Scraping only 5 startups ***\n")
        asyncio.run(run_crawler(max_startups=5, scrape_leaderboard=True))
    else:
        asyncio.run(run_crawler(
            max_startups=args.max_startups,
            scrape_leaderboard=not args.skip_leaderboard
        ))


if __name__ == "__main__":
    main()
