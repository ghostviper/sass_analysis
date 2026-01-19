"""
策展系统模块

提供母题判断和专题生成功能，用于 BuildWhat 发现页内容生成。

模块结构：
- config: 母题定义、证据字段、策展角色配置
- schemas: 数据结构定义
- evidence: 证据数据构建
- prompts: Prompt 模板
- validators: 验证逻辑
- judge: 母题判断器
- curator: 策展 Agent
- tasks: 定时任务
- cli: 命令行工具
"""

# 在导入任何子模块之前加载 .env
from pathlib import Path
from dotenv import load_dotenv
_env_path = Path(__file__).parent.parent / ".env"
if _env_path.exists():
    load_dotenv(_env_path)

from .config import MOTHER_THEMES, THEME_LAYERS, EVIDENCE_FIELDS
from .judge import MotherThemeJudge
from .curator import CuratorAgent, generate_topics

__all__ = [
    "MOTHER_THEMES",
    "THEME_LAYERS", 
    "EVIDENCE_FIELDS",
    "MotherThemeJudge",
    "CuratorAgent",
    "generate_topics",
]
