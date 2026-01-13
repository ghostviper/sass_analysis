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
    user_id: str = None,
    input_tokens: int = 0,
    output_tokens: int = 0
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
            input_tokens=input_tokens if input_tokens else None,
            output_tokens=output_tokens if output_tokens else None,
        )
        
        # 4. 新会话自动生成标题和摘要
        session = await ChatHistoryService.get_session(session_id)
        update_fields = {}
        
        # 生成标题（从用户消息）
        if user_message and (is_new_session or (session and not session.title)):
            title = await ChatHistoryService.generate_title_from_message(user_message)
            update_fields["title"] = title
            print(f"[Persistence] Generated title: {title}")
        
        # 生成摘要（从助手回复）
        if assistant_content and (is_new_session or (session and not session.summary)):
            summary = await ChatHistoryService.generate_summary_from_response(assistant_content)
            if summary:
                update_fields["summary"] = summary
                print(f"[Persistence] Generated summary: {summary[:50]}...")
        
        if update_fields:
            await ChatHistoryService.update_session(session_id, **update_fields)
            
    except Exception as e:
        # 持久化失败只记录日志，不影响用户
        import traceback
        print(f"[Persistence Error] session={session_id}: {e}\n{traceback.format_exc()}")


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
        total_input_tokens = 0
        total_output_tokens = 0
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
                    total_input_tokens = event.input_tokens or 0
                    total_output_tokens = event.output_tokens or 0
                    # 获取 Claude SDK 返回的 session_id，用于后续多轮对话
                    returned_session_id = event.session_id
                    if returned_session_id:
                        print(f"[DEBUG] Got session_id from Claude SDK: {returned_session_id}")
                        # 如果 Claude 返回了不同的 session_id，说明是新会话
                        if returned_session_id != local_session_id:
                            print(f"[DEBUG] Session ID changed: {local_session_id} -> {returned_session_id}, marking as new session")
                            is_new_session = True
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
            
            print(f"[DEBUG] Persist: session_id={local_session_id}, user_id={user_id}, context={context_data}, is_new={is_new_session}")
            
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
                input_tokens=total_input_tokens,
                output_tokens=total_output_tokens,
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

# Category-specific context for generating high-quality prompts
CATEGORY_CONTEXTS = {
    "product": {
        "persona": "indie hacker or solo developer looking to build a profitable SaaS",
        "pain_points": [
            "limited time and resources",
            "need to validate ideas quickly",
            "want to avoid saturated markets",
            "looking for replicable business models",
            "concerned about technical complexity vs revenue potential",
        ],
        "data_available": [
            "revenue data (MRR)",
            "growth rates",
            "technical complexity scores",
            "AI dependency levels",
            "target customer segments",
            "developer suitability scores",
        ],
        "good_examples": [
            "哪些低技术门槛的产品月收入超过5000美元？",
            "有没有不依赖AI但增长稳定的产品？",
            "B2C市场中启动成本最低的产品有哪些？",
            "哪些产品的收入/复杂度比值最高？",
        ],
        "bad_examples": [
            "有哪些SaaS产品？",  # too vague
            "推荐一些产品",  # no specific criteria
            "什么产品好？",  # meaningless
        ],
    },
    "trend": {
        "persona": "entrepreneur or investor analyzing market opportunities",
        "pain_points": [
            "hard to spot emerging trends early",
            "need to distinguish hype from real demand",
            "want to find underserved niches",
            "concerned about market timing",
            "looking for defensible positions",
        ],
        "data_available": [
            "category-level revenue distribution",
            "market concentration (Gini coefficient)",
            "blue ocean vs red ocean classification",
            "growth patterns across segments",
            "revenue standard deviation",
        ],
        "good_examples": [
            "哪些蓝海赛道的中位收入正在上升？",
            "AI工具赛道的竞争集中度如何？",
            "有哪些新兴类目头部玩家还未出现？",
            "哪些垂直市场的基尼系数最低？",
        ],
        "bad_examples": [
            "市场趋势是什么？",  # too broad
            "哪个赛道好？",  # no criteria
            "现在流行什么？",  # vague
        ],
    },
    "career": {
        "persona": "developer or professional considering indie hacking or side projects",
        "pain_points": [
            "unsure which skills translate to product building",
            "balancing day job with side projects",
            "finding the right niche for their background",
            "validating ideas without quitting job",
            "building in public vs stealth mode",
        ],
        "data_available": [
            "successful founder profiles",
            "common tech stacks in profitable products",
            "time-to-profitability patterns",
            "solo vs team success rates",
            "background-to-product-type correlations",
        ],
        "good_examples": [
            "后端开发者最适合做哪类SaaS？",
            "有没有非技术背景成功的案例？",
            "副业做SaaS平均需要多久盈利？",
            "哪些产品类型适合一个人运营？",
        ],
        "bad_examples": [
            "我该做什么？",  # too personal, no context
            "怎么赚钱？",  # too broad
            "独立开发好吗？",  # opinion-based
        ],
    },
    "developer": {
        "persona": "someone researching successful indie hackers and their strategies",
        "pain_points": [
            "want to learn from successful builders",
            "looking for replicable patterns",
            "understanding what separates winners from others",
            "finding mentors or role models",
            "analyzing portfolio strategies",
        ],
        "data_available": [
            "founder revenue rankings",
            "multi-product portfolios",
            "follower-to-revenue ratios",
            "product diversification strategies",
            "growth trajectories over time",
        ],
        "good_examples": [
            "哪些开发者拥有3个以上盈利产品？",
            "粉丝少但收入高的开发者有哪些特点？",
            "收入最高的开发者都做什么类型的产品？",
            "有没有从零到月入万刀的案例分析？",
        ],
        "bad_examples": [
            "谁最厉害？",  # no criteria
            "推荐开发者",  # vague
            "有哪些人？",  # meaningless
        ],
    },
}

# Default fallback prompts per category (high quality)
DEFAULT_PROMPTS = {
    "product": [
        "哪些产品技术复杂度低但月收入超过3000美元？",
        "不依赖AI的成熟期产品有哪些值得参考？",
        "B2D市场中适合独立开发者的产品有哪些？",
        "哪些早期产品的增长率最高？",
    ],
    "trend": [
        "目前哪些蓝海赛道竞争最小？",
        "AI工具类目的市场集中度如何变化？",
        "哪些新兴赛道还没有明显的头部玩家？",
        "收入中位数上涨最快的类目有哪些？",
    ],
    "career": [
        "前端开发背景适合做什么类型的SaaS？",
        "有哪些成功的非全职独立开发案例？",
        "一个人能运营好的产品有什么共同特点？",
        "从副业到全职需要达到什么收入水平？",
    ],
    "developer": [
        "拥有多个盈利产品的开发者有哪些？",
        "低粉丝高收入的开发者是怎么做到的？",
        "月收入最高的独立开发者做什么产品？",
        "有没有值得学习的产品组合策略？",
    ],
}


SUGGEST_SYSTEM_PROMPT = """You are an expert at crafting insightful questions for indie hackers and SaaS entrepreneurs.

Your task: Generate 4 high-quality questions in Chinese for the given category.

## Quality Criteria

GOOD questions are:
- Specific and actionable (include concrete criteria like revenue ranges, complexity levels)
- Data-driven (leverage the available metrics)
- Address real pain points of the target persona
- Lead to actionable insights, not just information

BAD questions are:
- Vague ("有哪些产品？", "什么趋势？")
- Opinion-based without data backing ("哪个好？")
- Too broad to answer meaningfully ("怎么赚钱？")
- Generic advice-seeking ("我该怎么做？")

## Output Format

Return exactly 4 questions, one per line.
No numbering, no bullet points, no explanations.
Each question should be 15-35 Chinese characters.
Questions must be in Chinese.
"""


@router.post("/chat/suggest-prompts", response_model=SuggestPromptsResponse)
async def suggest_prompts(request: SuggestPromptsRequest):
    """
    Generate high-quality suggested prompts for a category using LLM.

    The prompts are designed to:
    1. Address real pain points of indie hackers
    2. Leverage available data dimensions
    3. Be specific and actionable
    4. Avoid vague or generic questions
    """
    category = request.category
    context = CATEGORY_CONTEXTS.get(category)

    if not context:
        return SuggestPromptsResponse(prompts=DEFAULT_PROMPTS.get("product", []))

    api_key = os.getenv("ANTHROPIC_API_KEY")
    base_url = os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com")
    model = os.getenv("ANTHROPIC_MODEL")

    if not api_key or not model:
        return SuggestPromptsResponse(prompts=DEFAULT_PROMPTS.get(category, []))

    # Build a rich user prompt with context
    user_prompt = f"""Category: {category}

Target Persona: {context['persona']}

Their Pain Points:
{chr(10).join(f"- {p}" for p in context['pain_points'])}

Available Data Dimensions:
{chr(10).join(f"- {d}" for d in context['data_available'])}

Examples of GOOD questions:
{chr(10).join(f"- {e}" for e in context['good_examples'])}

Examples of BAD questions (avoid these patterns):
{chr(10).join(f"- {e}" for e in context['bad_examples'])}

Generate 4 new questions that are different from the examples but equally specific and actionable."""

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
                    "max_tokens": 512,
                    "temperature": 0.8,  # Higher temperature for variety
                    "system": SUGGEST_SYSTEM_PROMPT,
                    "messages": [{"role": "user", "content": user_prompt}],
                }
            )

            if response.status_code == 200:
                data = response.json()
                content = data.get("content", [{}])[0].get("text", "")

                # Parse response - filter empty lines and clean up
                prompts = []
                for line in content.split("\n"):
                    line = line.strip()
                    # Skip empty lines and lines that look like formatting
                    if not line or line.startswith("#") or line.startswith("-"):
                        continue
                    # Remove any leading numbers or bullets
                    cleaned = line.lstrip("0123456789.、-) ").strip()
                    if cleaned and len(cleaned) >= 10:  # Minimum reasonable length
                        prompts.append(cleaned)

                if len(prompts) >= 4:
                    return SuggestPromptsResponse(prompts=prompts[:4])
            else:
                print(f"[Suggest Prompts] API returned {response.status_code}: {response.text[:200]}")

            # Fallback to category-specific defaults
            return SuggestPromptsResponse(prompts=DEFAULT_PROMPTS.get(category, []))

    except Exception as e:
        print(f"[Suggest Prompts Error] {type(e).__name__}: {e}")
        return SuggestPromptsResponse(prompts=DEFAULT_PROMPTS.get(category, []))
