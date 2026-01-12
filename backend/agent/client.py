"""
Claude Agent SDK client wrapper for SaaS Analysis

Supports multi-turn conversations with session management.

重要：Claude Agent SDK 的多轮对话有两种方式：
1. 同一个 ClaudeSDKClient 上下文中多次调用 query() - 推荐用于实时对话
2. 使用 resume 参数恢复之前的会话 - 用于跨请求的会话恢复

由于 HTTP 请求是无状态的，我们使用方式2，通过 ResultMessage 中的 session_id 来恢复会话。
"""

import os
import sys
import asyncio
import time
from typing import AsyncIterator, Optional, Dict, Any
from dataclasses import dataclass

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
    UserMessage,
    AssistantMessage,
    SystemMessage,
    ResultMessage,
    TextBlock,
    ThinkingBlock,
    ToolUseBlock,
    ToolResultBlock,
)


@dataclass
class StreamEvent:
    """Streaming event for frontend consumption."""
    type: str  # "block_start", "block_delta", "block_end", "tool_start", "tool_end", "status", "done", "error"
    layer: str = "primary"  # "primary", "process"
    block_id: Optional[str] = None
    block_type: Optional[str] = None
    block_index: Optional[int] = None
    content: str = ""
    tool_name: str = ""
    tool_id: str = ""
    tool_input: Dict[str, Any] = None
    tool_result: str = ""
    display_text: str = ""
    cost: float = 0.0
    session_id: str = ""
    checkpoint_id: str = ""  # 新增：checkpoint ID for multi-turn
    timestamp: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        import time as time_module
        result = {
            "type": self.type,
            "layer": self.layer,
            "timestamp": self.timestamp or time_module.time(),
        }
        if self.block_id:
            result["block_id"] = self.block_id
        if self.block_type:
            result["block_type"] = self.block_type
        if self.block_index is not None:
            result["block_index"] = self.block_index
        if self.content:
            result["content"] = self.content
        if self.tool_name:
            result["tool_name"] = self.tool_name
        if self.tool_id:
            result["tool_id"] = self.tool_id
        if self.tool_input:
            result["tool_input"] = self.tool_input
        if self.tool_result:
            result["tool_result"] = self.tool_result
        if self.display_text:
            result["display_text"] = self.display_text
        if self.cost > 0:
            result["cost"] = self.cost
        if self.session_id:
            result["session_id"] = self.session_id
        if self.checkpoint_id:
            result["checkpoint_id"] = self.checkpoint_id
        return result


from .tools import (
    # 原子化工具 - 替代旧的 query_startups_tool
    get_startups_by_ids_tool,
    search_startups_tool,
    browse_startups_tool,
    # 分析工具
    get_category_analysis_tool,
    get_trend_report_tool,
    get_leaderboard_tool,
    # 开发者分析工具
    get_founder_products_tool,
    # 联网搜索工具
    web_search_tool,
)
from .prompts import SYSTEM_PROMPT


def _get_friendly_tool_description(tool_name: str, tool_input: Dict[str, Any]) -> str:
    """Convert a tool call into a user-friendly description."""
    if not isinstance(tool_input, dict):
        return ""

    clean_name = tool_name.replace("mcp__saas__", "")

    if clean_name == "get_startups_by_ids":
        ids = tool_input.get("ids", [])
        if ids:
            return f"精确查询产品 (IDs: {ids})"
        return "查询产品数据"

    elif clean_name == "search_startups":
        keyword = tool_input.get("keyword", "")
        return f"搜索产品「{keyword}」" if keyword else "搜索产品"

    elif clean_name == "browse_startups":
        parts = []
        if tool_input.get("category"):
            parts.append(f"类目: {tool_input['category']}")
        if tool_input.get("min_revenue"):
            parts.append(f"最低收入: ${tool_input['min_revenue']}")
        if parts:
            return f"浏览产品 ({', '.join(parts)})"
        return "浏览产品列表"

    # 保留旧工具名的兼容性
    elif clean_name == "query_startups":
        parts = []
        if tool_input.get("ids"):
            return f"查询产品 (IDs: {tool_input['ids']})"
        if tool_input.get("category"):
            parts.append(f"类目: {tool_input['category']}")
        if tool_input.get("search"):
            parts.append(f"搜索: {tool_input['search']}")
        if tool_input.get("tech_complexity"):
            parts.append(f"技术复杂度: {tool_input['tech_complexity']}")
        if parts:
            return f"查询产品 ({', '.join(parts[:3])})"
        return "查询产品数据库"

    elif clean_name == "get_category_analysis":
        category = tool_input.get("category")
        return f"分析「{category}」类目" if category else "分析所有类目"

    elif clean_name == "get_trend_report":
        return "生成市场趋势报告"

    elif clean_name == "get_leaderboard":
        return f"获取创始人排行榜 (Top {tool_input.get('limit', 20)})"

    elif clean_name == "find_excellent_developers":
        return f"查找优秀开发者"

    elif clean_name == "get_founder_products":
        username = tool_input.get("username", "")
        return f"分析开发者「{username}」的产品组合" if username else "查询开发者产品"

    elif clean_name == "web_search":
        query = tool_input.get("query", "")
        return f"搜索「{query[:40]}{'...' if len(query) > 40 else ''}"

    return ""


def _create_mcp_server():
    """Create a fresh MCP server instance."""
    return create_sdk_mcp_server(
        name="saas_analysis",
        version="1.0.0",
        tools=[
            # 原子化查询工具 - 语义清晰，避免模型选择困难
            get_startups_by_ids_tool,    # 有 ID 时用这个
            search_startups_tool,         # 按名称搜索用这个
            browse_startups_tool,         # 浏览筛选用这个
            # 分析工具
            get_category_analysis_tool,
            get_trend_report_tool,
            get_leaderboard_tool,
            # 开发者分析工具
            get_founder_products_tool,    # 查询开发者的所有产品
            # 联网搜索工具
            web_search_tool,
        ]
    )


class SaaSAnalysisAgent:
    """Claude Agent SDK client wrapper for SaaS Analysis."""

    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.base_url = os.getenv("ANTHROPIC_BASE_URL")
        self.cli_path = os.getenv("CLAUDE_CLI_PATH")
        self.model = os.getenv("ANTHROPIC_MODEL", "glm")
        self.max_turns = int(os.getenv("CLAUDE_MAX_TURNS", "10"))

        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")

        self._env = {
            "ANTHROPIC_API_KEY": self.api_key,
            "ANTHROPIC_MODEL": self.model,
            "NODE_OPTIONS": "--no-warnings",
            "FORCE_COLOR": "0",
        }
        if self.base_url:
            self._env["ANTHROPIC_BASE_URL"] = self.base_url

        # Proxy settings
        for var in ["HTTP_PROXY", "HTTPS_PROXY"]:
            if val := os.getenv(var):
                self._env[var] = val
                self._env[var.lower()] = val

        self._query_lock = asyncio.Lock()

    def _create_options(
        self,
        resume: Optional[str] = None,
        enable_web_search: bool = False,
        context: Optional[Dict[str, Any]] = None
    ) -> ClaudeAgentOptions:
        from pathlib import Path
        
        mcp_server = _create_mcp_server()
        
        # 获取 agent 目录的绝对路径
        # SDK 会从 cwd/.claude/ 目录加载配置文件（CLAUDE.md, settings.json 等）
        # 参考: claude-cookbooks/claude_agent_sdk/chief_of_staff_agent/agent.py
        agent_dir = Path(__file__).parent.absolute()
        
        options = {
            "mcp_servers": {"saas": mcp_server},
            "allowed_tools": [
                # MCP 工具 - 原子化数据查询
                "mcp__saas__get_startups_by_ids",  # 通过 ID 精确查询
                "mcp__saas__search_startups",       # 通过关键词搜索
                "mcp__saas__browse_startups",       # 浏览筛选
                # MCP 工具 - 分析
                "mcp__saas__get_category_analysis",
                "mcp__saas__get_trend_report",
                "mcp__saas__get_leaderboard",
                # MCP 工具 - 联网搜索
                "mcp__saas__web_search",
                # Task 工具 - 启用子代理委托
                # 子代理定义在 .claude/agents/ 目录下
                "Task",
            ],
            "model": self.model,
            "env": self._env,
            "include_partial_messages": True,
            "accumulate_streaming_content": True,  # 让 SDK 累积流式内容，确保流式输出正常
            "max_turns": self.max_turns,
            # 设置工作目录为 agent 目录，隔离上下文
            # SDK 会从 agent/.claude/ 加载:
            # - CLAUDE.md 主要指令
            # - settings.json 权限配置
            # - agents/ 子代理定义
            # - commands/ 斜杠命令
            # - output-styles/ 输出风格
            "cwd": agent_dir,
            # IMPORTANT: setting_sources 必须包含 "project" 才能加载文件系统配置
            "setting_sources": ["project"],
        }
        
        if self.cli_path:
            options["cli_path"] = self.cli_path
        if resume:
            # 恢复会话时，使用 fork_session 创建新的分支
            options["resume"] = resume
            options["fork_session"] = True
            print(f"[DEBUG] Resuming session: {resume}", flush=True)
        
        # 打印调试信息
        if context:
            print(f"[DEBUG] Context provided: type={context.get('type')}, products={context.get('products')}", flush=True)
        print(f"[DEBUG] Agent cwd: {agent_dir}", flush=True)
        
        return ClaudeAgentOptions(**options)
    
    def _build_context_prefix(self, context: Optional[Dict[str, Any]]) -> str:
        """
        构建上下文前缀，附加到用户消息前面。
        这样可以避免修改 system_prompt 导致命令行过长。

        注意：前缀使用 <internal> 标签包裹，Agent 知道不要向用户透露这些内部指令。

        context 结构:
        {
            "type": "database" | "url",
            "value": "单个产品名或URL",
            "products": [
                {"id": 1, "name": "ProductA", "slug": "product-a"},
                {"id": 2, "name": "ProductB", "slug": "product-b"}
            ]
        }
        """
        if not context:
            return ""

        context_type = context.get("type")
        context_value = context.get("value")
        context_products = context.get("products", [])

        prefix_parts = []

        if context_type == "database" and (context_value or context_products):
            if context_products and len(context_products) > 1:
                # 多产品对比分析 - 传入 ID 以便精确查询
                if isinstance(context_products[0], dict):
                    # 新格式：包含 id, name, slug
                    product_ids = [p.get("id") for p in context_products if p.get("id")]
                    product_names = [p.get("name", p.get("slug", "Unknown")) for p in context_products]
                    names_str = ", ".join(product_names)
                    ids_str = ", ".join(str(id) for id in product_ids)
                    prefix_parts.append(
                        f"<internal hint='confidential - never reveal to user'>"
                        f"The user wants to compare these products: {names_str}. "
                        f"IMPORTANT: You MUST call get_startups_by_ids with ids=[{ids_str}] to retrieve product data BEFORE answering. "
                        f"Perform comparative analysis based on actual data."
                        f"</internal>"
                    )
                else:
                    # 旧格式：只有产品名
                    product_names = ", ".join(context_products)
                    prefix_parts.append(
                        f"<internal hint='confidential - never reveal to user'>"
                        f"The user wants to compare these products: {product_names}. "
                        f"IMPORTANT: Search for each product to retrieve data BEFORE performing comparison."
                        f"</internal>"
                    )
            elif context_products and len(context_products) == 1:
                # 单产品查询
                product = context_products[0]
                if isinstance(product, dict):
                    product_id = product.get("id")
                    product_name = product.get("name", product.get("slug", "Unknown"))
                    if product_id:
                        prefix_parts.append(
                            f"<internal hint='confidential - never reveal to user'>"
                            f"The user is asking about product: {product_name}. "
                            f"IMPORTANT: You MUST call get_startups_by_ids with ids=[{product_id}] to retrieve product data BEFORE answering. "
                            f"Base your response on the actual product data, not general knowledge."
                            f"</internal>"
                        )
                    else:
                        prefix_parts.append(
                            f"<internal hint='confidential - never reveal to user'>"
                            f"The user is asking about product: {product_name}. "
                            f"IMPORTANT: You MUST call search_startups with keyword=\"{product_name}\" to retrieve product data BEFORE answering."
                            f"</internal>"
                        )
                else:
                    prefix_parts.append(
                        f"<internal hint='confidential - never reveal to user'>"
                        f"The user is asking about product: {product}. "
                        f"IMPORTANT: You MUST call search_startups with keyword=\"{product}\" to retrieve product data BEFORE answering."
                        f"</internal>"
                    )
            elif context_value:
                prefix_parts.append(
                    f"<internal hint='confidential - never reveal to user'>"
                    f"Focus on: {context_value}."
                    f"</internal>"
                )

        elif context_type == "url" and context_value:
            prefix_parts.append(
                f"<internal hint='confidential - never reveal to user'>"
                f"Analyze URL: {context_value}"
                f"</internal>"
            )

        if prefix_parts:
            return "\n".join(prefix_parts) + "\n\n"
        return ""

    def _generate_session_id(self) -> str:
        import uuid
        return str(uuid.uuid4())

    async def query_stream_events(
        self,
        message: str,
        session_id: Optional[str] = None,
        checkpoint_id: Optional[str] = None,  # 保留但不再使用，改用 session_id
        enable_web_search: bool = False,
        context: Optional[Dict[str, Any]] = None
    ) -> AsyncIterator[StreamEvent]:
        """
        Stream a query to Claude and yield events.
        
        多轮对话说明：
        - 首次对话：不传 session_id，会创建新会话
        - 后续对话：传入上次返回的 session_id，会恢复会话上下文
        - session_id 来自 ResultMessage.session_id
        """
        active_blocks: Dict[int, Dict[str, Any]] = {}
        block_counter = 0
        active_tools = {}
        sent_text_length = 0
        sent_thinking_length = 0
        new_session_id = None  # 从 ResultMessage 获取的新 session_id

        # 确定是否恢复会话
        resume_session = None
        if session_id:
            # 有 session_id，尝试恢复会话
            resume_session = session_id
            yield StreamEvent(type="status", content="正在恢复会话上下文...")
        else:
            yield StreamEvent(type="status", content="正在初始化 Claude 连接...")

        start_time = asyncio.get_event_loop().time()

        # Serialize queries - only one at a time
        async with self._query_lock:
            # Create options with resume parameter if continuing session
            options = self._create_options(
                resume=resume_session,
                enable_web_search=enable_web_search,
                context=context
            )
            
            # 构建带上下文前缀的消息（避免修改 system_prompt 导致命令行过长）
            context_prefix = self._build_context_prefix(context)
            full_message = context_prefix + message if context_prefix else message
            
            if context_prefix:
                print(f"[DEBUG] Added context prefix ({len(context_prefix)} chars) to message", flush=True)

            # Use context manager to ensure proper cleanup
            async with ClaudeSDKClient(options=options) as client:
                await client.query(full_message)

                final_cost = 0.0
                last_event_time = asyncio.get_event_loop().time()

                async for msg in client.receive_response():
                    # 更新最后事件时间
                    current_time = asyncio.get_event_loop().time()
                    time_since_last = current_time - last_event_time
                    last_event_time = current_time
                    
                    # 调试：打印事件类型
                    msg_type = type(msg).__name__
                    print(f"[DEBUG] Received message type: {msg_type}, time since last: {time_since_last:.1f}s")

                    # Handle partial streaming events (when include_partial_messages=True)
                    if hasattr(msg, 'type') and msg.type == 'stream_event':
                        # This is a streaming event - extract text delta if available
                        event = getattr(msg, 'event', None)
                        if event:
                            event_type = getattr(event, 'type', None)

                            # Handle different event types
                            if event_type == 'content_block_start':
                                content_block = getattr(event, 'content_block', None)
                                index = getattr(event, 'index', 0)

                                if content_block:
                                    block_type = getattr(content_block, 'type', None)

                                    # Generate unique block ID
                                    block_id = f"block_{block_counter}"
                                    block_counter += 1

                                    # Determine layer based on block type
                                    layer = "process" if block_type in ("thinking", "tool_use") else "primary"

                                    # Store block info
                                    block_info = {
                                        "type": block_type,
                                        "id": block_id,
                                        "content": "",
                                        "layer": layer,
                                    }

                                    if block_type == 'thinking':
                                        # Emit block_start event
                                        yield StreamEvent(
                                            type="block_start",
                                            layer="process",
                                            block_id=block_id,
                                            block_type="thinking",
                                            block_index=index
                                        )

                                    elif block_type == 'text':
                                        yield StreamEvent(
                                            type="block_start",
                                            layer="primary",
                                            block_id=block_id,
                                            block_type="text",
                                            block_index=index
                                        )

                                    elif block_type == 'tool_use':
                                        tool_name = getattr(content_block, 'name', '').replace("mcp__saas__", "")
                                        tool_id = getattr(content_block, 'id', '')
                                        tool_input = getattr(content_block, 'input', {}) or {}
                                        # Generate friendly description for the tool call
                                        friendly_desc = _get_friendly_tool_description(tool_name, tool_input)

                                        block_info["tool_id"] = tool_id
                                        block_info["tool_name"] = tool_name
                                        block_info["tool_input"] = tool_input
                                        block_info["display_text"] = friendly_desc

                                        # Store in active_tools for tool_result matching
                                        # Use tool_id as key (this is the same as block.id in ToolUseBlock)
                                        if tool_id:
                                            active_tools[tool_id] = {"name": tool_name, "display_text": friendly_desc}

                                        # Emit both block_start and tool_start for compatibility
                                        yield StreamEvent(
                                            type="block_start",
                                            layer="process",
                                            block_id=block_id,
                                            block_type="tool_use",
                                            block_index=index,
                                            tool_name=tool_name,
                                            tool_id=tool_id,
                                            display_text=friendly_desc
                                        )
                                        yield StreamEvent(
                                            type="tool_start",
                                            layer="process",
                                            block_id=block_id,
                                            tool_name=tool_name,
                                            tool_id=tool_id,
                                            tool_input=tool_input,
                                            display_text=friendly_desc
                                        )

                                    active_blocks[index] = block_info

                            elif event_type == 'content_block_delta':
                                delta = getattr(event, 'delta', None)
                                index = getattr(event, 'index', 0)

                                block_info = active_blocks.get(index, {})
                                block_id = block_info.get("id")

                                if delta:
                                    delta_type = getattr(delta, 'type', None)

                                    if delta_type == 'thinking_delta':
                                        thinking = getattr(delta, 'thinking', '')
                                        if thinking:
                                            block_info["content"] = block_info.get("content", "") + thinking
                                            # Update sent_thinking_length to avoid duplicates in AssistantMessage
                                            sent_thinking_length += len(thinking)
                                            # Emit block_delta event
                                            yield StreamEvent(
                                                type="block_delta",
                                                layer="process",
                                                block_id=block_id,
                                                block_type="thinking",
                                                content=thinking
                                            )

                                    elif delta_type == 'text_delta':
                                        text = getattr(delta, 'text', '')
                                        if text:
                                            block_info["content"] = block_info.get("content", "") + text
                                            # Update sent_text_length to avoid duplicates in AssistantMessage
                                            sent_text_length += len(text)
                                            # Emit block_delta event
                                            yield StreamEvent(
                                                type="block_delta",
                                                layer="primary",
                                                block_id=block_id,
                                                block_type="text",
                                                content=text
                                            )

                                    elif delta_type == 'input_json_delta':
                                        partial_json = getattr(delta, 'partial_json', '')
                                        # Accumulate tool input JSON
                                        block_info["input_json"] = block_info.get("input_json", "") + partial_json

                            elif event_type == 'content_block_stop':
                                index = getattr(event, 'index', 0)

                                # Get and remove block info
                                block_info = active_blocks.pop(index, {})
                                block_id = block_info.get("id")
                                block_type = block_info.get("type")
                                layer = block_info.get("layer", "primary")

                                if block_id and block_type:
                                    # Emit block_end event
                                    yield StreamEvent(
                                        type="block_end",
                                        layer=layer,
                                        block_id=block_id,
                                        block_type=block_type
                                    )

                            elif event_type == 'message_delta':
                                pass  # No action needed

                            elif event_type == 'message_stop':
                                pass  # No action needed

                        continue

                    # Handle UserMessage - 捕获 checkpoint ID
                    if isinstance(msg, UserMessage):
                        print(f"[DEBUG] UserMessage received", flush=True)
                        if hasattr(msg, 'uuid') and msg.uuid:
                            new_checkpoint_id = msg.uuid
                            print(f"[DEBUG] Captured checkpoint ID: {new_checkpoint_id}", flush=True)

                    # Handle complete assistant messages (fallback for non-streaming)
                    elif isinstance(msg, AssistantMessage):
                        print(f"[DEBUG] AssistantMessage received with {len(msg.content)} blocks", flush=True)
                        for i, block in enumerate(msg.content):
                            block_type_name = type(block).__name__
                            print(f"[DEBUG]   Block {i}: {block_type_name}", flush=True)
                            
                            if isinstance(block, TextBlock):
                                if block.text:
                                    print(f"[DEBUG]   TextBlock content length: {len(block.text)}, sent_text_length: {sent_text_length}", flush=True)
                                    print(f"[DEBUG]   TextBlock preview: {block.text[:200]}..." if len(block.text) > 200 else f"[DEBUG]   TextBlock content: {block.text}", flush=True)
                                    # Only yield new text (avoid duplicates from streaming)
                                    new_text = block.text[sent_text_length:]
                                    if new_text:
                                        print(f"[DEBUG]   Yielding new text length: {len(new_text)}", flush=True)
                                        yield StreamEvent(
                                            type="block_delta",
                                            layer="primary",
                                            block_type="text",
                                            content=new_text
                                        )
                                        sent_text_length = len(block.text)
                                    else:
                                        print(f"[DEBUG]   No new text to yield (already sent)", flush=True)
                                else:
                                    print(f"[DEBUG]   TextBlock is empty!", flush=True)

                            elif isinstance(block, ThinkingBlock):
                                # Only yield new thinking (avoid duplicates)
                                new_thinking = block.thinking[sent_thinking_length:]
                                if new_thinking:
                                    yield StreamEvent(
                                        type="block_delta",
                                        layer="process",
                                        block_type="thinking",
                                        content=new_thinking
                                    )
                                    sent_thinking_length = len(block.thinking)

                            elif isinstance(block, ToolUseBlock):
                                tool_name = block.name.replace("mcp__saas__", "")
                                tool_input = block.input if hasattr(block, 'input') else {}
                                print(f"[DEBUG]   ToolUseBlock: {tool_name}, input: {tool_input}", flush=True)
                                friendly_desc = _get_friendly_tool_description(tool_name, tool_input)
                                if block.id not in active_tools:
                                    active_tools[block.id] = {"name": tool_name, "display_text": friendly_desc}
                                    yield StreamEvent(
                                        type="tool_start",
                                        layer="process",
                                        tool_name=tool_name,
                                        tool_input=tool_input,
                                        display_text=friendly_desc
                                    )

                            elif isinstance(block, ToolResultBlock):
                                print(f"[DEBUG]   ToolResultBlock: tool_use_id={block.tool_use_id}", flush=True)
                                tool_info = active_tools.get(block.tool_use_id, {"name": "unknown", "display_text": ""})
                                tool_name = tool_info["name"] if isinstance(tool_info, dict) else tool_info
                                tool_display = tool_info.get("display_text", "") if isinstance(tool_info, dict) else ""
                                content = block.content if isinstance(block.content, str) else str(block.content)
                                # Truncate long results
                                if len(content) > 500:
                                    content = content[:500] + "..."
                                yield StreamEvent(
                                    type="tool_end",
                                    layer="process",
                                    tool_name=tool_name,
                                    tool_id=block.tool_use_id,
                                    tool_result=content,
                                    display_text=tool_display
                                )

                    # Handle SystemMessage
                    elif isinstance(msg, SystemMessage):
                        subtype = getattr(msg, 'subtype', 'unknown')
                        print(f"[DEBUG] SystemMessage received: subtype={subtype}", flush=True)
                        yield StreamEvent(type="status", layer="debug", content=f"System: {subtype}")

                    # Result message at end
                    elif isinstance(msg, ResultMessage):
                        print(f"[DEBUG] ResultMessage received!", flush=True)
                        final_cost = getattr(msg, 'total_cost_usd', 0) or 0
                        print(f"[DEBUG] Final cost: {final_cost}", flush=True)
                        
                        # 获取 session_id - 这是恢复会话的关键
                        result_session_id = getattr(msg, 'session_id', None)
                        if result_session_id:
                            new_session_id = result_session_id
                            print(f"[DEBUG] Got session_id from ResultMessage: {new_session_id}", flush=True)
                        else:
                            print(f"[DEBUG] No session_id in ResultMessage", flush=True)
                    
                    else:
                        # 未知消息类型
                        print(f"[DEBUG] Unknown message type: {msg_type}", flush=True)

                # 返回最终事件，包含 session_id 用于后续多轮对话
                final_session_id = new_session_id or session_id or ""
                print(f"[DEBUG] Final session_id to return: {final_session_id}", flush=True)
                
                yield StreamEvent(
                    type="done",
                    layer="primary",
                    cost=final_cost,
                    session_id=final_session_id,
                )

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
            # Collect text content from block_delta events with text type
            if event.type == "block_delta" and event.block_type == "text":
                response_parts.append(event.content)
            elif event.type == "done" and event.session_id:
                result_session_id = event.session_id

        return ''.join(response_parts), result_session_id
