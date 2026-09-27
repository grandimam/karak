from __future__ import annotations

from collections.abc import Callable
from collections.abc import Iterator

from karak.routing.base import BaseRouter
from karak.routing.matching import join_paths
from karak.routing.routes import RouteDefinition


class Router(BaseRouter):
    def __init__(
        self,
        *,
        routes: list[BaseRouter] | None = None,
    ) -> None:
        self._entries: list[BaseRouter | RouteDefinition] = []
        for route in routes or []:
            if not isinstance(route, BaseRouter):
                raise TypeError("routes must contain BaseRouter instances")
            self._entries.append(route)

    def get(self, path: str):
        return self._route(path, "GET")

    def post(self, path: str):
        return self._route(path, "POST")

    def _route(self, path: str, method: str):
        def wrap(handler: Callable):
            if path and not path.startswith("/"):
                raise ValueError("Route paths must be empty or start with '/'")
            self._entries.append(RouteDefinition(path, method, handler))
            return handler

        return wrap

    def flatten(self, prefix: str = "") -> Iterator[RouteDefinition]:
        for entry in self._entries:
            if isinstance(entry, BaseRouter):
                yield from entry.flatten(prefix)
            else:
                yield RouteDefinition(
                    join_paths(prefix, entry.path),
                    entry.method,
                    entry.handler,
                )
