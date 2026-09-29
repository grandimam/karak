---
title: Routers and modules
guide: true
description: Give each feature file a router, combine them in the application, and preserve imports as features grow into packages.
---

# Organize endpoints into modules.

<p class="lead">Give each feature a router and combine them into one application.</p>

You have already written endpoints, accepted inputs, and read request context.
When those endpoints no longer fit comfortably in one file, group related
operations into Python modules. Each module owns its router; the entry point
combines them and constructs the application.

## Move from one file to a package

Start with one file per feature, following the [project layout](project-layout.md).
Create this structure beside your earlier `main.py`:

```text
app/
├── __init__.py
├── main.py
├── resources.py
├── users.py
└── orders.py
```

Leave `__init__.py` empty. It marks `app` as a Python package. The new entry
point is `app/main.py`; the earlier root `main.py` is not used by the command
below. Put the following code in the named files. `resources.py` is where shared
resource factories will go; it can stay empty or be added when you introduce
your first [resource](resources.md).

## Organize routes across modules

Give each feature module its own router, then include those routers in the
application's root router. Keep full URL paths in each module:

```python
# app/users.py
from karak import Router

router = Router()

@router.get("/users/{user_id}")
async def get_user(user_id: int):
    return f"User {user_id}"
```

```python
# app/orders.py
from karak import Router

router = Router()

@router.get("/orders/{order_id}")
async def get_order(order_id: int):
    return f"Order {order_id}"
```

```python
# app/main.py
from karak import Karak
from karak import Router

from app.users import router as users_router
from app.orders import router as orders_router

router = Router()
router.include(users_router)
router.include(orders_router)

app = Karak(router=router)
```

Start this version from the repository root:

```sh
uv run uvicorn app.main:app --reload
```

Visit `/users/42` and `/orders/7`. Their responses should be `User 42` and
`Order 7`. `app.main:app` means the `app` object inside the `app.main` module.
Stop the earlier server first if it is still using port 8000.

`include()` copies the child router's current definitions into the parent in
registration order. Finish defining a child before including it: later changes
to the child do not update the parent. You can reuse a child in multiple parents
or include a router that already includes other routers. All routes become one
flat list; there is no extra routing step during requests.

Include routers before constructing `Karak`. Registering the same HTTP method
and exact path twice raises `ValueError` during application construction,
including duplicates across modules. GET and POST may share a path. Overlapping
patterns still follow registration order, so register `/users/me` before
`/users/{user_id}`.

## Use full paths

Write the complete URL path in each decorator, including any shared segments:

```python
@router.get("/api/users/{user_id}/posts/{post_id}")
async def post(user_id: int, post_id: int, preview: bool = False):
    return f"User {user_id}, post {post_id}, preview={preview}"
```

`GET /api/users/42/posts/7?preview=true` passes `user_id=42`, `post_id=7`, and
`preview=True` to `post`. A query value with the same name cannot override a
path value.

Paths must start with `/`; use `/` for the root endpoint. Trailing slashes
are matched exactly, with no automatic redirects. Duplicate parameter names
in a path are rejected when the application is constructed.

## Serve static files

Pass an existing directory when constructing the application:

```python
app = Karak(router=router, static_dir="static")
```

The built-in `StaticFiles` handler reserves `/static/` before decorated routes.
For example, `/static/css/style.css` serves `static/css/style.css`. Relative
directory paths are resolved from the process's working directory at construction.
Only the directory is checked at startup; files are opened when requested.

`GET` streams file bytes in chunks, and `HEAD` returns the same headers without
the body. Responses include the content type and file size. Missing files,
directories, and paths escaping the configured directory return `404` without
falling through to decorated routes. Other HTTP methods return `405`.

Files added or changed after startup are used on subsequent requests. Directory
listings, automatic index pages, conditional caching, and byte ranges are not
implemented.

## Prototype limitations

Keep these limitations in mind when trying routes:

- Use matching names for path placeholders and function parameters, and
  annotate every parameter. Mistakes here prevent application construction.
- An unknown URL currently returns HTTP 500 with `Route Not Found`, rather
  than HTTP 404. Check the URL and the routes you have defined.
- Routes are checked in registration order. Put static paths before overlapping
  parameterized paths. A method mismatch continues searching for a matching
  endpoint before returning HTTP 405.
- Literal characters such as `.` and `+` match exactly; `{name}` introduces a
  path parameter.

## Grow a feature without changing its URLs

Keep users and orders as individual files while they are easy to work with.
When users needs separate route and service files, replace `users.py` with a
`users/` package and export its router from `users/__init__.py`. The existing
`from app.users import router` import in `main.py` still works.

The [project layout guide](project-layout.md#expand-one-feature-when-it-needs-more-room)
shows the transition for both application code and tests. Each feature can grow
independently; orders does not need a package just because users has one.
