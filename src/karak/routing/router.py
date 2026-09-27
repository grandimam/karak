from collections.abc import Callable

from karak.response import Response
from karak.routing.matching import Match
from karak.routing.routes import BaseRoute
from karak.routing.routes import Route
from karak.types import Receive
from karak.types import Scope
from karak.types import Send


class Router:
    def __init__(
        self,
        *,
        routes: list[BaseRoute] | None = None,
    ) -> None:
        self._routes: list[BaseRoute] = routes if routes else []

    @staticmethod
    def wrap_asgi(func: Callable | None = None):
        async def not_found(scope: Scope, receive: Receive, send: Send):
            response = Response(status_code=500, content="Route Not Found")
            return await response(scope, receive, send)

        async def found(scope: Scope, receive: Receive, send: Send):
            return await func(scope, receive, send)

        return found if func else not_found

    def add_route(
        self,
        *,
        path: str,
        methods: list[str],
        handler: Callable,
    ):
        self._routes.append(Route(path, methods=methods, handler=handler))

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ):
        for route in self._routes:
            match = route.match(scope, receive)
            if match == Match.PARTIAL:
                return await Response(status_code=405, content="Method Not Allowed")(
                    scope, receive, send
                )
            if match == Match.FULL:
                return await Router.wrap_asgi(route)(scope, receive, send)
        return await Router.wrap_asgi()(scope, receive, send)
