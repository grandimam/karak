---
title: How Karak works
description: Understand routers, handlers, application resources, and the server that runs your code.
---

# The pieces of a Karak application.

<p class="lead">Connect a URL to a Python function, then let an ASGI server run your application.</p>

If you have not run an endpoint yet, start with the [quickstart](index.md).
You need Python 3.13 or newer. The repository's development environment includes
Uvicorn, the server used throughout these guides.

## Define handlers on a router

A handler is an async function that processes a request and returns a response.
Decorators register its URL and HTTP method:

```python
from karak import Karak
from karak import Router

router = Router()


@router.get("/users/{user_id}")
async def user(user_id: int, active: bool = True):
    return f"User {user_id} · active={active}"


app = Karak(router=router)
```

`Router` collects declarations. `Karak` reads those declarations and validates
handler signatures when you construct the application. Finish declaring routes
before calling `Karak(...)`. See [define routes](routing.md).

## Follow a request

When a client requests `/users/42?active=false`:

1. The server delivers the HTTP request to Karak.
2. Karak matches the URL and method to `user`.
3. The handler's annotations convert `42` into an integer and `false` into a boolean.
4. Karak awaits `user(user_id=42, active=False)`.
5. The returned string becomes the response body: `User 42 · active=False`.

Invalid or missing required values produce HTTP 422 before the handler runs.
Read [request values](parameters.md) for supported types and
[responses](responses.md) for status codes and errors.

## Share application services

Use `@resource` to declare a factory and register the handle with
`Karak(router=router, resources=[...])`. Karak initializes resources at startup
and makes them available to handlers through the handle's `.get()` method.

A factory parameter such as `pool: ResourceContext[DatabasePool]` asks Karak
to supply an already-initialized dependency. Access it through `pool.value`.
These annotations belong on resource factories, not endpoint parameters.

The [resource guide](resources.md) gives a complete example and explains cleanup,
dependency ordering, and application lifetimes.

## Run the application

Save the first example as `main.py`, then run:

```sh
uv run uvicorn main:app --reload
```

Uvicorn owns the listening socket and sends requests and startup/shutdown events
to Karak. Karak owns routing, input conversion, and registered resource lifetimes.
Your code owns business operations and their transaction boundaries.

See [run an application](application.md) for editing, ports, and startup hooks.

## Check the current boundaries

Karak supports async GET and POST handlers, typed path and query parameters,
text and byte responses, static files, and application resources. JSON body
binding, automatic JSON responses, and synchronous handlers are not supported.
Karak is experimental and is not ready for production use.
