"""Routing helpers for Derek Dashboard."""

from typing import Callable, Dict


class Router:
    """Simple in-memory router mapping."""

    def __init__(self):
        self._routes: Dict[str, Callable] = {}

    def add_route(self, path: str, handler: Callable) -> None:
        self._routes[path] = handler

    def resolve(self, path: str) -> Callable:
        return self._routes[path]

    def available_routes(self) -> Dict[str, Callable]:
        return dict(self._routes)
