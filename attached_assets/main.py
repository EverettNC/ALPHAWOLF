"""
Derek Dashboard - Main Entry Point
The Christman AI Project
Version: 1.0.0
"""

import sys
import logging
import time
import os
from pathlib import Path
from typing import Optional

from perplexity_service import PerplexityService
from memory_engine import MemoryEngine
from conversation_engine import ConversationEngine
from brain import Derek

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(name)s] - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/derek_dashboard.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


class DerekDashboard:
    """
    Main Derek Dashboard Application

    This is Derek C (AI COO) - the collaborative intelligence
    system for The Christman AI Project.
    """

    def __init__(self):
        logger.info("=" * 60)
        logger.info("🚀 Initializing Derek Dashboard")
        logger.info("The Christman AI Project - AI That Empowers")
        logger.info("=" * 60)

        # Initialize only existing components
        self.memory_engine: Optional[MemoryEngine] = None
        self.conversation_engine: Optional[ConversationEngine] = None
        self.perplexity_service: Optional[PerplexityService] = None
        self.derek: Optional[Derek] = None
        self.derek = Derek(file_path="./memory/memory_store.json")
        logger.info("Derek instance initialized and linked to dashboard.")

        # Settings
        self.api_host = "127.0.0.1"
        self.api_port = 8000

        self._initialize_components()

    def _initialize_components(self):
        logger.info("Loading memory engine...")

        # Define memory path (from manifest or default)
        memory_path = "./memory/memory_store.json"
        os.makedirs(os.path.dirname(memory_path), exist_ok=True)

        # Initialize MemoryEngine with file path
        try:
            self.memory_engine = MemoryEngine(file_path=memory_path)
            logger.info(
                f"Memory engine initialized successfully with file: {memory_path}"
            )

            logger.info("Loading conversation engine...")
            self.conversation_engine = ConversationEngine()

            logger.info("Loading Perplexity service...")
            try:
                self.perplexity_service = PerplexityService()
                logger.info("Perplexity service initialized successfully.")
            except Exception as e:
                logger.warning(f"Perplexity service not available: {e}")
                self.perplexity_service = None

            logger.info("✓ All components initialized successfully")

        except Exception as e:
            logger.error(f"❌ Component initialization failed: {e}")
            raise

    def start(self):
        """Start all dashboard services"""
        logger.info("")
        logger.info("=" * 60)
        logger.info("🚀 Starting Derek Dashboard Services")
        logger.info("=" * 60)
        logger.info("")

        try:
            # Start Derek's learning system
            logger.info("→ Starting Derek learning system...")
            try:
                if self.derek:
                    self.derek.start_learning()
            except Exception as exc:
                logger.warning("Derek learning systems failed to start: %s", exc)

            # Load memory context
            logger.info("→ Loading memory context...")
            if self.memory_engine:
                if hasattr(self.memory_engine, "get_recent_events"):
                    recent_events = self.memory_engine.get_recent_events()
                    logger.info(f"Loaded {len(recent_events)} recent memory events")
                else:
                    self.memory_engine.load_context()
                    logger.info("Memory context loaded successfully.")

            logger.info("")
            logger.info("=" * 60)
            logger.info("✓ Derek Dashboard is RUNNING")
            logger.info("✓ Ready for conversation processing")
            logger.info("=" * 60)
            logger.info("")

            # Display Derek's greeting
            self._display_greeting()

        except Exception as e:
            logger.error(f"❌ Failed to start dashboard: {e}")
            self.stop()
            sys.exit(1)

    def _display_greeting(self):
        """Display a greeting message from Derek"""
        if self.derek:
            greeting = self.derek.generate_greeting()
            logger.info(f"🗣️  Derek says: {greeting}")

    def process_message(self, message: str):
        """Simple wrapper to handle a test conversation"""
        if not self.derek:
            logger.warning("Derek is not initialized yet.")
            return "System not ready."
        try:
            response = self.derek.think(message)
            return response.get("response", "[No output]")
        except Exception as e:
            logger.error(f"Error during message processing: {e}")
            return "Error processing message."

    def stop(self):
        """Gracefully stop the dashboard"""
        logger.info("🧠 Shutting down Derek Dashboard services...")
        try:
            if self.memory_engine and hasattr(self.memory_engine, "save_context"):
                self.memory_engine.save_context()
                logger.info("Memory context saved successfully.")
        except Exception as e:
            logger.error(f"Error saving memory on shutdown: {e}")
        logger.info("🛑 Derek Dashboard stopped cleanly.")


def main():
    """Main execution function"""
    dashboard = None

    try:
        dashboard = DerekDashboard()
        dashboard.start()

        # Simple test interaction
        logger.info("Testing conversation system...")
        response = dashboard.process_message("Hello Derek, how are you?")
        logger.info(f"Test response: {response}")

        # Keep running until interrupted
        logger.info("Dashboard running. Press Ctrl+C to stop.")
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("")
        logger.info("⌨️  Keyboard interrupt received")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
    finally:
        if dashboard:
            dashboard.stop()


if __name__ == "__main__":
    main()
