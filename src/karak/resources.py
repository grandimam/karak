from __future__ import annotations

import inspect

from collections.abc import AsyncGenerator
from collections.abc import AsyncIterator
from collections.abc import Callable
from collections.abc import Coroutine
from collections.abc import Generator
from collections.abc import Iterator
from contextlib import AsyncExitStack
from contextlib import asynccontextmanager
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import get_args
from typing import get_origin
from typing import get_type_hints
from typing import overload

from karak.request import Request


RESOURCE_STATE_KEY = "karak.resources"
_current_session: ContextVar[_ResourceSession | None] = ContextVar(
    "karak_resource_session", default=None
)


@dataclass(frozen=True, slots=True)
class ResourceContext[T]:
    """One resolved value supplied to a resource factory or route handler."""

    value: T


class Resource[T]:
    """A resource declaration; instances belong to application lifespans."""

    def __init__(self, factory: Callable[..., Any]) -> None:
        self.factory = factory

    def get(self) -> T:
        """Return this resource's initialized instance in the active application."""
        session = _current_session.get()
        if not session or not session.active:
            raise RuntimeError("Resource access requires an active application lifespan")
        if self not in session.values:
            raise RuntimeError(
                f"Resource '{self.factory.__name__}' is not initialized in this application"
            )
        return session.values[self]


@overload
def resource[T](factory: Callable[..., AsyncIterator[T]]) -> Resource[T]: ...


@overload
def resource[T](factory: Callable[..., Iterator[T]]) -> Resource[T]: ...


@overload
def resource[T](factory: Callable[..., Coroutine[Any, Any, T]]) -> Resource[T]: ...


@overload
def resource[T](factory: Callable[..., T]) -> Resource[T]: ...


def resource(factory: Callable[..., Any]) -> Resource[Any]:
    """Declare a factory for registration in Karak(resources=[...])."""
    return Resource(factory)


@dataclass
class _ResourceSession:
    registry: _ResourceRegistry
    values: dict[Resource[Any], Any] = field(default_factory=dict)
    active: bool = True


def _provided_type(item: Resource[Any], hints: dict[str, Any]) -> Any:
    annotation = hints.get("return", inspect.Signature.empty)
    factory = item.factory
    if inspect.isasyncgenfunction(factory):
        if get_origin(annotation) not in (AsyncIterator, AsyncGenerator):
            raise TypeError(
                f"Resource '{factory.__name__}' must declare AsyncIterator[T] "
                "or AsyncGenerator[T, None]"
            )
        arguments = get_args(annotation)
        annotation = arguments[0] if arguments else inspect.Signature.empty
    elif inspect.isgeneratorfunction(factory):
        if get_origin(annotation) not in (Iterator, Generator):
            raise TypeError(
                f"Resource '{factory.__name__}' must declare Iterator[T] "
                "or Generator[T, None, None]"
            )
        arguments = get_args(annotation)
        annotation = arguments[0] if arguments else inspect.Signature.empty
    if annotation is inspect.Signature.empty or annotation is Any:
        raise TypeError(f"Resource '{factory.__name__}' requires a concrete return type")
    return annotation


class _ResourceRegistry:
    def __init__(self, resources: list[Resource[Any]]) -> None:
        self._dependencies: dict[Resource[Any], dict[str, Resource[Any]]] = {}
        self._order: list[Resource[Any]] = []
        providers = {}
        self._providers = providers
        hints_by_resource = {}
        for item in resources:
            if not isinstance(item, Resource):
                raise TypeError("Register resources declared with @resource")
            if item in hints_by_resource:
                raise ValueError(f"Resource '{item.factory.__name__}' is registered twice")
            hints = get_type_hints(item.factory)
            provided = _provided_type(item, hints)
            if provided is Request:
                raise ValueError("Request is a built-in request-scoped resource")
            if provided in providers:
                previous = providers[provided]
                raise ValueError(
                    f"Ambiguous resource type {provided!r}: "
                    f"'{previous.factory.__name__}' and '{item.factory.__name__}'"
                )
            providers[provided] = item
            hints_by_resource[item] = hints

        for item, hints in hints_by_resource.items():
            dependencies = {}
            for name, parameter in inspect.signature(item.factory).parameters.items():
                if parameter.kind in (
                    inspect.Parameter.POSITIONAL_ONLY,
                    inspect.Parameter.VAR_POSITIONAL,
                    inspect.Parameter.VAR_KEYWORD,
                ):
                    raise TypeError(
                        f"Resource '{item.factory.__name__}' parameter '{name}' "
                        "must accept a keyword argument"
                    )
                annotation = hints.get(name)
                if get_origin(annotation) is not ResourceContext:
                    raise TypeError(
                        f"Resource '{item.factory.__name__}' parameter '{name}' "
                        "must declare ResourceContext[T]"
                    )
                dependency_type = get_args(annotation)[0]
                if dependency_type is Request:
                    raise ValueError("Application resources cannot depend on request-scoped Request")
                if dependency_type not in providers:
                    raise ValueError(
                        f"Resource '{item.factory.__name__}' parameter '{name}' "
                        f"has no registered provider for {dependency_type!r}"
                    )
                dependencies[name] = providers[dependency_type]
            self._dependencies[item] = dependencies

        visiting = []
        visited = set()

        def visit(item):
            if item in visiting:
                chain = " -> ".join(
                    entry.factory.__name__ for entry in [*visiting, item]
                )
                raise ValueError(f"Resource dependency cycle: {chain}")
            if item in visited:
                return
            visiting.append(item)
            for dependency in self._dependencies[item].values():
                visit(dependency)
            visiting.pop()
            visited.add(item)
            self._order.append(item)

        for item in resources:
            visit(item)

    def provider_for(self, resource_type: Any) -> Resource[Any]:
        if resource_type not in self._providers:
            raise ValueError(f"No registered provider for handler resource {resource_type!r}")
        return self._providers[resource_type]

    @contextmanager
    def bind(self, session):
        if not isinstance(session, _ResourceSession) or session.registry is not self:
            session = None
        token = _current_session.set(session)
        try:
            yield
        finally:
            _current_session.reset(token)

    @asynccontextmanager
    async def lifespan(self):
        session = _ResourceSession(self)
        with self.bind(session):
            try:
                async with AsyncExitStack() as stack:
                    for item in self._order:
                        arguments = {
                            name: ResourceContext(session.values[dependency])
                            for name, dependency in self._dependencies[item].items()
                        }
                        factory = item.factory
                        if inspect.isasyncgenfunction(factory):
                            value = await stack.enter_async_context(
                                asynccontextmanager(factory)(**arguments)
                            )
                        elif inspect.isgeneratorfunction(factory):
                            value = stack.enter_context(contextmanager(factory)(**arguments))
                        else:
                            value = factory(**arguments)
                            if inspect.isawaitable(value):
                                value = await value
                        session.values[item] = value
                    yield session
            finally:
                session.active = False
                session.values.clear()
