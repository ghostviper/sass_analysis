#!/usr/bin/env python3
"""
Quick Start Script for Channel Search Feature

This script helps you quickly set up and test the channel search functionality.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))


def print_header(text: str):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_step(step: int, text: str):
    """Print a step"""
    print(f"\n[Step {step}] {text}")


def check_env_file():
    """Check if .env file exists"""
    env_file = backend_dir / ".env"
    if not env_file.exists():
        print("❌ .env file not found!")
        print("\nPlease create .env file:")
        print("  cp .env.example .env")
        return False
    return True


def check_api_keys():
    """Check which API keys are configured"""
    print_step(1, "Checking API Configuration")

    from config.search_config import get_search_config

    config = get_search_config()
    status = config.get_status_report()

    print("\n📊 Configuration Status:")
    print(f"  Google Custom Search: {'✅' if status['google']['custom_search'] else '❌'}")
    print(f"  SerpAPI: {'✅' if status['google']['serpapi'] else '❌'}")
    print(f"  Tavily: {'✅' if status['google']['tavily'] else '❌'}")
    print(f"  Reddit: {status['reddit']['mode']} mode")

    if not status['google']['configured']:
        print("\n⚠️  No Google search backend configured!")
        print("\nTo enable search, configure at least one backend:")
        print("\n1. Tavily (Recommended - AI optimized):")
        print("   Visit: https://tavily.com/")
        print("   Add to .env: TAVILY_API_KEY=your_key")
        print("\n2. Google Custom Search (Free - 100 queries/day):")
        print("   Visit: https://programmablesearchengine.google.com/")
        print("   Add to .env: GOOGLE_CUSTOM_SEARCH_API_KEY and GOOGLE_CUSTOM_SEARCH_ENGINE_ID")
        print("\n3. SerpAPI (Commercial - $50/month):")
        print("   Visit: https://serpapi.com/")
        print("   Add to .env: SERPAPI_API_KEY")
        return False

    print(f"\n✅ Using backend: {status['google']['default_backend']}")
    return True


async def test_search():
    """Test search functionality"""
    print_step(2, "Testing Search Functionality")

    from services.search.factory import SearchServiceFactory

    try:
        # Get best backend
        backend = SearchServiceFactory.get_best_google_backend()
        print(f"\n🔍 Testing with backend: {backend}")

        service = SearchServiceFactory.get_google_service(backend)

        # Test basic search
        print("\n  Testing: 'SaaS products'")
        response = await service.search("SaaS products", limit=3)

        print(f"  ✅ Found {len(response.results)} results in {response.search_time:.2f}s")

        if response.results:
            print(f"\n  First result:")
            print(f"    Title: {response.results[0].title}")
            print(f"    URL: {response.results[0].url}")

        return True

    except Exception as e:
        print(f"\n  ❌ Error: {e}")
        return False


async def test_channel_search():
    """Test multi-channel search"""
    print_step(3, "Testing Multi-Channel Search")

    from agent.tools import search_channels

    try:
        print("\n  Searching channels: ['reddit', 'google']")
        results = await search_channels(
            query="indie developer tools",
            channels=["reddit", "google"],
            limit_per_channel=2
        )

        print(f"  ✅ Total results: {results['total_results']}")

        for channel, channel_results in results['channels'].items():
            if isinstance(channel_results, list) and channel_results:
                print(f"\n  {channel.upper()}: {len(channel_results)} results")
                if channel_results and 'title' in channel_results[0]:
                    print(f"    - {channel_results[0]['title'][:60]}...")

        return True

    except Exception as e:
        print(f"\n  ❌ Error: {e}")
        return False


def check_dependencies():
    """Check if required dependencies are installed"""
    print_step(4, "Checking Dependencies")

    missing = []

    try:
        import aiohttp
        print("  ✅ aiohttp")
    except ImportError:
        print("  ❌ aiohttp")
        missing.append("aiohttp")

    try:
        import fastapi
        print("  ✅ fastapi")
    except ImportError:
        print("  ❌ fastapi")
        missing.append("fastapi")

    try:
        from claude_agent_sdk import tool
        print("  ✅ claude-agent-sdk")
    except ImportError:
        print("  ❌ claude-agent-sdk")
        missing.append("claude-agent-sdk")

    if missing:
        print(f"\n⚠️  Missing dependencies: {', '.join(missing)}")
        print("\nInstall with:")
        print(f"  pip install {' '.join(missing)}")
        return False

    return True


def print_next_steps():
    """Print next steps"""
    print_header("✅ Setup Complete!")

    print("\n📝 Next Steps:")
    print("\n1. Start the backend server:")
    print("   cd backend")
    print("   uvicorn api.main:app --port 8001 --reload")

    print("\n2. Start the frontend (in another terminal):")
    print("   cd frontend")
    print("   npm run dev")

    print("\n3. Test the feature:")
    print("   - Visit http://localhost:3000/assistant")
    print("   - Click '渠道探索' button")
    print("   - Select channels (Reddit, Google, etc.)")
    print("   - Ask: '搜索Reddit上关于独立开发者的讨论'")

    print("\n4. Test API endpoints:")
    print("   curl http://localhost:8001/api/search/status")
    print("   curl http://localhost:8001/api/search/health")

    print("\n📚 Documentation:")
    print("   - CLAUDE.md - Full documentation")
    print("   - CHANNEL_SEARCH_TODO.md - Development plan")
    print("   - CHANNEL_SEARCH_IMPLEMENTATION.md - Implementation summary")

    print("\n🔧 Troubleshooting:")
    print("   - Run: python test_search.py")
    print("   - Check: backend/.env configuration")
    print("   - Verify: API keys are valid")


async def main():
    """Main function"""
    print_header("🚀 Channel Search Quick Start")

    print("\nThis script will help you set up and test the channel search feature.")

    # Check .env file
    if not check_env_file():
        return

    # Check API keys
    if not check_api_keys():
        print("\n⚠️  Please configure at least one search backend to continue.")
        return

    # Check dependencies
    if not check_dependencies():
        return

    # Test search
    search_ok = await test_search()

    if search_ok:
        # Test channel search
        await test_channel_search()

    # Print next steps
    print_next_steps()

    print("\n" + "=" * 70)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
