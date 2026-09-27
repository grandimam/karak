from abc import ABC
from abc import abstractmethod
from collections.abc import Callable
from typing import Any

from karak.exceptions import RequestValidationError
from karak.parameters import Inspector
from karak.parameters import ParameterSource
from karak.request import Request
from karak.response import Response
from karak.routing.matching import Match
from karak.routing.matching import PARAM_RE
from karak.routing.matching import compile_path
from karak.types import Receive
from karak.types import Scope
from karak.types import Send


class BaseRoute(ABC):
    @abstractmethod
    def match(self, scope: Scope, receive: Receive) -> Match:
        raise NotImplementedError

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        raise NotImplementedError


class Route(BaseRoute):
    def __init__(
        self,
        path: str,
        *,
        methods: list[str] | None,
        handler: Callable[..., Any],
    ):
        self._path = path
        self._handler = handler
        self._methods = methods or ["GET"]
        self._path_regex = compile_path(self._path)
        self._path_parameter_names = set(PARAM_RE.findall(self._path))
        self._handler_params = Inspector.inspect(
            self._handler,
            self._path_parameter_names,
        )

    def match(self, scope: Scope, receive: Receive) -> Match:
        match = self._path_regex.match(scope["path"])
        if not match:
            return Match.NONE
        scope["path_params"] = match.groupdict()
        return Match.FULL if scope["method"] in self._methods else Match.PARTIAL

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        request = Request(scope, receive)
        path_params = scope.get("path_params", {})
        query_params = request.params
        handler_arguments = {}

        for name, parameter in self._handler_params.items():
            if parameter.source is ParameterSource.PATH:
                raw_value = path_params.get(name)
            else:
                values = query_params.get(name)
                if values and len(values) > 1 and not parameter.multiple:
                    raise RequestValidationError(
                        parameter.source.value,
                        name,
                        "expected one value",
                    )
                # query params returns an array always.
                raw_value = values[0] if values else None

            if raw_value is None:
                if parameter.required:
                    raise RequestValidationError(
                        parameter.source.value,
                        name,
                        "field required",
                    )
                continue

            try:
                if parameter.multiple:
                    handler_arguments[name] = [
                        parameter.converter(value) for value in values
                    ]
                else:
                    handler_arguments[name] = parameter.converter(raw_value)
            except (TypeError, ValueError) as exc:
                raise RequestValidationError(
                    parameter.source.value,
                    name,
                    str(exc),
                ) from exc

        result = await self._handler(**handler_arguments)
        if isinstance(result, Response):
            return await result(scope, receive, send)
        return await Response(content=result)(scope, receive, send)
