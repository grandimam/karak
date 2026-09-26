---
title: Responses
description: Return text, bytes, and custom status codes, and understand error responses.
---

# Send something back.

<p class="lead">Return text, bytes, or an explicit response.</p>

```python
from karak import Karak
from karak import Response

app = Karak()


@app.get(path="/", methods=["GET"])
async def index():
    return "Hello from Karak"


@app.get(path="/accepted", methods=["GET"])
async def accepted():
    return Response(status_code=202, content="Accepted")
```

Ordinary text is encoded as UTF-8. The default status is 200. A `Response`
lets you set another status code explicitly.

## Bytes and empty bodies

Bytes can be returned directly. Return `b""` for an empty body. Automatic JSON
serialization, custom response headers, and streaming responses are not
implemented in the ASGI framework yet.

## Errors

Invalid or missing input produces HTTP 422 with a text explanation. An
unexpected handler exception is logged through `karak.errors`; the client
receives HTTP 500 with the body `Internal Server Error`.

Routing errors have [prototype limitations](routing.md#prototype-limitations),
including the current status for unmatched paths.

## The other implementation

The [free-threaded experiment](free-threaded.md) has its own `Response` type
with JSON support. It is not interchangeable with `karak.Response`.
