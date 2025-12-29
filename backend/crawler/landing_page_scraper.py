"""
Landing Page Scraper - 爬取产品官网Landing Page
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass
from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError

from .browser import BrowserManager
from .html_extractor import HTMLExtractor

logger = logging.getLogger(__name__)


@dataclass
class LandingPageResult:
    """Landing Page爬取结果"""
    startup_id: int
    url: str
    status: str  # success, failed, timeout, blocked
    html_content: Optional[str] = None
    raw_text: Optional[str] = None
    snapshot_path: Optional[str] = None
    page_load_time_ms: Optional[int] = None
    content_length: Optional[int] = None
    error_message: Optional[str] = None
    scraped_at: Optional[datetime] = None

    def __post_init__(self):
        if self.scraped_at is None:
            self.scraped_at = datetime.utcnow()


class LandingPageScraper:
    """Landing Page爬虫 - 爬取产品官网首页"""

    # 快照保存目录
    LANDING_PAGE_DIR = Path(__file__).parent.parent / "data" / "landing_pages"

    # 超时和重试设置
    PAGE_TIMEOUT = 30000  # 30秒
    MAX_RETRIES = 2

    # 页面加载完成标识选择器
    WAIT_SELECTORS = [
        "h1",
        "header",
        '[class*="hero"]',
        '[class*="header"]',
        "main",
        '[role="main"]',
        '[class*="landing"]',
    ]

    def __init__(self, browser_manager: BrowserManager):
        self.browser = browser_manager
        self.LANDING_PAGE_DIR.mkdir(parents=True, exist_ok=True)

    async def scrape_landing_page(
        self,
        startup_id: int,
        url: str,
        save_snapshot: bool = True
    ) -> LandingPageResult:
        """
        爬取产品Landing Page

        Args:
            startup_id: 产品ID
            url: 产品官网URL
            save_snapshot: 是否保存HTML快照

        Returns:
            LandingPageResult对象
        """
        result = LandingPageResult(
            startup_id=startup_id,
            url=url,
            status="pending"
        )

        # 验证URL
        if not url or not url.startswith(("http://", "https://")):
            result.status = "failed"
            result.error_message = f"Invalid URL: {url}"
            return result

        start_time = datetime.now()

        for attempt in range(self.MAX_RETRIES):
            try:
                async with self.browser.get_page() as page:
                    logger.info(f"Scraping {url} (attempt {attempt + 1}/{self.MAX_RETRIES})")

                    # 导航到页面
                    await page.goto(
                        url,
                        wait_until="domcontentloaded",
                        timeout=self.PAGE_TIMEOUT
                    )

                    # 等待页面关键元素加载
                    await self._wait_for_page_load(page)

                    # 随机延迟，模拟人类行为
                    await self.browser.random_delay(1, 2)

                    # 滚动页面以触发懒加载
                    await self.browser.scroll_page(page, scroll_count=3)

                    # 提取清理后的HTML
                    html_content = await HTMLExtractor.extract(
                        page,
                        wait_timeout=10000,
                        extra_wait=2000,
                        keep_images=True
                    )

                    # 提取纯文本用于关键词分析
                    raw_text = await page.evaluate(
                        "() => document.body.innerText"
                    )

                    # 计算指标
                    end_time = datetime.now()
                    load_time = int((end_time - start_time).total_seconds() * 1000)

                    result.status = "success"
                    result.html_content = html_content
                    result.raw_text = raw_text
                    result.page_load_time_ms = load_time
                    result.content_length = len(html_content) if html_content else 0

                    # 保存快照
                    if save_snapshot and html_content:
                        snapshot_path = self.LANDING_PAGE_DIR / f"{startup_id}.html"
                        snapshot_path.write_text(html_content, encoding="utf-8")
                        result.snapshot_path = str(snapshot_path)
                        logger.info(f"Saved snapshot to {snapshot_path}")

                    return result

            except PlaywrightTimeoutError as e:
                result.status = "timeout"
                result.error_message = f"Page load timeout after {self.PAGE_TIMEOUT}ms"
                logger.warning(f"Timeout scraping {url}: {e}")

            except Exception as e:
                result.status = "failed"
                result.error_message = str(e)
                logger.error(f"Error scraping {url}: {e}")

            # 重试前等待
            if attempt < self.MAX_RETRIES - 1:
                await asyncio.sleep(2)

        return result

    async def _wait_for_page_load(self, page: Page):
        """等待页面关键元素加载"""
        for selector in self.WAIT_SELECTORS:
            try:
                await page.wait_for_selector(selector, timeout=5000)
                return  # 找到任一元素即认为页面已加载
            except PlaywrightTimeoutError:
                continue

        # 如果没有找到任何标识元素，等待网络空闲
        try:
            await page.wait_for_load_state("networkidle", timeout=10000)
        except PlaywrightTimeoutError:
            pass

    async def extract_pricing_section(self, page: Page) -> Optional[str]:
        """提取定价部分HTML"""
        pricing_selectors = [
            '[id*="pricing"]',
            '[class*="pricing"]',
            '[id*="price"]',
            '[class*="price"]',
            'section:has-text("Pricing")',
            'div:has-text("$/month")',
        ]

        for selector in pricing_selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    return await element.inner_html()
            except Exception:
                continue
        return None

    async def extract_cta_buttons(self, page: Page) -> list:
        """提取所有CTA按钮文案"""
        cta_selectors = [
            "button",
            'a[href*="signup"]',
            'a[href*="register"]',
            'a[href*="trial"]',
            'a[href*="demo"]',
            'a[href*="start"]',
            '[class*="cta"]',
            '[class*="button"]',
        ]

        ctas = []
        for selector in cta_selectors:
            try:
                elements = await page.query_selector_all(selector)
                for el in elements:
                    text = await el.text_content()
                    if text and len(text.strip()) < 50:
                        ctas.append(text.strip())
            except Exception:
                continue

        return list(set(ctas))  # 去重

    async def batch_scrape(
        self,
        items: list,
        delay_between: float = 3.0,
        save_snapshots: bool = True
    ) -> list:
        """
        批量爬取Landing Pages

        Args:
            items: [(startup_id, url), ...] 列表
            delay_between: 请求间隔(秒)
            save_snapshots: 是否保存快照

        Returns:
            LandingPageResult列表
        """
        results = []

        for i, (startup_id, url) in enumerate(items):
            logger.info(f"Processing {i + 1}/{len(items)}: {url}")

            result = await self.scrape_landing_page(
                startup_id=startup_id,
                url=url,
                save_snapshot=save_snapshots
            )
            results.append(result)

            # 请求间隔
            if i < len(items) - 1:
                await asyncio.sleep(delay_between)

        # 统计结果
        success_count = sum(1 for r in results if r.status == "success")
        logger.info(f"Batch scrape completed: {success_count}/{len(items)} successful")

        return results


async def run_landing_scraper(
    items: list,
    delay: float = 3.0
) -> list:
    """
    运行Landing Page爬虫的便捷函数

    Args:
        items: [(startup_id, url), ...] 列表
        delay: 请求间隔

    Returns:
        爬取结果列表
    """
    browser = BrowserManager()
    await browser.start()

    try:
        scraper = LandingPageScraper(browser)
        results = await scraper.batch_scrape(items, delay_between=delay)
        return results
    finally:
        await browser.stop()
