---
title: Path and query parameters
lesson: 4
description: Accept filters, page numbers, and repeated values, with useful defaults and input validation.
---

# Accept the values your endpoint needs.

<p class="lead">Use Python types and defaults to describe a request.</p>

In the previous lesson, a fixed path selected a handler. Now let part of the
URL vary. A path placeholder such as `{user_id}` names a value inside the path;
the query string after `?` supplies optional controls such as pagination.

Suppose you want a user endpoint with a page number and an active-user filter.
Add this handler to the `main.py` from lesson 2, before `app = Karak(...)`:

```python
@router.get("/users/{user_id}")
async def user(user_id: int, page: int = 1, active: bool = True):
    return f"User {user_id} · page={page} · active={active}"
```

A request to `/users/42?page=2&active=false` produces:

```text
User 42 · page=2 · active=False
```

Karak gives your function an integer for `user_id`, an integer for `page`, and
a boolean for `active`. You can use those values directly in your Python code.
The `: int` and `: bool` parts are type annotations. Python annotations do not
normally convert strings by themselves; Karak reads them to choose converters
for incoming path and query values.

## Decide where a value comes from

If a parameter’s name appears in a path placeholder, it comes from that part
of the URL. Other parameters come from the query string after `?`.

In the example, `user_id` comes from `/users/42`. The query string supplies
`page` and `active`.

## Set a default or require a value

A default such as `page: int = 1` is used when the caller omits that query key.
Without a default, a value is required. For example:

```python
@router.get("/search")
async def search(term: str):
    return f"Searching for {term}"
```

`/search?term=python` works. `/search` produces HTTP 422 because `term` is missing.
A present empty string is a supplied value: `term=` is valid for a string,
while `page=` fails integer conversion.

## Accept several values

Use a list when the caller should be able to repeat a query key:

```python
@router.get("/tags")
async def tags(tag: list[str]):
    return ", ".join(tag)
```

`/tags?tag=python&tag=web` produces `python, web`. Lists are available for query
values only. Repeating a key for a single value, such as `page=1&page=2`, returns
HTTP 422.

## Limit the choices

```python
from typing import Literal


@router.get("/products")
async def products(sort: Literal["price", "newest"] = "newest"):
    return f"Sort by {sort}"
```

`/products?sort=price` works. A value outside those two choices is rejected.

## Choose a supported type

| What you want | Python type | Example input |
| --- | --- | --- |
| Text | `str` | `name=karak` |
| A whole number | `int` | `page=2` |
| A fractional number | `float` | `ratio=0.5` |
| A yes/no option | `bool` | `active=true` |
| An identifier | `UUID` from `uuid` | A valid UUID string |
| A date | `date` from `datetime` | `day=2026-09-25` |
| A date and time | `datetime` from `datetime` | `at=2026-09-25T12:30:00Z` |
| A decimal value | `Decimal` from `decimal` | `amount=19.99` |
| One of your enum members | An `Enum` subclass | A member’s value |
| A fixed choice | `Literal` from `typing` | `sort=price` |
| Several values | `list[T]` | `id=1&id=2` for `list[int]` |

Boolean input accepts `true/false`, `1/0`, `yes/no`, and `on/off`, without case
sensitivity. Import types such as `UUID`, `date`, and `Literal` before using
them in your function signature.

## Handle invalid input

A missing required value or a failed conversion returns HTTP 422. The response
identifies the parameter that needs attention, and your function is not called.

Use supported types for every parameter. Types such as `str | None`, nested
lists, dictionaries, and body models are not supported in the main framework
yet. An unsupported annotation prevents the application from being constructed.

## Predict the handler's inputs

Try `/users/42`, `/users/42?page=2&active=false`, and `/users/alex` with curl.
Before each request, predict either the Python values the handler receives or
the validation failure. Add a required `limit: int` parameter to a separate
endpoint and compare an omitted limit with `limit=0`.

Next, choose the status and body your caller receives. Headers, cookies, and
body bytes are introduced in the later [request context lesson](request-context.md).
