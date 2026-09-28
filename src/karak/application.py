from __future__ import annotations

from pathlib import Path

from karak.types import Scope
from karak.types import Receive
from karak.types import Send

from karak.response import Response
from karak.routing import Router
from karak.routing import Match
from karak.routing import Route
from karak.routing.staticfiles import StaticFiles
from karak.middleware import ExceptionMiddleware


class Karak:
    def __init__(
        self,
        *,
        router: Router,
        static_dir: str | Path | None = None,
    ) -> None:
        self._static_files = StaticFiles(static_dir) if static_dir else None
        self._routes = [
            Route(
                definition.path,
                methods=[definition.method],
                handler=definition.handler,
            )
            for definition in router
        ]
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
        while True:
            message = await receive()
            if message["type"] == "lifespan.startup":
                await send({"type": "lifespan.startup.complete"})
            elif message["type"] == "lifespan.shutdown":
                await send({"type": "lifespan.shutdown.complete"})
                return

    async def _http(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
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
