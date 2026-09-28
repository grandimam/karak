from __future__ import annotations

from collections.abc import Callable
from collections.abc import Iterator

from karak.routing.route import RouteDefinition


class Router:
    def __init__(self) -> None:
        self._entries: list[RouteDefinition] = []

    def get(self, path: str):
        return self._route(path, "GET")

    def post(self, path: str):
        return self._route(path, "POST")

    def _route(self, path: str, method: str):
        def wrap(handler: Callable):
            if not path.startswith("/"):
                raise ValueError("Route paths must start with '/'")
            self._entries.append(RouteDefinition(path, method, handler))
            return handler

        return wrap

    def __iter__(self) -> Iterator[RouteDefinition]:
        return iter(self._entries)
