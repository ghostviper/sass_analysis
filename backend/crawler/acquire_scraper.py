"""
Scraper for TrustMRR Acquire page (https://trustmrr.com/acquire)
"""

import re
import asyncio
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from playwright.async_api import Page

from .browser import BrowserManager
from .html_extractor import HTMLExtractor


class AcquireScraper:
    """Scrapes startup listings from TrustMRR Acquire page"""
    
    BASE_URL = "https://trustmrr.com/acquire"
    HTML_SNAPSHOT_DIR = Path(__file__).parent.parent / "data" / "html_snapshots"
    
    def __init__(self, browser_manager: BrowserManager):
        self.browser = browser_manager
        # Create HTML snapshot directory if it doesn't exist
        self.HTML_SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    
    async def scrape_all_urls(self) -> List[str]:
        """
        Scrape all startup URLs from the Acquire page using infinite scroll
        
        Returns:
            List of startup URLs
        """
        startup_urls = []
        
        async with self.browser.get_page() as page:
            print(f"Navigating to {self.BASE_URL}...")
            await page.goto(self.BASE_URL, wait_until="networkidle", timeout=60000)
            await self.browser.random_delay(2, 4)
            
            # Infinite scroll until we reach the footer
            print("Starting infinite scroll to load all startups...")
            previous_count = 0
            no_change_count = 0
            max_no_change = 5  # Stop if count doesn't change after 5 scrolls
            
            while no_change_count < max_no_change:
                # Extract current URLs
                urls = await self._extract_startup_urls(page)
                current_count = len(urls)
                
                print(f"Found {current_count} startup URLs so far...")
                
                # Check if we got new items
                if current_count == previous_count:
                    no_change_count += 1
                    print(f"No new items found ({no_change_count}/{max_no_change})")
                else:
                    no_change_count = 0
                    previous_count = current_count
                
                # Check if footer is visible (indicates end of content)
                footer_visible = await page.evaluate("""
                    () => {
                        const footer = document.querySelector('footer');
                        if (!footer) return false;
                        const rect = footer.getBoundingClientRect();
                        return rect.top < window.innerHeight + 1000;
                    }
                """)
                
                if footer_visible:
                    print("Footer detected, stopping scroll...")
                    break
                
                # Scroll down
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await self.browser.random_delay(1.5, 2.5)
            
            # Final extraction
            startup_urls = await self._extract_startup_urls(page)
            print(f"Total startup URLs collected: {len(startup_urls)}")
        
        return startup_urls
    
    async def _extract_startup_urls(self, page: Page) -> List[str]:
        """Extract all unique startup URLs from the current page state"""
        links = await page.query_selector_all('a[href*="/startup/"]')
        
        urls = set()
        for link in links:
            try:
                href = await link.get_attribute("href")
                if href and "/startup/" in href:
                    # Convert relative URLs to absolute
                    if href.startswith("/"):
                        href = f"https://trustmrr.com{href}"
                    urls.add(href)
            except Exception as e:
                continue
        
        return sorted(list(urls))
    
    async def scrape_startup_detail(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Scrape a single startup detail page and save HTML snapshot
        
        Args:
            url: Full URL to the startup page
            
        Returns:
            Dictionary with startup data or None if failed
        """
        # Extract slug from URL
        slug_match = re.search(r'/startup/([^/?]+)', url)
        if not slug_match:
            print(f"Could not extract slug from URL: {url}")
            return None
        
        slug = slug_match.group(1)
        
        async with self.browser.get_page() as page:
            try:
                print(f"Scraping {slug}...")
                await page.goto(url, wait_until="networkidle", timeout=60000)

                # 等待页面初始加载
                await self.browser.random_delay(2, 3)

                # 提取图表时序数据 (通过 API 请求)
                from .chart_extractor import extract_revenue_history
                revenue_history = await extract_revenue_history(page, slug)
                if revenue_history:
                    print(f"  Extracted {len(revenue_history)} days of revenue history")
                else:
                    print(f"  No revenue history data available")

                # 使用HTMLExtractor获取完整渲染后的纯净HTML
                html_content = await HTMLExtractor.extract(
                    page,
                    wait_selector='main h1',  # 等待主标题出现
                    wait_timeout=15000,
                    extra_wait=3000  # 额外等待3秒确保动态内容渲染
                )

                html_path = self.HTML_SNAPSHOT_DIR / f"{slug}.html"
                html_path.write_text(html_content, encoding='utf-8')
                print(f"  Saved rendered HTML snapshot ({len(html_content)} bytes) to {html_path.name}")

                # 使用 HTMLParser 解析完整数据 (与 update 命令使用相同的解析器)
                from .html_parser import parse_html_file
                startup_data = parse_html_file(html_path)

                # 补充 HTMLParser 没有的字段
                startup_data['html_snapshot_path'] = str(html_path)
                startup_data['revenue_history'] = revenue_history or []
                startup_data['is_for_sale'] = startup_data.get('is_for_sale', True)
                startup_data['profile_url'] = url

                return startup_data

            except Exception as e:
                print(f"Error scraping {slug}: {e}")
                return None
    
    async def _parse_startup_page(self, page: Page, slug: str, url: str) -> Dict[str, Any]:
        """Parse startup information from the detail page"""
        
        # Extract name
        name = await page.evaluate("""
            () => {
                const h1 = document.querySelector('h1');
                return h1 ? h1.textContent.trim() : '';
            }
        """)
        
        # Extract description
        description = await page.evaluate("""
            () => {
                const desc = document.querySelector('meta[name="description"]');
                if (desc) return desc.getAttribute('content');
                const p = document.querySelector('p');
                return p ? p.textContent.trim() : '';
            }
        """)
        
        # Get all text content for parsing
        text_content = await page.evaluate("() => document.body.textContent")
        
        # Parse financial metrics
        revenue_30d = self._extract_metric(text_content, r'(?:Revenue|MRR)[:\s]*\$?([\d,.]+)\s*([kKmM])?')
        asking_price = self._extract_metric(text_content, r'(?:Asking Price|Price)[:\s]*\$?([\d,.]+)\s*([kKmM])?')
        multiple = self._extract_float(text_content, r'(?:Multiple)[:\s]*([\d.]+)\s*x')
        growth_rate = self._extract_float(text_content, r'(?:Growth)[:\s]*([\d.]+)\s*%')
        
        # Extract founder information
        founder_name = None
        founder_username = None
        
        founder_link = await page.query_selector('a[href*="/founder/"]')
        if founder_link:
            founder_href = await founder_link.get_attribute("href")
            if founder_href:
                username_match = re.search(r'/founder/([^/?]+)', founder_href)
                if username_match:
                    founder_username = username_match.group(1)
                founder_name = await founder_link.text_content()
                if founder_name:
                    founder_name = founder_name.strip()
        
        # Extract category
        category = None
        categories = [
            "AI", "SaaS", "Fintech", "Marketing", "Developer Tools",
            "Productivity", "E-commerce", "Design Tools", "No-Code",
            "Analytics", "Education", "Health", "Social Media",
            "Content Creation", "Sales", "Community", "Artificial Intelligence"
        ]
        for cat in categories:
            if cat.lower() in text_content.lower():
                category = cat
                break
        
        return {
            "name": name or slug.replace('-', ' ').title(),
            "slug": slug,
            "description": description,
            "category": category,
            "founder_name": founder_name,
            "founder_username": founder_username,
            "revenue_30d": revenue_30d,
            "asking_price": asking_price,
            "multiple": multiple,
            "growth_rate": growth_rate,
            "is_for_sale": True,
            "profile_url": url,
            "scraped_at": datetime.utcnow().isoformat(),
        }
    
    def _extract_metric(self, text: str, pattern: str) -> Optional[float]:
        """Extract monetary value from text"""
        match = re.search(pattern, text, re.IGNORECASE)
        if not match:
            return None
        
        try:
            value = float(match.group(1).replace(',', ''))
            multiplier = match.group(2) if len(match.groups()) > 1 else None
            
            if multiplier:
                if multiplier.lower() == 'k':
                    value *= 1000
                elif multiplier.lower() == 'm':
                    value *= 1000000
            
            return value
        except (ValueError, IndexError):
            return None
    
    def _extract_float(self, text: str, pattern: str) -> Optional[float]:
        """Extract float value from text"""
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                return None
        return None
    
    async def scrape(self, max_items: int = 0) -> List[Dict[str, Any]]:
        """
        Main scraping method - scrapes all startups with details and HTML snapshots

        Args:
            max_items: Maximum number of startups to scrape (0 = no limit, scrape all)

        Returns:
            List of startup dictionaries
        """
        # Step 1: Collect all URLs
        all_urls = await self.scrape_all_urls()
        urls_to_scrape = all_urls[:max_items] if max_items > 0 else all_urls

        print(f"\nCollected {len(all_urls)} URLs, will scrape {len(urls_to_scrape)}")
        
        # Step 2: Scrape each startup detail page
        startups = []
        for i, url in enumerate(urls_to_scrape, 1):
            print(f"\n[{i}/{len(urls_to_scrape)}] Scraping startup...")
            startup_data = await self.scrape_startup_detail(url)
            if startup_data:
                startups.append(startup_data)
            
            # Add delay between requests to be respectful
            if i < len(urls_to_scrape):
                await asyncio.sleep(1)
        
        print(f"\nScraping complete. Successfully scraped {len(startups)} startups")
        return startups


async def main():
    """Test the scraper"""
    browser = BrowserManager()
    await browser.start()
    
    try:
        scraper = AcquireScraper(browser)
        
        # Test URL collection
        print("Testing URL collection...")
        urls = await scraper.scrape_all_urls()
        print(f"Found {len(urls)} URLs")
        
        # Test detail scraping (just first 3)
        if urls:
            print("\nTesting detail scraping (first 3)...")
            startups = []
            for url in urls[:3]:
                startup = await scraper.scrape_startup_detail(url)
                if startup:
                    startups.append(startup)
            
            print("\n--- Scraped Startups ---")
            for s in startups:
                print(f"  {s['name']}: ${s.get('revenue_30d', 'N/A')} MRR")
                print(f"    Founder: {s.get('founder_name', 'N/A')}")
                print(f"    HTML saved: {s.get('html_snapshot_path', 'N/A')}")
    finally:
        await browser.stop()


if __name__ == "__main__":
    asyncio.run(main())
