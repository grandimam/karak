---
title: Follow a request
guide: true
description: Trace an HTTP request through the server, router, handler, and response, then understand why Karak handlers use async def.
---

# Follow a request from the client to Python.

<p class="lead">The client asks, the server receives, and your handler decides the response.</p>

You have already run [Hello World](index.md) and added [endpoints](endpoints.md).
Keep that `main.py` open. This guide explains what the code and server are doing
before we add input validation.

## Trace GET /health

When you run `curl -i http://127.0.0.1:8000/health`:

1. **curl is the client.** It sends an HTTP request with method GET and path `/health`.
2. **Uvicorn is the server.** It listens on port 8000 and delivers the request to Karak.
3. **Karak matches a route.** It finds the function registered for GET `/health`.
4. **Your handler runs.** `health()` returns the string `"ok"`.
5. **Karak creates the response.** It encodes that string as bytes with status 200.
6. **Uvicorn sends it back.** curl prints the status, headers, and body.

HTTP is the request/response protocol used here. ASGI is the Python interface
between Uvicorn and Karak. You do not need to implement ASGI to write handlers.
The [testing guide](testing.md) uses that interface to call the application directly.

## Separate setup from request handling

Python imports `main.py` when the server starts. Importing creates the router,
registers the decorated functions, and constructs `app`. It does not call each
handler once to prepare a response.

When a matching request arrives, Karak calls the handler for that request.
Two requests can therefore execute the same function with different inputs.
A module-level object can be shared between requests; a local variable inside
a handler belongs to that invocation.

This distinction will matter when we introduce request state and application
resources. For now, avoid storing a caller's data in a shared module variable.

## Understand async def and await

Karak handlers use `async def`. Calling an async function creates a coroutine;
Karak awaits it so its body can run. You can return a value immediately, as the
health endpoint does. An async function does not have to contain `await`.

When your code awaits an operation that is not finished, the event loop can run
other tasks while that operation waits. For example, you can read
request bytes with `await request.body()`.

`async def` does not make blocking work nonblocking. A slow synchronous library
call or a long CPU loop still occupies the event-loop thread. Use libraries with
async interfaces for asynchronous I/O, and treat CPU-heavy work as a separate
design decision. The endpoints in these examples perform only small operations.

## Recognize where a failure happens

A connection failure means the client could not reach a server. An HTTP error
response means a server answered: for example, Karak returns 405 when a path
matches but the method does not. If a handler raises an unexpected exception,
Karak logs it and returns 500.

See [responses and errors](responses.md) for the caller-facing behavior. To pass
values into a handler, continue with [path and query parameters](parameters.md).
