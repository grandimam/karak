---
title: Test your backend
guide: true
description: Write repeatable tests for a service, HTTP responses, invalid input, and application resource cleanup.
---

# Turn a working example into repeatable checks.

<p class="lead">A test describes an observable result and checks that your application produces it.</p>

Until now, you have used a browser or curl to check your work. Those checks are
useful, but easy to forget after changing a handler. Automated tests let you
repeat the same checks without manually starting a server for each one.

We will use Python's built-in `unittest` module. The example builds on
[shared resources](resources.md) and [application lifecycle](application.md).

## Use a small catalog application

Replace the root `main.py` with this complete example. Keep the multi-module
version from [routers and modules](routing.md) separately if you want to return to it later.

```python
from collections.abc import AsyncIterator
from dataclasses import dataclass

from karak import Karak
from karak import ResourceContext
from karak import Response
from karak import Router
from karak import resource


@dataclass
class Catalog:
    names: dict[int, str]

    def name_for(self, product_id: int) -> str:
        return self.names.get(product_id, "")


@resource
async def catalog() -> AsyncIterator[Catalog]:
    value = Catalog({1: "Tea", 2: "Coffee"})
    try:
        yield value
    finally:
        value.names.clear()


router = Router()


@router.get("/products/{product_id}")
async def product(product_id: int, data: ResourceContext[Catalog]):
    name = data.value.name_for(product_id)
    if not name:
        return Response(status_code=404, content="Product not found")
    return name


app = Karak(router=router, resources=[catalog])
```

`Catalog` contains ordinary Python behavior. The handler translates its result
into HTTP. The resource factory owns the catalog's lifetime. Test those
responsibilities at their boundaries.

## Start with the service itself

Create `test_main.py` beside `main.py`:

```python
import unittest

from main import Catalog


class CatalogTests(unittest.TestCase):
    def test_known_product(self):
        catalog = Catalog({1: "Tea"})
        self.assertEqual(catalog.name_for(1), "Tea")

    def test_missing_product(self):
        catalog = Catalog({1: "Tea"})
        self.assertEqual(catalog.name_for(99), "")
```

Run your application tests from the repository root:

```sh
uv run python -m unittest test_main -v
```

The two tests should pass. Each constructs its own catalog, performs one
operation, and checks the result. These are **unit tests**: they exercise the
Python object without a server or framework lifecycle.

## Exercise HTTP through the application

An **integration test** checks collaborating parts. Here, that means routing,
input conversion, resource injection, handler code, and response generation.
We can call the ASGI application directly without opening a network socket.

Create `asgi_helpers.py` with the following helpers. They play the small part
of the server needed by these tests:

```python
import asyncio
from contextlib import asynccontextmanager


@asynccontextmanager
async def running(app):
    incoming = asyncio.Queue()
    outgoing = asyncio.Queue()
    state = {}
    task = asyncio.create_task(
        app({"type": "lifespan", "state": state}, incoming.get, outgoing.put)
    )
    try:
        await incoming.put({"type": "lifespan.startup"})
        started = await asyncio.wait_for(outgoing.get(), timeout=2)
        if started["type"] != "lifespan.startup.complete":
            raise AssertionError(started)
        try:
            yield state
        finally:
            await incoming.put({"type": "lifespan.shutdown"})
            stopped = await asyncio.wait_for(outgoing.get(), timeout=2)
            if stopped["type"] != "lifespan.shutdown.complete":
                raise AssertionError(stopped)
            await task
    finally:
        if not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass


async def get(app, path, state):
    messages = []

    async def receive():
        return {"type": "http.request", "body": b""}

    async def send(message):
        messages.append(message)

    await app(
        {
            "type": "http", "method": "GET", "path": path,
            "query_string": b"", "state": state.copy(),
        },
        receive,
        send,
    )
    return messages[0]["status"], messages[1]["body"]
```

`running()` starts the application, keeps its resources alive while a test
runs, and shuts it down afterward. The queues exchange lifecycle messages
with the app. The task lets the application wait for shutdown while the test
makes requests. The timeout makes a broken startup fail instead of hanging.

`get()` supplies a request scope and records outgoing response messages.
The scope is a dictionary describing the request. Copying lifespan state into
it makes the initialized resources available. This helper is intentionally
limited to these non-streaming GET examples; it is not a general HTTP client.

Add these imports at the top of `test_main.py`:

```python
from main import app
from asgi_helpers import get
from asgi_helpers import running
```

Then add this test class below `CatalogTests`:

```python
class ProductHTTPTests(unittest.IsolatedAsyncioTestCase):
    async def test_product_responses(self):
        async with running(app) as state:
            status, body = await get(app, "/products/1", state)
            self.assertEqual(status, 200)
            self.assertEqual(body, b"Tea")

            status, body = await get(app, "/products/not-a-number", state)
            self.assertEqual(status, 422)
            self.assertIn(b"product_id", body)

            status, body = await get(app, "/products/99", state)
            self.assertEqual(status, 404)
            self.assertEqual(body, b"Product not found")
```

`IsolatedAsyncioTestCase` runs async test methods in an event loop. The response
body is bytes, which is why the assertions use `b"Tea"` rather than `"Tea"`.
The invalid integer is rejected before the handler runs; the missing integer
ID reaches the handler and produces its explicit 404.

Run `uv run python -m unittest test_main -v` again. There are now three tests.
These HTTP checks do not measure Uvicorn or real network behavior; curl and the
[benchmark suite](benchmarks.md) exercise that additional layer.

## Check resource cleanup

A factory's cleanup is also behavior worth testing. Add these imports to
`test_main.py`:

```python
from contextlib import asynccontextmanager
from main import catalog
```

Add one more class:

```python
class CatalogLifetimeTests(unittest.IsolatedAsyncioTestCase):
    async def test_cleanup_clears_catalog(self):
        async with asynccontextmanager(catalog.factory)() as value:
            self.assertEqual(value.name_for(1), "Tea")
        self.assertEqual(value.names, {})
```

This test drives the generator factory directly and checks its cleanup after
leaving the context. It tests factory behavior; the earlier HTTP test exercises
the framework's startup and shutdown messages. All four tests should now pass.

## Extend the checks as your application grows

The single-file example keeps `test_main.py` beside `main.py` for convenience.
For a multi-feature application, start with `tests/test_users.py` and
`tests/test_orders.py`, plus an empty `tests/__init__.py`. When a feature needs
several test files, grow just that feature into a test package. See
[project layout](project-layout.md#grow-tests-at-the-same-pace) for the directory
structure and discovery command. Shared ASGI helpers can move into
`tests/helpers.py`; update imports to use `tests.helpers`.

Keep service tests focused on business behavior and HTTP tests focused on the
public response. When adding an endpoint, cover its successful result and the
meaningful failures callers can encounter. For cookies, test the outgoing
`Set-Cookie` header and a subsequent request carrying `Cookie`.

Use [routers](routing.md) to organize a larger application; the same ASGI test
helpers can call its composed app. Tests that use resources must keep lifespan
running so handlers receive initialized instances.
