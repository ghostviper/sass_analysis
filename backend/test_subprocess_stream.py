#!/usr/bin/env python
"""
Test subprocess streaming on Windows.
This tests if the Claude Code CLI can stream output.
"""

import asyncio
import os
import sys
import json
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(dotenv_path=Path(__file__).parent / ".env")


async def test_cli_direct():
    """Directly test Claude Code CLI streaming."""
    cli_path = os.getenv("CLAUDE_CLI_PATH", "claude")

    print(f"Testing CLI: {cli_path}")
    print("=" * 60)

    # Build environment
    env = os.environ.copy()
    env["ANTHROPIC_API_KEY"] = os.getenv("ANTHROPIC_API_KEY", "")
    if os.getenv("ANTHROPIC_BASE_URL"):
        env["ANTHROPIC_BASE_URL"] = os.getenv("ANTHROPIC_BASE_URL")

    # Simple prompt
    prompt = "Count from 1 to 5 slowly, one number per line."

    # Run CLI with --output-format stream-json
    cmd = [
        cli_path,
        "--print",  # Non-interactive mode
        "--output-format", "stream-json",
        "--max-turns", "1",
        "-p", prompt
    ]

    print(f"Command: {' '.join(cmd)}")
    print("-" * 60)

    try:
        # Create subprocess with unbuffered stdout
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
        )

        line_count = 0
        # Read line by line
        while True:
            line = await process.stdout.readline()
            if not line:
                break

            line_count += 1
            decoded = line.decode('utf-8', errors='replace').strip()

            # Print with timestamp to see if streaming
            import time
            timestamp = time.strftime("%H:%M:%S")
            print(f"[{timestamp}] Line {line_count}: {decoded[:100]}...")

            # Try to parse as JSON
            try:
                data = json.loads(decoded)
                msg_type = data.get('type', 'unknown')
                print(f"         Type: {msg_type}")
            except:
                pass

        # Wait for completion
        await process.wait()
        print(f"\nProcess exited with code: {process.returncode}")

        # Print any stderr
        stderr = await process.stderr.read()
        if stderr:
            print(f"Stderr: {stderr.decode('utf-8', errors='replace')}")

    except FileNotFoundError:
        print(f"ERROR: CLI not found at {cli_path}")
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")


async def test_simple_subprocess():
    """Test basic subprocess streaming with a simple command."""
    print("\n" + "=" * 60)
    print("Testing basic subprocess streaming (ping localhost)")
    print("=" * 60)

    # Use ping which outputs line by line
    process = await asyncio.create_subprocess_exec(
        "ping", "-n", "3", "localhost",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    import time
    while True:
        line = await process.stdout.readline()
        if not line:
            break
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {line.decode('utf-8', errors='replace').strip()}")

    await process.wait()
    print("Basic subprocess test complete.")


if __name__ == "__main__":
    print(f"Python: {sys.version}")
    print(f"Platform: {sys.platform}")
    print()

    # First test basic subprocess
    asyncio.run(test_simple_subprocess())

    # Then test CLI
    print("\n")
    asyncio.run(test_cli_direct())
