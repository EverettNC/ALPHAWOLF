# memory_engine.py
import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class MemoryEngine:
    """Handles memory persistence, retrieval, and contextual queries."""

    def __init__(self, file_path: str = "./memory/memory_store.json"):
        self.file_path = file_path
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        self._memory: List[Dict[str, Any]] = []
        self.load_memory()

    def load_memory(self):
        """Load stored memory entries from disk."""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    self._memory = json.load(f)
                logger.info(f"Loaded {len(self._memory)} memory entries.")
            except Exception as e:
                logger.error(f"Failed to load memory file: {e}")
                self._memory = []
        else:
            logger.info("No existing memory file found, starting fresh.")
            self._memory = []

    def save_memory(self):
        """Persist memory to disk."""
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self._memory, f, indent=2)
            logger.info(f"Saved {len(self._memory)} memory entries.")
        except Exception as e:
            logger.error(f"Failed to save memory: {e}")

    def save(self, entry: Dict[str, Any]):
        """Save a new entry into memory."""
        entry["timestamp"] = datetime.utcnow().isoformat() + "Z"
        self._memory.append(entry)
        self.save_memory()
        logger.debug(f"Stored new memory entry: {entry}")

    def query(self, text: str, intent: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieve contextually relevant memory entries.
        This is a minimal working version so Derek can recall context.
        """
        logger.debug(f"Querying memory for context (intent={intent}): {text}")

        # For now, we’ll return the last few memory items
        if not self._memory:
            return {"context": "No prior context found."}

        # Optionally filter by intent
        if intent:
            relevant = [m for m in self._memory if m.get("intent") == intent]
        else:
            relevant = self._memory[-5:]  # last 5 items

        # Return summarized context
        context_snippets = [
            f"{m.get('input', '')} → {m.get('output', '')}" for m in relevant[-5:]
        ]
        return {"context": "\n".join(context_snippets[-5:])}

    def get_recent_events(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Return the most recent memory events."""
        return list(reversed(self._memory[-limit:]))

    def clear(self):
        """Erase all memory (use with caution)."""
        self._memory = []
        self.save_memory()
        logger.warning("All memory has been cleared.")
