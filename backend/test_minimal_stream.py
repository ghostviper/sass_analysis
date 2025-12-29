#!/usr/bin/env python
"""
Minimal test for Claude Agent SDK streaming on Windows.
No MCP servers, just basic streaming test.
"""

import asyncio
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(dotenv_path=Path(__file__).parent / ".env")


async def test_minimal_streaming():
    """Minimal streaming test without MCP servers."""
    from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

    print("=" * 60)
    print("Minimal Streaming Test (no MCP)")
    print("=" * 60)

    api_key = os.getenv("ANTHROPIC_API_KEY")
    base_url = os.getenv("ANTHROPIC_BASE_URL")
    model = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5")
    cli_path = os.getenv("CLAUDE_CLI_PATH")

    env = {"ANTHROPIC_API_KEY": api_key}
    if base_url:
        env["ANTHROPIC_BASE_URL"] = base_url

    # Minimal options - just streaming
    options = ClaudeAgentOptions(
        model=model,
        env=env,
        include_partial_messages=True,
        max_turns=1,
    )
    if cli_path:
        options.cli_path = cli_path

    print(f"include_partial_messages: True")
    print(f"Model: {model}")
    print("-" * 60)

    start_time = time.time()
    msg_count = 0
    first_msg_time = None

    try:
        async with ClaudeSDKClient(options=options) as client:
            await client.query("从1数到10，每个数字单独一行")

            async for msg in client.receive_response():
                msg_count += 1
                now = time.time()
                elapsed = now - start_time

                if first_msg_time is None:
                    first_msg_time = elapsed

                msg_type = type(msg).__name__

                # Check if it's a stream event
                if hasattr(msg, 'type'):
                    msg_type = f"{msg_type}(type={msg.type})"

                print(f"[{elapsed:.2f}s] Msg #{msg_count}: {msg_type}")

                # Try to extract text from stream events
                if hasattr(msg, 'type') and getattr(msg, 'type', None) == 'stream_event':
                    event = getattr(msg, 'event', None)
                    if event:
                        event_type = getattr(event, 'type', 'unknown')
                        print(f"         Event type: {event_type}")

                        if event_type == 'content_block_delta':
                            delta = getattr(event, 'delta', None)
                            if delta and hasattr(delta, 'text'):
                                print(f"         Text: '{delta.text}'")

    except Exception as e:
        import traceback
        print(f"\nERROR: {e}")
        traceback.print_exc()

    total_time = time.time() - start_time
    print("-" * 60)
    print(f"Total messages: {msg_count}")
    print(f"First message at: {first_msg_time:.2f}s" if first_msg_time else "No messages")
    print(f"Total time: {total_time:.2f}s")

    if first_msg_time and total_time > 0:
        if first_msg_time > total_time * 0.9:
            print("\n⚠️  PROBLEM: First message came very late - NOT streaming!")
        else:
            print("\n✓ Messages appear to be streaming")


async def test_with_anyio():
    """Test using anyio like the examples show."""
    import anyio
    from claude_agent_sdk import query, ClaudeAgentOptions

    print("\n" + "=" * 60)
    print("Testing with anyio + query()")
    print("=" * 60)

    api_key = os.getenv("ANTHROPIC_API_KEY")
    base_url = os.getenv("ANTHROPIC_BASE_URL")
    model = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5")
    cli_path = os.getenv("CLAUDE_CLI_PATH")

    env = {"ANTHROPIC_API_KEY": api_key}
    if base_url:
        env["ANTHROPIC_BASE_URL"] = base_url

    options_dict = {
        "model": model,
        "env": env,
        "max_turns": 1,
    }
    if cli_path:
        options_dict["cli_path"] = cli_path

    options = ClaudeAgentOptions(**options_dict)

    start_time = time.time()
    msg_count = 0

    try:
        async for msg in query(prompt="说'你好'", options=options):
            msg_count += 1
            elapsed = time.time() - start_time
            print(f"[{elapsed:.2f}s] {type(msg).__name__}")

    except Exception as e:
        print(f"ERROR: {e}")

    print(f"\nTotal: {msg_count} messages in {time.time() - start_time:.2f}s")


if __name__ == "__main__":
    print(f"Python: {sys.version}")
    print(f"Platform: {sys.platform}")
    print(f"Event loop: {asyncio.get_event_loop_policy().__class__.__name__}")
    print()

    # Run minimal test
    asyncio.run(test_minimal_streaming())

    # Also test with anyio style
    # asyncio.run(test_with_anyio())
