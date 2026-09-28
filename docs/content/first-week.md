---
title: Your first week with Karak
description: Build backend fundamentals through seven practical sessions, from your first endpoint to a tested application.
---

# Build backend skills in your first week.

<p class="lead">Build a small catalog backend while learning the decisions behind production applications.</p>

Karak's goal is to make building production Python backends a coherent skill:
handling HTTP, validating inputs, managing resources, and operating an application.
Start with the HTTP foundation available today. Karak is experimental; this
week prepares you to build and explain a small local application, not to claim
that it is ready to serve production traffic.

This suggested pace assumes basic Python: functions, imports, dictionaries,
classes, and exceptions. Set aside roughly one to two hours per session and
repeat a session when its checkpoint is still unclear. If Python is new too,
take longer. You do not need to understand all of ASGI before your first endpoint.

## Day 1: Answer a request

Follow [installation](installation.md), the [quickstart](index.md), and
[how Karak works](introduction.md). Run `main.py`, visit `/`, edit the message,
and observe the result. A backend waits for requests and sends responses;
Uvicorn handles network connections while Karak calls your handler.

**Checkpoint:** Starting from a stopped server, run it and explain the roles of
`Router`, `Karak`, and Uvicorn without copying the guide.

## Day 2: Organize operations

Read [define routes](routing.md). Add `/products/{product_id}` and
`/products/featured`. Put the literal `/products/featured` route first. Split
product and preference endpoints into modules and combine them with `include()`.

**Checkpoint:** Predict which handler receives each URL. Deliberately register
a duplicate GET path and read the construction error, then fix it.

## Day 3: Validate caller input

Read [request values](parameters.md). Add `limit: int = 10` and repeated query
filters to a list endpoint. Try a missing required input, invalid integer,
and valid request. Use [responses](responses.md) to return a 404 when a requested
product does not exist in your small in-memory catalog.

**Checkpoint:** Explain the difference between invalid input (422), a missing
product (your explicit 404), and a handler bug (500). Notice that unknown routes
currently return 500; this is a framework limitation.

## Day 4: Read context and remember a preference

Run the complete [request context example](request-context.md). Inspect request
headers, store a theme cookie, send it back, and delete it. Read a raw body with
`await request.body()` and use `request.state` in a helper.

**Checkpoint:** Explain why changing request state does not persist a preference
for tomorrow, and why a client-provided cookie cannot prove who a user is.

## Day 5: Share a service with a defined lifetime

Run the [resource guide](resources.md). Inject `ResourceContext[ProductService]`
into a handler and compare its lifetime with `ResourceContext[Request]`.
Add a generator factory and observe its setup and cleanup.

**Checkpoint:** Explain why a pool can be shared while a current user's identity
must not be stored in that shared object. Stop the server and verify cleanup.

## Day 6: Test the request path

Read [testing the application](resources.md#test-services-and-applications).
Test your catalog class directly, then exercise the ASGI application. Start
lifespan when a test uses registered resources. Use the repository tests as
working examples: `tests/test_route_validation.py` for requests and
`tests/test_request_context.py` for cookies, bodies, and resource contexts.

From the repository root, run:

```sh
uv run python -m unittest discover -s tests
```

**Checkpoint:** Your application checks a successful request, invalid input,
missing product, cookie round trip, and isolated state for simultaneous callers.
A test should check an observable outcome, not just call the function.

## Day 7: Explain what operating it would require

Review [application lifecycle](application.md) and [Karak's direction](design.md).
Write down where data lives, who owns each resource, what happens on failure,
and how you would observe a failed request.

Your catalog is still in memory. Persistence, authentication, authorization,
request-size limits, migrations, deployment, and operational monitoring need
explicit decisions and implementation before a real service can rely on it.
Karak does not provide a complete production stack today. `--reload` is for
local development. Learning the framework's API is one part of backend engineering.

**Checkpoint:** Demonstrate your endpoints and tests, trace one request from
client to response, and identify the remaining work for your particular service.

By the end of these sessions, you have a concrete foundation: a modular, tested
HTTP application and an understanding of its boundaries. Continue by applying
those concepts to a small backend you care about.
