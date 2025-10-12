"""UI module registration for Derek Dashboard."""

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
