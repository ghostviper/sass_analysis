"""
Chat API Routes - AI-powered Q&A for BuildWhat

Lightweight streaming implementation for smooth AI responses.
"""

import json
import asyncio
import time
import uuid
from typing import Optional, List
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from agent.client import SaaSAnalysisAgent, StreamEvent

router = APIRouter()


# ============================================================================
# Request/Response Models
# ============================================================================

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None  # Session ID for multi-turn conversations
    history: Optional[List[ChatMessage]] = []  # Legacy field, kept for compatibility
    channels: Optional[List[str]] = None  # Selected channels for search (e.g., ["reddit", "google"])
    context: Optional[dict] = None  # Additional context (product info, URLs, etc.)
    enable_web_search: bool = False  # Enable web search capability


class ChatResponse(BaseModel):
    response: str
    session_id: Optional[str] = None  # Return session_id for client to track
    sources: Optional[List[dict]] = None


# ============================================================================
# Agent Instance Management
# ============================================================================

# Global agent instance (lazy loaded)
_agent_instance = None


def get_agent() -> Optional[SaaSAnalysisAgent]:
    """
    Get or create the SaaS Analysis Agent instance.

    Returns:
        SaaSAnalysisAgent instance or None if API key not configured
    """
    global _agent_instance

    if _agent_instance is None:
        try:
            _agent_instance = SaaSAnalysisAgent()
        except ValueError as e:
            # API key not configured
            print(f"[Agent Init Error] {e}")
            return None
        except Exception as e:
            # Other initialization errors
            print(f"[Agent Init Error] {type(e).__name__}: {e}")
            return None

    return _agent_instance


# ============================================================================
# API Endpoints
# ============================================================================

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Standard chat endpoint (non-streaming).

    Processes user questions about SaaS startups, market trends, and analysis.
    Claude Agent will automatically call appropriate tools to query data.
    Supports multi-turn conversations via session_id.

    Args:
        request: ChatRequest with message and optional session_id

    Returns:
        ChatResponse with complete AI response and session_id

    Example:
        POST /api/chat
        {
            "message": "分析 AI 赛道的趋势",
            "session_id": null
        }
    """
    try:
        agent = get_agent()

        if not agent:
            return ChatResponse(
                response="请在 .env 文件中配置 ANTHROPIC_API_KEY 以启用 AI 分析功能。",
                session_id=None,
                sources=None
            )

        # Collect complete response from stream
        response_parts = []
        result_session_id = request.session_id

        async for event in agent.query_stream_events(
            request.message,
            session_id=request.session_id,
            enable_web_search=request.enable_web_search,
            context=request.context
        ):
            if event.type == "text":
                response_parts.append(event.content)
            elif event.type == "done" and event.session_id:
                result_session_id = event.session_id

        return ChatResponse(
            response=''.join(response_parts),
            session_id=result_session_id,
            sources=None
        )

    except Exception as e:
        import traceback
        error_detail = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
        print(f"[Chat Error] {error_detail}")
        raise HTTPException(status_code=500, detail=error_detail)


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Streaming chat endpoint with Server-Sent Events (SSE).

    Lightweight version - no persistence during streaming to ensure smooth output.
    Session persistence is handled separately if needed.

    Args:
        request: ChatRequest with message and optional session_id

    Returns:
        StreamingResponse with SSE events
    """
    async def generate():
        """Generator function for SSE streaming"""
        # Generate session_id if not provided
        session_id = request.session_id or str(uuid.uuid4())

        try:
            agent = get_agent()

            if not agent:
                yield f"data: {json.dumps({'type': 'error', 'content': '请在 .env 文件中配置 ANTHROPIC_API_KEY 以启用 AI 分析功能。'}, ensure_ascii=False)}\n\n"
                yield "data: [DONE]\n\n"
                return

            # Stream response directly without any persistence
            async for event in agent.query_stream_events(
                request.message,
                session_id=session_id,
                enable_web_search=request.enable_web_search,
                context=request.context
            ):
                # Override session_id in done event
                if event.type == "done":
                    event = StreamEvent(
                        type="done",
                        layer="primary",
                        cost=event.cost,
                        session_id=session_id
                    )

                # Format as SSE event
                event_data = json.dumps(event.to_dict(), ensure_ascii=False)
                yield f"data: {event_data}\n\n"

            # Signal completion
            yield "data: [DONE]\n\n"

        except Exception as e:
            import traceback
            error_detail = f"{type(e).__name__}: {str(e)}"
            print(f"[Stream Error] {error_detail}\n{traceback.format_exc()}")
            error_data = json.dumps({'type': 'error', 'layer': 'primary', 'content': error_detail}, ensure_ascii=False)
            yield f"data: {error_data}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Content-Type": "text/event-stream",
        }
    )


@router.get("/chat/test-stream")
async def test_stream():
    """
    Test endpoint to verify SSE streaming works on Windows.

    This sends 10 messages with 500ms delays to verify streaming.
    If this works but /chat/stream doesn't, the issue is in Claude Agent SDK.
    """
    async def generate():
        for i in range(10):
            msg = {"type": "text", "content": f"测试消息 {i+1}/10... "}
            yield f"data: {json.dumps(msg, ensure_ascii=False)}\n\n"
            # Force flush by yielding empty and sleeping
            await asyncio.sleep(0.5)

        yield f"data: {json.dumps({'type': 'done'})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Content-Type": "text/event-stream",
        }
    )


@router.post("/chat/stream-debug")
async def chat_stream_debug(request: ChatRequest):
    """
    Debug version of streaming endpoint with console output.
    Supports multi-turn conversations via session_id.
    """
    async def generate():
        try:
            print(f"\n[DEBUG] Starting stream for: {request.message[:50]}...", flush=True)
            print(f"[DEBUG] Session ID: {request.session_id}", flush=True)

            agent = get_agent()
            if not agent:
                yield f"data: {json.dumps({'type': 'error', 'content': 'Agent not configured'}, ensure_ascii=False)}\n\n"
                yield "data: [DONE]\n\n"
                return

            event_count = 0
            async for event in agent.query_stream_events(
                request.message,
                session_id=request.session_id,
                enable_web_search=request.enable_web_search,
                context=request.context
            ):
                event_count += 1
                event_dict = event.to_dict()
                print(f"[DEBUG] Event #{event_count}: {event.type} - {str(event_dict)[:100]}...", flush=True)

                # Yield the event
                event_data = json.dumps(event_dict, ensure_ascii=False)
                yield f"data: {event_data}\n\n"

                # Small delay to help with buffering
                await asyncio.sleep(0.01)

            print(f"[DEBUG] Stream complete. Total events: {event_count}", flush=True)
            yield "data: [DONE]\n\n"

        except Exception as e:
            import traceback
            error_detail = f"{type(e).__name__}: {str(e)}"
            print(f"[DEBUG ERROR] {error_detail}\n{traceback.format_exc()}", flush=True)
            yield f"data: {json.dumps({'type': 'error', 'content': error_detail}, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Content-Type": "text/event-stream",
        }
    )
