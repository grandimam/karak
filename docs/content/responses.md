---
title: Send responses
description: Return a message, choose a status code, and understand the errors callers receive.
---

# Choose what your caller receives.

<p class="lead">Send back a message and a status that describes the result.</p>

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


app = Karak(routes=[router])
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

## Can I return JSON?

Automatic JSON responses, custom headers, and streaming are not available in
the main framework yet. Use text or bytes for the current examples. JSON
request and response support is part of [the plan](design.md).

## Understand error responses

| Response | What to do |
| --- | --- |
| HTTP 422 | Check the parameter named in the response. A required value may be missing or have the wrong format. |
| HTTP 500 with `Internal Server Error` | Check the server terminal for the traceback from your endpoint. |
| HTTP 500 with `Route Not Found` | Check the requested URL. Unknown paths do not return 404 yet. |
| HTTP 405 | Check that the endpoint supports the requested HTTP method. |

For the routing-related cases, see [current limitations](routing.md#prototype-limitations).
