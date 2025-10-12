"""Derek's master learning coordinator."""

import logging
import time
from typing import Any, Dict

from ai_learning_engine import get_self_improvement_engine
from advanced_learning import AdvancedLearningSystem
from self_modifying_code import get_self_modifying_code_engine

logger = logging.getLogger(__name__)


class DerekLearningCoordinator:
    """Coordinates Derek's learning, analysis, and code improvement systems."""

    def __init__(self) -> None:
        self.self_improvement = get_self_improvement_engine()
        self.advanced_learning = AdvancedLearningSystem()
        self.code_modifier = get_self_modifying_code_engine()
        logger.info("Derek Learning Coordinator initialized")

    def start_all_systems(self) -> None:
        """Start the engines Derek uses for continuous learning."""
        try:
            self.self_improvement.start_learning()
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.error("Self-improvement engine failed to start: %s", exc)
        try:
            self.code_modifier.start_auto_mode()
        except Exception as exc:  # pragma: no cover
            logger.error("Code modifier auto-mode failed to start: %s", exc)
        else:
            logger.info("All Derek learning systems active")

    def daily_learning_cycle(self) -> None:
        """Run Derek's daily learning workflow."""
        current_time = time.time()

        for (
            source_id,
            source_info,
        ) in self.advanced_learning.external_knowledge_sources.items():
            last_update = source_info.get("last_update", 0)
            update_frequency = source_info.get("update_frequency", 86_400)
            if current_time - last_update < update_frequency:
                continue

            try:
                self.advanced_learning.process_knowledge_update(
                    source_id, source_info, current_time
                )
            except Exception as exc:  # pragma: no cover
                logger.error("Failed knowledge update for %s: %s", source_id, exc)
            else:
                source_info["last_update"] = current_time

        try:
            suggestions = self.self_improvement.get_improvement_suggestions()
        except Exception as exc:  # pragma: no cover
            logger.error("Failed to collect improvement suggestions: %s", exc)
            suggestions = []

        for suggestion in suggestions:
            if suggestion.get("severity") != "high":
                continue
            file_path = suggestion.get("module") or "unknown"
            description = suggestion.get("description", "High severity issue")
            try:
                queued = self.code_modifier.queue_modification(
                    file_path=file_path,
                    issue_description=description,
                    modification_type="bugfix",
                )
                if queued:
                    logger.info("Queued high severity fix for %s", file_path)
            except Exception as exc:  # pragma: no cover
                logger.error("Unable to queue modification for %s: %s", file_path, exc)

        try:
            self.advanced_learning.generate_daily_summary()
        except Exception as exc:  # pragma: no cover
            logger.error("Failed to generate daily summary: %s", exc)
        else:
            logger.info("Daily learning cycle complete")


derek_coordinator = DerekLearningCoordinator()


def start_derek_learning() -> None:
    """Initialize Derek's learning systems."""
    derek_coordinator.start_all_systems()
