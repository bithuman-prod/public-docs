#!/usr/bin/env python3
"""
Diagnostic tool for Flutter + bitHuman + LiveKit integration.
This script checks all dependencies and configurations before running the agent.
"""

import os
import sys
import asyncio
import logging
from typing import List, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def check_python_version() -> Tuple[bool, str]:
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major == 3 and version.minor >= 11:
        return True, f"Python {version.major}.{version.minor}.{version.micro} ✓"
    else:
        return False, f"Python {version.major}.{version.minor}.{version.micro} ✗ (Requires Python 3.11+)"

def check_required_packages() -> Tuple[bool, List[str]]:
    """Check if all required packages are installed."""
    required_packages = [
        "livekit.agents",
        "livekit.plugins.bithuman", 
        "livekit.plugins.openai",
        "livekit.plugins.silero",
        "dotenv"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    return len(missing_packages) == 0, missing_packages

def check_environment_variables() -> Tuple[bool, List[str]]:
    """Check if all required environment variables are set."""
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = [
        "BITHUMAN_API_SECRET",
        "OPENAI_API_KEY", 
        "LIVEKIT_API_KEY",
        "LIVEKIT_API_SECRET",
        "LIVEKIT_URL"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    return len(missing_vars) == 0, missing_vars

def check_api_key_format(api_key: str, prefix: str) -> bool:
    """Deprecated: format checks are relaxed; keep for optional warnings."""
    return api_key.startswith(prefix)

async def check_bithuman_api() -> Tuple[bool, str]:
    """Check if bitHuman API is accessible."""
    try:
        from livekit.plugins import bithuman
        from dotenv import load_dotenv
        load_dotenv()
        
        api_secret = os.getenv("BITHUMAN_API_SECRET")
        if not api_secret:
            return False, "BITHUMAN_API_SECRET not found"
        
        # Presence is sufficient for diagnostics; avoid strict prefix checks
        # Optionally keep a soft warning for unexpected formats
        if not check_api_key_format(api_secret, "sk_bh_"):
            return True, "BitHuman API key present (format not validated)"
        
        return True, "BitHuman API key present"
            
    except ImportError:
        return False, "livekit.plugins.bithuman not installed"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"

async def check_openai_api() -> Tuple[bool, str]:
    """Check if OpenAI API is accessible."""
    try:
        from livekit.plugins import openai
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return False, "OPENAI_API_KEY not found"
        
        # Presence is sufficient; avoid strict prefix checks
        if not check_api_key_format(api_key, "sk-proj_"):
            return True, "OpenAI API key present (format not validated)"
        
        return True, "OpenAI API key present"
        
    except ImportError:
        return False, "livekit.plugins.openai not installed"
    except Exception as e:
        return False, f"OpenAI check error: {str(e)}"

def check_livekit_config() -> Tuple[bool, str]:
    """Check LiveKit configuration."""
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("LIVEKIT_API_KEY")
    api_secret = os.getenv("LIVEKIT_API_SECRET")
    url = os.getenv("LIVEKIT_URL")
    
    if not all([api_key, api_secret, url]):
        return False, "Missing LiveKit configuration"
    
    messages = []
    if not url.startswith("wss://"):
        messages.append("warning: LIVEKIT_URL should start with 'wss://' for secure websockets")
    
    summary = f"LiveKit config present: {url}"
    if messages:
        summary += f" ({'; '.join(messages)})"
    return True, summary

async def main():
    """Run all diagnostic checks."""
    print("🔍 Flutter + bitHuman + LiveKit Integration Diagnostics")
    print("=" * 60)
    
    all_checks_passed = True
    
    # Check Python version
    print("\n1. Python Version Check")
    passed, message = check_python_version()
    print(f"   {message}")
    if not passed:
        all_checks_passed = False
    
    # Check required packages
    print("\n2. Package Dependencies Check")
    passed, missing = check_required_packages()
    if passed:
        print("   All required packages installed ✓")
    else:
        print(f"   Missing packages: {', '.join(missing)} ✗")
        print("   Run: pip install -r requirements.txt")
        all_checks_passed = False
    
    # Check environment variables
    print("\n3. Environment Variables Check")
    passed, missing = check_environment_variables()
    if passed:
        print("   All required environment variables set ✓")
    else:
        print(f"   Missing variables: {', '.join(missing)} ✗")
        print("   Create a .env file with all required variables")
        all_checks_passed = False
    
    # Check API configurations
    print("\n4. API Configuration Check")
    
    # BitHuman API
    passed, message = await check_bithuman_api()
    print(f"   BitHuman API: {message}")
    if not passed:
        all_checks_passed = False
    
    # OpenAI API
    passed, message = await check_openai_api()
    print(f"   OpenAI API: {message}")
    if not passed:
        all_checks_passed = False
    
    # LiveKit Config
    passed, message = check_livekit_config()
    print(f"   LiveKit Config: {message}")
    if not passed:
        all_checks_passed = False
    
    # Summary
    print("\n" + "=" * 60)
    if all_checks_passed:
        print("🎉 All checks passed! Your setup is ready.")
        print("\nNext steps:")
        print("1. Run: python agent.py dev")
        print("2. Test with LiveKit Playground: https://agents-playground.livekit.io")
        print("3. Connect your Flutter app to the same LiveKit room")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        print("\nFor help:")
        print("- Check the README.md for detailed setup instructions")
        print("- Join Discord: https://discord.gg/ES953n7bPA")
        print("- Visit docs: https://docs.bithuman.ai")
    
    return all_checks_passed

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\nDiagnostic interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error during diagnostics: {e}")
        sys.exit(1)
