---
title: Parameters
description: Supported path and query types, defaults, lists, and validation errors.
---

# Let types do the explaining.

<p class="lead">Handler annotations describe the values your code receives.</p>

Names present in path placeholders come from the path. Other parameters come
from the query string. Every handler parameter needs a supported annotation.

## Supported types

| Type | Input | Value |
| --- | --- | --- |
| `str` | `name=karak` | A string |
| `int` | `page=2` | An integer |
| `float` | `ratio=0.5` | A float |
| `bool` | `active=true` | A boolean |
| `UUID` | A valid UUID string | A UUID object |
| `date` | `day=2026-09-25` | An ISO date |
| `datetime` | `at=2026-09-25T12:30:00Z` | An ISO datetime |
| `Decimal` | `amount=19.99` | A decimal value |
| `Enum` | A member’s value | The matching enum member |
| `Literal["price", "newest"]` | `sort=price` | An allowed value |
| `list[int]` | `id=1&id=2` | `[1, 2]` |

Boolean conversion accepts `true/false`, `1/0`, `yes/no`, and `on/off`, without
case sensitivity. Lists are supported for query parameters only.

## Defaults and empty values

```python
from karak import Karak

app = Karak()


@app.get(path="/users", methods=["GET"])
async def users(page: int = 1, name: str = ""):
    return f"Page {page}, name: {name}"
```

Python defaults apply when a query key is absent. A present empty string is a
value: `name=` is valid for `str`, while `page=` fails integer conversion.

## Repeated values

```python
from typing import Literal


@app.get(path="/products", methods=["GET"])
async def products(tag: list[str], sort: Literal["price", "newest"] = "newest"):
    return f"Tags: {', '.join(tag)} · sort={sort}"
```

Request `/products?tag=python&tag=web&sort=price` to receive both tags. Repeated
keys are rejected for scalar parameters.

## Validation

Missing required values and failed conversions produce HTTP 422 text responses.
Unsupported annotations fail during registration. Union types such as
`str | None`, nested lists, dictionaries, and automatic model binding are not
supported by the current ASGI parameter converter.
