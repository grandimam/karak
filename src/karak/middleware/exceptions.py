import logging

from karak.exceptions import RequestValidationError
from karak.response import Response
from karak.types import KarakApp
from karak.types import Receive
from karak.types import Scope
from karak.types import Send


logger = logging.getLogger("karak.errors")


class ExceptionMiddleware:
    def __init__(self, app: KarakApp) -> None:
        self._app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        response_started = False

        async def send_response(message):
            nonlocal response_started
            if message["type"] == "http.response.start":
                response_started = True
            await send(message)

        try:
            await self._app(scope, receive, send_response)
        except RequestValidationError as exc:
            if response_started:
                raise
            await Response(status_code=422, content=str(exc))(scope, receive, send)
        except Exception:
            if response_started:
                raise
            logger.exception(
                "Unhandled exception while serving %s %s",
                scope.get("method", ""),
                scope.get("path", ""),
            )
            await Response(status_code=500, content="Internal Server Error")(
                scope, receive, send
            )
