"""
Playwright browser management for web scraping
"""

import asyncio
import random
from typing import Optional
from contextlib import asynccontextmanager
from playwright.async_api import async_playwright, Browser, Page, BrowserContext


class BrowserManager:
    """Manages Playwright browser instances with anti-detection features"""
    
    # User agents pool for rotation
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    ]
    
    def __init__(self):
        self._playwright = None
        self._browser: Optional[Browser] = None
    
    async def start(self):
        """Start the browser"""
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
            ]
        )
        print("Browser started successfully")
    
    async def stop(self):
        """Stop the browser"""
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
        print("Browser stopped")
    
    @asynccontextmanager
    async def get_page(self):
        """Get a new page with anti-detection settings"""
        if not self._browser:
            await self.start()
        
        context: BrowserContext = await self._browser.new_context(
            user_agent=random.choice(self.USER_AGENTS),
            viewport={"width": 1920, "height": 1080},
            locale="en-US",
        )
        
        # Add anti-detection scripts
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        page = await context.new_page()
        
        try:
            yield page
        finally:
            await page.close()
            await context.close()
    
    @staticmethod
    async def random_delay(min_sec: float = 1.0, max_sec: float = 3.0):
        """Add random delay to mimic human behavior"""
        delay = random.uniform(min_sec, max_sec)
        await asyncio.sleep(delay)
    
    @staticmethod
    async def scroll_page(page: Page, scroll_count: int = 3):
        """Scroll page to load lazy content"""
        for _ in range(scroll_count):
            await page.evaluate("window.scrollBy(0, window.innerHeight)")
            await asyncio.sleep(random.uniform(0.5, 1.5))
