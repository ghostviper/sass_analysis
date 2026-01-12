"""
Chat API Routes - AI-powered Q&A for BuildWhat

Lightweight streaming implementation for smooth AI responses.
Integrates with ChatHistoryService for session persistence.
Supports user association and quota management.
"""

import json
import asyncio
import uuid
import time
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import httpx
import os

from agent.client import SaaSAnalysisAgent, StreamEvent
from services.chat_history import ChatHistoryService
from api.routes.auth import get_current_user, decode_token

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


class SuggestPromptsRequest(BaseModel):
    category: str  # "product", "trend", "career", "developer"


class SuggestPromptsResponse(BaseModel):
    prompts: List[str]


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
async def chat(request: ChatRequest, req: Request):
    """
    Standard chat endpoint (non-streaming).

    Processes user questions about SaaS startups, market trends, and analysis.
    Claude Agent will automatically call appropriate tools to query data.
    Supports multi-turn conversations via session_id.

    Args:
        request: ChatRequest with message and optional session_id

    Returns:
        ChatResponse with complete AI response and session_id
    """
    # 尝试获取当前用户（可选）
    user_id = None
    token = req.cookies.get("auth_token")
    if token:
        user_id = decode_token(token)
    
    try:
        agent = get_agent()

        if not agent:
            return ChatResponse(
                response="请在 .env 文件中配置 ANTHROPIC_API_KEY 以启用 AI 分析功能。",
                session_id=None,
                sources=None
            )

        # Generate or use provided session_id
        session_id = request.session_id or str(uuid.uuid4())
        is_new_session = not request.session_id
        start_time = time.time()
        model_used = os.getenv("ANTHROPIC_MODEL", "claude")

        # Collect response (no DB operations during streaming)
        response_parts = []
        tool_calls = []
        total_cost = 0.0
        result_session_id = session_id

        async for event in agent.query_stream_events(
            request.message,
            session_id=session_id,
            enable_web_search=request.enable_web_search,
            context=request.context
        ):
            if event.type == "block_delta" and event.block_type == "text":
                response_parts.append(event.content)
            elif event.type == "tool_start":
                tool_calls.append({
                    "name": event.tool_name,
                    "input": event.tool_input,
                    "output": None,
                    "duration_ms": None
                })
            elif event.type == "tool_end":
                for tc in reversed(tool_calls):
                    if tc["name"] == event.tool_name and tc["output"] is None:
                        tc["output"] = event.tool_result[:500] if event.tool_result else None
                        break
            elif event.type == "done":
                total_cost = event.cost or 0.0
                if event.session_id:
                    result_session_id = event.session_id

        response_content = ''.join(response_parts)
        duration_ms = int((time.time() - start_time) * 1000)

        # 异步后台持久化
        context_data = {
            "type": request.context.get("type") if request.context else None,
            "value": request.context.get("value") if request.context else None,
            "products": request.context.get("products") if request.context else None,
        } if request.context else None
        
        asyncio.create_task(_persist_chat_async(
            session_id=session_id,
            user_message=request.message,
            assistant_content=response_content,
            tool_calls=tool_calls,
            cost=total_cost,
            model=model_used,
            duration_ms=duration_ms,
            is_new_session=is_new_session,
            context=context_data,
            enable_web_search=request.enable_web_search,
            user_id=user_id,
        ))

        return ChatResponse(
            response=response_content,
            session_id=result_session_id,
            sources=None
        )

    except Exception as e:
        import traceback
        error_detail = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
        print(f"[Chat Error] {error_detail}")
        raise HTTPException(status_code=500, detail=error_detail)


async def _persist_chat_async(
    session_id: str,
    user_message: str,
    assistant_content: str,
    tool_calls: list,
    cost: float,
    model: str,
    duration_ms: int,
    is_new_session: bool,
    context: dict = None,
    enable_web_search: bool = False,
    user_id: str = None  # 新增：用户ID
):
    """
    异步持久化聊天记录（后台任务，不阻塞响应）
    
    流式完成后调用，所有数据库操作在这里执行
    """
    try:
        # 1. 确保会话存在
        await ChatHistoryService.ensure_session_exists(
            session_id=session_id,
            user_id=user_id,  # 传入用户ID
            enable_web_search=enable_web_search,
            context=context
        )
        
        # 2. 保存用户消息
        await ChatHistoryService.add_message(
            session_id=session_id,
            role="user",
            content=user_message,
        )
        
        # 3. 保存助手消息
        await ChatHistoryService.add_message(
            session_id=session_id,
            role="assistant",
            content=assistant_content,
            tool_calls=tool_calls if tool_calls else None,
            cost=cost,
            model=model,
            duration_ms=duration_ms,
        )
        
        # 4. 新会话自动生成标题
        if is_new_session and user_message:
            title = await ChatHistoryService.generate_title_from_message(user_message)
            await ChatHistoryService.update_session(session_id, title=title)
            
    except Exception as e:
        # 持久化失败只记录日志，不影响用户
        print(f"[Persistence Error] session={session_id}: {e}")


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest, req: Request):
    """
    Streaming chat endpoint with Server-Sent Events (SSE).

    多轮对话说明：
    - 首次对话：不传 session_id
    - 后续对话：传入上次返回的 claude_session_id（来自 done 事件）
    - Claude SDK 会自动恢复会话上下文

    Args:
        request: ChatRequest with message and optional session_id

    Returns:
        StreamingResponse with SSE events
    """
    # 尝试获取当前用户（可选）
    user_id = None
    token = req.cookies.get("auth_token")
    if token:
        user_id = decode_token(token)
    
    # 使用请求中的 session_id（如果有的话，这是 Claude SDK 的 session_id）
    claude_session_id = request.session_id  # 可能为 None（新会话）
    
    # 生成一个本地 session_id 用于数据库存储
    local_session_id = request.session_id or str(uuid.uuid4())
    is_new_session = not request.session_id

    async def generate():
        """Generator function for SSE streaming"""
        nonlocal claude_session_id, local_session_id, is_new_session, user_id
        
        # 内存累积变量（流式过程中不做任何 DB 操作）
        start_time = time.time()
        accumulated_content = ""
        tool_calls = []
        total_cost = 0.0
        returned_session_id = None  # Claude SDK 返回的 session_id
        model_used = os.getenv("ANTHROPIC_MODEL", "claude")

        try:
            agent = get_agent()

            if not agent:
                yield f"data: {json.dumps({'type': 'error', 'content': '请在 .env 文件中配置 ANTHROPIC_API_KEY 以启用 AI 分析功能。'}, ensure_ascii=False)}\n\n"
                yield "data: [DONE]\n\n"
                return

            # 流式响应 - 传入 Claude session_id 用于恢复会话
            async for event in agent.query_stream_events(
                request.message,
                session_id=claude_session_id,  # 传入 Claude SDK 的 session_id
                enable_web_search=request.enable_web_search,
                context=request.context
            ):
                # 内存累积（无 IO）
                if event.type == "block_delta" and event.block_type == "text":
                    accumulated_content += event.content
                elif event.type == "tool_start":
                    tool_calls.append({
                        "name": event.tool_name,
                        "input": event.tool_input,
                        "output": None,
                        "duration_ms": None
                    })
                elif event.type == "tool_end":
                    for tc in reversed(tool_calls):
                        if tc["name"] == event.tool_name and tc["output"] is None:
                            tc["output"] = event.tool_result[:500] if event.tool_result else None
                            break
                elif event.type == "done":
                    total_cost = event.cost or 0.0
                    # 获取 Claude SDK 返回的 session_id，用于后续多轮对话
                    returned_session_id = event.session_id
                    if returned_session_id:
                        print(f"[DEBUG] Got session_id from Claude SDK: {returned_session_id}")
                        # 更新 local_session_id 为 Claude 返回的 session_id
                        local_session_id = returned_session_id

                # 立即输出事件
                event_data = json.dumps(event.to_dict(), ensure_ascii=False)
                yield f"data: {event_data}\n\n"

            # 先发送完成信号，再异步持久化
            yield "data: [DONE]\n\n"
            
            # 异步后台持久化（不阻塞响应）
            duration_ms = int((time.time() - start_time) * 1000)
            context_data = {
                "type": request.context.get("type") if request.context else None,
                "value": request.context.get("value") if request.context else None,
                "products": request.context.get("products") if request.context else None,
            } if request.context else None
            
            asyncio.create_task(_persist_chat_async(
                session_id=local_session_id,
                user_message=request.message,
                assistant_content=accumulated_content,
                tool_calls=tool_calls,
                cost=total_cost,
                model=model_used,
                duration_ms=duration_ms,
                is_new_session=is_new_session,
                context=context_data,
                enable_web_search=request.enable_web_search,
                user_id=user_id,
            ))

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


# ============================================================================
# Prompt Suggestion API
# ============================================================================

# Category descriptions for prompt generation
CATEGORY_PROMPTS = {
    "product": "SaaS产品分析、产品对比、功能评估、定价策略、竞品分析",
    "trend": "市场趋势、行业动态、技术发展、投资热点、增长预测",
    "career": "职业发展、技能提升、创业建议、行业转型、个人成长",
    "developer": "开发者工具、技术栈选择、开源项目、编程效率、技术学习",
}


@router.post("/chat/suggest-prompts", response_model=SuggestPromptsResponse)
async def suggest_prompts(request: SuggestPromptsRequest):
    """
    Generate suggested prompts for a category using LLM.
    
    Args:
        request: SuggestPromptsRequest with category
        
    Returns:
        SuggestPromptsResponse with list of 4 prompts
    """
    category_desc = CATEGORY_PROMPTS.get(request.category, "通用问题")
    
    system_prompt = """你是一个SaaS行业分析助手。请根据给定的类别生成4个有价值的问题建议。
要求：
1. 问题要具体、有深度、有实用价值
2. 问题要与SaaS行业、创业、产品分析相关
3. 每个问题控制在30字以内
4. 直接返回4个问题，每行一个，不要编号或其他格式"""

    user_prompt = f"请为「{category_desc}」类别生成4个有价值的问题建议。"
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    base_url = os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com")
    model = os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307")
    
    if not api_key:
        # Return default prompts if no API key
        return SuggestPromptsResponse(prompts=[
            "有哪些值得关注的SaaS产品？",
            "当前市场有什么新趋势？",
            "如何评估一个SaaS产品的潜力？",
            "有什么推荐的开发者工具？",
        ])
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{base_url}/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": model,
                    "max_tokens": 256,
                    "system": system_prompt,
                    "messages": [{"role": "user", "content": user_prompt}],
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("content", [{}])[0].get("text", "")
                # Parse the response - split by newlines and filter empty lines
                prompts = [line.strip() for line in content.split("\n") if line.strip()]
                # Take first 4 prompts
                prompts = prompts[:4]
                if len(prompts) >= 4:
                    return SuggestPromptsResponse(prompts=prompts)
            
            # Fallback to defaults
            return SuggestPromptsResponse(prompts=[
                "有哪些值得关注的SaaS产品？",
                "当前市场有什么新趋势？",
                "如何评估一个SaaS产品的潜力？",
                "有什么推荐的开发者工具？",
            ])
            
    except Exception as e:
        print(f"[Suggest Prompts Error] {e}")
        return SuggestPromptsResponse(prompts=[
            "有哪些值得关注的SaaS产品？",
            "当前市场有什么新趋势？",
            "如何评估一个SaaS产品的潜力？",
            "有什么推荐的开发者工具？",
        ])
