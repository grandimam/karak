---
title: Project layout
guide: true
description: Start with one file per feature, then expand individual features and their tests into packages when they need more room.
---

# Start with files. Grow into packages.

<p class="lead">Keep the application easy to navigate while it is small, and split a feature when its responsibilities grow.</p>

A single `main.py` is enough for [Hello World](index.md). When you add features,
Karak's recommended layout keeps them as files inside an `app` package:

```text
my-backend/
├── pyproject.toml
├── uv.lock
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── resources.py
│   ├── users.py
│   └── orders.py
└── tests/
    ├── __init__.py
    ├── test_users.py
    └── test_orders.py
```

Leave the two `__init__.py` files empty. They make `app` and `tests` Python
packages. A `.py` file such as `users.py` is already a module; a package lets
that module grow into several files later.

This is a recommended convention, not a directory structure enforced by Karak.
Add each file when you need it. `resources.py` can wait until the application
has a shared resource, and a small feature does not need separate routes,
services, and data-access files.

## Give each file a clear responsibility

| File | Responsibility |
| --- | --- |
| `app/main.py` | Create the root router, include feature routers, register resources, and construct `app` |
| `app/resources.py` | Declare shared resource factories and their startup/cleanup behavior |
| `app/users.py` | Define the users router, its handlers, and small user-related functions or classes |
| `app/orders.py` | Define the orders router, its handlers, and small order-related functions or classes |
| `tests/test_users.py` | Check user-related behavior |
| `tests/test_orders.py` | Check order-related behavior |

Keep HTTP handling in route functions: read inputs, call application behavior,
and return a response. Other functions and classes can take ordinary Python
values, so they are useful independently of HTTP and easy to test.

Follow [routers and modules](routing.md) for the complete `users.py`, `orders.py`,
and `main.py` examples. Run the application from the project root:

```sh
uv run uvicorn app.main:app --reload
```

When introducing resources, put the factories in `app/resources.py` and register
their handles in `main.py`. Handlers ask for initialized values with
`ResourceContext[T]`. The [resource guide](resources.md) explains that lifecycle.

Feature modules should not import `app.main`: it assembles the application and
already imports them. Keep reusable service code independent of application
assembly. Resource factories can import the service classes they construct.

## Expand one feature when it needs more room

If `users.py` starts mixing substantial HTTP handling and business logic, replace
that file with a `users/` package:

```text
app/
├── __init__.py
├── main.py
├── resources.py
├── users/
│   ├── __init__.py
│   ├── routes.py
│   └── service.py
└── orders.py
```

Move the users router and handlers into `app/users/routes.py`. Move substantial
business logic into `app/users/service.py`; create this file only when there is
logic to move. Re-export the router from `app/users/__init__.py`:

```python
from app.users.routes import router
```

The application entry point can keep its existing import:

```python
from app.users import router as users_router
```

Replace `app/users.py` with the package; do not leave both forms side by side.
The URLs and `router.include(users_router)` stay the same. The new file layout
does not introduce a new routing layer or a URL prefix.

`orders.py` can remain a single file until it also benefits from being split.
There is no required file count or line limit. Split when a responsibility is
hard to find, understand, or change in the current file. Add database or schema
modules only when the feature actually has those responsibilities.

## Grow tests at the same pace

Start with one test file per feature. When a feature's tests become difficult
to navigate, replace `test_users.py` with a package grouped by the behavior tested:

```text
tests/
├── __init__.py
├── users/
│   ├── __init__.py
│   ├── test_routes.py
│   └── test_service.py
└── test_orders.py
```

Keep the `__init__.py` files so Python's unittest discovery can descend into
these packages. Remove the old `test_users.py` after moving its tests; keep test
filenames beginning with `test_`. Run all tests from the project root:

```sh
uv run python -m unittest discover -s tests -t . -v
```

Tests can grow independently of application files. A single `users.py` may
already need several test files, while a small users package may still fit in
one `test_users.py`. Add a shared `tests/helpers.py` only when several tests
need the same setup, and import it as `from tests.helpers import ...`.

See [testing](testing.md) for runnable service, HTTP, and cleanup checks. Keep
the test behavior the same when moving files; reorganizing should not change
what the application does.
