#!/usr/bin/env python3
"""
BitHuman Avatar Diagnostic Tool

This script helps diagnose common issues with BitHuman avatar setup.
Run this before running the main agent to identify potential problems.
"""

import asyncio
import logging
import os
import sys

import aiohttp
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


async def check_bithuman_api():
    """Test BitHuman API connectivity and authentication"""
    logger.info("🔍 Checking BitHuman API...")

    api_secret = os.getenv("BITHUMAN_API_SECRET")
    if not api_secret:
        logger.error("❌ BITHUMAN_API_SECRET not found in environment variables")
        return False

    if not api_secret.startswith("sk_bh_"):
        logger.warning(
            "⚠️  BITHUMAN_API_SECRET doesn't start with 'sk_bh_' - this might be incorrect"
        )

    api_url = os.getenv("BITHUMAN_API_URL", "https://api.bithuman.ai")

    try:
        async with aiohttp.ClientSession() as session:
            # Test API connectivity (note: this is a basic connectivity test)
            headers = {"Authorization": f"Bearer {api_secret}"}
            timeout = aiohttp.ClientTimeout(total=10)
            async with session.get(
                f"{api_url}/health", headers=headers, timeout=timeout
            ) as response:
                if response.status == 200:
                    logger.info(
                        "✅ BitHuman API is accessible and authentication works"
                    )
                    return True
                else:
                    logger.error(f"❌ BitHuman API returned status {response.status}")
                    return False
    except Exception as e:
        logger.error(f"❌ Failed to connect to BitHuman API: {str(e)}")
        return False


def check_avatar_id():
    """Check avatar ID configuration"""
    logger.info("🎭 Checking Avatar ID...")

    avatar_id = os.getenv("BITHUMAN_AVATAR_ID", "A33NZN6384")
    logger.info(f"Using Avatar ID: {avatar_id}")

    if avatar_id == "A33NZN6384":
        logger.warning(
            "⚠️  Using default avatar ID. Consider trying a different one if you encounter issues."
        )
        logger.info(
            "💡 Browse available avatars at: https://imaginex.bithuman.ai/#community"
        )

    return True


def check_openai_api():
    """Check OpenAI API configuration"""
    logger.info("🤖 Checking OpenAI API...")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("❌ OPENAI_API_KEY not found in environment variables")
        return False

    if not (api_key.startswith("sk-proj_") or api_key.startswith("sk-")):
        logger.warning("⚠️  OPENAI_API_KEY format looks unusual")

    logger.info("✅ OpenAI API key is configured")
    return True


def check_livekit_config():
    """Check LiveKit configuration"""
    logger.info("📡 Checking LiveKit configuration...")

    api_key = os.getenv("LIVEKIT_API_KEY")
    api_secret = os.getenv("LIVEKIT_API_SECRET")
    url = os.getenv("LIVEKIT_URL")

    issues = []
    if not api_key:
        issues.append("LIVEKIT_API_KEY missing")
    elif not api_key.startswith("API"):
        issues.append("LIVEKIT_API_KEY should start with 'API'")

    if not api_secret:
        issues.append("LIVEKIT_API_SECRET missing")

    if not url:
        issues.append("LIVEKIT_URL missing")
    elif not url.startswith("wss://"):
        issues.append("LIVEKIT_URL should start with 'wss://'")

    if issues:
        logger.error(f"❌ LiveKit configuration issues: {', '.join(issues)}")
        return False

    logger.info("✅ LiveKit configuration looks good")
    return True


def check_dependencies():
    """Check if required packages are installed"""
    logger.info("📦 Checking dependencies...")

    required_packages = [
        "livekit-agents",
        "livekit-plugins-bithuman",
        "livekit-plugins-openai",
        "livekit-plugins-silero",
        "python-dotenv",
    ]

    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        logger.error(f"❌ Missing packages: {', '.join(missing_packages)}")
        logger.info("💡 Install with: pip install -r requirements.txt")
        return False

    logger.info("✅ All required packages are installed")
    return True


async def main():
    """Run all diagnostic checks"""
    logger.info("🚀 Starting BitHuman Avatar Diagnostics")
    logger.info("=" * 50)

    checks = [
        ("Dependencies", check_dependencies),
        ("OpenAI API", check_openai_api),
        ("LiveKit Config", check_livekit_config),
        ("Avatar ID", check_avatar_id),
        ("BitHuman API", check_bithuman_api),
    ]

    results = {}
    for name, check_func in checks:
        try:
            if asyncio.iscoroutinefunction(check_func):
                result = await check_func()
            else:
                result = check_func()
            results[name] = result
        except Exception as e:
            logger.error(f"❌ {name} check failed with error: {str(e)}")
            results[name] = False

        logger.info("-" * 30)

    # Summary
    logger.info("📊 DIAGNOSTIC SUMMARY")
    logger.info("=" * 50)

    all_passed = True
    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"{name}: {status}")
        if not passed:
            all_passed = False

    logger.info("-" * 50)

    if all_passed:
        logger.info("🎉 All checks passed! Your setup should work.")
        logger.info("💡 If you still encounter issues, try:")
        logger.info("   - Using a different avatar ID")
        logger.info("   - Checking BitHuman service status")
        logger.info("   - Waiting a few minutes and trying again")
    else:
        logger.error(
            "⚠️  Some checks failed. Please fix the issues above before running the agent."
        )
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
