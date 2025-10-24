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
"""UI module registration for AlphaWolf Dashboard."""

from typing import Callable, Dict


class UIModuleRegistry:
    """Stores UI component factories."""

    def __init__(self):
        self._registry: Dict[str, Callable] = {}

    def register(self, name: str, factory: Callable) -> None:
        self._registry[name] = factory

    def get(self, name: str) -> Callable:
        return self._registry[name]

    def available(self) -> Dict[str, Callable]:
        return dict(self._registry)
