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
"""Combined autonomous learning and self-improvement runner for AlphaWolf."""

import asyncio
import logging
import aioschedule as schedule
import time
from datetime import datetime

# from core.autonomous_learner import AutonomousLearner  # TODO: Create this module
from self_modifying_code import CodeModifier

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [AlphaWolf] - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# Temporary placeholder until autonomous_learner module is created
class AutonomousLearner:
    """Placeholder for autonomous learning system"""
    async def autonomous_learning_session(self):
        return {
            "total_articles_learned": 0,
            "chambers_processed": []
        }


class AlphaWolfAutonomousSystem:
    """Coordinates AlphaWolf's learning chambers and self-modification cycles."""

    def __init__(self, safe_mode: bool = False) -> None:
        self.learner = AutonomousLearner()
        self_modifying_code = CodeModifier(backup_dir="./memory/daily")  # CodeModifier uses backup_dir parameter, not safe_mode
        self.safe_mode = safe_mode
        self.is_running = False

    async def daily_learning_cycle(self) -> None:
        logger.info("Starting daily learning cycle")
        try:
            report = await self.learner.autonomous_learning_session()
            logger.info(
                "Learning cycle complete: %s articles across %s chambers",
                report["total_articles_learned"],
                len(report["chambers_processed"]),
            )
        except Exception as exc:
            logger.error("Learning cycle failed: %s", exc)

    # Note: Weekly self-improvement is still synchronous.
    # If it becomes I/O bound, consider making it async as well.
    def weekly_self_improvement_cycle(self) -> None:
        logger.info("Starting weekly self-improvement cycle")
        try:
            report = self.modifier.improve_codebase()
            logger.info(
                "Self-improvement cycle complete: %s files modified",
                report["files_modified"],
            )
        except Exception as exc:
            logger.error("Self-improvement cycle failed: %s", exc)

    async def start_autonomous_operation(self) -> None:
        logger.info("AlphaWolf Autonomous System activated")
        self.is_running = True

        # Schedule the asynchronous daily learning cycle
        schedule.every().day.at("02:00").do(self.daily_learning_cycle)

        # Schedule the synchronous weekly self-improvement cycle
        schedule.every().sunday.at("03:00").do(self.weekly_self_improvement_cycle)

        logger.info("Scheduler started. Waiting for the first run.")
        while self.is_running:
            await schedule.run_pending()
            await asyncio.sleep(1)  # Use asyncio.sleep in an async function

    def stop(self) -> None:
        self.is_running = False
        logger.info("AlphaWolf Autonomous System deactivated")


async def main() -> None:
    system = AlphaWolfAutonomousSystem()
    try:
        await system.start_autonomous_operation()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received; shutting down")
        system.stop()
    except asyncio.CancelledError:
        logger.info("Async operation cancelled; shutting down")
        system.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application shutdown.")

