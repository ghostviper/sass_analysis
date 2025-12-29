"""
统一日志配置模块
"""
import logging
from pathlib import Path
from datetime import datetime


def setup_logging(log_level: str = "INFO", log_dir: Path = None):
    """
    配置统一的日志记录

    Args:
        log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
        log_dir: 日志目录路径，默认为 backend/logs/

    Returns:
        日志文件路径
    """
    if log_dir is None:
        log_dir = Path(__file__).parent / 'logs'

    log_dir.mkdir(exist_ok=True)

    log_file = log_dir / f"sass_analysis_{datetime.now().strftime('%Y%m%d')}.log"

    # 文件处理器格式（详细）
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 控制台处理器格式（简洁）
    console_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )

    # 文件处理器
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)

    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    console_handler.setFormatter(console_formatter)

    # 配置根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # 清除已有的处理器（避免重复）
    root_logger.handlers.clear()

    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    return log_file


def get_logger(name: str) -> logging.Logger:
    """获取指定名称的日志器"""
    return logging.getLogger(name)
