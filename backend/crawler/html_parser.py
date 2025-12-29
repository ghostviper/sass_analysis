"""
HTML Parser - 从HTML快照中提取startup数据
"""

import re
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from bs4 import BeautifulSoup
from dataclasses import dataclass, asdict
import json


@dataclass
class StartupData:
    """Startup数据结构"""
    # 基本信息
    name: str = ""
    slug: str = ""
    description: str = ""
    website_url: str = ""  # 产品官网链接
    logo_url: str = ""
    trustmrr_url: str = ""  # TrustMRR页面链接

    # 收入数据
    total_revenue: str = ""
    total_revenue_raw: int = 0
    mrr: str = ""
    mrr_raw: int = 0
    revenue_last_4_weeks: str = ""
    revenue_last_4_weeks_raw: int = 0
    revenue_change_percent: str = ""
    active_subscriptions: int = 0

    # 排名
    rank: int = 0

    # 创始人信息
    founder_name: str = ""
    founder_username: str = ""
    founder_followers: int = 0  # 粉丝数量
    founder_social_platform: str = ""  # 社交平台 (如 𝕏, Twitter, LinkedIn)
    founder_profile_url: str = ""
    founder_avatar_url: str = ""  # 创始人头像URL

    # 公司信息
    founded: str = ""
    country: str = ""
    country_code: str = ""
    category: str = ""
    category_slug: str = ""

    # 出售信息
    is_for_sale: bool = False
    asking_price: str = ""
    asking_price_raw: int = 0
    revenue_multiple: str = ""
    buyers_interested: int = 0  # 最近关注/查看的买家数量

    # 元数据
    last_updated: str = ""
    verified_source: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class HTMLParser:
    """从HTML快照解析startup数据"""

    def __init__(self, html_content: str):
        self.soup = BeautifulSoup(html_content, 'lxml')
        self.data = StartupData()

    @classmethod
    def from_file(cls, file_path: Union[str, Path]) -> 'HTMLParser':
        """从文件加载"""
        path = Path(file_path)
        content = path.read_text(encoding='utf-8')
        parser = cls(content)
        # 从文件名获取slug
        parser.data.slug = path.stem
        return parser

    def parse(self) -> StartupData:
        """解析所有数据"""
        self._parse_basic_info()
        self._parse_revenue_cards()
        self._parse_founder_info()
        self._parse_company_info()
        self._parse_sale_info()
        self._parse_metadata()
        return self.data

    def _parse_basic_info(self) -> None:
        """解析基本信息：名称、描述、网站URL、Logo"""
        # 名称 - 从h1标签获取
        h1 = self.soup.find('h1', class_=re.compile(r'text-[23]xl.*font-bold'))
        if h1:
            self.data.name = h1.get_text(strip=True)

        # 描述 - 从特定的p标签获取
        desc_p = self.soup.find('p', class_=re.compile(r'text-sm.*text-muted-foreground.*leading-relaxed'))
        if desc_p:
            self.data.description = desc_p.get_text(strip=True)

        # 产品官网URL - 从Visit按钮获取
        visit_link = self.soup.find('a', string=re.compile(r'Visit'))
        if not visit_link:
            # 尝试找包含Visit文本的a标签
            for a in self.soup.find_all('a', target='_blank'):
                if 'Visit' in a.get_text():
                    visit_link = a
                    break

        if visit_link and visit_link.get('href'):
            url = visit_link['href']
            # 移除tracking参数
            if '?ref=' in url:
                url = url.split('?ref=')[0]
            self.data.website_url = url

        # TrustMRR页面链接
        if self.data.slug:
            self.data.trustmrr_url = f"https://trustmrr.com/startup/{self.data.slug}"

        # Logo URL
        if self.data.name:
            logo_img = self.soup.find('img', alt=self.data.name)
            if logo_img and logo_img.get('src'):
                src = logo_img['src']
                # 转换为完整URL
                if src.startswith('/'):
                    src = f"https://trustmrr.com{src}"
                self.data.logo_url = src

    def _parse_revenue_cards(self) -> None:
        """解析收入相关的卡片数据"""
        cards = self.soup.find_all('div', class_=re.compile(r'bg-card.*rounded-xl.*border'))

        for card in cards:
            card_text = card.get_text()

            # Total revenue 卡片
            if 'Total revenue' in card_text:
                self._parse_total_revenue_card(card)

            # MRR 卡片
            elif 'MRR' in card_text:
                self._parse_mrr_card(card)

            # Revenue last 4 weeks 卡片 (图表卡片)
            elif 'revenue last 4 weeks' in card_text:
                self._parse_recent_revenue_card(card)

    def _parse_total_revenue_card(self, card) -> None:
        """解析总收入卡片"""
        # 收入金额
        amount_div = card.find('div', class_=re.compile(r'text-2xl.*font-bold'))
        if amount_div:
            self.data.total_revenue = amount_div.get_text(strip=True)
            self.data.total_revenue_raw = self._parse_money(self.data.total_revenue)

        # 排名
        rank_span = card.find('span', class_=re.compile(r'cursor-help'))
        if rank_span:
            rank_text = rank_span.get_text(strip=True)
            match = re.search(r'#(\d+)', rank_text)
            if match:
                self.data.rank = int(match.group(1))

        # 变化百分比 - 查找包含 "MoM growth" 的div
        growth_div = card.find('div', title=re.compile(r'vs previous'))
        if growth_div:
            # 从title属性提取百分比
            title = growth_div.get('title', '')
            match = re.search(r'(\d+(?:\.\d+)?)\s*%', title)
            if match:
                self.data.revenue_change_percent = f"{match.group(1)}%"

        # 备选方案：从span中查找
        if not self.data.revenue_change_percent:
            growth_span = card.find('span', class_=re.compile(r'text-xs.*font-semibold.*(text-red|text-green)'))
            if growth_span:
                text = growth_span.get_text(strip=True)
                if '%' in text:
                    self.data.revenue_change_percent = text

    def _parse_mrr_card(self, card) -> None:
        """解析MRR卡片"""
        # MRR金额
        amount_div = card.find('div', class_=re.compile(r'text-2xl.*font-bold'))
        if amount_div:
            self.data.mrr = amount_div.get_text(strip=True)
            self.data.mrr_raw = self._parse_money(self.data.mrr)

        # Active subscriptions
        sub_p = card.find('p', class_=re.compile(r'text-xs.*text-muted-foreground'))
        if sub_p:
            sub_text = sub_p.get_text(strip=True)
            match = re.search(r'(\d+)\s*active\s*subscription', sub_text)
            if match:
                self.data.active_subscriptions = int(match.group(1))

    def _parse_recent_revenue_card(self, card) -> None:
        """解析近期收入卡片"""
        # 金额
        amount_div = card.find('div', class_=re.compile(r'text-2xl.*font-bold'))
        if amount_div:
            self.data.revenue_last_4_weeks = amount_div.get_text(strip=True)
            self.data.revenue_last_4_weeks_raw = self._parse_money(self.data.revenue_last_4_weeks)

    def _parse_founder_info(self) -> None:
        """解析创始人信息"""
        # 找到Founder卡片
        founder_link = self.soup.find('a', href=re.compile(r'/founder/'))
        if not founder_link:
            return

        # Founder profile URL
        href = founder_link.get('href', '')
        if href.startswith('/'):
            self.data.founder_profile_url = f"https://trustmrr.com{href}"
        else:
            self.data.founder_profile_url = href

        # Username from URL
        match = re.search(r'/founder/([^/]+)', self.data.founder_profile_url)
        if match:
            self.data.founder_username = match.group(1)

        # Founder avatar - 查找 rounded-full 的 img 标签
        avatar_img = founder_link.find('img', class_=re.compile(r'rounded-full'))
        if avatar_img and avatar_img.get('src'):
            self.data.founder_avatar_url = avatar_img['src']
        elif self.data.founder_username:
            # 如果没找到头像，使用 unavatar.io 服务构建
            self.data.founder_avatar_url = f"https://unavatar.io/x/{self.data.founder_username}"

        # Founder name
        name_span = founder_link.find('span', class_=re.compile(r'truncate'))
        if name_span:
            self.data.founder_name = name_span.get_text(strip=True)

        # Followers and platform - 查找 "X followers on Y" 模式
        followers_text = founder_link.get_text()

        # 匹配 "135 followers on 𝕏" 或 "1.2k followers on Twitter" 等
        followers_match = re.search(r'([\d,.]+[kKmM]?)\s*followers?\s*(?:on\s+)?([𝕏XTwitterLinkedIn]*)?', followers_text, re.IGNORECASE)
        if followers_match:
            followers_str = followers_match.group(1).replace(',', '')
            # 处理 k/m 后缀
            if followers_str.lower().endswith('k'):
                self.data.founder_followers = int(float(followers_str[:-1]) * 1000)
            elif followers_str.lower().endswith('m'):
                self.data.founder_followers = int(float(followers_str[:-1]) * 1000000)
            else:
                try:
                    self.data.founder_followers = int(float(followers_str))
                except ValueError:
                    self.data.founder_followers = 0

            # 社交平台
            platform = followers_match.group(2)
            if platform:
                # 𝕏 是Twitter的新标识
                if platform in ['𝕏', 'X', 'x']:
                    self.data.founder_social_platform = 'X (Twitter)'
                else:
                    self.data.founder_social_platform = platform

    def _parse_company_info(self) -> None:
        """解析公司信息：成立时间、国家、分类"""
        # 找到Founded卡片
        cards = self.soup.find_all('div', class_=re.compile(r'bg-card.*rounded-xl.*border'))

        for card in cards:
            card_text = card.get_text()
            if 'Founded' not in card_text:
                continue

            # Founded date - 查找包含月份的文本
            # HTML结构: <div class="text-2xl font-bold"><div class="flex flex-col"><div>December 2023</div>...
            amount_div = card.find('div', class_=re.compile(r'text-2xl.*font-bold'))
            if amount_div:
                # 查找所有纯文本div（不是链接）
                date_months = ['January', 'February', 'March', 'April', 'May', 'June',
                               'July', 'August', 'September', 'October', 'November', 'December']

                # 遍历所有div子元素
                for div in amount_div.find_all('div', recursive=True):
                    # 跳过包含链接的div
                    if div.find('a'):
                        continue

                    text = div.get_text(strip=True)
                    # 检查是否是日期格式（包含月份名 + 年份）
                    if text and any(month in text for month in date_months):
                        # 确保只包含日期，不包含国家名
                        # 日期格式通常是 "Month Year" 或 "Month YYYY"
                        if re.match(r'^[A-Za-z]+\s+\d{4}$', text):
                            self.data.founded = text
                            break

            # Country - 从country链接获取
            country_link = card.find('a', href=re.compile(r'/country/'))
            if country_link:
                country_span = country_link.find('span', class_=re.compile(r'text-muted-foreground'))
                if country_span:
                    self.data.country = country_span.get_text(strip=True)
                # Country code from URL
                match = re.search(r'/country/([^/]+)', country_link.get('href', ''))
                if match:
                    self.data.country_code = match.group(1).upper()

            # Category - 从category链接获取
            category_link = card.find('a', href=re.compile(r'/category/'))
            if category_link:
                category_span = category_link.find('span')
                if category_span:
                    self.data.category = category_span.get_text(strip=True)
                # Category slug from URL
                match = re.search(r'/category/([^/]+)', category_link.get('href', ''))
                if match:
                    self.data.category_slug = match.group(1)

            break

    def _parse_sale_info(self) -> None:
        """解析出售信息"""
        # 检查是否有出售横幅
        sale_banner = self.soup.find(string=re.compile(r'This startup is for sale'))
        if not sale_banner:
            return

        self.data.is_for_sale = True

        # 找到包含出售信息的banner
        banner = self.soup.find('div', class_=re.compile(r'bg-gradient-to-r.*amber'))
        if not banner:
            # 尝试其他方式查找
            banner = sale_banner.find_parent('div', class_=re.compile(r'sticky|bg-'))

        if not banner:
            return

        banner_text = banner.get_text()

        # Asking price - 查找 "Asking price: $X" 模式
        price_match = re.search(r'Asking price[:\s]*\$?([\d,]+(?:\.\d+)?[kKmM]?)', banner_text)
        if price_match:
            self.data.asking_price = f"${price_match.group(1)}"
            self.data.asking_price_raw = self._parse_money(price_match.group(1))
        else:
            # 备选：查找font-bold的span
            price_span = banner.find('span', class_=re.compile(r'font-bold'))
            if price_span:
                price_text = price_span.get_text(strip=True)
                if '$' in price_text or price_text.replace(',', '').replace('.', '').isdigit():
                    self.data.asking_price = price_text
                    self.data.asking_price_raw = self._parse_money(price_text)

        # Revenue multiple - 查找 "X.Xx revenue" 模式
        multiple_match = re.search(r'([\d.]+)x\s*(?:revenue)?', banner_text, re.IGNORECASE)
        if multiple_match:
            self.data.revenue_multiple = f"{multiple_match.group(1)}x"

        # Buyers interested - 查找 "X buyers saw this" 模式
        buyers_match = re.search(r'(\d+)\s*(?:buyers?\s*(?:saw|viewed|interested)|people\s*viewed)', banner_text, re.IGNORECASE)
        if buyers_match:
            self.data.buyers_interested = int(buyers_match.group(1))

    def _parse_metadata(self) -> None:
        """解析元数据：验证来源、最后更新时间"""
        # 验证来源
        verified_text = self.soup.find(string=re.compile(r'verified with'))
        if verified_text:
            if 'Stripe' in verified_text:
                self.data.verified_source = 'Stripe'
            elif 'Paddle' in verified_text:
                self.data.verified_source = 'Paddle'
            else:
                self.data.verified_source = 'Unknown'

        # Last updated
        updated_span = self.soup.find('span', string=re.compile(r'Last updated'))
        if updated_span:
            match = re.search(r'Last updated:\s*(.+)', updated_span.get_text())
            if match:
                self.data.last_updated = match.group(1).strip()

    @staticmethod
    def _parse_money(text: str) -> int:
        """将金额字符串解析为整数（单位：美分或美元）"""
        if not text:
            return 0
        # 移除$符号和逗号
        text = text.replace('$', '').replace(',', '').strip()
        # 处理k后缀
        if text.lower().endswith('k'):
            return int(float(text[:-1]) * 1000)
        # 处理m后缀
        if text.lower().endswith('m'):
            return int(float(text[:-1]) * 1000000)
        try:
            return int(float(text))
        except ValueError:
            return 0


def parse_html_file(file_path: Union[str, Path]) -> Dict[str, Any]:
    """便捷函数：解析HTML文件并返回字典"""
    parser = HTMLParser.from_file(file_path)
    data = parser.parse()
    return data.to_dict()


def parse_all_snapshots(snapshot_dir: Union[str, Path]) -> List[Dict[str, Any]]:
    """解析目录中所有HTML快照"""
    snapshot_dir = Path(snapshot_dir)
    results = []

    for html_file in snapshot_dir.glob('*.html'):
        try:
            data = parse_html_file(html_file)
            results.append(data)
            print(f"Parsed: {html_file.name} -> {data.get('name', 'Unknown')}")
        except Exception as e:
            print(f"Error parsing {html_file.name}: {e}")

    return results


# CLI入口
if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        # 解析指定文件
        file_path = sys.argv[1]
        data = parse_html_file(file_path)
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        # 解析所有快照
        snapshot_dir = Path(__file__).parent.parent / 'data' / 'html_snapshots'
        if snapshot_dir.exists():
            results = parse_all_snapshots(snapshot_dir)
            print(f"\n{'='*60}")
            print(f"Total parsed: {len(results)} files")

            # 打印第一个结果作为示例
            if results:
                print(f"\nExample output for '{results[0].get('name')}':")
                print(json.dumps(results[0], indent=2, ensure_ascii=False))
        else:
            print(f"Snapshot directory not found: {snapshot_dir}")
