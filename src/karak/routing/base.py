from abc import ABC
from abc import abstractmethod
from collections.abc import Iterator

from karak.routing.routes import RouteDefinition


class BaseRouter(ABC):
    @abstractmethod
    def flatten(self, prefix: str = "") -> Iterator[RouteDefinition]:
        raise NotImplementedError
