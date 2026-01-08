"""
Session Management API Routes - 会话历史管理
"""

from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from services.chat_history import ChatHistoryService

router = APIRouter()


# ============================================================================
# Request/Response Models
# ============================================================================

class SessionCreateRequest(BaseModel):
    session_id: str
    title: Optional[str] = None
    user_id: Optional[str] = None
    enable_web_search: bool = False
    context: Optional[dict] = None


class SessionUpdateRequest(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    is_archived: Optional[bool] = None


class SessionListResponse(BaseModel):
    sessions: List[dict]
    total: int


class SessionDetailResponse(BaseModel):
    session: dict
    messages: List[dict]


class StatsResponse(BaseModel):
    total_sessions: int
    total_messages: int
    total_cost: float


# ============================================================================
# API Endpoints
# ============================================================================

@router.get("/sessions", response_model=SessionListResponse)
async def list_sessions(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    include_archived: bool = Query(False, description="Include archived sessions"),
    limit: int = Query(50, ge=1, le=100, description="Number of sessions to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """
    获取会话列表

    返回用户的所有会话，按更新时间倒序排列。
    """
    sessions = await ChatHistoryService.list_sessions(
        user_id=user_id,
        include_archived=include_archived,
        limit=limit,
        offset=offset
    )

    return SessionListResponse(
        sessions=sessions,
        total=len(sessions)
    )


@router.post("/sessions")
async def create_session(request: SessionCreateRequest):
    """
    创建新会话

    通常由聊天接口自动创建，此接口用于手动创建。
    """
    try:
        session = await ChatHistoryService.create_session(
            session_id=request.session_id,
            title=request.title,
            user_id=request.user_id,
            enable_web_search=request.enable_web_search,
            context=request.context
        )
        return {"success": True, "session": session.to_dict()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """
    获取会话详情

    返回会话信息和所有消息。
    """
    session = await ChatHistoryService.get_session_dict(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = await ChatHistoryService.get_messages(session_id)

    return SessionDetailResponse(
        session=session,
        messages=messages
    )


@router.get("/sessions/{session_id}/messages")
async def get_session_messages(
    session_id: str,
    limit: Optional[int] = Query(None, ge=1, le=500, description="Number of messages to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """
    获取会话消息列表

    支持分页获取消息。
    """
    # 检查会话是否存在
    session = await ChatHistoryService.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = await ChatHistoryService.get_messages(
        session_id=session_id,
        limit=limit,
        offset=offset
    )

    return {
        "session_id": session_id,
        "messages": messages,
        "total": len(messages)
    }


@router.patch("/sessions/{session_id}")
async def update_session(session_id: str, request: SessionUpdateRequest):
    """
    更新会话信息

    可更新标题、摘要、归档状态等。
    """
    success = await ChatHistoryService.update_session(
        session_id=session_id,
        title=request.title,
        summary=request.summary,
        is_archived=request.is_archived
    )

    if not success:
        raise HTTPException(status_code=404, detail="Session not found")

    return {"success": True}


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    hard_delete: bool = Query(False, description="Permanently delete session and messages")
):
    """
    删除会话

    默认软删除，设置 hard_delete=true 永久删除。
    """
    success = await ChatHistoryService.delete_session(
        session_id=session_id,
        hard_delete=hard_delete
    )

    if not success:
        raise HTTPException(status_code=404, detail="Session not found")

    return {"success": True}


@router.post("/sessions/{session_id}/archive")
async def archive_session(session_id: str):
    """归档会话"""
    success = await ChatHistoryService.update_session(
        session_id=session_id,
        is_archived=True
    )

    if not success:
        raise HTTPException(status_code=404, detail="Session not found")

    return {"success": True}


@router.post("/sessions/{session_id}/unarchive")
async def unarchive_session(session_id: str):
    """取消归档会话"""
    success = await ChatHistoryService.update_session(
        session_id=session_id,
        is_archived=False
    )

    if not success:
        raise HTTPException(status_code=404, detail="Session not found")

    return {"success": True}


@router.get("/sessions/stats/overview", response_model=StatsResponse)
async def get_stats():
    """
    获取会话统计信息

    返回总会话数、总消息数、总消耗等。
    """
    stats = await ChatHistoryService.get_session_stats()
    return StatsResponse(**stats)
