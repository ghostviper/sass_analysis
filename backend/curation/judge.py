"""
母题判断器

核心类 MotherThemeJudge，负责调用 LLM 进行母题判断。
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

from database.models import (
    Startup,
    LandingPageAnalysis,
    ProductSelectionAnalysis,
    CategoryAnalysis,
)
from services.openai_service import OpenAIService

from .config import MOTHER_THEMES, PROMPT_VERSION
from .evidence import build_context, build_evidence_availability
from .prompts import MOTHER_THEME_SYSTEM_PROMPT, build_one_shot_prompt, build_single_theme_prompt
from .validators import validate_judgment, needs_fallback

logger = logging.getLogger(__name__)


class MotherThemeJudge:
    """母题判断器 - 支持三层架构"""

    def __init__(self, openai_service: OpenAIService):
        self.openai = openai_service

    async def judge_single_theme(
        self,
        theme: Dict[str, Any],
        startup: Startup,
        analysis: LandingPageAnalysis,
        selection: Optional[ProductSelectionAnalysis] = None,
        category_analysis: Optional[CategoryAnalysis] = None,
    ) -> Dict[str, Any]:
        """判断单个母题"""
        evidence_availability = build_evidence_availability(
            startup, analysis, selection, category_analysis
        )
        context = build_context(
            startup, analysis, selection, category_analysis,
            evidence_availability=evidence_availability
        )
        prompt = build_single_theme_prompt(context, theme)
        result = await self._call_ai(prompt)
        validated = validate_judgment(theme, result, evidence_availability=evidence_availability)
        validated["_meta"] = {
            "theme": theme["key"],
            "layer": theme.get("layer", "unknown"),
            "prompt_version": PROMPT_VERSION,
            "model": self.openai.default_model,
        }
        return validated

    async def judge_all_themes(
        self,
        startup: Startup,
        analysis: LandingPageAnalysis,
        selection: Optional[ProductSelectionAnalysis] = None,
        category_analysis: Optional[CategoryAnalysis] = None,
        themes: Optional[List[Dict[str, Any]]] = None,
        fallback_on_invalid: bool = False,
    ) -> Dict[str, Dict[str, Any]]:
        """一次请求返回全部母题的判断结果"""
        if themes is None:
            themes = MOTHER_THEMES

        evidence_availability = build_evidence_availability(
            startup, analysis, selection, category_analysis
        )
        context = build_context(
            startup, analysis, selection, category_analysis,
            evidence_availability=evidence_availability
        )
        prompt = build_one_shot_prompt(context, themes)
        result = await self._call_ai(prompt)

        # 检查响应格式
        if not isinstance(result, dict) or "judgments" not in result:
            if fallback_on_invalid:
                return await self._fallback_to_single(
                    themes, startup, analysis, selection, category_analysis
                )
            return {"_error": {"error": "缺少 judgments 字段", "raw_response": result}}

        judgments_raw = result.get("judgments", {})
        output: Dict[str, Dict[str, Any]] = {}

        for theme in themes:
            theme_key = theme["key"]
            if theme_key not in judgments_raw:
                validated = {"error": "缺少该母题结果"}
            else:
                t_res = judgments_raw.get(theme_key, {})
                validated = validate_judgment(theme, t_res, evidence_availability=evidence_availability)

            # 需要回退时单独判断
            if fallback_on_invalid and needs_fallback(validated):
                fallback_result = await self.judge_single_theme(
                    theme, startup, analysis, selection, category_analysis
                )
                fallback_result.setdefault("_meta", {})
                fallback_result["_meta"]["fallback"] = "single_theme"
                validated = fallback_result
            else:
                validated["_meta"] = {
                    "theme": theme_key,
                    "layer": theme.get("layer", "unknown"),
                    "prompt_version": PROMPT_VERSION,
                    "model": self.openai.default_model,
                }

            output[theme_key] = validated

        return output


    async def _fallback_to_single(
        self,
        themes: List[Dict[str, Any]],
        startup: Startup,
        analysis: LandingPageAnalysis,
        selection: Optional[ProductSelectionAnalysis],
        category_analysis: Optional[CategoryAnalysis],
    ) -> Dict[str, Dict[str, Any]]:
        """回退到逐个判断"""
        output: Dict[str, Dict[str, Any]] = {}
        for theme in themes:
            fallback_result = await self.judge_single_theme(
                theme, startup, analysis, selection, category_analysis
            )
            fallback_result.setdefault("_meta", {})
            fallback_result["_meta"]["fallback"] = "single_theme"
            output[theme["key"]] = fallback_result
        return output

    async def _call_ai(
        self, 
        prompt: str, 
        attempts: int = 2, 
        retry_delay: float = 1.0
    ) -> Dict[str, Any]:
        """调用 AI 并解析结果"""
        last_error: Optional[str] = None
        for attempt in range(attempts):
            try:
                response = await self.openai.chat(
                    messages=[
                        {"role": "system", "content": MOTHER_THEME_SYSTEM_PROMPT},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.3,
                )
                return self._parse_json(response)
            except Exception as exc:
                last_error = str(exc)
                logger.error(f"AI 调用失败（第 {attempt + 1} 次）: {exc}")
                if attempt < attempts - 1:
                    await asyncio.sleep(retry_delay)
        return {"error": last_error or "unknown_error"}

    @staticmethod
    def _parse_json(content: str) -> Dict[str, Any]:
        """解析 AI 响应中的 JSON"""
        if isinstance(content, dict):
            return content
        if not isinstance(content, str):
            return {"error": "响应不是字符串", "raw_response": content}

        def _attempt_parse(text: str) -> Optional[Dict[str, Any]]:
            try:
                parsed = json.loads(text)
            except json.JSONDecodeError:
                return None
            return parsed if isinstance(parsed, dict) else None

        def _extract_braced(text: str) -> Optional[str]:
            start = text.find("{")
            end = text.rfind("}")
            if start == -1 or end == -1 or end <= start:
                return None
            return text[start : end + 1]

        # 直接解析
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass

        # 尝试从 markdown 代码块提取
        if "```json" in content:
            start = content.find("```json") + 7
            end = content.find("```", start)
            if end == -1:
                end = len(content)
            candidate = content[start:end].strip()
            parsed = _attempt_parse(candidate)
            if parsed is not None:
                return parsed

        if "```" in content:
            start = content.find("```") + 3
            end = content.find("```", start)
            if end == -1:
                end = len(content)
            candidate = content[start:end].strip()
            parsed = _attempt_parse(candidate)
            if parsed is not None:
                return parsed

        # 尝试提取花括号内容
        braced = _extract_braced(content)
        if braced:
            parsed = _attempt_parse(braced)
            if parsed is not None:
                return parsed

        return {"error": "JSON 解析失败", "raw_response": content}
