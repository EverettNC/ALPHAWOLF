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
AlphaWolf Core System
Part of The Christman AI Project - Powered by LumaCognify AI

Core cognitive and learning systems for AlphaWolf.
"""

import sys
import os

# Add core directory to path
sys.path.insert(0, os.path.dirname(__file__))

from core.memory_engine import MemoryEngine
from core.conversation_engine import ConversationEngine, get_conversation_engine
from core.ai_learning_engine import (
    SelfImprovementEngine,
    get_self_improvement_engine,
    learn_from_text
)
from core.local_reasoning_engine import (
    LocalReasoningEngine,
    get_local_reasoning_engine
)

__all__ = [
    'MemoryEngine',
    'ConversationEngine',
    'get_conversation_engine',
    'SelfImprovementEngine',
    'get_self_improvement_engine',
    'learn_from_text',
    'LocalReasoningEngine',
    'get_local_reasoning_engine'
]
