from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

from karak.routing.base import BaseRouter
from karak.routing.matching import join_paths
from karak.routing.routes import RouteDefinition


@dataclass(slots=True)
class Mount(BaseRouter):
    path: str
    router: BaseRouter

    def __post_init__(self) -> None:
        if not self.path.startswith("/"):
            raise ValueError("Mount paths must start with '/'")

    def flatten(self, prefix: str = "") -> Iterator[RouteDefinition]:
        yield from self.router.flatten(join_paths(prefix, self.path))
