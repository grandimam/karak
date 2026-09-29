from collections.abc import Callable
from datetime import date
from datetime import datetime
from decimal import Decimal
from decimal import InvalidOperation
from typing import Any
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


def get_converter(annotation: Any) -> Callable[[str], Any]:
    converter = CONVERTERS.get(annotation)
    if converter:
        return converter

    raise TypeError(f"Unsupported annotation: {annotation!r}")
