"""Autonomous Boot Module for Derek's Self-Improvement"""

import logging
from ai_learning_engine import get_self_improvement_engine

logger = logging.getLogger(__name__)


def main():
    """Start Derek's autonomous learning engine."""
    logger.info("Launching Derek's autonomous learning engine...")
    engine = get_self_improvement_engine()
    engine.start_learning()
    logger.info("Derek's self-improvement engine is now active.")
