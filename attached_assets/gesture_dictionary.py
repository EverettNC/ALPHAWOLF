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
AlphaVox - Gesture Dictionary Module
------------------------------------
This module provides a direct mapping approach for gestures and their meanings,
which complements the AI learning system by providing immediate fallback options.
"""

import json
import logging
import os
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class GestureDictionary:
    def __init__(self, data_file: Optional[str] = None, allow_override: bool = False):
        """Initialize the gesture dictionary with default mappings."""
        # Core gestures that shouldn't be overridden unless explicitly allowed
        self.core_gestures = {
            "blink_once": "Hello",
            "blink_twice": "Yes",
            "look_left": "No",
            "hand_wave": "Goodbye",
            "head_tilt": "I need help",
            "center_gaze": "I'm listening",
            "left_gaze": "Previous option",
            "right_gaze": "Next option",
        }

        self.custom_gestures: Dict[str, str] = {}
        self.allow_override = allow_override

        # Set custom gesture file path
        base_dir = os.path.dirname(os.path.dirname(__file__))
        self.data_file = (
            data_file
            or os.getenv("GESTURE_DATA_PATH")
            or os.path.join(base_dir, "data", "custom_gestures.json")
        )

        self._load_custom_gestures()

    def get_meaning(self, gesture: str, use_fallback: bool = True) -> Optional[str]:
        """Get the meaning of a gesture."""
        if gesture in self.custom_gestures:
            return self.custom_gestures[gesture]
        return self.core_gestures.get(gesture) if use_fallback else None

    def add_gesture(self, gesture: str, meaning: str) -> bool:
        """Add a new custom gesture or update an existing one."""
        if not gesture or len(gesture) < 3:
            logger.warning(f"Invalid gesture name: {gesture}")
            return False

        if gesture in self.core_gestures and not self.allow_override:
            logger.warning(f"Attempt to override core gesture '{gesture}' denied.")
            return False

        self.custom_gestures[gesture] = meaning
        self._save_custom_gestures()
        logger.info(f"Added/updated gesture: {gesture} -> {meaning}")
        return True

    def remove_gesture(self, gesture: str) -> bool:
        """Remove a custom gesture."""
        if gesture in self.custom_gestures:
            del self.custom_gestures[gesture]
            self._save_custom_gestures()
            logger.info(f"Removed gesture: {gesture}")
            return True
        return False

    def list_all_gestures(self) -> Dict[str, str]:
        """List all gestures (core and custom)."""
        all_gestures = self.core_gestures.copy()
        all_gestures.update(self.custom_gestures)
        return all_gestures

    def list_custom_gestures(self) -> Dict[str, str]:
        """List only custom gestures."""
        return self.custom_gestures.copy()

    def find_gesture_by_meaning(self, meaning: str) -> List[str]:
        """Find all gestures with a specific meaning."""
        return [
            gesture
            for gesture, m in self.list_all_gestures().items()
            if m.lower() == meaning.lower()
        ]

    def print_dictionary(self):
        """Print the full gesture dictionary (CLI-style)."""
        for gesture, meaning in self.list_all_gestures().items():
            print(f"{gesture:20} -> {meaning}")

    def _save_custom_gestures(self):
        """Save custom gestures to a JSON file."""
        try:
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            with open(self.data_file, "w") as f:
                json.dump(self.custom_gestures, f, indent=2)
            logger.info(
                f"Saved {len(self.custom_gestures)} custom gestures to {self.data_file}"
            )
        except Exception as e:
            logger.error(f"Error saving custom gestures: {e}")

    def _load_custom_gestures(self):
        """Load custom gestures from a JSON file."""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, "r") as f:
                    self.custom_gestures = json.load(f)
                logger.info(
                    f"Loaded {len(self.custom_gestures)} custom gestures from {self.data_file}"
                )
        except Exception as e:
            logger.error(f"Error loading custom gestures: {e}")
            self.custom_gestures = {}
