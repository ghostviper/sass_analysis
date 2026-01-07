"""监听所有网络请求，查找图表数据 API"""
import asyncio
from crawler.browser import BrowserManager
import json


async def monitor_all_requests():
    test_url = "https://trustmrr.com/startup/a-marketing-platform"

    browser = BrowserManager()
    await browser.start()

    try:
        async with browser.get_page() as page:
            all_requests = []
            all_responses = []

            # 监听所有请求
            async def handle_request(request):
                all_requests.append({
                    'url': request.url,
                    'method': request.method,
                    'resource_type': request.resource_type
                })

            # 监听所有响应
            async def handle_response(response):
                url = response.url
                status = response.status
                content_type = response.headers.get('content-type', '')

                # 记录所有响应
                all_responses.append({
                    'url': url,
                    'status': status,
                    'content_type': content_type
                })

                # 如果是 JSON 响应，尝试读取内容
                if 'json' in content_type or 'application/json' in content_type:
                    try:
                        body = await response.text()
                        if body and len(body) > 10:
                            # 检查是否包含 revenue 或 date
                            if 'revenue' in body.lower() or 'date' in body.lower():
                                print(f"\n[API FOUND] {url}")
                                print(f"  状态: {status}")
                                print(f"  类型: {content_type}")
                                print(f"  内容长度: {len(body)}")
                                print(f"  内容预览: {body[:500]}")
                    except Exception as e:
                        pass

            page.on('request', handle_request)
            page.on('response', handle_response)

            print(f"正在访问: {test_url}")
            print("监听所有网络请求...\n")

            await page.goto(test_url, wait_until="networkidle", timeout=60000)

            # 等待额外的异步请求
            print("\n等待额外的异步请求...")
            await asyncio.sleep(5)

            # 尝试滚动页面，可能触发懒加载
            print("\n滚动页面，尝试触发懒加载...")
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(3)

            print(f"\n\n{'='*60}")
            print(f"总请求数: {len(all_requests)}")
            print(f"总响应数: {len(all_responses)}")
            print('='*60)

            # 统计请求类型
            print("\n请求类型统计:")
            resource_types = {}
            for req in all_requests:
                rt = req['resource_type']
                resource_types[rt] = resource_types.get(rt, 0) + 1

            for rt, count in sorted(resource_types.items(), key=lambda x: x[1], reverse=True):
                print(f"  {rt}: {count}")

            # 列出所有 XHR/Fetch 请求
            print("\n\nXHR/Fetch 请求:")
            xhr_requests = [r for r in all_requests if r['resource_type'] in ['xhr', 'fetch']]
            for req in xhr_requests:
                print(f"  {req['method']} {req['url']}")

            # 列出所有 API 相关的请求
            print("\n\nAPI 相关请求:")
            api_requests = [r for r in all_requests if 'api' in r['url'].lower() or '/v' in r['url']]
            for req in api_requests:
                print(f"  {req['method']} {req['url']}")

    finally:
        await browser.stop()


if __name__ == "__main__":
    asyncio.run(monitor_all_requests())
