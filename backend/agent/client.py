"""
Claude Agent SDK client wrapper for SaaS Analysis

Supports multi-turn conversations with session management.
"""

import os
import sys
import asyncio
import time
from typing import AsyncIterator, Optional, Dict, Any, List
from dataclasses import dataclass, field

# Ensure ProactorEventLoopPolicy on Windows for subprocess (Claude CLI)
if sys.platform == "win32":
    try:
        policy = asyncio.get_event_loop_policy()
        if not isinstance(policy, asyncio.WindowsProactorEventLoopPolicy):
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    except Exception:
        pass

from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    create_sdk_mcp_server,
    # Message types
    UserMessage,
    AssistantMessage,
    SystemMessage,
    ResultMessage,
    # Content block types
    TextBlock,
    ThinkingBlock,
    ToolUseBlock,
    ToolResultBlock,
)


@dataclass
class StreamEvent:
    """Represents a streaming event for the frontend."""
    type: str  # "text", "tool_start", "tool_end", "thinking", "status", "done"
    content: str = ""
    tool_name: str = ""
    tool_input: Dict[str, Any] = None
    tool_result: str = ""
    cost: float = 0.0
    session_id: str = ""  # Return session_id for frontend to track

    def to_dict(self) -> Dict[str, Any]:
        result = {"type": self.type}
        if self.content:
            result["content"] = self.content
        if self.tool_name:
            result["tool_name"] = self.tool_name
        if self.tool_input:
            result["tool_input"] = self.tool_input
        if self.tool_result:
            result["tool_result"] = self.tool_result
        if self.cost > 0:
            result["cost"] = self.cost
        if self.session_id:
            result["session_id"] = self.session_id
        return result


@dataclass
class ChatMessage:
    """Represents a chat message for history."""
    role: str  # "user" or "assistant"
    content: str


@dataclass
class SessionInfo:
    """Tracks session state and metadata.

    Note: We store session_id instead of client because:
    1. ClaudeSDKClient is closed after each query's context manager exits
    2. The SDK's `resume` parameter uses session_id to restore conversation context
    3. This follows the official SDK pattern for multi-turn conversations
    """
    session_id: str  # Backend session ID for resuming conversations
    created_at: float
    last_used_at: float
    turn_count: int = 0
    total_cost: float = 0.0

from .tools import (
    query_startups_tool,
    get_category_analysis_tool,
    get_trend_report_tool,
    get_leaderboard_tool,
)
from .prompts import SYSTEM_PROMPT


def _create_mcp_server():
    """Create a fresh MCP server instance.

    NOTE: MCP servers should be created fresh for each client session
    to avoid state issues with reused server instances.
    """
    return create_sdk_mcp_server(
        name="saas_analysis",
        version="1.0.0",
        tools=[
            query_startups_tool,
            get_category_analysis_tool,
            get_trend_report_tool,
            get_leaderboard_tool,
        ]
    )


class SaaSAnalysisAgent:
    """
    Claude Agent SDK client wrapper for SaaS Analysis.

    Provides streaming query capabilities with access to custom MCP tools
    for querying startups, analyzing categories, and generating trend reports.

    Supports multi-turn conversations with session management.
    """

    def __init__(self):
        """Initialize the SaaS Analysis Agent with Claude SDK"""
        # Get API configuration from environment
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.base_url = os.getenv("ANTHROPIC_BASE_URL")  # Optional for third-party endpoints
        self.model = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5")
        self.cli_path = os.getenv("CLAUDE_CLI_PATH")  # Optional: custom CLI path
        self.debug_stream = os.getenv("DEBUG_STREAM", "0") == "1"

        # Session management configuration
        self.max_turns = int(os.getenv("CLAUDE_MAX_TURNS", "10"))  # Max conversation turns
        self.session_timeout = int(os.getenv("CLAUDE_SESSION_TIMEOUT", "1800"))  # 30 minutes

        # Session storage: session_id -> SessionInfo
        self._sessions: Dict[str, SessionInfo] = {}

        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")

        # Build environment variables for Claude CLI
        self._env = {
            "ANTHROPIC_API_KEY": self.api_key,
            # Force Node.js to use unbuffered stdout (may help streaming on Windows)
            "NODE_OPTIONS": "--no-warnings",
            "FORCE_COLOR": "0",  # Disable color output which can cause buffering
        }
        if self.base_url:
            self._env["ANTHROPIC_BASE_URL"] = self.base_url

        # Pass proxy settings if configured (both upper and lower case for compatibility)
        http_proxy = os.getenv("HTTP_PROXY")
        https_proxy = os.getenv("HTTPS_PROXY")
        if http_proxy:
            self._env["HTTP_PROXY"] = http_proxy
            self._env["http_proxy"] = http_proxy
        if https_proxy:
            self._env["HTTPS_PROXY"] = https_proxy
            self._env["https_proxy"] = https_proxy

        # Short system prompt
        self._system_prompt = (
            "You are a SaaS industry analyst. Use the available tools to query startup data, "
            "analyze categories, and generate trend reports. Respond in the user's language."
        )

        # Query lock to serialize requests (only one query at a time)
        self._query_lock = asyncio.Lock()

    def _create_options(self, resume: Optional[str] = None) -> ClaudeAgentOptions:
        """Create ClaudeAgentOptions for a query.

        Args:
            resume: Optional session ID to resume a previous conversation
        """
        # Create a fresh MCP server for each session to avoid state issues
        mcp_server = _create_mcp_server()

        options_kwargs = {
            "mcp_servers": {"saas": mcp_server},
            "allowed_tools": [
                "mcp__saas__query_startups",
                "mcp__saas__get_category_analysis",
                "mcp__saas__get_trend_report",
                "mcp__saas__get_leaderboard",
            ],
            "system_prompt": self._system_prompt,
            "model": self.model,
            "env": self._env,
            "include_partial_messages": True,  # Always enable streaming
            "accumulate_streaming_content": True,  # Let SDK accumulate deltas into TextBlock
            "max_turns": self.max_turns,  # Configurable conversation limit
        }

        # Add cli_path only if specified
        if self.cli_path:
            options_kwargs["cli_path"] = self.cli_path

        # Add resume parameter for multi-turn conversations
        if resume:
            options_kwargs["resume"] = resume

        return ClaudeAgentOptions(**options_kwargs)

    def _generate_session_id(self) -> str:
        """Generate a unique session ID."""
        import uuid
        return str(uuid.uuid4())

    def _cleanup_expired_sessions(self) -> None:
        """Remove sessions that have exceeded the timeout."""
        current_time = time.time()
        expired = [
            sid for sid, info in self._sessions.items()
            if current_time - info.last_used_at > self.session_timeout
        ]
        for sid in expired:
            if self.debug_stream:
                print(f"[Agent] Cleaning up expired session: {sid}", flush=True)
            del self._sessions[sid]

    def get_session_info(self, session_id: str) -> Optional[SessionInfo]:
        """Get session info by ID, returns None if not found or expired."""
        self._cleanup_expired_sessions()
        return self._sessions.get(session_id)

    async def query_stream(
        self,
        message: str,
        session_id: Optional[str] = None
    ) -> AsyncIterator[str]:
        """
        Stream a query to Claude and yield text responses.

        Args:
            message: User's question or request
            session_id: Optional session ID for multi-turn conversations

        Yields:
            Text chunks from Claude's response

        Example:
            async for chunk in agent.query_stream("分析 AI 赛道"):
                print(chunk, end="", flush=True)
        """
        async for event in self.query_stream_events(message, session_id=session_id):
            if event.type == "text":
                yield event.content

    async def query_stream_events(
        self,
        message: str,
        session_id: Optional[str] = None
    ) -> AsyncIterator[StreamEvent]:
        """
        Stream a query to Claude and yield detailed events including tool usage.

        This method provides full visibility into the agent's actions:
        - text: Text content from Claude's response (streaming)
        - tool_start: When a tool is being called
        - tool_end: When a tool returns results
        - done: Query completed with cost info and session_id

        Args:
            message: User's question or request
            session_id: Optional session ID for multi-turn conversations.
                       If None, creates a new session. If provided, resumes the session.

        Yields:
            StreamEvent objects with detailed information

        Example:
            async for event in agent.query_stream_events("分析 AI 赛道"):
                if event.type == "text":
                    print(event.content, end="", flush=True)
                elif event.type == "tool_start":
                    print(f"\\n[调用工具: {event.tool_name}]")
                elif event.type == "done":
                    print(f"\\nSession: {event.session_id}")
        """
        # Cleanup expired sessions first
        self._cleanup_expired_sessions()

        # Track tool usage to avoid duplicate events
        active_tools = {}
        # Track text we've already sent to avoid duplicates
        sent_text_length = 0  # persists across messages when accumulate_streaming_content=True

        # Determine if resuming or creating new session
        resume_session = None
        if session_id and session_id in self._sessions:
            session_info = self._sessions[session_id]
            # Check if we've exceeded max turns
            if session_info.turn_count >= self.max_turns:
                yield StreamEvent(
                    type="status",
                    content=f"会话已达到最大轮数 ({self.max_turns})，开始新会话..."
                )
                # Create new session instead
                session_id = self._generate_session_id()
            else:
                resume_session = session_id
                if self.debug_stream:
                    print(f"[Agent] Resuming session {session_id}, turn {session_info.turn_count + 1}", flush=True)
        elif session_id:
            # Session ID provided but not found (expired or invalid)
            yield StreamEvent(
                type="status",
                content="会话已过期，开始新会话..."
            )
            session_id = self._generate_session_id()
        else:
            # No session ID provided, create new
            session_id = self._generate_session_id()

        # Status heartbeat so frontend立即有反馈
        if self._query_lock.locked():
            yield StreamEvent(type="status", content="等待可用的 Claude 连接...")
        else:
            status_msg = "正在继续对话..." if resume_session else "正在初始化 Claude 连接..."
            yield StreamEvent(type="status", content=status_msg)

        start_time = asyncio.get_event_loop().time()

        def _t(msg: str) -> None:
            """Debug timing helper."""
            if self.debug_stream:
                elapsed = asyncio.get_event_loop().time() - start_time
                print(f"[Agent +{elapsed:.2f}s] {msg}", flush=True)

        # Serialize queries - only one at a time
        async with self._query_lock:
            # Create options with resume parameter if continuing session
            options = self._create_options(resume=resume_session)

            if self.debug_stream:
                if resume_session:
                    print(f"[Agent] Creating ClaudeSDKClient with resume={resume_session}...", flush=True)
                else:
                    print(f"[Agent] Creating new ClaudeSDKClient, session_id={session_id}...", flush=True)

            # Use context manager to ensure proper cleanup
            async with ClaudeSDKClient(options=options) as client:
                _t("client ready, sending query")
                await client.query(message)
                _t("query sent, awaiting stream")

                final_cost = 0.0

                async for msg in client.receive_response():
                    # ========== 消息类型调试打印 ==========
                    msg_type = type(msg).__name__
                    print(f"\n{'='*60}", flush=True)
                    print(f"📨 [MESSAGE TYPE] {msg_type}", flush=True)

                    # 打印消息的所有属性以便调试
                    if hasattr(msg, '__dict__'):
                        print(f"   属性: {list(msg.__dict__.keys())}", flush=True)
                    print(f"{'='*60}", flush=True)

                    # Handle partial streaming events (when include_partial_messages=True)
                    if hasattr(msg, 'type') and msg.type == 'stream_event':
                        print(f"  🔄 [StreamEvent]", flush=True)
                        # This is a streaming event - extract text delta if available
                        event = getattr(msg, 'event', None)
                        if event:
                            event_type = getattr(event, 'type', None)
                            print(f"     ├─ event.type: {event_type}", flush=True)

                            # ========== 详细打印各种 event type ==========
                            if event_type == 'message_start':
                                print(f"     │  🚀 [message_start] 消息开始", flush=True)
                                message = getattr(event, 'message', None)
                                if message:
                                    print(f"     │     ├─ id: {getattr(message, 'id', 'N/A')}", flush=True)
                                    print(f"     │     ├─ model: {getattr(message, 'model', 'N/A')}", flush=True)
                                    print(f"     │     └─ role: {getattr(message, 'role', 'N/A')}", flush=True)

                            elif event_type == 'content_block_start':
                                content_block = getattr(event, 'content_block', None)
                                index = getattr(event, 'index', 'N/A')
                                print(f"     │  📦 [content_block_start] index={index}", flush=True)
                                if content_block:
                                    block_type = getattr(content_block, 'type', None)
                                    print(f"     │     └─ content_block.type: {block_type}", flush=True)

                                    if block_type == 'thinking':
                                        print(f"     │        💭 开始思考块", flush=True)
                                    elif block_type == 'text':
                                        print(f"     │        📝 开始文本块", flush=True)
                                    elif block_type == 'tool_use':
                                        tool_name = getattr(content_block, 'name', '').replace("mcp__saas__", "")
                                        tool_id = getattr(content_block, 'id', '')
                                        print(f"     │        🔧 开始工具调用块", flush=True)
                                        print(f"     │           ├─ name: {tool_name}", flush=True)
                                        print(f"     │           └─ id: {tool_id}", flush=True)
                                        if tool_id and tool_id not in active_tools:
                                            active_tools[tool_id] = tool_name
                                            yield StreamEvent(
                                                type="tool_start",
                                                tool_name=tool_name,
                                                tool_input={}
                                            )

                            elif event_type == 'content_block_delta':
                                delta = getattr(event, 'delta', None)
                                index = getattr(event, 'index', 'N/A')
                                print(f"     │  📤 [content_block_delta] index={index}", flush=True)
                                if delta:
                                    delta_type = getattr(delta, 'type', None)
                                    print(f"     │     └─ delta.type: {delta_type}", flush=True)

                                    if delta_type == 'thinking_delta':
                                        thinking = getattr(delta, 'thinking', '')
                                        preview = thinking[:60] + "..." if len(thinking) > 60 else thinking
                                        print(f"     │        💭 thinking_delta: {preview}", flush=True)
                                        # Yield thinking event for frontend
                                        yield StreamEvent(type="thinking", content=thinking)

                                    elif delta_type == 'text_delta':
                                        text = getattr(delta, 'text', '')
                                        preview = text[:60] + "..." if len(text) > 60 else text
                                        print(f"     │        📝 text_delta: {preview}", flush=True)
                                        yield StreamEvent(type="text", content=text)

                                    elif delta_type == 'signature_delta':
                                        signature = getattr(delta, 'signature', '')
                                        print(f"     │        🔏 signature_delta: {signature[:40]}...", flush=True)

                                    elif delta_type == 'input_json_delta':
                                        partial_json = getattr(delta, 'partial_json', '')
                                        print(f"     │        📋 input_json_delta: {partial_json[:60]}...", flush=True)

                                    else:
                                        print(f"     │        ❓ unknown delta: {delta}", flush=True)

                            elif event_type == 'content_block_stop':
                                index = getattr(event, 'index', 'N/A')
                                print(f"     │  ⏹️ [content_block_stop] index={index} 内容块结束", flush=True)

                            elif event_type == 'message_delta':
                                delta = getattr(event, 'delta', None)
                                print(f"     │  📊 [message_delta]", flush=True)
                                if delta:
                                    stop_reason = getattr(delta, 'stop_reason', None)
                                    stop_sequence = getattr(delta, 'stop_sequence', None)
                                    print(f"     │     ├─ stop_reason: {stop_reason}", flush=True)
                                    print(f"     │     └─ stop_sequence: {stop_sequence}", flush=True)
                                usage = getattr(event, 'usage', None)
                                if usage:
                                    print(f"     │     └─ usage: {usage}", flush=True)

                            elif event_type == 'message_stop':
                                print(f"     │  🏁 [message_stop] 消息结束", flush=True)

                            else:
                                print(f"     │  ❓ [unknown event_type] {event_type}", flush=True)
                                print(f"     │     └─ raw event: {str(event)[:100]}...", flush=True)

                            _t(f"stream_event: {event_type}")
                        continue

                    # Handle UserMessage
                    if isinstance(msg, UserMessage):
                        print(f"  👤 [UserMessage]", flush=True)
                        if hasattr(msg, 'uuid') and msg.uuid:
                            print(f"     └─ uuid: {msg.uuid}", flush=True)
                        if isinstance(msg.content, str):
                            print(f"     └─ content: {msg.content[:100]}..." if len(msg.content) > 100 else f"     └─ content: {msg.content}", flush=True)
                        else:
                            print(f"     └─ content blocks: {len(msg.content)}", flush=True)
                            for i, block in enumerate(msg.content):
                                block_type = type(block).__name__
                                print(f"        [{i}] {block_type}", flush=True)
                                if isinstance(block, TextBlock):
                                    print(f"            └─ 📝 text: {block.text[:80]}..." if len(block.text) > 80 else f"            └─ 📝 text: {block.text}", flush=True)
                                elif isinstance(block, ToolResultBlock):
                                    print(f"            └─ 📤 tool_use_id: {block.tool_use_id}", flush=True)
                                    content_preview = str(block.content)[:80] if block.content else "None"
                                    print(f"            └─ 📤 content: {content_preview}...", flush=True)
                                    print(f"            └─ is_error: {block.is_error}", flush=True)

                    # Handle complete assistant messages
                    elif isinstance(msg, AssistantMessage):
                        print(f"  🤖 [AssistantMessage]", flush=True)
                        if hasattr(msg, 'model'):
                            print(f"     └─ model: {msg.model}", flush=True)
                        if hasattr(msg, 'error') and msg.error:
                            print(f"     └─ ❌ error: {msg.error}", flush=True)
                        print(f"     └─ content blocks: {len(msg.content)}", flush=True)

                        for i, block in enumerate(msg.content):
                            block_type = type(block).__name__
                            print(f"        [{i}] {block_type}", flush=True)

                            if isinstance(block, TextBlock):
                                if block.text:
                                    preview = block.text[:80] + "..." if len(block.text) > 80 else block.text
                                    print(f"            └─ 📝 text ({len(block.text)} chars): {preview}", flush=True)
                                    # Only yield new text (avoid duplicates from partial messages)
                                    new_text = block.text[sent_text_length:]
                                    if new_text:
                                        _t(f"text block ({len(new_text)} chars)")
                                        yield StreamEvent(type="text", content=new_text)
                                        sent_text_length = len(block.text)

                            elif isinstance(block, ThinkingBlock):
                                thinking_preview = block.thinking[:100] + "..." if len(block.thinking) > 100 else block.thinking
                                print(f"            └─ 💭 thinking ({len(block.thinking)} chars): {thinking_preview}", flush=True)
                                if hasattr(block, 'signature'):
                                    print(f"            └─ signature: {block.signature[:50]}..." if len(str(block.signature)) > 50 else f"            └─ signature: {block.signature}", flush=True)
                                # Yield thinking event for frontend
                                yield StreamEvent(type="thinking", content=block.thinking)

                            elif isinstance(block, ToolUseBlock):
                                tool_name = block.name.replace("mcp__saas__", "")
                                print(f"            └─ 🔧 tool_use: {block.name}", flush=True)
                                print(f"            └─ id: {block.id}", flush=True)
                                print(f"            └─ input: {str(block.input)[:100]}..." if len(str(block.input)) > 100 else f"            └─ input: {block.input}", flush=True)
                                if block.id not in active_tools:
                                    active_tools[block.id] = tool_name
                                    _t(f"tool_start: {tool_name}")
                                    yield StreamEvent(
                                        type="tool_start",
                                        tool_name=tool_name,
                                        tool_input=block.input if hasattr(block, 'input') else {}
                                    )

                            elif isinstance(block, ToolResultBlock):
                                tool_name = active_tools.get(block.tool_use_id, "unknown")
                                content = block.content if isinstance(block.content, str) else str(block.content)
                                print(f"            └─ 📤 tool_result for: {block.tool_use_id}", flush=True)
                                print(f"            └─ tool_name: {tool_name}", flush=True)
                                print(f"            └─ is_error: {block.is_error}", flush=True)
                                print(f"            └─ content ({len(content)} chars): {content[:80]}...", flush=True)
                                # Truncate long results for the event
                                if len(content) > 500:
                                    content = content[:500] + "..."
                                _t(f"tool_end: {tool_name}")
                                yield StreamEvent(
                                    type="tool_end",
                                    tool_name=tool_name,
                                    tool_result=content
                                )
                            else:
                                # Unknown block type
                                print(f"            └─ ❓ unknown block: {block}", flush=True)
                    # Do not reset sent_text_length here; we accumulate across messages

                    # Handle SystemMessage
                    elif isinstance(msg, SystemMessage):
                        print(f"  ⚙️ [SystemMessage]", flush=True)
                        if hasattr(msg, 'subtype'):
                            print(f"     └─ subtype: {msg.subtype}", flush=True)
                        if hasattr(msg, 'data'):
                            data_str = str(msg.data)
                            print(f"     └─ data: {data_str[:100]}..." if len(data_str) > 100 else f"     └─ data: {msg.data}", flush=True)
                        # Yield system event for frontend
                        yield StreamEvent(type="status", content=f"System: {getattr(msg, 'subtype', 'unknown')}")

                    # Result message at end
                    elif isinstance(msg, ResultMessage):
                        print(f"  ✅ [ResultMessage]", flush=True)
                        final_cost = getattr(msg, 'total_cost_usd', 0) or 0
                        print(f"     └─ total_cost_usd: ${final_cost:.4f}", flush=True)
                        if hasattr(msg, 'usage') and msg.usage:
                            print(f"     └─ usage:", flush=True)
                            print(f"        └─ input_tokens: {msg.usage.get('input_tokens', 'N/A')}", flush=True)
                            print(f"        └─ output_tokens: {msg.usage.get('output_tokens', 'N/A')}", flush=True)
                        if hasattr(msg, 'session_id'):
                            print(f"     └─ session_id: {msg.session_id}", flush=True)
                        if hasattr(msg, 'structured_output') and msg.structured_output:
                            print(f"     └─ structured_output: {msg.structured_output}", flush=True)
                        # Get the session ID from the result if available
                        result_session_id = getattr(msg, 'session_id', None)
                        if result_session_id:
                            session_id = result_session_id

                    else:
                        # Unknown message type
                        print(f"  ❓ [Unknown Message Type] {msg_type}", flush=True)
                        print(f"     └─ raw: {str(msg)[:200]}...", flush=True)

                # Update or create session info
                current_time = time.time()
                if session_id in self._sessions:
                    # Update existing session
                    session_info = self._sessions[session_id]
                    session_info.last_used_at = current_time
                    session_info.turn_count += 1
                    session_info.total_cost += final_cost
                else:
                    # Create new session record (store session_id for resume)
                    self._sessions[session_id] = SessionInfo(
                        session_id=session_id,
                        created_at=current_time,
                        last_used_at=current_time,
                        turn_count=1,
                        total_cost=final_cost,
                    )

                _t(f"done, cost={final_cost}, session={session_id}")
                yield StreamEvent(type="done", cost=final_cost, session_id=session_id)

    async def query(
        self,
        message: str,
        session_id: Optional[str] = None
    ) -> tuple[str, str]:
        """
        Send a query to Claude and get the complete response.

        Args:
            message: User's question or request
            session_id: Optional session ID for multi-turn conversations

        Returns:
            Tuple of (response_text, session_id)

        Example:
            response, session_id = await agent.query("有哪些高收入的 SaaS 产品？")
            print(response)
            # Use session_id for follow-up queries
            response2, _ = await agent.query("还有其他的吗？", session_id=session_id)
        """
        response_parts = []
        result_session_id = session_id or ""

        async for event in self.query_stream_events(message, session_id=session_id):
            if event.type == "text":
                response_parts.append(event.content)
            elif event.type == "done" and event.session_id:
                result_session_id = event.session_id

        return ''.join(response_parts), result_session_id
