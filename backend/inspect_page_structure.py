"""检查 TrustMRR 页面的实际数据结构"""
import asyncio
from crawler.browser import BrowserManager


async def inspect_page():
    test_url = "https://trustmrr.com/startup/100lead-com"

    browser = BrowserManager()
    await browser.start()

    try:
        async with browser.get_page() as page:
            print(f"正在访问: {test_url}\n")
            await page.goto(test_url, wait_until="networkidle", timeout=60000)
            await asyncio.sleep(3)

            # 1. 检查所有 script 标签
            print("=== 检查 Script 标签 ===")
            scripts = await page.query_selector_all('script')
            print(f"Script 标签数量: {len(scripts)}")

            # 检查每个 script 的内容
            for i, script in enumerate(scripts[:10], 1):  # 只检查前10个
                content = await script.text_content()
                if content and len(content) > 50:
                    # 检查是否包含可能的数据关键字
                    keywords = ['revenue', 'daily', 'chart', 'data', 'mrr', 'self.__next']
                    found_keywords = [kw for kw in keywords if kw.lower() in content.lower()]
                    if found_keywords:
                        print(f"\nScript {i} (长度: {len(content)}):")
                        print(f"  包含关键字: {found_keywords}")
                        print(f"  前200字符: {content[:200]}")

            # 2. 检查 Next.js 数据
            print("\n\n=== 检查 Next.js 数据 ===")
            next_data = await page.evaluate("""
                () => {
                    // 检查 __NEXT_DATA__
                    if (window.__NEXT_DATA__) {
                        return {
                            found: true,
                            keys: Object.keys(window.__NEXT_DATA__),
                            hasProps: !!window.__NEXT_DATA__.props
                        };
                    }
                    return { found: false };
                }
            """)
            print(f"__NEXT_DATA__: {next_data}")

            # 3. 搜索页面中所有包含 "revenue" 的文本
            print("\n\n=== 搜索 Revenue 相关内容 ===")
            html_content = await page.content()

            import re
            # 查找所有包含 revenue 的 JSON 对象
            revenue_patterns = [
                r'"revenue":\s*\d+',
                r'"mrr":\s*\d+',
                r'"totalRevenue":\s*\d+',
                r'"monthlyRevenue":\s*\d+',
                r'revenue["\s:]+\d+',
            ]

            for pattern in revenue_patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                if matches:
                    print(f"\n模式 '{pattern}' 找到 {len(matches)} 个匹配:")
                    for match in matches[:5]:
                        print(f"  {match}")

            # 4. 检查是否有图表相关的 div
            print("\n\n=== 检查图表元素 ===")
            chart_selectors = [
                '[class*="chart"]',
                '[class*="graph"]',
                '[class*="recharts"]',
                'canvas',
                'svg'
            ]

            for selector in chart_selectors:
                elements = await page.query_selector_all(selector)
                if elements:
                    print(f"{selector}: {len(elements)} 个元素")

    finally:
        await browser.stop()


if __name__ == "__main__":
    asyncio.run(inspect_page())
