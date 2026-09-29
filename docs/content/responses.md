---
title: Responses and errors
guide: true
description: Return a message, choose a status code, and understand the errors callers receive.
---

# Choose what your caller receives.

<p class="lead">Send back a message and a status that describes the result.</p>

You can now receive typed inputs. A response is your application's answer:
a numeric status, optional headers, and a body. The status communicates the
outcome; the body carries the content. Use a plain return value for text, or a `Response` object when you need
control over the status, headers, or cookies.

## Return a message

Using the router from the quickstart, return a string from your endpoint to
send a text response with HTTP 200:

```python
@router.get("/")
async def index():
    return "Hello from Karak"
```

The caller receives `Hello from Karak`. Text can include Unicode characters.

## Choose a status code

Use `Response` when you want to specify the status yourself. This is a complete
example you can save as `main.py`:

```python
from karak import Karak
from karak import Router
from karak import Response

router = Router()


@router.get("/users/{user_id}")
async def user(user_id: int):
    if user_id != 42:
        return Response(status_code=404, content="User not found")
    return "User 42"


app = Karak(router=router)
```

Start it with `uv run uvicorn main:app --reload`, then inspect the status and
body together:

```sh
curl -i http://127.0.0.1:8000/users/7
```

The response has status 404 and the body `User not found`. Request `/users/42`
instead to receive HTTP 200 with `User 42`.

## Return bytes or an empty body

You can return bytes directly. Return `b""` when you want an empty response
body, or use `Response(status_code=204, content=b"")` for a response with no
content and an explicit 204 status.

## Send headers

Headers are named metadata sent before the response body. For example, a
content type tells the caller how to interpret the bytes:

```python
response = Response(
    content="Hello",
    headers={"content-type": "text/plain; charset=utf-8"},
)
response.headers["x-example"] = "karak"
```

Return `response` from your handler. Header names are case-insensitive.
Assignment replaces all existing values for that name. Use
`response.headers.append("x-tag", "another")` to add a repeated field,
`.getlist("x-tag")` to read all its values, or `del response.headers["x-tag"]`
to remove it. `.get()` returns the first value. Invalid names and control
characters in values are rejected. Set headers before returning the response.

## Set and delete cookies

Use the response to ask a browser to remember a value:

```python
response = Response(content="Preference saved")
response.set_cookie("theme", "dark", max_age=604800, httponly=True)
```

Each call adds a separate `Set-Cookie` header. On a later request, read the
value through `context.value.cookies`. Follow the [cookie round-trip example](request-context.md#save-a-cookie-then-send-it-back)
to see both sides working together.

| Option | Meaning |
| --- | --- |
| `max_age=604800` | Keep the cookie for seven days, expressed in seconds; omitted by default |
| `expires=...` | An HTTP date string or UTC-aware `datetime` for expiry; omitted by default |
| `path="/"` | Send the cookie to paths beneath `/`; this is the default |
| `domain=...` | Optional domain scope; omitted by default |
| `secure=True` | Only send over secure connections; defaults to `False` for local HTTP |
| `httponly=True` | Hide the cookie from browser JavaScript; defaults to `False` |
| `samesite="lax"` | Browser cross-site cookie policy; accepts `lax`, `strict`, or `none` |

Use `secure=True` when serving cookies over HTTPS. These helpers serialize
cookie attributes; they do not implement authentication or session storage.

To remove the preference:

```python
response = Response(content="Preference removed")
response.delete_cookie("theme")
```

Deletion sends an expired cookie with `Max-Age=0`. Pass the same `path` and
`domain` used when setting it; a cookie with a different scope is a different
cookie.

## Can I return JSON?

Automatic JSON responses and streaming are not available in the main framework
yet. You can serialize JSON explicitly with Python's `json.dumps()` and return
the resulting string in a `Response` with `content-type: application/json`.

## Understand error responses

| Response | What to do |
| --- | --- |
| HTTP 422 | Check the parameter named in the response. A required value may be missing or have the wrong format. |
| HTTP 500 with `Internal Server Error` | Check the server terminal for the traceback from your endpoint. |
| HTTP 500 with `Route Not Found` | Check the requested URL. Unknown paths do not return 404 yet. |
| HTTP 405 | Check that the endpoint supports the requested HTTP method. |

For the routing-related cases, see [current limitations](routing.md#prototype-limitations).

## Compare validation and application errors

For the complete user example above:

| Request | Outcome | Where it is decided |
| --- | --- | --- |
| `/users/42` | HTTP 200, `User 42` | The handler finds the user |
| `/users/7` | HTTP 404, `User not found` | The handler rejects an unknown ID |
| `/users/alex` | HTTP 422 | Karak rejects the invalid integer before calling the handler |

Use `curl -i` to inspect the status, headers, and body together. Continue with
[request context](request-context.md) to read the headers and cookies sent by
the caller.
