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
import json
from typing import Dict, List, Optional


class GestureManager:
    def __init__(self):
        self.categories: Dict[str, List[Dict[str, str]]] = {
            "Basic": [
                {"blink_once": "single blink"},
                {"blink_twice": "double blink"},
                {"look_left": "looking to the left"},
            ],
            "Greetings": [{"hand_wave": "wave hello"}],
            "Help": [{"head_tilt": "asking for help"}],
        }

    def add_gesture(
        self, gesture: str, meaning: str, category: str = "Uncategorized"
    ) -> bool:
        if category not in self.categories:
            self.categories[category] = []

        if any(gesture in g for g in self.categories[category]):
            return False

        self.categories[category].append({gesture: meaning})
        return True

    def remove_gesture(self, gesture: str) -> bool:
        for cat, gesture_list in self.categories.items():
            for g in gesture_list:
                if gesture in g:
                    gesture_list.remove(g)
                    return True
        return False

    def get_meaning(self, gesture: str) -> Optional[str]:
        for gestures in self.categories.values():
            for g in gestures:
                if gesture in g:
                    return g[gesture]
        return None

    def get_category(self, gesture: str) -> Optional[str]:
        for category, gestures in self.categories.items():
            for g in gestures:
                if gesture in g:
                    return category
        return None

    def list_all_gestures(self) -> List[str]:
        return [
            gesture for cat in self.categories.values() for g in cat for gesture in g
        ]

    def export_gestures(self, file_path: str):
        try:
            with open(file_path, "w") as f:
                json.dump(self.categories, f, indent=2)
            return True
        except Exception as e:
            print(f"Error exporting gestures: {e}")
            return False
