"""
Event loop handler for Derek Dashboard
Manages continuous processes and background tasks
"""

import asyncio
import logging
from typing import Optional, List, Callable
from datetime import datetime

logger = logging.getLogger(__name__)


class EventLoop:
    """
    Manages background processes and event handling for Derek Dashboard
    """

    def __init__(self):
        self.running = False
        self.tasks: List[asyncio.Task] = []
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        logger.info("Event loop initialized")

    async def heartbeat(self):
        """System heartbeat - runs every 30 seconds"""
        while self.running:
            try:
                logger.debug(f"💓 Heartbeat at {datetime.now().isoformat()}")
                # Add health checks, monitoring, etc.
                await asyncio.sleep(30)
            except asyncio.CancelledError:
                break
            except Exception as e:  # pragma: no cover - log unexpected issues
                logger.error(f"Heartbeat error: {e}")

    async def memory_consolidation(self):
        """Periodic memory consolidation - runs every 5 minutes"""
        while self.running:
            try:
                logger.debug("🧠 Running memory consolidation...")
                # Consolidate short-term to long-term memory
                await asyncio.sleep(300)  # 5 minutes
            except asyncio.CancelledError:
                break
            except Exception as e:  # pragma: no cover
                logger.error(f"Memory consolidation error: {e}")

    async def analytics_processing(self):
        """Process analytics - runs every 10 minutes"""
        while self.running:
            try:
                logger.debug("📊 Processing analytics...")
                # Process usage analytics, patterns, etc.
                await asyncio.sleep(600)  # 10 minutes
            except asyncio.CancelledError:
                break
            except Exception as e:  # pragma: no cover
                logger.error(f"Analytics processing error: {e}")

    def register_task(self, coro: Callable):
        """Register a custom async task"""
        if self.loop and self.running:
            task = self.loop.create_task(coro())
            self.tasks.append(task)
            logger.info(f"Registered new task: {coro.__name__}")

    def start(self):
        """Start the event loop"""
        if self.running:
            logger.warning("Event loop already running")
            return

        logger.info("Starting event loop...")
        self.running = True

        try:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

            # Start background tasks
            self.tasks = [
                self.loop.create_task(self.heartbeat()),
                self.loop.create_task(self.memory_consolidation()),
                self.loop.create_task(self.analytics_processing()),
            ]

            logger.info("✓ Event loop started with background tasks")

            # Run until stopped
            self.loop.run_forever()

        except Exception as e:  # pragma: no cover
            logger.error(f"Event loop error: {e}")
        finally:
            self.stop()

    def stop(self):
        """Stop the event loop"""
        if not self.running:
            return

        logger.info("Stopping event loop...")
        self.running = False

        # Cancel all tasks
        for task in self.tasks:
            task.cancel()

        # Stop the loop
        if self.loop:
            self.loop.stop()
            self.loop.close()

        logger.info("✓ Event loop stopped")


# Singleton instance
event_loop = EventLoop()
