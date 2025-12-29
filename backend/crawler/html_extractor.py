"""
HTML Extractor - 获取完整渲染后的纯净DOM并美化输出
"""

from bs4 import BeautifulSoup, Comment
from playwright.async_api import Page
from typing import Optional
import re


class HTMLExtractor:
    """提取和美化渲染后的HTML内容"""

    # 需要移除的标签
    REMOVE_TAGS = {
        'script',
        'style',
        'link',
        'noscript',
        'iframe',
        'meta',
        'template',
        'svg',
        'path',
    }

    # 需要保留的属性
    KEEP_ATTRS = {
        'href',
        'src',
        'alt',
        'title',
        'class',
        'id',
        'name',
        'type',
        'value',
        'placeholder',
        'for',
        'action',
        'method',
        'target',
        'rel',
        'width',
        'height',
    }

    @classmethod
    async def extract(
        cls,
        page: Page,
        wait_selector: Optional[str] = None,
        wait_timeout: int = 15000,
        extra_wait: int = 2000,
        keep_images: bool = True
    ) -> str:
        """
        从Playwright页面提取完整渲染后的纯净HTML

        Args:
            page: Playwright页面对象
            wait_selector: 等待出现的选择器（确保内容加载）
            wait_timeout: 等待选择器的超时时间(ms)
            extra_wait: 额外等待时间(ms)，确保动态内容渲染完成
            keep_images: 是否保留图片标签

        Returns:
            美化后的HTML字符串
        """
        # 等待特定元素出现
        if wait_selector:
            try:
                await page.wait_for_selector(wait_selector, timeout=wait_timeout)
            except Exception:
                pass

        # 等待页面完全加载
        try:
            await page.wait_for_load_state('networkidle', timeout=10000)
        except Exception:
            pass

        # 等待document.readyState === 'complete'
        try:
            await page.wait_for_function(
                "() => document.readyState === 'complete'",
                timeout=10000
            )
        except Exception:
            pass

        # 额外等待，确保JS渲染完成
        if extra_wait > 0:
            await page.wait_for_timeout(extra_wait)

        # 获取渲染后的body内容
        body_html = await page.evaluate("() => document.body.innerHTML")

        # 获取页面标题
        title = await page.title() or "Page"

        # 清理和美化HTML
        clean_html = cls._clean_html(body_html, title, keep_images)

        return clean_html

    @classmethod
    def _clean_html(cls, body_html: str, title: str, keep_images: bool = True) -> str:
        """
        清理HTML，移除脚本、样式等非内容元素，并美化输出
        """
        # 使用lxml解析器（更快更准确）
        soup = BeautifulSoup(body_html, 'lxml')

        # 1. 移除注释
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()

        # 2. 移除指定标签
        remove_tags = cls.REMOVE_TAGS.copy()
        if not keep_images:
            remove_tags.add('img')

        for tag_name in remove_tags:
            for tag in soup.find_all(tag_name):
                tag.decompose()

        # 3. 移除隐藏元素
        for tag in soup.find_all(attrs={'hidden': True}):
            tag.decompose()

        # 4. 移除display:none的元素
        for tag in soup.find_all(style=re.compile(r'display\s*:\s*none', re.I)):
            tag.decompose()

        # 5. 清理属性
        for tag in soup.find_all(True):
            cls._clean_attributes(tag)

        # 6. 移除空元素
        cls._remove_empty_elements(soup)

        # 7. 获取body内容
        body = soup.find('body')
        if body:
            content = body.decode_contents()
        else:
            content = str(soup)

        # 8. 美化HTML
        formatted_content = cls._prettify_html(content)

        # 9. 构建完整文档
        html_doc = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{title}</title>
</head>
<body>
{formatted_content}
</body>
</html>'''

        return html_doc

    @classmethod
    def _clean_attributes(cls, tag) -> None:
        """清理标签属性，只保留有意义的属性"""
        if not hasattr(tag, 'attrs') or not tag.attrs:
            return

        attrs_to_remove = []

        for attr_name in list(tag.attrs.keys()):
            # 保留在白名单中的属性
            if attr_name in cls.KEEP_ATTRS:
                continue
            # 移除其他所有属性
            attrs_to_remove.append(attr_name)

        for attr_name in attrs_to_remove:
            del tag.attrs[attr_name]

    @classmethod
    def _remove_empty_elements(cls, soup) -> None:
        """递归移除空元素"""
        # 自闭合标签（不移除）
        void_tags = {'img', 'br', 'hr', 'input', 'area', 'base', 'col', 'embed', 'source', 'track', 'wbr'}
        # 结构性标签（即使空也保留）
        structural_tags = {'html', 'head', 'body', 'main', 'header', 'footer', 'nav', 'section', 'article', 'aside'}

        # 多次迭代直到没有变化
        for _ in range(10):
            changed = False
            for tag in soup.find_all(True):
                if tag.name in void_tags or tag.name in structural_tags:
                    continue

                # 获取文本内容（忽略空白）
                text = tag.get_text(strip=True)

                # 检查是否有有意义的子元素
                has_meaningful_children = bool(tag.find_all(void_tags | structural_tags))

                if not text and not has_meaningful_children:
                    tag.decompose()
                    changed = True

            if not changed:
                break

    @classmethod
    def _prettify_html(cls, html: str) -> str:
        """美化HTML，添加缩进和换行"""
        # 重新解析以获得干净的结构
        soup = BeautifulSoup(html, 'lxml')
        body = soup.find('body')

        if body:
            content = body.decode_contents()
        else:
            content = str(soup)

        # 使用BeautifulSoup的prettify
        temp_soup = BeautifulSoup(content, 'lxml')
        pretty = temp_soup.body.prettify() if temp_soup.body else temp_soup.prettify()

        # 移除多余的空行
        lines = pretty.split('\n')
        cleaned_lines = []
        prev_empty = False

        for line in lines:
            is_empty = not line.strip()
            if is_empty and prev_empty:
                continue
            cleaned_lines.append(line)
            prev_empty = is_empty

        result = '\n'.join(cleaned_lines)

        # 添加整体缩进
        indented_lines = ['  ' + line if line.strip() else line for line in result.split('\n')]

        return '\n'.join(indented_lines)
