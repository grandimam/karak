from __future__ import annotations

from pathlib import Path
from collections.abc import Callable
from contextlib import AbstractAsyncContextManager
from contextlib import nullcontext

from karak.types import Scope
from karak.types import Receive
from karak.types import Send

from karak.response import Response
from karak.request import Request
from karak.request import REQUEST_SCOPE_KEY
from karak.routing import Router
from karak.routing import Match
from karak.routing import Route
from karak.routing.staticfiles import StaticFiles
from karak.middleware import ExceptionMiddleware
from karak.resources import RESOURCE_STATE_KEY
from karak.resources import _ResourceRegistry


class Karak:
    def __init__(
        self,
        *,
        router: Router,
        static_dir: str | Path | None = None,
        lifespan: Callable[[], AbstractAsyncContextManager[None]] | None = None,
    ) -> None:
        self._lifespan_factory = lifespan
        self._resources = _ResourceRegistry()
        self._static_files = StaticFiles(static_dir) if static_dir else None
        self._routes: list[Route] = []
        registered: set[tuple[str, str]] = set()
        for definition in router:
            key = (definition.method, definition.path)
            if key in registered:
                raise ValueError(
                    f"Duplicate route: {definition.method} {definition.path}"
                )
            registered.add(key)
            route = Route(
                definition.path,
                methods=[definition.method],
                handler=definition.handler,
            )
            for resource_type in route._context_types.values():
                self._resources.provider_for(resource_type)
            self._routes.append(route)
        self._app = ExceptionMiddleware(self._dispatch)

    async def _dispatch(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        if self._static_files and self._static_files.matches(scope["path"]):
            await self._static_files(scope, receive, send)
            return

        partial_match = False
        for route in self._routes:
            match = route.match(scope, receive)
            if match == Match.PARTIAL:
                partial_match = True
            if match == Match.FULL:
                await route(scope, receive, send)
                return

        if partial_match:
            response = Response(status_code=405, content="Method Not Allowed")
        else:
            response = Response(status_code=500, content="Route Not Found")
        await response(scope, receive, send)

    async def _lifespan(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        message = await receive()
        if message["type"] != "lifespan.startup":
            raise RuntimeError("Expected lifespan.startup")

        phase = "startup"
        try:
            async with self._resources.lifespan() as session:
                scope.setdefault("state", {})[RESOURCE_STATE_KEY] = session
                manager = self._lifespan_factory() if self._lifespan_factory else nullcontext()
                async with manager:
                    await send({"type": "lifespan.startup.complete"})
                    phase = "shutdown"
                    message = await receive()
                    if message["type"] != "lifespan.shutdown":
                        raise RuntimeError("Expected lifespan.shutdown")
        except Exception as exc:
            await send({"type": f"lifespan.{phase}.failed", "message": str(exc)})
            return
        await send({"type": "lifespan.shutdown.complete"})

    async def _http(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        session = scope.get("state", {}).get(RESOURCE_STATE_KEY)
        scope = dict(scope)
        scope[REQUEST_SCOPE_KEY] = Request(scope, receive)
        with self._resources.bind(session):
            await self._app(scope, receive, send)

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ):
        if scope["type"] == "lifespan":
            await self._lifespan(scope, receive, send)

        if scope["type"] == "http":
            await self._http(scope, receive, send)
