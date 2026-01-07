"""调试 100lead-com 的图表数据提取"""
import asyncio
from crawler.browser import BrowserManager
from crawler.chart_extractor import extract_revenue_history


async def debug_100lead():
    url = "https://trustmrr.com/startup/100lead-com"
    slug = "100lead-com"

    browser = BrowserManager()
    await browser.start()

    try:
        async with browser.get_page() as page:
            print(f"正在访问: {url}\n")
            await page.goto(url, wait_until="networkidle", timeout=60000)
            await asyncio.sleep(3)

            print(f"尝试提取 {slug} 的收入数据...\n")

            # 方法1: 使用 extract_revenue_history
            print("方法1: 使用 extract_revenue_history")
            revenue_history = await extract_revenue_history(page, slug)
            if revenue_history:
                print(f"  [SUCCESS] 提取到 {len(revenue_history)} 天的数据")
                print(f"  前3条: {revenue_history[:3]}")
            else:
                print("  [FAILED] 未提取到数据")

            # 方法2: 直接调用 API
            print("\n方法2: 直接调用 API")
            api_url = f"https://trustmrr.com/api/startup/revenue/{slug}?granularity=daily&period=4w"
            print(f"  API URL: {api_url}")

            try:
                response = await page.request.get(api_url)
                print(f"  状态码: {response.status}")
                print(f"  Headers: {response.headers}")

                if response.status == 200:
                    data = await response.json()
                    print(f"  响应数据: {data}")
                else:
                    body = await response.text()
                    print(f"  错误响应: {body[:500]}")
            except Exception as e:
                print(f"  API 请求异常: {e}")

            # 方法3: 检查页面是否需要认证
            print("\n方法3: 检查认证状态")
            auth_check = await page.evaluate("""
                () => {
                    // 检查是否有登录相关的元素
                    const loginButton = document.querySelector('[href*="login"]');
                    const signupButton = document.querySelector('[href*="signup"]');

                    return {
                        hasLoginButton: !!loginButton,
                        hasSignupButton: !!signupButton,
                        cookies: document.cookie
                    };
                }
            """)
            print(f"  认证检查: {auth_check}")

    finally:
        await browser.stop()


if __name__ == "__main__":
    asyncio.run(debug_100lead())
