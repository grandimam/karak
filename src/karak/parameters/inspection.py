import inspect

from collections import OrderedDict
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any
from typing import get_args
from typing import get_origin
from typing import get_type_hints

from karak.parameters.conversion import get_converter
from karak.resources import ResourceContext


VARS_AND_KWARGS = {
    inspect.Parameter.VAR_POSITIONAL,
    inspect.Parameter.VAR_KEYWORD,
}


def _validate_path_parameters(
    signature: inspect.Signature,
    path_parameter_names: set[str],
) -> None:
    missing = path_parameter_names - signature.parameters.keys()
    if missing:
        names = ", ".join(sorted(missing))
        raise ValueError(f"Path parameters missing from handler signature: {names}")


def _validate_parameter(parameter: inspect.Parameter, annotation: Any) -> None:
    if parameter.kind is inspect.Parameter.POSITIONAL_ONLY:
        raise TypeError(f"Handler parameter '{parameter.name}' must accept a keyword argument")
    if parameter.kind in VARS_AND_KWARGS:
        raise TypeError(
            f"Variadic handler parameter '{parameter.name}' is not supported"
        )
    if annotation is inspect.Parameter.empty:
        raise TypeError(
            f"Handler parameter '{parameter.name}' requires a type annotation"
        )


def _validate_list_source(
    name: str,
    path_parameter_names: set[str],
) -> None:
    if name in path_parameter_names:
        raise TypeError(
            f"List handler parameter '{name}' must be a query parameter"
        )


def _validate_list_item_type(name: str, annotation: Any) -> None:
    if len(get_args(annotation)) != 1:
        raise TypeError(f"List handler parameter '{name}' requires an item type")


def _get_parameter_converter(
    name: str,
    annotation: Any,
    item_annotation: Any,
) -> Callable[[str], Any]:
    try:
        return get_converter(item_annotation)
    except TypeError as exc:
        raise TypeError(
            f"Unsupported annotation for handler parameter '{name}': {annotation!r}"
        ) from exc


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


def inspect_handler(
    func: Callable[..., Any],
    path_params: set[str],
) -> OrderedDict[str, _Param | _ContextParam]:
    signature = inspect.signature(func)
    type_hints = get_type_hints(func)

    _validate_path_parameters(signature, path_params)

    parameters: OrderedDict[str, _Param | _ContextParam] = OrderedDict()
    for name, parameter in signature.parameters.items():
        annotation = type_hints.get(name, parameter.annotation)
        _validate_parameter(parameter, annotation)
        if annotation is ResourceContext or get_origin(annotation) is ResourceContext:
            arguments = get_args(annotation)
            if len(arguments) != 1 or arguments[0] is Any:
                raise TypeError(f"Handler parameter '{name}' requires ResourceContext[T] with a concrete type")
            if name in path_params:
                raise TypeError(f"Context parameter '{name}' cannot be a path parameter")
            if parameter.default is not inspect.Parameter.empty:
                raise TypeError(f"Context parameter '{name}' cannot have a default")
            parameters[name] = _ContextParam(name, arguments[0])
            continue
        is_multi = get_origin(annotation) is list
        item_annotation = annotation

        if is_multi:
            _validate_list_source(name, path_params)
            _validate_list_item_type(name, annotation)
            item_annotation = get_args(annotation)[0]

        converter = _get_parameter_converter(name, annotation, item_annotation)

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
