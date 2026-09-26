---
title: Application
description: Create an ASGI application and understand its request and lifespan handling.
---

# The application.

<p class="lead">A small ASGI entry point for your Python handlers.</p>

```python
from karak import Karak

app = Karak()
```

An ASGI server such as Uvicorn calls `app(scope, receive, send)`. The server
owns the network connections; Karak handles the application logic.

## Request handling

For HTTP requests, the application passes control through exception handling,
route matching, parameter conversion, the async handler, and the response.

```text
ASGI server
  → Karak
  → ExceptionHandler
  → Router
  → Route and parameter validation
  → Async handler
  → Response
```

Handlers must currently be `async def` functions. A synchronous executor is a
design goal, not part of the ASGI implementation yet.

## Lifecycle

Karak acknowledges ASGI startup and shutdown messages. It does not yet expose
user-defined startup or shutdown hooks.

## Low-level requests

`Request` wraps an ASGI scope and receive callable. Code that works directly
with ASGI can use it to read request metadata and body bytes:

```python
from karak import Request


async def inspect_request(scope, receive):
    request = Request(scope, receive)
    body = await request.body()
    return request.path, request.method, request.params, body
```

`params` maps query keys to lists of strings. `body()` consumes request messages
and joins their chunks. Read the body once and keep the result; it is not cached.
The method raises `RuntimeError` if the client disconnects while it is reading.

This helper is low-level ASGI code, not a registered route. Route handlers do
not currently receive an injected `Request`. There is no `Request.json()`
method or automatic body binding.

## Current scope

Dependency injection, WebSockets, user lifecycle hooks, and durable background
jobs are future work. See [design notes](design.md) for the broader direction.
