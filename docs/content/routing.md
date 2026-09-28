---
title: Define routes
description: Give your application endpoints and read values from their URLs.
---

# Give your application another endpoint.

<p class="lead">Choose the URL someone visits and the function that answers it.</p>

A route connects a URL to your code. In the [quickstart](index.md), `/` returned
a greeting. Define endpoints on your `router` before constructing the application
with `Karak(router=router)`:

```python
@router.get("/users/{user_id}")
async def user(user_id: int):
    return f"User {user_id}"
```

Start the server and visit
[localhost:8000/users/42](http://127.0.0.1:8000/users/42). The response is:

```text
User 42
```

## Accept a value in the URL

`{user_id}` marks the part of the URL that can change. Name the function
parameter `user_id` too, and use `int` to ask for an integer.

Visit `/users/7` to receive `User 7`. Visit `/users/alex` and Karak returns an
HTTP 422 validation response because `alex` cannot be converted to an integer.

## Add optional controls

Use query parameters for values such as filters or page numbers. Add this
parameter to the same user endpoint:

```python
@router.get("/users/{user_id}")
async def user(user_id: int, active: bool = True):
    return f"User {user_id} · active={active}"
```

Replace the earlier `user` endpoint with this version rather than registering
both. `/users/42?active=false` responds with `User 42 · active=False`. If you
leave `active` out, the default `True` applies.

Continue to [read request values](parameters.md) for lists, defaults, and
other supported types.

## Choose an HTTP method

Use `@router.get(path)` for GET endpoints and `@router.post(path)` for POST
endpoints. The decorator selects the HTTP method; there is no `methods=`
argument. Other method decorators and automatic JSON request-body handling are
not supported.

```python
@router.post("/users")
async def create_user(name: str):
    return f"Created {name}"
```

## Construct the application

After defining your endpoints, pass the router into the application:

```python
app = Karak(router=router)
```

Each decorator records an endpoint's full path, HTTP method, and handler.
`Karak` uses those definitions to create executable routes and validate handler
signatures during initialization. The application then matches those routes
directly when serving requests.

Finish decorating your router before constructing the app. Routers remain
editable, but later additions are only included when a new application is
constructed. There is no separate startup compilation or freezing step.

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
