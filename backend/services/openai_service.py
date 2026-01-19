"""
OpenAI Service - Wrapper for OpenAI API calls
"""

import os
import json
import logging
from typing import Dict, Any, Optional
import httpx
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


# Landing Page分析专用Prompt
LANDING_PAGE_ANALYSIS_PROMPT = """你是一位专业的SaaS产品分析师。请分析以下产品的Landing Page内容，并以JSON格式返回结构化分析结果。

## 产品基本信息
- 名称: {startup_name}
- 分类: {startup_category}
- 描述: {startup_description}
- 月收入: ${startup_revenue}

## Landing Page内容
```
{page_content}
```

## 分析要求

请从以下维度分析Landing Page，并返回JSON格式的分析结果：

```json
{{
    "target_audience": ["目标用户群体列表"],
    "target_roles": ["目标角色/职位列表，如：开发者、产品经理、创业者等"],
    "use_cases": ["使用场景列表"],

    "core_features": ["核心功能列表，最多5个"],
    "feature_count": 5,
    "value_propositions": ["价值主张列表，产品承诺带来的核心价值"],

    "pain_points": ["产品解决的痛点列表"],
    "pain_point_sharpness": 7.5,
    "uses_before_after": true,
    "uses_emotional_words": true,

    "potential_moats": ["潜在竞争优势/护城河列表"],

    "pricing_model": "subscription",
    "pricing_tiers": [
        {{"name": "Free", "price": 0, "billing": "monthly", "features": ["..."]}}
    ],
    "pricing_clarity_score": 8.0,
    "has_free_tier": true,
    "has_trial": true,

    "cta_count": 5,
    "cta_texts": ["Get Started", "Try Free", "See Demo"],
    "conversion_funnel_steps": 3,
    "has_instant_value_demo": true,
    "conversion_friendliness_score": 8.0,

    "industry_keywords": {{"关键词1": 5, "关键词2": 3}},
    "headline_text": "页面主标题",
    "tagline_text": "副标题或标语",

    "positioning_clarity_score": 7.5,
    "replication_difficulty_score": 6.0,
    "individual_replicability_score": 7.0,
    "product_maturity_score": 7.0
}}
```

## 评分说明 (0-10分)

- **pain_point_sharpness**: 痛点定义的锋利程度 (10分=问题描述极其清晰精准)
- **pricing_clarity_score**: 定价透明度 (10分=立刻能理解价格和包含内容)
- **conversion_friendliness_score**: 转化友好度 (10分=几乎无摩擦即可开始使用)
- **positioning_clarity_score**: 产品定位清晰度 (10分=立刻明白产品是做什么的)
- **replication_difficulty_score**: 复制难度 (10分=非常难以复制，有技术/数据/网络效应壁垒)
- **individual_replicability_score**: 个人开发者可复制性 (10分=非常适合个人开发者复制)
- **product_maturity_score**: 产品成熟度 (10分=功能完善、UI精致、文档齐全)

**重要**: 请只返回JSON，不要包含其他解释文字。"""


class OpenAIService:
    """OpenAI API服务封装"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None
    ):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL")
        self.default_model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")

        # 代理配置
        self.https_proxy = None #os.getenv("HTTPS_PROXY") or os.getenv("https_proxy")

        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not configured")

        # 创建客户端，支持自定义base_url和代理
        client_kwargs = {"api_key": self.api_key}
        if self.base_url:
            client_kwargs["base_url"] = self.base_url

        # 如果配置了代理，使用自定义httpx客户端
        self._http_client = None
        if self.https_proxy:
            logger.info(f"Using proxy: {self.https_proxy}")
            self._http_client = httpx.AsyncClient(proxy=self.https_proxy)
            client_kwargs["http_client"] = self._http_client

        self.client = AsyncOpenAI(**client_kwargs)

    async def close(self):
        """关闭客户端连接"""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def analyze_landing_page(
        self,
        page_content: str,
        startup_info: Dict[str, Any],
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        使用OpenAI分析Landing Page内容

        Args:
            page_content: Landing Page的文本内容
            startup_info: 产品基本信息 (name, category, description, revenue_30d)
            model: 使用的模型，默认gpt-4o-mini

        Returns:
            分析结果字典
        """
        model = model or self.default_model

        # 截断过长的内容
        max_chars = 30000
        if len(page_content) > max_chars:
            page_content = page_content[:max_chars] + "\n\n... [内容已截断]"

        # 构建prompt
        prompt = LANDING_PAGE_ANALYSIS_PROMPT.format(
            startup_name=startup_info.get("name", "Unknown"),
            startup_category=startup_info.get("category", "Unknown"),
            startup_description=startup_info.get("description", "N/A"),
            startup_revenue=startup_info.get("revenue_30d", "N/A"),
            page_content=page_content
        )

        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "你是一位专业的SaaS产品分析师，擅长分析产品Landing Page并提取结构化信息。请始终以JSON格式返回分析结果。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=4000
            )

            content = response.choices[0].message.content

            # 解析JSON响应
            analysis = self._parse_json_response(content)
            analysis["ai_model_used"] = model

            return analysis

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return self._get_default_analysis(str(e))

    def _parse_json_response(self, content: str) -> Dict[str, Any]:
        """解析AI响应中的JSON"""
        try:
            # 尝试直接解析
            return json.loads(content)
        except json.JSONDecodeError:
            pass

        # 尝试从markdown代码块中提取
        try:
            if "```json" in content:
                start = content.find("```json") + 7
                end = content.find("```", start)
                json_str = content[start:end].strip()
                return json.loads(json_str)
            elif "```" in content:
                start = content.find("```") + 3
                end = content.find("```", start)
                json_str = content[start:end].strip()
                return json.loads(json_str)
        except (json.JSONDecodeError, ValueError):
            pass

        logger.warning("Failed to parse AI response as JSON")
        return self._get_default_analysis("JSON parse error")

    def _get_default_analysis(self, error_msg: str = "") -> Dict[str, Any]:
        """返回默认分析结果"""
        return {
            "target_audience": [],
            "target_roles": [],
            "use_cases": [],
            "core_features": [],
            "feature_count": 0,
            "value_propositions": [],
            "pain_points": [],
            "pain_point_sharpness": 5.0,
            "uses_before_after": False,
            "uses_emotional_words": False,
            "potential_moats": [],
            "pricing_model": "unknown",
            "pricing_tiers": [],
            "pricing_clarity_score": 5.0,
            "has_free_tier": False,
            "has_trial": False,
            "cta_count": 0,
            "cta_texts": [],
            "conversion_funnel_steps": 0,
            "has_instant_value_demo": False,
            "conversion_friendliness_score": 5.0,
            "industry_keywords": {},
            "headline_text": "",
            "tagline_text": "",
            "positioning_clarity_score": 5.0,
            "replication_difficulty_score": 5.0,
            "individual_replicability_score": 5.0,
            "product_maturity_score": 5.0,
            "ai_model_used": "none",
            "error": error_msg
        }

    async def chat(
        self,
        messages: list,
        model: Optional[str] = None,
        temperature: float = 0.7
    ) -> str:
        """
        通用聊天接口

        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数

        Returns:
            AI响应文本
        """
        model = model or self.default_model

        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI chat error: {e}")
            raise
