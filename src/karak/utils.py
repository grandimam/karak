import inspect

from collections import OrderedDict
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from datetime import datetime
from decimal import Decimal
from decimal import InvalidOperation
from enum import Enum
from typing import Any
from typing import Literal
from typing import get_args
from typing import get_origin
from typing import get_type_hints
from uuid import UUID


def _convert_bool(value: str) -> bool:
    normalized = value.lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ValueError("expected a boolean value")


def _convert_decimal(value: str) -> Decimal:
    try:
        return Decimal(value)
    except InvalidOperation as exc:
        raise ValueError("expected a decimal value") from exc


CONVERTERS: dict[type[Any], Callable[[str], Any]] = {
    str: str,
    int: int,
    float: float,
    bool: _convert_bool,
    UUID: UUID,
    date: date.fromisoformat,
    datetime: datetime.fromisoformat,
    Decimal: _convert_decimal,
}


def _get_converter(annotation: Any) -> Callable[[str], Any]:
    converter = CONVERTERS.get(annotation)
    if converter:
        return converter

    if isinstance(annotation, type) and issubclass(annotation, Enum):
        choices = [(member.value, member) for member in annotation]
    elif get_origin(annotation) is Literal:
        choices = [(value, value) for value in get_args(annotation)]
    else:
        raise TypeError(f"Unsupported annotation: {annotation!r}")

    converters = [
        (_get_converter(type(value)), value, result) for value, result in choices
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


VARS_AND_KWARGS = {
    inspect.Parameter.VAR_POSITIONAL,
    inspect.Parameter.VAR_KEYWORD,
}


class InspectorValidationMixin:
    @staticmethod
    def _missing(
        signature: inspect.Signature,
        path_parameter_names: set[str],
    ) -> None:
        missing = path_parameter_names - signature.parameters.keys()
        if missing:
            names = ", ".join(sorted(missing))
            raise ValueError(f"Path parameters missing from handler signature: {names}")

    @staticmethod
    def _args_and_empty(parameter: inspect.Parameter, annotation: Any) -> None:
        if parameter.kind in VARS_AND_KWARGS:
            raise TypeError(
                f"Variadic handler parameter '{parameter.name}' is not supported"
            )
        if annotation is inspect.Parameter.empty:
            raise TypeError(
                f"Handler parameter '{parameter.name}' requires a type annotation"
            )

    @staticmethod
    def _list(
        name: str,
        path_parameter_names: set[str],
    ) -> None:
        if name in path_parameter_names:
            raise TypeError(
                f"List handler parameter '{name}' must be a query parameter"
            )

    @staticmethod
    def _list_item_type(name: str, annotation: Any) -> None:
        if len(get_args(annotation)) != 1:
            raise TypeError(f"List handler parameter '{name}' requires an item type")

    @staticmethod
    def _converter(
        name: str,
        annotation: Any,
        item_annotation: Any,
    ) -> Callable[[str], Any]:
        try:
            return _get_converter(item_annotation)
        except TypeError as exc:
            raise TypeError(
                f"Unsupported annotation for handler parameter '{name}': {annotation!r}"
            ) from exc


class ParameterSource(Enum):
    PATH = "path"
    QUERY = "query"


@dataclass(frozen=True)
class _Param:
    name: str
    source: ParameterSource
    converter: Callable[[str], Any]
    required: bool
    multiple: bool = False


class Inspector(InspectorValidationMixin):
    @staticmethod
    def inspect(
        func: Callable[..., Any],
        path_params: set[str],
    ) -> OrderedDict[str, _Param]:
        signature = inspect.signature(func)
        type_hints = get_type_hints(func)

        Inspector._missing(signature, path_params)

        parameters: OrderedDict[str, _Param] = OrderedDict()
        for name, parameter in signature.parameters.items():
            annotation = type_hints.get(name, parameter.annotation)
            Inspector._args_and_empty(parameter, annotation)
            is_multi = get_origin(annotation) is list
            item_annotation = annotation

            if is_multi:
                Inspector._list(name, path_params)
                Inspector._list_item_type(name, annotation)
                item_annotation = get_args(annotation)[
                    0
                ]  # tuple, that's why we need 0th index

            converter = Inspector._converter(name, annotation, item_annotation)

            source = (
                ParameterSource.PATH if name in path_params else ParameterSource.QUERY
            )
            parameters[name] = _Param(
                name=name,
                source=source,
                converter=converter,
                required=parameter.default is inspect.Parameter.empty,
                multiple=is_multi,
            )

        return parameters
