"""完整提取 Next.js RSC 数据并保存到文件"""
import asyncio
from crawler.browser import BrowserManager
import json
import re


async def extract_and_save():
    test_url = "https://trustmrr.com/startup/a-marketing-platform"

    browser = BrowserManager()
    await browser.start()

    try:
        async with browser.get_page() as page:
            print(f"正在访问: {test_url}\n")
            await page.goto(test_url, wait_until="networkidle", timeout=60000)
            await asyncio.sleep(3)

            # 提取所有包含 revenue 和 date 的 script
            rsc_scripts = await page.evaluate("""
                () => {
                    const scripts = document.querySelectorAll('script');
                    const results = [];

                    scripts.forEach((script, idx) => {
                        const content = script.textContent || '';

                        if (content.includes('self.__next_f.push')) {
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

            print(f"找到 {len(rsc_scripts)} 个包含 revenue 和 date 的 script\n")

            if rsc_scripts:
                # 保存完整内容到文件
                with open('rsc_data_full.txt', 'w', encoding='utf-8') as f:
                    for script_data in rsc_scripts:
                        f.write(f"{'='*80}\n")
                        f.write(f"Script {script_data['scriptIndex']}\n")
                        f.write(f"{'='*80}\n")
                        f.write(script_data['content'])
                        f.write('\n\n')

                print("完整数据已保存到 rsc_data_full.txt")

                # 尝试提取 dailyRevenue 数组
                content = rsc_scripts[0]['content']

                # 查找所有可能的数组模式
                print("\n尝试提取数组数据...")

                # 模式1: 查找 "dailyRevenue":[...]
                pattern1 = r'"dailyRevenue"\s*:\s*(\[[^\]]*\])'
                match1 = re.search(pattern1, content)
                if match1:
                    print("[FOUND] 找到 dailyRevenue 字段")
                    array_str = match1.group(1)
                    print(f"数组长度: {len(array_str)}")
                    print(f"预览: {array_str[:300]}")

                # 模式2: 查找包含 date 和 revenue 的数组
                pattern2 = r'\[(?:[^[\]]|\[[^\]]*\])*?"date"[^[\]]*?"revenue"[^[\]]*?\]'
                matches2 = re.findall(pattern2, content)
                if matches2:
                    print(f"\n[FOUND] 找到 {len(matches2)} 个包含 date 和 revenue 的数组")
                    for i, arr in enumerate(matches2[:3], 1):
                        print(f"\n数组 {i}:")
                        print(f"  长度: {len(arr)}")
                        print(f"  预览: {arr[:300]}")

                        # 尝试解析
                        try:
                            # 清理转义字符
                            cleaned = arr.replace('\\', '')
                            parsed = json.loads(cleaned)
                            print(f"  [SUCCESS] 成功解析，包含 {len(parsed)} 条记录")
                            if parsed and len(parsed) > 0:
                                print(f"  第一条: {parsed[0]}")
                                if len(parsed) > 1:
                                    print(f"  最后一条: {parsed[-1]}")
                        except Exception as e:
                            print(f"  [FAILED] 解析失败: {e}")

                # 模式3: 直接搜索 JSON 对象数组
                pattern3 = r'\[\s*\{[^}]*"date"[^}]*\}(?:\s*,\s*\{[^}]*"date"[^}]*\})*\s*\]'
                matches3 = re.findall(pattern3, content, re.DOTALL)
                if matches3:
                    print(f"\n[FOUND] 找到 {len(matches3)} 个 JSON 对象数组")
                    for i, arr in enumerate(matches3[:2], 1):
                        print(f"\n数组 {i}:")
                        print(f"  长度: {len(arr)}")
                        print(f"  预览: {arr[:500]}")

    finally:
        await browser.stop()


if __name__ == "__main__":
    asyncio.run(extract_and_save())
