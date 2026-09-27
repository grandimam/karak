import logging

from karak.exceptions import RequestValidationError
from karak.response import Response
from karak.types import KarakApp
from karak.types import Receive
from karak.types import Scope
from karak.types import Send


logger = logging.getLogger("karak.errors")


class ExceptionHandler:
    def __init__(self, app: KarakApp) -> None:
        self._app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        try:
            await self._app(scope, receive, send)
        except RequestValidationError as exc:
            await Response(status_code=422, content=str(exc))(scope, receive, send)
        except Exception:
            logger.exception(
                "Unhandled exception while serving %s %s",
                scope.get("method", ""),
                scope.get("path", ""),
            )
            await Response(status_code=500, content="Internal Server Error")(
                scope, receive, send
            )
