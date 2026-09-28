# ASGI request handling

The main application is `Karak`, exported by `karak` and implemented in
[`src/karak/application.py`](../src/karak/application.py). An ASGI server such as Uvicorn
owns the network connections and calls the application with `scope`, `receive`,
and `send`.

`KarakApp` in `karak.types` is a callable type alias used by the middleware.
It is not the application class.

## Request flow

```text
ASGI server
    → Karak.__call__
    → ExceptionMiddleware
    → Karak._dispatch
    → Route: parameter conversion and validation
    → async handler
    → Response
    → ASGI send
```

Router decorators store endpoint definitions: full path, method, and handler.

During application construction, `Karak` iterates over the supplied router
and creates each `Route` once, using its complete path. `inspect_handler` then
reads the handler signature, validates all path placeholders, and selects
converters. The original definitions remain reusable and editable.

During a request, `Karak._dispatch` checks its routes in order. The matching `Route`
builds handler arguments from path and query values, awaits the handler, and
sends its result through a `Response`. No route construction or handler inspection
runs during requests or lifespan startup.

See the [ASGI guide](asgi.md) for runnable examples and routing limitations.

## Request object

`Request` is a low-level wrapper around the ASGI scope and receive callable.
It is used internally by `Route` and is exported for code that works directly
with ASGI:

```python
from karak import Request


async def inspect_request(scope, receive):
    request = Request(scope, receive)
    return request.path, request.method, request.params, await request.body()
```

`params` maps query keys to lists of strings and preserves blank values.
`body()` consumes request messages and joins their body chunks into bytes; it
raises `RuntimeError` if the client disconnects while the body is being read.
The body is not cached, so read it once and retain the result if needed.

There is no `Request.json()` method or automatic `Request` injection into route
handlers in the current ASGI implementation.

## Response and lifecycle

`Response` sends `http.response.start` with the status code, followed by
`http.response.body`. Ordinary text results are encoded as UTF-8; bytes can be
returned directly. The default status is 200.

For lifespan scopes, the application enters the optional `lifespan=` async context
manager before acknowledging startup and exits it before acknowledging shutdown.
Setup and cleanup errors send ASGI lifespan failure messages. Registered resources
initialize before the hook and clean up after it. Resource factory parameters
annotated with `ResourceContext[T]` receive wrappers around resolved dependencies.
Karak carries the resource session through ASGI lifespan state and binds it while
serving each request, allowing handle `.get()` calls to select the correct instance.

The [original server notes](../notes/server.md) preserve the earlier design
exploration, including proposed APIs.
