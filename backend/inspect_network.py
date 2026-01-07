"""监听网络请求，查看图表数据是如何加载的"""
import asyncio
from crawler.browser import BrowserManager
import json


async def inspect_network():
    test_url = "https://trustmrr.com/startup/100lead-com"

    browser = BrowserManager()
    await browser.start()

    try:
        async with browser.get_page() as page:
            # 存储所有 API 请求
            api_requests = []

            # 监听所有响应
            async def handle_response(response):
                url = response.url
                # 只关注 API 请求或包含数据的请求
                if any(keyword in url.lower() for keyword in ['api', 'data', 'json', 'revenue', 'chart']):
                    try:
                        content_type = response.headers.get('content-type', '')
                        if 'json' in content_type:
                            body = await response.text()
                            api_requests.append({
                                'url': url,
                                'status': response.status,
                                'content_type': content_type,
                                'body_preview': body[:500] if body else None
                            })
                    except Exception as e:
                        pass

            page.on('response', handle_response)

            print(f"正在访问: {test_url}")
            print("监听网络请求...\n")

            await page.goto(test_url, wait_until="networkidle", timeout=60000)
            await asyncio.sleep(5)  # 等待额外的异步请求

            print(f"\n=== 捕获到 {len(api_requests)} 个 API 请求 ===\n")

            for i, req in enumerate(api_requests, 1):
                print(f"{i}. {req['url']}")
                print(f"   状态: {req['status']}")
                if req['body_preview']:
                    print(f"   内容预览: {req['body_preview'][:200]}")
                print()

            # 检查页面中是否有隐藏的数据
            print("\n=== 检查页面中的 JSON 数据 ===")
            json_data = await page.evaluate("""
                () => {
                    const results = [];

                    // 检查所有 script 标签中的 JSON
                    const scripts = document.querySelectorAll('script');
                    scripts.forEach((script, idx) => {
                        const content = script.textContent || '';

                        // 查找包含 revenue 或 daily 的 JSON 对象
                        if (content.includes('revenue') || content.includes('daily')) {
                            // 尝试提取 JSON 对象
                            const jsonMatches = content.match(/\{[^{}]*"[^"]*"[^{}]*\}/g);
                            if (jsonMatches) {
                                results.push({
                                    scriptIndex: idx,
                                    preview: content.substring(0, 300),
                                    jsonCount: jsonMatches.length
                                });
                            }
                        }
                    });

                    return results;
                }
            """)

            if json_data:
                print(f"找到 {len(json_data)} 个包含 revenue/daily 的 script:")
                for item in json_data:
                    print(f"\nScript {item['scriptIndex']}:")
                    print(f"  JSON 对象数: {item['jsonCount']}")
                    print(f"  预览: {item['preview'][:200]}")
            else:
                print("未找到包含 revenue/daily 的 JSON 数据")

            # 检查是否有 React/Next.js 的数据注入
            print("\n\n=== 检查 React Props ===")
            react_data = await page.evaluate("""
                () => {
                    // 查找所有可能包含 React props 的元素
                    const elements = document.querySelectorAll('[data-reactroot], [data-reactid], #__next, [id^="__next"]');
                    return {
                        reactElements: elements.length,
                        hasNextRoot: !!document.getElementById('__next')
                    };
                }
            """)
            print(f"React 元素: {react_data}")

    finally:
        await browser.stop()


if __name__ == "__main__":
    asyncio.run(inspect_network())
