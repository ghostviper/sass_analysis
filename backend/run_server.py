#!/usr/bin/env python
"""
Start the FastAPI server.

NOTE: On Windows, --reload mode breaks subprocess support for Claude Agent SDK.
This script disables reload mode to ensure proper functionality.
"""

import os
import sys
import asyncio

# Force unbuffered output for better streaming on Windows
os.environ["PYTHONUNBUFFERED"] = "1"
sys.stdout.reconfigure(line_buffering=True) if hasattr(sys.stdout, 'reconfigure') else None
sys.stderr.reconfigure(line_buffering=True) if hasattr(sys.stderr, 'reconfigure') else None

import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8001"))
    debug = os.getenv("DEBUG", "true").lower() == "true"

    print(f"Starting server on {host}:{port}")
    print(f"Event loop policy: {asyncio.get_event_loop_policy().__class__.__name__}")

    # IMPORTANT: --reload mode breaks subprocess support on Windows
    # Claude Agent SDK requires subprocess, so we must disable reload
    if debug:
        print("NOTE: Hot reload is DISABLED for Claude Agent SDK compatibility on Windows")
        print("      Restart the server manually after code changes")

    uvicorn.run(
        "api.main:app",
        host=host,
        port=port,
        reload=False,  # MUST be False for Claude Agent SDK on Windows
        loop="asyncio",
    )
