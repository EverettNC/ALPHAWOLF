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
"""Basic intent detection module."""


def detect_intent(text: str) -> str:
    """Detect intent from input text."""
    text_lower = text.lower()

    if any(word in text_lower for word in ["hello", "hi", "hey"]):
        return "greeting"
    elif any(word in text_lower for word in ["bye", "goodbye", "see you"]):
        return "farewell"
    elif any(word in text_lower for word in ["help", "assist", "support"]):
        return "help"
    elif any(word in text_lower for word in ["what", "how", "when", "where", "why"]):
        return "question"
    else:
        return "general"
