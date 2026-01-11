"""
运行数据库迁移的辅助脚本
"""

import sys
from pathlib import Path

# 确保可以导入 backend 模块
sys.path.insert(0, str(Path(__file__).parent))

import asyncio
from migrations.add_checkpoint_id import main

if __name__ == "__main__":
    print("=" * 60)
    print("运行数据库迁移")
    print("=" * 60)
    asyncio.run(main())
    print("\n迁移完成！现在可以使用多轮对话功能了。")
