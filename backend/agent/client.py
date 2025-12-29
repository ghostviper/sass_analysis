"""
Claude Agent SDK client wrapper for SaaS Analysis
"""

import os
from typing import AsyncIterator, Optional, Dict, Any
from dataclasses import dataclass

from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    create_sdk_mcp_server,
    AssistantMessage,
    TextBlock,
    ToolUseBlock,
    ToolResultBlock,
    ResultMessage,
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
        return result

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
    """

    def __init__(self):
        """Initialize the SaaS Analysis Agent with Claude SDK"""
        # Get API configuration from environment
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.base_url = os.getenv("ANTHROPIC_BASE_URL")  # Optional for third-party endpoints
        self.model = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5")
        self.cli_path = os.getenv("CLAUDE_CLI_PATH")  # Optional: custom CLI path

        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")

        # Build environment variables for Claude CLI
        env = {
            "ANTHROPIC_API_KEY": self.api_key,
            # Force Node.js to use unbuffered stdout (may help streaming on Windows)
            "NODE_OPTIONS": "--no-warnings",
            "FORCE_COLOR": "0",  # Disable color output which can cause buffering
        }
        if self.base_url:
            env["ANTHROPIC_BASE_URL"] = self.base_url

        # Pass proxy settings if configured (both upper and lower case for compatibility)
        http_proxy = os.getenv("HTTP_PROXY")
        https_proxy = os.getenv("HTTPS_PROXY")
        if http_proxy:
            env["HTTP_PROXY"] = http_proxy
            env["http_proxy"] = http_proxy
        if https_proxy:
            env["HTTPS_PROXY"] = https_proxy
            env["https_proxy"] = https_proxy

        # Create fresh MCP server for this session
        mcp_server = _create_mcp_server()

        # Build Claude Agent options
        # Use a shorter system prompt to avoid initialization timeout
        short_prompt = (
            "You are a SaaS industry analyst. Use the available tools to query startup data, "
            "analyze categories, and generate trend reports. Respond in the user's language."
        )

        options_kwargs = {
            "mcp_servers": {"saas": mcp_server},
            "allowed_tools": [
                "mcp__saas__query_startups",
                "mcp__saas__get_category_analysis",
                "mcp__saas__get_trend_report",
                "mcp__saas__get_leaderboard",
            ],
            "system_prompt": short_prompt,
            "model": self.model,
            "env": env,
        }

        # Add cli_path only if specified
        if self.cli_path:
            options_kwargs["cli_path"] = self.cli_path

        self.options = ClaudeAgentOptions(**options_kwargs)

    async def query_stream(self, message: str) -> AsyncIterator[str]:
        """
        Stream a query to Claude and yield text responses.

        Args:
            message: User's question or request

        Yields:
            Text chunks from Claude's response

        Example:
            async for chunk in agent.query_stream("分析 AI 赛道"):
                print(chunk, end="", flush=True)
        """
        async for event in self.query_stream_events(message):
            if event.type == "text":
                yield event.content

    async def query_stream_events(self, message: str) -> AsyncIterator[StreamEvent]:
        """
        Stream a query to Claude and yield detailed events including tool usage.

        This method provides full visibility into the agent's actions:
        - text: Text content from Claude's response (streaming)
        - tool_start: When a tool is being called
        - tool_end: When a tool returns results
        - done: Query completed with cost info

        Args:
            message: User's question or request

        Yields:
            StreamEvent objects with detailed information

        Example:
            async for event in agent.query_stream_events("分析 AI 赛道"):
                if event.type == "text":
                    print(event.content, end="", flush=True)
                elif event.type == "tool_start":
                    print(f"\\n[调用工具: {event.tool_name}]")
        """
        # Create fresh MCP server for this query
        mcp_server = _create_mcp_server()

        # Build options for this query with streaming enabled
        options_kwargs = {
            "mcp_servers": {"saas": mcp_server},
            "allowed_tools": [
                "mcp__saas__query_startups",
                "mcp__saas__get_category_analysis",
                "mcp__saas__get_trend_report",
                "mcp__saas__get_leaderboard",
            ],
            "system_prompt": self.options.system_prompt,
            "model": self.model,
            "env": self.options.env,
            "include_partial_messages": True,  # Enable streaming partial messages
        }

        if self.cli_path:
            options_kwargs["cli_path"] = self.cli_path

        query_options = ClaudeAgentOptions(**options_kwargs)

        # Track tool usage to avoid duplicate events
        active_tools = {}
        # Track text we've already sent to avoid duplicates
        sent_text_length = 0

        # Use ClaudeSDKClient for streaming with partial messages
        async with ClaudeSDKClient(options=query_options) as client:
            await client.query(message)

            async for msg in client.receive_response():
                # Handle partial streaming events (when include_partial_messages=True)
                if hasattr(msg, 'type') and msg.type == 'stream_event':
                    # This is a streaming event - extract text delta if available
                    event = getattr(msg, 'event', None)
                    if event:
                        event_type = getattr(event, 'type', None)
                        # Handle text delta events
                        if event_type == 'content_block_delta':
                            delta = getattr(event, 'delta', None)
                            if delta and hasattr(delta, 'text'):
                                yield StreamEvent(type="text", content=delta.text)
                        # Handle content block start (for tool use)
                        elif event_type == 'content_block_start':
                            content_block = getattr(event, 'content_block', None)
                            if content_block:
                                block_type = getattr(content_block, 'type', None)
                                if block_type == 'tool_use':
                                    tool_name = getattr(content_block, 'name', '').replace("mcp__saas__", "")
                                    tool_id = getattr(content_block, 'id', '')
                                    if tool_id and tool_id not in active_tools:
                                        active_tools[tool_id] = tool_name
                                        yield StreamEvent(
                                            type="tool_start",
                                            tool_name=tool_name,
                                            tool_input={}
                                        )
                    continue

                # Handle complete assistant messages
                if isinstance(msg, AssistantMessage):
                    for block in msg.content:
                        if isinstance(block, TextBlock):
                            if block.text:
                                # Only yield new text (avoid duplicates from partial messages)
                                new_text = block.text[sent_text_length:]
                                if new_text:
                                    yield StreamEvent(type="text", content=new_text)
                                    sent_text_length = len(block.text)

                        elif isinstance(block, ToolUseBlock):
                            tool_name = block.name.replace("mcp__saas__", "")
                            if block.id not in active_tools:
                                active_tools[block.id] = tool_name
                                yield StreamEvent(
                                    type="tool_start",
                                    tool_name=tool_name,
                                    tool_input=block.input if hasattr(block, 'input') else {}
                                )

                        elif isinstance(block, ToolResultBlock):
                            tool_name = active_tools.get(block.tool_use_id, "unknown")
                            content = block.content if isinstance(block.content, str) else str(block.content)
                            # Truncate long results for the event
                            if len(content) > 500:
                                content = content[:500] + "..."
                            yield StreamEvent(
                                type="tool_end",
                                tool_name=tool_name,
                                tool_result=content
                            )
                    # Reset for next message
                    sent_text_length = 0

                # Result message at end
                elif isinstance(msg, ResultMessage):
                    cost = getattr(msg, 'total_cost_usd', 0) or 0
                    yield StreamEvent(type="done", cost=cost)

    async def query(self, message: str) -> str:
        """
        Send a query to Claude and get the complete response.

        Args:
            message: User's question or request

        Returns:
            Complete response text from Claude

        Example:
            response = await agent.query("有哪些高收入的 SaaS 产品？")
            print(response)
        """
        response_parts = []
        async for event in self.query_stream_events(message):
            if event.type == "text":
                response_parts.append(event.content)

        return ''.join(response_parts)
