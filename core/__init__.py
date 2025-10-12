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
