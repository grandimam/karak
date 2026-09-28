# ASGI guide

Karak’s main implementation is an ASGI application. It runs on Python 3.13+,
uses async route handlers, and has no runtime dependencies. Use an ASGI server
such as Uvicorn to serve it.

This is the HTTP foundation of the [integrated backend direction](content/design.md).
The server boundary described here is current behavior; the shared production
lifecycle and operational model are planned.

## Run an example

Save the application below as `example.py`, then run from the repository root:

```bash
uv sync
uv run uvicorn example:app --reload
```

Then, in another terminal:

```bash
curl 'http://127.0.0.1:8000/users/42?active=true'
```

The response is `User 42 · active=True`.

## Define an application

Save this as `example.py` in the repository root:

```python
from karak import Karak
from karak import Router
from karak import Response

router = Router()


@router.get("/users/{user_id}")
async def user(user_id: int, active: bool = True):
    return f"User {user_id} · active={active}"


@router.get("/accepted")
async def accepted():
    return Response(status_code=202, content="Accepted")


app = Karak(router=router)
```

Run it with `uv run uvicorn example:app --reload`.

Define endpoints with `@router.get(path)` or `@router.post(path)`, then construct
`Karak(router=router)`. The decorator selects the HTTP method. The app
builds its routes from the supplied router during initialization,
so declare endpoints before constructing it.

## Path and query parameters

Every handler parameter needs a supported type annotation. Names present in
`{placeholders}` are path parameters; other parameters come from the query
string. Each placeholder must have a matching parameter in the handler.

A Python default makes a query parameter optional. For example, `active: bool =
True` uses `True` when the query key is absent. A present empty value, such as
`name=`, is passed through conversion; it is valid for a string.

The [supported types table](../README.md#types-do-the-parsing) lists the available
converters. Use `list[T]` for repeated query values:

```python
@router.get("/tags")
async def tags(tag: list[str]):
    return ", ".join(tag)
```

`/tags?tag=python&tag=web` produces `python, web`. Lists are supported only for
query parameters. Repeated scalar keys, missing required values, and invalid
values produce HTTP 422 responses. Unsupported annotations and missing path
parameters in the handler signature fail during application construction.

## Route registration

Define full paths on one router using decorators, then pass it to
`Karak(router=router)`. See the [routing guide](content/routing.md) for examples.

Applications capture the routes available at construction. Routers remain
editable and reusable, but later additions require constructing a new app to
become visible. No route processing takes place during lifespan startup.

## Responses and errors

Return text, bytes, or a `Response`. Text is encoded as UTF-8, and a `Response`
lets you set the status code. Return `b""` when an empty body is required.
Automatic JSON serialization and custom response headers are not implemented.

Validation failures produce a text response with HTTP 422. Unhandled handler
exceptions are logged through `karak.errors` and produce HTTP 500 with
`Internal Server Error` as the body.

## Current boundaries

The application accepts a `lifespan=` async context manager for startup and
shutdown. Register `@resource` factories through `resources=[...]`; resource
factories declare dependencies with `ResourceContext[T]` and access their values
through `.value`. Handlers access initialized resources through `.get()` on a
resource handle. See [application resources](content/resources.md).
Automatic request body binding, injected `Request` parameters, WebSockets, and a synchronous
handler executor are also not implemented.

Routing remains a prototype: an unmatched path currently returns HTTP 500.
Routes are checked in registration order; put static paths before overlapping
parameterized paths. HTTP 405 is returned when paths match but none accepts the
requested method.

The [design documents](README.md#work-on-karak) describe future capabilities.

## Development

```bash
uv run python -m unittest discover -s tests
```

See [request handling](server.md) for the implementation structure and
[load testing](load-testing.md) for measuring the ASGI demo.
