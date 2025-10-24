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
import re
from typing import Optional


class GestureValidator:
    VALID_GESTURE_PATTERN = r"^[a-z][a-z0-9_]{2,29}$"

    @classmethod
    def validate_gesture_name(cls, gesture: str) -> tuple[bool, Optional[str]]:
        """Validate gesture name format."""
        if not gesture:
            return False, "Gesture name cannot be empty"

        if not re.match(cls.VALID_GESTURE_PATTERN, gesture):
            return (
                False,
                "Gesture must start with a letter, contain only lowercase letters, numbers, and underscores, and be 3-30 characters long",
            )

        return True, None

    @classmethod
    def validate_category(cls, category: str) -> tuple[bool, Optional[str]]:
        """Validate category name."""
        if not category:
            return False, "Category name cannot be empty"

        if not re.match(r"^[a-zA-Z][a-zA-Z0-9_\s]{2,29}$", category):
            return (
                False,
                "Category must start with a letter and be 3-30 characters long",
            )

        return True, None

    @classmethod
    def validate_meaning(cls, meaning: str) -> tuple[bool, Optional[str]]:
        """Validate gesture meaning."""
        if not meaning.strip():
            return False, "Meaning cannot be empty"

        if len(meaning) > 100:
            return False, "Meaning must be less than 100 characters"

        return True, None
