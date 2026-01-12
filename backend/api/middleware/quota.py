"""
配额检查中间件

检查用户的对话配额，限制免费用户的使用次数
"""

import os
from datetime import datetime
from typing import Optional

from fastapi import HTTPException, Depends, Request
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from database.db import get_db
from api.routes.auth import get_current_user, decode_token


# 配额配置
PLAN_LIMITS = {
    "free": int(os.getenv("FREE_DAILY_CHAT_LIMIT", "10")),
    "pro": int(os.getenv("PRO_DAILY_CHAT_LIMIT", "100")),
    "enterprise": 999999,  # 无限制
}


class QuotaExceededError(HTTPException):
    """配额超限异常"""
    def __init__(self, plan: str, limit: int, used: int):
        super().__init__(
            status_code=429,
            detail={
                "error": "quota_exceeded",
                "message": f"您今日的对话次数已用完 ({used}/{limit})",
                "plan": plan,
                "limit": limit,
                "used": used,
                "upgrade_url": "/settings/billing"
            }
        )


async def get_user_quota(
    user_id: str,
    plan: str,
    db: AsyncSession
) -> dict:
    """
    获取用户配额信息
    
    Returns:
        {
            "limit": 每日限制,
            "used": 今日已用,
            "remaining": 剩余次数,
            "can_chat": 是否可以继续对话
        }
    """
    limit = PLAN_LIMITS.get(plan, PLAN_LIMITS["free"])
    
    # 查询今日使用量
    today = datetime.utcnow().date()
    result = await db.execute(
        text('''
            SELECT COUNT(*) as count
            FROM chat_sessions 
            WHERE user_id = :user_id 
              AND DATE(created_at) = :today
              AND is_deleted = false
        '''),
        {"user_id": user_id, "today": today}
    )
    row = result.fetchone()
    used = row.count if row else 0
    
    return {
        "limit": limit,
        "used": used,
        "remaining": max(0, limit - used),
        "can_chat": used < limit
    }


async def check_chat_quota(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Optional[dict]:
    """
    检查用户对话配额的依赖项
    
    用法:
        @router.post("/chat")
        async def chat(
            request: ChatRequest,
            quota: dict = Depends(check_chat_quota)
        ):
            # quota 包含用户配额信息
            pass
    
    Returns:
        配额信息字典，如果用户未登录则返回 None（允许匿名用户）
    
    Raises:
        QuotaExceededError: 如果配额已用完
    """
    # 尝试获取用户
    token = request.cookies.get("auth_token")
    if not token:
        # 匿名用户，不检查配额（可以根据需求修改）
        return None
    
    user_id = decode_token(token)
    if not user_id:
        return None
    
    # 查询用户信息
    result = await db.execute(
        text('SELECT id, plan FROM "user" WHERE id = :id'),
        {"id": user_id}
    )
    user = result.fetchone()
    
    if not user:
        return None
    
    plan = user.plan or "free"
    quota = await get_user_quota(user_id, plan, db)
    
    # 检查配额
    if not quota["can_chat"]:
        raise QuotaExceededError(plan, quota["limit"], quota["used"])
    
    return {
        "user_id": user_id,
        "plan": plan,
        **quota
    }


async def increment_usage(user_id: str, db: AsyncSession):
    """
    增加用户使用计数
    
    注意：这个函数应该在会话创建成功后调用
    由于 chat_sessions 表已经记录了创建时间，
    实际上不需要额外的计数器，直接查询即可
    """
    # 当前实现中，使用量是通过查询 chat_sessions 表计算的
    # 所以不需要额外的增量操作
    pass
