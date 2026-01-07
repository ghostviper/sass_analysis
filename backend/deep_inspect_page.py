"""深入检查有 Recharts 的页面，查看数据结构"""
import asyncio
from crawler.browser import BrowserManager
import json


async def deep_inspect():
    # 使用有 Recharts 的页面
    test_url = "https://trustmrr.com/startup/a-marketing-platform"

    browser = BrowserManager()
    await browser.start()

    try:
        async with browser.get_page() as page:
            print(f"正在访问: {test_url}\n")
            await page.goto(test_url, wait_until="networkidle", timeout=60000)
            await asyncio.sleep(3)

            print("=== 1. 检查 Recharts 元素的数据 ===")
            recharts_data = await page.evaluate("""
                () => {
                    const recharts = document.querySelectorAll('[class*="recharts"]');
                    const results = [];

                    recharts.forEach((el, idx) => {
                        // 获取元素的类名
                        const className = el.className;

                        // 尝试获取相关的数据属性
                        const dataAttrs = {};
                        for (let attr of el.attributes) {
                            if (attr.name.startsWith('data-')) {
                                dataAttrs[attr.name] = attr.value;
                            }
                        }

                        // 检查父元素
                        const parent = el.parentElement;
                        const parentClass = parent ? parent.className : '';

                        results.push({
                            index: idx,
                            className: className,
                            tagName: el.tagName,
                            dataAttrs: dataAttrs,
                            parentClass: parentClass,
                            hasChildren: el.children.length > 0
                        });
                    });

                    return results;
                }
            """)

            print(f"找到 {len(recharts_data)} 个 Recharts 元素:")
            for item in recharts_data[:5]:
                print(f"\n  元素 {item['index']}:")
                print(f"    标签: {item['tagName']}")
                className = str(item.get('className', ''))
                parentClass = str(item.get('parentClass', ''))
                print(f"    类名: {className[:100]}")
                print(f"    父类: {parentClass[:100]}")

            print("\n\n=== 2. 搜索包含 'metrics' 的内容 ===")
            metrics_data = await page.evaluate("""
                () => {
                    const html = document.documentElement.innerHTML;

                    // 查找 metrics 相关的 JSON 数据
                    const patterns = [
                        /"metrics"\\s*:\\s*\\{[^}]+\\}/g,
                        /"metrics"\\s*:\\s*\\[[^\\]]+\\]/g,
                        /metrics["\\'\\s:]+\\{[^}]+\\}/g
                    ];

                    const matches = [];
                    patterns.forEach(pattern => {
                        const found = html.match(pattern);
                        if (found) {
                            matches.push(...found);
                        }
                    });

                    return {
                        matchCount: matches.length,
                        samples: matches.slice(0, 3)
                    };
                }
            """)

            print(f"找到 {metrics_data['matchCount']} 个 metrics 匹配")
            if metrics_data['samples']:
                print("\n样本:")
                for i, sample in enumerate(metrics_data['samples'], 1):
                    print(f"  {i}. {sample[:200]}")

            print("\n\n=== 3. 检查所有 script 标签中的 JSON 数据 ===")
            script_json = await page.evaluate("""
                () => {
                    const scripts = document.querySelectorAll('script');
                    const results = [];

                    scripts.forEach((script, idx) => {
                        const content = script.textContent || '';

                        // 查找包含数组的 JSON 数据（可能是时序数据）
                        // 匹配类似 [{...}, {...}] 的模式
                        const arrayPattern = /\\[\\s*\\{[^\\[\\]]*"date"[^\\[\\]]*\\}[^\\[\\]]*\\]/g;
                        const matches = content.match(arrayPattern);

                        if (matches && matches.length > 0) {
                            results.push({
                                scriptIndex: idx,
                                matchCount: matches.length,
                                firstMatch: matches[0].substring(0, 300)
                            });
                        }
                    });

                    return results;
                }
            """)

            if script_json:
                print(f"找到 {len(script_json)} 个包含日期数组的 script:")
                for item in script_json[:3]:
                    print(f"\n  Script {item['scriptIndex']}:")
                    print(f"    匹配数: {item['matchCount']}")
                    print(f"    内容: {item['firstMatch']}")
            else:
                print("未找到包含日期数组的 script")

            print("\n\n=== 4. 尝试直接从 DOM 中提取数据 ===")
            # 有时候数据会存储在隐藏的元素中
            hidden_data = await page.evaluate("""
                () => {
                    // 查找所有隐藏的 script 或 data 元素
                    const dataElements = document.querySelectorAll('[type="application/json"], [data-json], script[type="application/json"]');

                    const results = [];
                    dataElements.forEach((el, idx) => {
                        const content = el.textContent || el.innerHTML;
                        if (content && content.length > 10) {
                            results.push({
                                index: idx,
                                type: el.type,
                                preview: content.substring(0, 200)
                            });
                        }
                    });

                    return results;
                }
            """)

            if hidden_data:
                print(f"找到 {len(hidden_data)} 个数据元素:")
                for item in hidden_data:
                    print(f"\n  元素 {item['index']}:")
                    print(f"    类型: {item['type']}")
                    print(f"    内容: {item['preview']}")
            else:
                print("未找到隐藏的数据元素")

            print("\n\n=== 5. 检查 Next.js 的 RSC Payload ===")
            # Next.js 13+ 使用 React Server Components，数据可能在特殊的 script 中
            rsc_data = await page.evaluate("""
                () => {
                    const scripts = document.querySelectorAll('script');
                    const results = [];

                    scripts.forEach((script, idx) => {
                        const content = script.textContent || '';

                        // 查找 Next.js 的数据注入模式
                        if (content.includes('self.__next_f') ||
                            content.includes('__NEXT_DATA__') ||
                            content.includes('$RC')) {

                            // 检查是否包含 revenue 或 date
                            const hasRevenue = content.includes('revenue');
                            const hasDate = content.includes('date');

                            if (hasRevenue || hasDate) {
                                results.push({
                                    scriptIndex: idx,
                                    hasRevenue,
                                    hasDate,
                                    length: content.length,
                                    preview: content.substring(0, 500)
                                });
                            }
                        }
                    });

                    return results;
                }
            """)

            if rsc_data:
                print(f"找到 {len(rsc_data)} 个 Next.js 数据 script:")
                for item in rsc_data[:2]:
                    print(f"\n  Script {item['scriptIndex']}:")
                    print(f"    包含 revenue: {item['hasRevenue']}")
                    print(f"    包含 date: {item['hasDate']}")
                    print(f"    长度: {item['length']}")
                    print(f"    预览: {item['preview'][:300]}")
            else:
                print("未找到 Next.js RSC 数据")

    finally:
        await browser.stop()


if __name__ == "__main__":
    asyncio.run(deep_inspect())
