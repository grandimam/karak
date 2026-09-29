import inspect as inspect_module

from collections import OrderedDict
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any
from typing import Literal
from typing import get_args
from typing import get_origin
from typing import get_type_hints

from karak.parameters.conversion import get_converter
from karak.resources import ResourceContext


VARS_AND_KWARGS = {
    inspect_module.Parameter.VAR_POSITIONAL,
    inspect_module.Parameter.VAR_KEYWORD,
}


class ParameterSource(Enum):
    PATH = "path"
    QUERY = "query"
    CONTEXT = "context"


@dataclass(frozen=True)
class _ContextParam:
    name: str
    resource_type: Any
    source: ParameterSource = ParameterSource.CONTEXT


@dataclass(frozen=True)
class _Param:
    name: str
    source: ParameterSource
    converter: Callable[[str], Any]
    required: bool
    multiple: bool = False


class ParamInspector:
    """Inspect and validate a handler's parameters."""

    def __init__(
        self,
        func: Callable[..., Any],
        path_params: set[str],
    ) -> None:
        self._func = func
        self._path_params = path_params

    def inspect(self) -> OrderedDict[str, _Param | _ContextParam]:
        signature = inspect_module.signature(self._func)
        type_hints = get_type_hints(self._func)
        self._validate_path_parameters(signature)

        parameters: OrderedDict[str, _Param | _ContextParam] = OrderedDict()
        for name, parameter in signature.parameters.items():
            annotation = type_hints.get(name, parameter.annotation)
            self._validate_kind(parameter)
            self._validate_annotation(name, annotation)

            if annotation is ResourceContext or get_origin(annotation) is ResourceContext:
                parameters[name] = self._inspect_context(name, parameter, annotation)
                continue

            multiple = get_origin(annotation) is list
            item_annotation = self._inspect_list(name, annotation) if multiple else annotation
            parameters[name] = _Param(
                name=name,
                source=(
                    ParameterSource.PATH
                    if name in self._path_params else ParameterSource.QUERY
                ),
                converter=self._get_converter(item_annotation),
                required=parameter.default is inspect_module.Parameter.empty,
                multiple=multiple,
            )

        return parameters

    def _validate_path_parameters(self, signature: inspect_module.Signature) -> None:
        missing = self._path_params - signature.parameters.keys()
        if missing:
            names = ", ".join(sorted(missing))
            raise ValueError(f"Path parameters missing from handler signature: {names}")

    def _validate_kind(self, parameter: inspect_module.Parameter) -> None:
        if parameter.kind is inspect_module.Parameter.POSITIONAL_ONLY:
            raise TypeError(
                f"Handler parameter '{parameter.name}' must accept a keyword argument"
            )
        if parameter.kind in VARS_AND_KWARGS:
            raise TypeError(
                f"Variadic handler parameter '{parameter.name}' is not supported"
            )

    def _validate_annotation(self, name: str, annotation: Any) -> None:
        if annotation is inspect_module.Parameter.empty:
            raise TypeError(
                f"Handler parameter '{name}' requires a type annotation"
            )

    def _inspect_context(
        self,
        name: str,
        parameter: inspect_module.Parameter,
        annotation: Any,
    ) -> _ContextParam:
        arguments = get_args(annotation)
        if len(arguments) != 1 or arguments[0] is Any:
            raise TypeError(
                f"Handler parameter '{name}' requires ResourceContext[T] "
                "with a concrete type"
            )
        if name in self._path_params:
            raise TypeError(
                f"Context parameter '{name}' cannot be a path parameter"
            )
        if parameter.default is not inspect_module.Parameter.empty:
            raise TypeError(
                f"Context parameter '{name}' cannot have a default"
            )
        return _ContextParam(name, arguments[0])

    def _inspect_list(self, name: str, annotation: Any) -> Any:
        if name in self._path_params:
            raise TypeError(
                f"List handler parameter '{name}' must be a query parameter"
            )
        arguments = get_args(annotation)
        if len(arguments) != 1:
            raise TypeError(
                f"List handler parameter '{name}' requires an item type"
            )
        return arguments[0]

    def _get_converter(self, annotation: Any) -> Callable[[str], Any]:
        if isinstance(annotation, type) and issubclass(annotation, Enum):
            choices = [(member.value, member) for member in annotation]
        elif get_origin(annotation) is Literal:
            choices = [(value, value) for value in get_args(annotation)]
        else:
            return get_converter(annotation)
        return self._get_choice_converter(choices)

    def _get_choice_converter(
        self,
        choices: list[tuple[Any, Any]],
    ) -> Callable[[str], Any]:
        converters = [
            (self._get_converter(type(value)), value, result)
            for value, result in choices
        ]

        def convert_choice(raw: str) -> Any:
            for convert, value, result in converters:
                try:
                    converted = convert(raw)
                except (TypeError, ValueError):
                    continue
                if type(converted) is type(value) and converted == value:
                    return result
            allowed = ", ".join(repr(value) for value, _ in choices)
            raise ValueError(f"expected one of: {allowed}")

        return convert_choice
