#!/usr/bin/env python
"""
Test script to verify Claude Agent SDK streaming behavior on Windows.

Run this directly to see if streaming works at the SDK level:
    python test_streaming.py
"""

import asyncio
import os
import sys
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv(dotenv_path=Path(__file__).parent / ".env")


async def test_basic_streaming():
    """Test basic streaming with Claude Agent SDK."""
    from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, AssistantMessage, TextBlock, ResultMessage

    print("=" * 60)
    print("Testing Claude Agent SDK Streaming")
    print("=" * 60)

    # Get configuration
    api_key = os.getenv("ANTHROPIC_API_KEY")
    base_url = os.getenv("ANTHROPIC_BASE_URL")
    model = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5")
    cli_path = os.getenv("CLAUDE_CLI_PATH")

    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set")
        return

    print(f"Model: {model}")
    print(f"Base URL: {base_url}")
    print(f"CLI Path: {cli_path}")
    print()

    # Build environment
    env = {"ANTHROPIC_API_KEY": api_key}
    if base_url:
        env["ANTHROPIC_BASE_URL"] = base_url

    http_proxy = os.getenv("HTTP_PROXY")
    https_proxy = os.getenv("HTTPS_PROXY")
    if http_proxy:
        env["HTTP_PROXY"] = http_proxy
        env["http_proxy"] = http_proxy
    if https_proxy:
        env["HTTPS_PROXY"] = https_proxy
        env["https_proxy"] = https_proxy

    # Build options with streaming enabled
    options_kwargs = {
        "system_prompt": "You are a helpful assistant. Keep responses brief.",
        "model": model,
        "env": env,
        "include_partial_messages": True,  # Enable streaming
        "max_turns": 1,
    }
    if cli_path:
        options_kwargs["cli_path"] = cli_path

    options = ClaudeAgentOptions(**options_kwargs)

    print("Sending query: '写一首关于编程的短诗'")
    print("-" * 60)

    try:
        async with ClaudeSDKClient(options=options) as client:
            await client.query("写一首关于编程的短诗，4行即可")

            message_count = 0
            async for msg in client.receive_response():
                message_count += 1
                msg_type = type(msg).__name__

                # Check for stream events (partial messages)
                if hasattr(msg, 'type') and msg.type == 'stream_event':
                    event = getattr(msg, 'event', None)
                    if event:
                        event_type = getattr(event, 'type', None)
                        if event_type == 'content_block_delta':
                            delta = getattr(event, 'delta', None)
                            if delta and hasattr(delta, 'text'):
                                # Print streaming text without newline
                                print(delta.text, end='', flush=True)
                                continue
                        print(f"[STREAM EVENT: {event_type}]", flush=True)
                    continue

                # Handle complete messages
                if isinstance(msg, AssistantMessage):
                    print(f"\n[COMPLETE MESSAGE #{message_count}]")
                    for block in msg.content:
                        if isinstance(block, TextBlock):
                            print(f"Text: {block.text[:100]}...")

                elif isinstance(msg, ResultMessage):
                    print(f"\n[RESULT] Cost: ${getattr(msg, 'total_cost_usd', 0):.4f}")

                else:
                    print(f"[{msg_type}] {str(msg)[:100]}")

    except Exception as e:
        import traceback
        print(f"\nERROR: {type(e).__name__}: {e}")
        traceback.print_exc()

    print()
    print("=" * 60)
    print(f"Total messages received: {message_count}")
    print("=" * 60)


async def test_without_partial_messages():
    """Test without partial messages to compare."""
    from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, TextBlock

    print("\n" + "=" * 60)
    print("Testing WITHOUT include_partial_messages")
    print("=" * 60)

    api_key = os.getenv("ANTHROPIC_API_KEY")
    base_url = os.getenv("ANTHROPIC_BASE_URL")
    model = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5")
    cli_path = os.getenv("CLAUDE_CLI_PATH")

    env = {"ANTHROPIC_API_KEY": api_key}
    if base_url:
        env["ANTHROPIC_BASE_URL"] = base_url

    options_kwargs = {
        "system_prompt": "You are a helpful assistant.",
        "model": model,
        "env": env,
        "max_turns": 1,
    }
    if cli_path:
        options_kwargs["cli_path"] = cli_path

    options = ClaudeAgentOptions(**options_kwargs)

    print("Sending query: '说三个数字'")
    print("-" * 60)

    message_count = 0
    try:
        async for msg in query(prompt="说三个数字，用逗号分隔", options=options):
            message_count += 1
            print(f"[MSG #{message_count}] {type(msg).__name__}", flush=True)

            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        print(f"  Text: {block.text}")

    except Exception as e:
        print(f"ERROR: {e}")

    print(f"\nTotal messages: {message_count}")


if __name__ == "__main__":
    print("Python version:", sys.version)
    print("Event loop policy:", asyncio.get_event_loop_policy().__class__.__name__)
    print()

    # Run tests
    asyncio.run(test_basic_streaming())

    # Optionally test without partial messages
    # asyncio.run(test_without_partial_messages())
