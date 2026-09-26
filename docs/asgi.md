# ASGI guide

Karak’s main implementation is an ASGI application. It runs on Python 3.13+,
uses async route handlers, and has no runtime dependencies. Use an ASGI server
such as Uvicorn to serve it.

## Run the included example

From the repository root:

```bash
uv sync
uv run uvicorn examples.basic:app --reload
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
from karak import Response

app = Karak()


@app.get(path="/users/{user_id}", methods=["GET"])
async def user(user_id: int, active: bool = True):
    return f"User {user_id} · active={active}"


@app.get(path="/accepted", methods=["GET"])
async def accepted():
    return Response(status_code=202, content="Accepted")
```

Run it with `uv run uvicorn example:app --reload`.

The current decorator takes keyword arguments: `path=` and `methods=`.
Despite its name, `app.get(...)` registers the methods supplied in `methods`.
Separate `app.post(...)`, `app.put(...)`, and `app.delete(...)` helpers are not
implemented in the ASGI version.

## Path and query parameters

Every handler parameter needs a supported type annotation. Names present in
`{placeholders}` are path parameters; other parameters come from the query
string. Each placeholder must have a matching parameter in the handler.

A Python default makes a query parameter optional. For example, `active: bool =
True` uses `True` when the query key is absent. A present empty value, such as
`name=`, is passed through conversion; it is valid for a string.

The [supported types table](../README.md#parameter-types) lists the available
converters. Use `list[T]` for repeated query values:

```python
@app.get(path="/tags", methods=["GET"])
async def tags(tag: list[str]):
    return ", ".join(tag)
```

`/tags?tag=python&tag=web` produces `python, web`. Lists are supported only for
query parameters. Repeated scalar keys, missing required values, and invalid
values produce HTTP 422 responses. Unsupported annotations and missing path
parameters in the handler signature fail during route registration.

## Responses and errors

Return text, bytes, or a `Response`. Text is encoded as UTF-8, and a `Response`
lets you set the status code. Return `b""` when an empty body is required.
Automatic JSON serialization and custom response headers are not implemented.

Validation failures produce a text response with HTTP 422. Unhandled handler
exceptions are logged through `karak.errors` and produce HTTP 500 with
`Internal Server Error` as the body.

## Current boundaries

The application acknowledges ASGI startup and shutdown events. It does not yet
provide user-defined lifecycle hooks. Dependency injection, automatic request
body binding, injected `Request` parameters, WebSockets, and a synchronous
handler executor are also not implemented.

Routing remains a prototype: an unmatched path currently returns HTTP 500,
and the router returns HTTP 405 as soon as it finds a matching path with a
different method. Avoid registering separate method-specific handlers for the
same path until method selection is improved.

The [design documents](README.md#design-proposals-and-working-notes) describe
future capabilities. The [free-threaded experiment](../experiments/free_threaded/README.md)
has its own synchronous API and server; its features are separate from this API.

## Development

```bash
uv run python -m unittest discover -s tests
```

See [request handling](server.md) for the implementation structure and
[load testing](load-testing.md) for measuring the ASGI demo.
