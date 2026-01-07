"""
Chart Data Extractor - 从 TrustMRR 页面提取收入时序数据

TrustMRR 的时序数据通过单独的 API 请求获取:
API: https://trustmrr.com/api/startup/revenue/{slug}?granularity=daily&period=4w

数据格式:
{
    "loading": false,
    "data": [
        {
            "date": "2025-12-11",
            "revenue": 0,
            "charges": 0,
            "mrr": 299,
            "activeSubscriptions": 1
        },
        ...
    ]
}
"""

import asyncio
import json
from typing import List, Dict, Any, Optional
from playwright.async_api import Page, Response


class ChartDataExtractor:
    """从 TrustMRR 页面提取收入时序数据"""

    # API 端点模式
    REVENUE_API_PATTERN = "/api/startup/revenue/"

    @classmethod
    async def extract(cls, page: Page, slug: str = None, timeout: int = 15000) -> Optional[List[Dict[str, Any]]]:
        """
        从页面提取收入时序数据（通过拦截 API 请求）

        注意：此方法应该在页面导航之前调用，以便能够拦截 API 请求。
        或者，如果页面已经加载，可以尝试从已有的响应中提取数据。

        Args:
            page: Playwright 页面对象
            slug: Startup slug（如果已知）
            timeout: 等待 API 响应的超时时间 (毫秒)

        Returns:
            收入时序数据列表，如果提取失败则返回 None
        """
        # 如果没有提供 slug，尝试从 URL 中提取
        if not slug:
            url = page.url
            if '/startup/' in url:
                slug = url.split('/startup/')[-1].split('?')[0].split('#')[0]

        if not slug:
            return None

        # 尝试直接调用 API 获取数据
        try:
            api_url = f"https://trustmrr.com/api/startup/revenue/{slug}?granularity=daily&period=4w"

            # 使用 page.request 发起 API 请求（会携带页面的 cookies 和 headers）
            response = await page.request.get(api_url)

            if response.status == 200:
                data = await response.json()

                # 提取数据数组
                if isinstance(data, dict) and 'data' in data:
                    return data['data']
        except Exception as e:
            # API 请求失败，返回 None
            pass

        return None

    @classmethod
    def validate_data(cls, data: List[Dict[str, Any]]) -> bool:
        """验证提取的数据格式是否正确"""
        if not data or not isinstance(data, list):
            return False

        # 检查第一条记录是否包含必要字段
        if len(data) > 0:
            first_entry = data[0]
            required_fields = ['date', 'revenue']
            return all(field in first_entry for field in required_fields)

        return False

    @classmethod
    def normalize_data(cls, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        标准化数据格式

        确保所有记录都有统一的字段名和类型
        """
        normalized = []
        for entry in data:
            normalized_entry = {
                'date': entry.get('date', ''),
                'revenue': cls._to_int(entry.get('revenue')),
                'mrr': cls._to_int(entry.get('mrr')),
                'charges': cls._to_int(entry.get('charges')),
                'subscription_revenue': cls._to_int(entry.get('subscriptionRevenue')),
            }
            # 只添加有效日期的记录
            if normalized_entry['date']:
                normalized.append(normalized_entry)

        return normalized

    @staticmethod
    def _to_int(value) -> Optional[int]:
        """将值转换为整数"""
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None


# 便捷函数
async def extract_revenue_history(page: Page, slug: str = None) -> Optional[List[Dict[str, Any]]]:
    """
    便捷函数：从页面提取并标准化收入时序数据

    Args:
        page: Playwright 页面对象
        slug: Startup slug（可选，如果不提供会从 URL 中提取）

    Returns:
        标准化的收入时序数据列表
    """
    data = await ChartDataExtractor.extract(page, slug)
    if data and ChartDataExtractor.validate_data(data):
        return ChartDataExtractor.normalize_data(data)
    return None
