"""提取并解析 Next.js RSC 中的完整数据"""
import asyncio
from crawler.browser import BrowserManager
import json
import re


async def extract_rsc_data():
    test_url = "https://trustmrr.com/startup/a-marketing-platform"

    browser = BrowserManager()
    await browser.start()

    try:
        async with browser.get_page() as page:
            print(f"正在访问: {test_url}\n")
            await page.goto(test_url, wait_until="networkidle", timeout=60000)
            await asyncio.sleep(3)

            print("=== 提取所有 Next.js RSC 数据 ===\n")

            # 提取所有包含 revenue 和 date 的 script
            rsc_scripts = await page.evaluate("""
                () => {
                    const scripts = document.querySelectorAll('script');
                    const results = [];

                    scripts.forEach((script, idx) => {
                        const content = script.textContent || '';

                        if (content.includes('self.__next_f.push')) {
                            // 检查是否同时包含 revenue 和 date
                            const hasRevenue = content.includes('revenue');
                            const hasDate = content.includes('date');

                            if (hasRevenue && hasDate) {
                                results.push({
                                    scriptIndex: idx,
                                    content: content
                                });
                            }
                        }
                    });

                    return results;
                }
            """)

            print(f"找到 {len(rsc_scripts)} 个同时包含 revenue 和 date 的 script\n")

            for i, script_data in enumerate(rsc_scripts, 1):
                content = script_data['content']
                print(f"{'='*60}")
                print(f"Script {script_data['scriptIndex']} (长度: {len(content)})")
                print('='*60)

                # 尝试解析 self.__next_f.push() 的参数
                # 格式: self.__next_f.push([1,"..."])
                matches = re.findall(r'self\.__next_f\.push\(\[(.*?)\]\)', content, re.DOTALL)

                if matches:
                    print(f"找到 {len(matches)} 个 push 调用\n")

                    for j, match in enumerate(matches[:3], 1):  # 只看前3个
                        print(f"Push 调用 {j}:")
                        # 尝试解析参数
                        try:
                            # match 格式: 1,"..."
                            parts = match.split(',', 1)
                            if len(parts) == 2:
                                index = parts[0].strip()
                                data_str = parts[1].strip().strip('"')

                                # 数据可能是转义的 JSON
                                # 尝试查找 revenue 相关的数据
                                if 'revenue' in data_str.lower():
                                    print(f"  索引: {index}")
                                    print(f"  数据长度: {len(data_str)}")

                                    # 查找可能的 JSON 数组
                                    # 查找包含 date 和 revenue 的数组
                                    array_pattern = r'\[(?:[^[\]]|\[[^\]]*\])*"date"[^[\]]*\]'
                                    arrays = re.findall(array_pattern, data_str)

                                    if arrays:
                                        print(f"  找到 {len(arrays)} 个包含 date 的数组")
                                        print(f"  第一个数组预览: {arrays[0][:300]}")

                                        # 尝试解析第一个数组
                                        try:
                                            # 清理转义字符
                                            cleaned = arrays[0].replace('\\', '')
                                            parsed = json.loads(cleaned)
                                            print(f"  [SUCCESS] 成功解析数组，包含 {len(parsed)} 条记录")
                                            if parsed:
                                                print(f"  第一条记录: {parsed[0]}")
                                                print(f"  最后一条记录: {parsed[-1]}")
                                        except Exception as e:
                                            print(f"  [FAILED] 解析失败: {e}")
                                    else:
                                        # 显示部分内容用于调试
                                        print(f"  数据预览: {data_str[:500]}")

                        except Exception as e:
                            print(f"  解析错误: {e}")

                        print()

    finally:
        await browser.stop()


if __name__ == "__main__":
    asyncio.run(extract_rsc_data())
