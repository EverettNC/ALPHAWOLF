# © 2025 The Christman AI Project. All rights reserved.
#
# This code is released as part of a trauma-informed, dignity-first AI ecosystem
# designed to protect, empower, and elevate vulnerable populations.
#
# By using, modifying, or distributing this software, you agree to uphold the following:
# 1. Truth — No deception, no manipulation.
# 2. Dignity — Respect the autonomy and humanity of all users.
# 3. Protection — Never use this to exploit or harm vulnerable individuals.
# 4. Transparency — Disclose all modifications and contributions clearly.
# 5. No Erasure — Preserve the mission and ethical origin of this work.
#
# This is not just code. This is redemption in code.
# Contact: lumacognify@thechristmanaiproject.com
# https://thechristmanaiproject.com
"""
Internet Mode Module
--------------------
Handles Derek's secure connection to online knowledge sources.

Phase 1: Controlled Internet Mode
Author: Everett Christman & The Christman AI Project
"""

import os
import sys
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional

# -------------------------------------------------------------
# Ensure project root is available for imports
# -------------------------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# -------------------------------------------------------------
# Internal module imports
# -------------------------------------------------------------
from perplexity_service import PerplexityService
from memory_engine import MemoryEngine
from brain import derek

# -------------------------------------------------------------
# Logging setup
# -------------------------------------------------------------
os.makedirs("logs/internet_activity", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [InternetMode] - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/internet_activity/internet_log.txt"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("InternetMode")

# -------------------------------------------------------------
# Configuration
# -------------------------------------------------------------
ENABLE_INTERNET_MODE = os.getenv("ENABLE_INTERNET_MODE", "false").lower() == "true"

# Initialize key systems
perplexity = PerplexityService()
memory_engine = MemoryEngine()

# -------------------------------------------------------------
# Query the Internet
# -------------------------------------------------------------
def query_internet(query: str) -> Dict[str, Any]:
    if not ENABLE_INTERNET_MODE:
        logger.warning("Internet Mode is disabled — returning local fallback.")
        return {"response": "Internet Mode is currently disabled."}
    try:
        logger.info(f"🌐 Querying Perplexity for: {query}")
        result = perplexity.generate_content(query)
        summary = result.get("content", "")
        _log_search(query, summary)
        memory_engine.save({
            "query": query,
            "summary": summary,
            "status": "success",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        return {
            "query": query,
            "summary": summary,
            "status": "success",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        logger.error(f"❌ Internet query failed: {e}")
        return {"error": str(e), "status": "failed"}




# -------------------------------------------------------------
# Logging Helper
# -------------------------------------------------------------
def _log_search(query: str, summary: str):
    """Log internet search interactions."""
    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "query": query,
        "summary": summary,
    }
    log_path = "logs/internet_activity/internet_log.jsonl"
    with open(log_path, "a") as f:
        f.write(json.dumps(log_entry) + "\n")
    logger.info(f"✅ Logged: {query}")

# -------------------------------------------------------------
# Interactive Test
# -------------------------------------------------------------
def main():
    print(f"\n🌍 Internet Mode Test — ENABLED? {ENABLE_INTERNET_MODE}\n")
    if not ENABLE_INTERNET_MODE:
        print("💡 To enable, run this first in your terminal:")
        print("   export ENABLE_INTERNET_MODE=True\n")

    while True:
        query = input("🔎 Ask AlphaWolf something (or 'exit'): ").strip()
        if query.lower() in ("exit", "quit"):
            print("👋 Exiting Internet Mode.")
            break

        result = query_internet(query)
        print(f"\n🧠 AlphaWolf (Internet): {result.get('summary', 'No response')}\n")

# -------------------------------------------------------------
if __name__ == "__main__":
    main()


