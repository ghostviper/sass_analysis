"""
Scraper for TrustMRR Leaderboard (homepage top 100 products)
"""

import re
import asyncio
from typing import List, Dict, Any
from datetime import datetime
from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError

from .browser import BrowserManager


class LeaderboardScraper:
    """Scrapes top 100 product leaderboard from TrustMRR homepage"""
    
    BASE_URL = "https://trustmrr.com"
    
    def __init__(self, browser_manager: BrowserManager):
        self.browser = browser_manager
    
    async def scrape(self, max_items: int = 100) -> List[Dict[str, Any]]:
        """
        Scrape top 100 products from the leaderboard
        
        Args:
            max_items: Maximum number of products to scrape (default 100)
            
        Returns:
            List of leaderboard entry dictionaries
        """
        leaderboard_entries = []
        
        async with self.browser.get_page() as page:
            print(f"Navigating to {self.BASE_URL}...")
            await page.goto(self.BASE_URL, wait_until="networkidle", timeout=60000)
            await self.browser.random_delay(2, 4)
            
            # Scroll to leaderboard section
            print("Scrolling to leaderboard section...")
            await self.browser.scroll_page(page, 2)
            await self.browser.random_delay(1, 2)
            
            # Click "Show more" button to load all 100 products
            print("Looking for 'Show more' button...")
            try:
                # Find and click the "Show more" button
                show_more_button = await page.wait_for_selector(
                    'button:has-text("Show more")',
                    timeout=10000
                )
                
                if show_more_button:
                    print("Clicking 'Show more' button...")
                    await show_more_button.click()
                    await self.browser.random_delay(2, 3)
                    
                    # Wait for additional items to load
                    await page.wait_for_timeout(2000)
                else:
                    print("Show more button not found, proceeding with visible items...")
                    
            except PlaywrightTimeoutError:
                print("Show more button not found (timeout), proceeding with visible items...")
            except Exception as e:
                print(f"Error clicking show more button: {e}")
            
            # Extract leaderboard entries
            leaderboard_entries = await self._extract_leaderboard_entries(page, max_items)
            print(f"Scraping complete. Total: {len(leaderboard_entries)} leaderboard entries")
        
        return leaderboard_entries
    
    async def _extract_leaderboard_entries(self, page: Page, max_items: int) -> List[Dict[str, Any]]:
        """Extract leaderboard entries from the page"""
        entries = []
        
        # Find all startup/product links in the leaderboard
        # The leaderboard typically shows products with their metrics
        links = await page.query_selector_all('a[href*="/startup/"]')
        
        seen_slugs = set()
        rank = 1
        
        for link in links:
            if len(entries) >= max_items:
                break
                
            try:
                href = await link.get_attribute("href")
                if not href or "/startup/" not in href:
                    continue
                
                # Extract slug from URL
                slug_match = re.search(r'/startup/([^/?]+)', href)
                if not slug_match:
                    continue
                
                slug = slug_match.group(1)
                
                # Skip duplicates
                if slug in seen_slugs:
                    continue
                seen_slugs.add(slug)
                
                # Try to get the parent container to extract metrics
                parent = await link.evaluate_handle("el => el.closest('div, li, article')")
                parent_element = parent.as_element()
                
                if parent_element:
                    text_content = await parent_element.text_content() or ""
                else:
                    text_content = await link.text_content() or ""
                
                # Parse metrics from the card/row
                entry = self._parse_leaderboard_entry(slug, text_content, rank)
                if entry:
                    entries.append(entry)
                    rank += 1
                    
            except Exception as e:
                print(f"Error extracting leaderboard entry: {e}")
                continue
        
        return entries
    
    def _parse_leaderboard_entry(self, slug: str, text: str, rank: int) -> Dict[str, Any]:
        """Parse leaderboard entry from text content"""
        
        # Extract revenue (MRR)
        revenue_30d = None
        revenue_match = re.search(r'\$?([\d,.]+)\s*([kKmM])?(?:\s*MRR|\s*revenue)', text, re.IGNORECASE)
        if revenue_match:
            try:
                value = float(revenue_match.group(1).replace(',', ''))
                multiplier = revenue_match.group(2)
                if multiplier:
                    if multiplier.lower() == 'k':
                        value *= 1000
                    elif multiplier.lower() == 'm':
                        value *= 1000000
                revenue_30d = value
            except ValueError:
                pass
        
        # Extract growth rate
        growth_rate = None
        growth_match = re.search(r'([\d.]+)\s*%', text)
        if growth_match:
            try:
                growth_rate = float(growth_match.group(1))
            except ValueError:
                pass
        
        # Extract multiple
        multiple = None
        multiple_match = re.search(r'([\d.]+)\s*x', text, re.IGNORECASE)
        if multiple_match:
            try:
                multiple = float(multiple_match.group(1))
            except ValueError:
                pass
        
        return {
            "startup_slug": slug,
            "rank": rank,
            "revenue_30d": revenue_30d,
            "growth_rate": growth_rate,
            "multiple": multiple,
            "leaderboard_date": datetime.utcnow().isoformat(),
            "scraped_at": datetime.utcnow().isoformat(),
        }


async def main():
    """Test the scraper"""
    browser = BrowserManager()
    await browser.start()
    
    try:
        scraper = LeaderboardScraper(browser)
        entries = await scraper.scrape(max_items=100)
        
        print("\n--- Scraped Leaderboard Entries ---")
        for entry in entries[:10]:
            print(f"  #{entry['rank']} {entry['startup_slug']}: ${entry.get('revenue_30d', 'N/A')} MRR")
        
        print(f"\nTotal entries: {len(entries)}")
    finally:
        await browser.stop()


if __name__ == "__main__":
    asyncio.run(main())
