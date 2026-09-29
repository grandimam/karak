---
title: Request context
lesson: 6
description: Receive the current request through ResourceContext, read headers and cookies, and keep data isolated between callers.
---

# Get the request your handler is answering.

<p class="lead">Use ResourceContext[Request] to read headers, cookies, raw body bytes, and request-local state.</p>

A request is one message from a client to your backend. Its URL tells you which
operation to run. Headers carry additional information, such as the format the
client accepts. Cookies are named values a browser stores and sends back on
later requests.

You already use typed parameters for URL values. Keep using those for inputs
such as `user_id: int`. Add a context parameter when you need the rest of the
request.

`ResourceContext[Request]` is a typed wrapper. The brackets name the value you
want Karak to supply; `.value` accesses that value. The wrapper is a Python
object, not data sent by the client. In lesson 8 the same convention supplies
a shared application service with a longer lifetime.

## Run a complete example

After the [quickstart](index.md), replace `main.py` with:

```python
from karak import Karak
from karak import Request
from karak import ResourceContext
from karak import Response
from karak import Router

router = Router()


@router.get("/users/{user_id}")
async def user(user_id: int, context: ResourceContext[Request]):
    request = context.value
    theme = request.cookies.get("theme", "light")
    client = request.headers.get("user-agent", "unknown")
    response = Response(content=f"User {user_id}; theme={theme}; client={client}")
    response.headers["content-type"] = "text/plain; charset=utf-8"
    return response


@router.post("/preferences")
async def preferences(theme: str):
    if theme not in ("light", "dark"):
        return Response(status_code=422, content="Choose light or dark")
    response = Response(content=f"Saved theme={theme}")
    response.set_cookie("theme", theme, max_age=604800, httponly=True)
    return response


@router.post("/preferences/reset")
async def reset_preferences():
    response = Response(content="Removed theme preference")
    response.delete_cookie("theme")
    return response


app = Karak(router=router)
```

Run `uv run uvicorn main:app --reload`. In another terminal:

```sh
curl -i -H 'User-Agent: learning-karak' http://127.0.0.1:8000/users/42
```

The body is `User 42; theme=light; client=learning-karak`.
`context.value` is the current `Request`. Karak supplies it automatically;
you do not register a factory for it or send a `context` query parameter.
The name `context` is your choice; the annotation selects the value.

## Save a cookie, then send it back

Use curl's cookie jar, a local file that acts like a browser's cookie storage:

```sh
curl -i -c cookies.txt -X POST 'http://127.0.0.1:8000/preferences?theme=dark'
curl -i -b cookies.txt -H 'User-Agent: learning-karak' http://127.0.0.1:8000/users/42
```

The first response includes `Set-Cookie`. `-c` saves it to `cookies.txt`.
The second command uses `-b` to send that cookie; the response now says
`theme=dark`. POST inputs still come from the query string in this example.
Karak does not automatically bind a JSON request body.

Remove the preference and update the cookie jar:

```sh
curl -i -b cookies.txt -c cookies.txt -X POST http://127.0.0.1:8000/preferences/reset
curl -i -b cookies.txt http://127.0.0.1:8000/users/42
```

The theme is back to `light`. Deletion sends an expired cookie to the client;
it does not modify the cookies on the request already being processed.

Cookies are client-controlled strings. This example stores a display preference,
not an authenticated identity. Signing cookies and managing login sessions are
not built into Karak.

## Read headers and repeated values

```python
request.headers.get("accept", "*/*")
request.headers.getlist("x-tag")
```

Header names are case-insensitive: `User-Agent` and `user-agent` find the same
field. `.get()` returns the first value or your default. `.getlist()` returns
all values in order, or an empty list. `request.headers["missing"]` raises
`KeyError`. The request header collection is read-only.

Repeated headers are preserved instead of combined automatically. Repeated
incoming `Cookie` fields are joined with `; ` before parsing. Cookie names
are case-sensitive; duplicate names use the last parsed value. Cookie parsing
uses Python's `SimpleCookie`; malformed input may be ignored or produce an
empty cookie dictionary. Do not use a preference cookie as an authorization check.

## Know which data you are reading

| API | Example | Meaning |
| --- | --- | --- |
| `request.method` | `"GET"` | HTTP operation |
| `request.path` | `"/users/42"` | URL path without query string |
| `request.path_params` | `{"user_id": "42"}` | Raw matched strings; the handler receives converted `user_id=42` |
| `request.params` | `{"tag": ["python", "http"]}` | Query values, always stored as lists |
| `request.headers` | `.get("user-agent")` | Read-only header lookup |
| `request.cookies` | `.get("theme", "light")` | Parsed cookie strings |
| `request.state` | `{"request_id": "..."}` | Your mutable data for this request |
| `await request.body()` | `b"hello"` | Complete body bytes |

## Read a body explicitly

Add this endpoint **before** constructing `app`:

```python
@router.post("/echo")
async def echo(context: ResourceContext[Request]):
    body = await context.value.body()
    return Response(content=body, headers={"content-type": "application/octet-stream"})
```

```sh
curl --data-binary 'hello' http://127.0.0.1:8000/echo
```

The response is `hello`. `await` lets other work proceed while bytes arrive.
The body is cached: reading it again returns the same bytes, including `b""`
for an empty body. Concurrent reads on the same request share that cache.
A disconnect before the body completes raises `RuntimeError`.

The body is buffered in memory and currently has no built-in size limit.
Streaming, form parsing, and automatic JSON body validation are not implemented.

## Keep state inside one request

Use `request.state` to pass data between helpers handling the same request:

```python
async def describe_request(request: Request) -> str:
    return request.state["operation"]


@router.get("/operation")
async def operation(context: ResourceContext[Request]):
    request = context.value
    request.state["operation"] = "show-operation"
    return await describe_request(request)
```

Each request starts with its own empty dictionary. Two simultaneous callers
cannot overwrite each other's state through this dictionary. Multiple
`ResourceContext[Request]` parameters in a handler refer to the same request.
This state is separate from application resources and ASGI lifespan state.
It is not persistent storage; do not retain the request in a shared service.

## Use the same convention for shared services

`service: ResourceContext[ProductService]` supplies a registered application
service; `context: ResourceContext[Request]` supplies the current request.
Both expose `.value`. See the [complete service example](resources.md).

Karak checks context annotations and provider registration when constructing the
application. Context parameters cannot have defaults, be positional-only, or
use the name of a path placeholder. Query parameters cannot override them.
A missing registered provider prevents startup. An application resource cannot
depend on `Request`, because it lives longer than one request.

## Trace the preference round trip

Start with no cookie jar, save a dark theme, read it back, and reset it. Identify
which response carries `Set-Cookie` and which later request carries `Cookie`.
Then send a cookie directly with `curl -b 'theme=blue'`: the server receives a
client-supplied value even though the preference endpoint only sets light or
dark. Explain where validation would belong if the theme controlled behavior.

Next, move related endpoints into separate modules while preserving their URLs.
