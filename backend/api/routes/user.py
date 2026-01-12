"""
用户管理 API 路由

提供用户信息管理、会话关联、使用统计等功能
"""

from datetime import datetime
from typing import Optional, List
import os

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from sqlalchemy import text, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from database.db import get_db
from api.routes.auth import get_current_user

router = APIRouter(prefix="/user", tags=["User"])


# ============================================================================
# Pydantic Models
# ============================================================================

class ProfileUpdateRequest(BaseModel):
    name: Optional[str] = None
    image: Optional[str] = None


class PreferencesUpdateRequest(BaseModel):
    locale: Optional[str] = None
    theme: Optional[str] = None
    preferences: Optional[dict] = None


class UsageResponse(BaseModel):
    total_sessions: int
    total_messages: int
    total_tokens: int
    total_cost: float
    daily_chat_used: int
    daily_chat_limit: int


class SessionClaimRequest(BaseModel):
    session_ids: List[str]


class UserSessionResponse(BaseModel):
    session_id: str
    title: Optional[str]
    message_count: int
    created_at: str
    updated_at: str


# ============================================================================
# Profile APIs
# ============================================================================

@router.get("/profile")
async def get_profile(user: dict = Depends(get_current_user)):
    """获取当前用户信息"""
    if not user:
        raise HTTPException(status_code=401, detail="未登录")
    
    return {
        "id": user["id"],
        "email": user["email"],
        "name": user.get("name"),
        "image": user.get("image"),
        "plan": user.get("plan", "free"),
        "emailVerified": user.get("emailVerified", False),
        "createdAt": user.get("createdAt").isoformat() if user.get("createdAt") else None,
    }


@router.put("/profile")
async def update_profile(
    data: ProfileUpdateRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新用户信息"""
    if not user:
        raise HTTPException(status_code=401, detail="未登录")
    
    update_fields = {}
    if data.name is not None:
        update_fields["name"] = data.name
    if data.image is not None:
        update_fields["image"] = data.image
    
    if not update_fields:
        return {"success": True, "message": "无更新内容"}
    
    update_fields['"updatedAt"'] = datetime.utcnow()
    
    # 构建动态 SQL
    set_clause = ", ".join([f'"{k}" = :{k.replace(chr(34), "")}' if '"' in k else f'{k} = :{k}' for k in update_fields.keys()])
    params = {k.replace('"', ''): v for k, v in update_fields.items()}
    params["user_id"] = user["id"]
    
    await db.execute(
        text(f'UPDATE "user" SET {set_clause} WHERE id = :user_id'),
        params
    )
    await db.commit()
    
    return {"success": True}


@router.put("/preferences")
async def update_preferences(
    data: PreferencesUpdateRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新用户偏好设置"""
    if not user:
        raise HTTPException(status_code=401, detail="未登录")
    
    # 目前 user 表没有 preferences 字段，可以扩展
    # 这里先返回成功
    return {"success": True}


# ============================================================================
# Usage & Stats APIs
# ============================================================================

@router.get("/usage", response_model=UsageResponse)
async def get_usage(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取用户使用统计"""
    if not user:
        raise HTTPException(status_code=401, detail="未登录")
    
    user_id = user["id"]
    
    # 查询用户的会话统计
    result = await db.execute(
        text('''
            SELECT 
                COUNT(*) as total_sessions,
                COALESCE(SUM(message_count), 0) as total_messages,
                COALESCE(SUM(total_input_tokens + total_output_tokens), 0) as total_tokens,
                COALESCE(SUM(total_cost), 0) as total_cost
            FROM chat_sessions 
            WHERE user_id = :user_id AND is_deleted = false
        '''),
        {"user_id": user_id}
    )
    stats = result.fetchone()
    
    # 获取今日使用量
    today = datetime.utcnow().date()
    result = await db.execute(
        text('''
            SELECT COUNT(*) as daily_count
            FROM chat_sessions 
            WHERE user_id = :user_id 
              AND DATE(created_at) = :today
              AND is_deleted = false
        '''),
        {"user_id": user_id, "today": today}
    )
    daily_stats = result.fetchone()
    
    # 根据用户计划获取限制
    plan = user.get("plan", "free")
    daily_limit = {
        "free": int(os.getenv("DEFAULT_DAILY_CHAT_LIMIT", "10")),
        "pro": int(os.getenv("PRO_DAILY_CHAT_LIMIT", "100")),
        "enterprise": 999999,
    }.get(plan, 10)
    
    return UsageResponse(
        total_sessions=stats.total_sessions if stats else 0,
        total_messages=int(stats.total_messages) if stats else 0,
        total_tokens=int(stats.total_tokens) if stats else 0,
        total_cost=float(stats.total_cost) if stats else 0.0,
        daily_chat_used=daily_stats.daily_count if daily_stats else 0,
        daily_chat_limit=daily_limit,
    )


# ============================================================================
# Session Management APIs
# ============================================================================

@router.get("/sessions")
async def get_user_sessions(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    include_archived: bool = Query(False)
):
    """获取用户的所有会话"""
    if not user:
        raise HTTPException(status_code=401, detail="未登录")
    
    user_id = user["id"]
    
    query = '''
        SELECT session_id, title, message_count, turn_count, 
               created_at, updated_at, last_message_at, is_archived
        FROM chat_sessions 
        WHERE user_id = :user_id AND is_deleted = false
    '''
    
    if not include_archived:
        query += ' AND is_archived = false'
    
    query += ' ORDER BY updated_at DESC LIMIT :limit OFFSET :offset'
    
    result = await db.execute(
        text(query),
        {"user_id": user_id, "limit": limit, "offset": offset}
    )
    sessions = result.fetchall()
    
    return {
        "sessions": [
            {
                "session_id": s.session_id,
                "title": s.title,
                "message_count": s.message_count,
                "turn_count": s.turn_count,
                "created_at": s.created_at.isoformat() if s.created_at else None,
                "updated_at": s.updated_at.isoformat() if s.updated_at else None,
                "last_message_at": s.last_message_at.isoformat() if s.last_message_at else None,
                "is_archived": s.is_archived,
            }
            for s in sessions
        ],
        "total": len(sessions)
    }


@router.post("/sessions/claim")
async def claim_sessions(
    data: SessionClaimRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    认领匿名会话
    
    将指定的匿名会话（user_id 为空）关联到当前用户
    """
    if not user:
        raise HTTPException(status_code=401, detail="未登录")
    
    user_id = user["id"]
    session_ids = data.session_ids
    
    if not session_ids:
        return {"success": True, "claimed": 0}
    
    # 只认领 user_id 为空的会话
    result = await db.execute(
        text('''
            UPDATE chat_sessions 
            SET user_id = :user_id, updated_at = :now
            WHERE session_id = ANY(:session_ids) 
              AND (user_id IS NULL OR user_id = '')
              AND is_deleted = false
        '''),
        {
            "user_id": user_id,
            "session_ids": session_ids,
            "now": datetime.utcnow()
        }
    )
    await db.commit()
    
    return {"success": True, "claimed": result.rowcount}


@router.post("/sessions/{session_id}/transfer")
async def transfer_session(
    session_id: str,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    将当前会话转移到用户名下
    
    用于登录后自动关联当前正在进行的会话
    """
    if not user:
        raise HTTPException(status_code=401, detail="未登录")
    
    user_id = user["id"]
    
    # 检查会话是否存在且未被其他用户占用
    result = await db.execute(
        text('''
            SELECT user_id FROM chat_sessions 
            WHERE session_id = :session_id AND is_deleted = false
        '''),
        {"session_id": session_id}
    )
    session = result.fetchone()
    
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    # 如果会话已有其他用户，不允许转移
    if session.user_id and session.user_id != user_id:
        raise HTTPException(status_code=403, detail="无权操作此会话")
    
    # 转移会话
    await db.execute(
        text('''
            UPDATE chat_sessions 
            SET user_id = :user_id, updated_at = :now
            WHERE session_id = :session_id
        '''),
        {
            "user_id": user_id,
            "session_id": session_id,
            "now": datetime.utcnow()
        }
    )
    await db.commit()
    
    return {"success": True}


# ============================================================================
# Account Management APIs
# ============================================================================

@router.delete("/account")
async def delete_account(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    删除用户账户
    
    这将删除用户的所有数据，包括：
    - 用户信息
    - 关联的账户（OAuth）
    - 聊天会话和消息
    """
    if not user:
        raise HTTPException(status_code=401, detail="未登录")
    
    user_id = user["id"]
    
    # 1. 删除聊天消息
    await db.execute(
        text('''
            DELETE FROM chat_messages 
            WHERE session_id IN (
                SELECT session_id FROM chat_sessions WHERE user_id = :user_id
            )
        '''),
        {"user_id": user_id}
    )
    
    # 2. 删除聊天会话
    await db.execute(
        text('DELETE FROM chat_sessions WHERE user_id = :user_id'),
        {"user_id": user_id}
    )
    
    # 3. 删除账户关联
    await db.execute(
        text('DELETE FROM account WHERE "userId" = :user_id'),
        {"user_id": user_id}
    )
    
    # 4. 删除用户
    await db.execute(
        text('DELETE FROM "user" WHERE id = :user_id'),
        {"user_id": user_id}
    )
    
    await db.commit()
    
    return {"success": True, "message": "账户已删除"}
