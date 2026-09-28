---
title: Share application resources
description: Register resources, declare typed dependencies with ResourceContext, and share initialized services across requests.
---

# Create a service once and share it across requests.

<p class="lead">Declare resource factories. Karak handles dependency ordering, startup, and cleanup.</p>

An application resource is an object that lives while your application is running:
a database pool, a client, a cache, or a service. Decorate its factory with
`@resource` and register the resulting handle with `Karak(resources=[...])`.

## Build a working example

Save this as `main.py` in your repository checkout. It uses an in-memory catalog
so you can run it without a database or additional packages:

```python
from collections.abc import AsyncIterator
from dataclasses import dataclass

from karak import Karak
from karak import ResourceContext
from karak import Router
from karak import resource


@dataclass
class Catalog:
    names: dict[int, str]


class ProductService:
    def __init__(self, catalog: Catalog):
        self.catalog = catalog

    def name_for(self, product_id: int) -> str:
        return self.catalog.names.get(product_id, "Unknown product")


@resource
async def catalog() -> AsyncIterator[Catalog]:
    value = Catalog(names={1: "Tea", 2: "Coffee"})
    try:
        yield value
    finally:
        value.names.clear()


@resource
def products(data: ResourceContext[Catalog]) -> ProductService:
    return ProductService(data.value)


router = Router()


@router.get("/products/{product_id}")
async def product(product_id: int):
    return products.get().name_for(product_id)


app = Karak(router=router, resources=[products, catalog])
```

Start the server:

```sh
uv run uvicorn main:app --reload
```

In another terminal:

```sh
curl http://127.0.0.1:8000/products/1
```

The response is `Tea`. Both resources are initialized before the server starts
accepting requests. The catalog is created before the service even though it
appears second in the registration list.

## Declare a dependency with its type

In `data: ResourceContext[Catalog]`, `Catalog` identifies the required resource
type. Karak finds its provider, initializes it, then wraps the instance in a
`ResourceContext`. The factory accesses the instance through `data.value`.

The parameter name `data` is your choice. It does not have to match the provider
name `catalog`. The factory remains synchronous because Karak finishes resolving
its dependencies before calling it.

Every resource factory needs a return annotation. For a regular function or
coroutine, annotate the value it returns. For a generator, annotate the yielded
type using `Iterator[T]` or `AsyncIterator[T]`.

Matching uses the exact declared type. Karak does not infer providers from
parameter names, subclasses, or the runtime type of a returned object. Return
annotations are declarations; returned values are not runtime type-checked.
Keep annotated classes importable at module scope so postponed annotations can
be resolved when the application is constructed.

`ResourceContext[T]` is a wrapper for one dependency in a resource factory.
It is not a lookup dictionary, and it is not injected into endpoint parameters.
Declare each factory parameter as `ResourceContext[T]`; use keyword-compatible
parameters, without positional-only parameters, `*args`, or `**kwargs`.

## Register every provider

The decorator creates a handle; registration assigns it to an application:

```python
app = Karak(router=router, resources=[products, catalog])
```

Include every dependency in the list. Karak does not scan modules or register
dependencies implicitly. Missing providers, duplicate registrations, ambiguous
types, and dependency cycles are rejected while constructing the application,
before any resource factory runs.

There must be one provider per declared type. Two providers returning the same
`DatabasePool` type are ambiguous, even if their names differ. For read and write
pools, use distinct application wrapper types or one resource containing both
pools. Named qualifiers are not supported.

## Access resources from a handler

The decorated name is a typed `Resource[T]` handle. Its `.get()` method returns
the initialized instance for the application serving the current request:

```python
@router.get("/products/{product_id}")
async def product(product_id: int):
    service = products.get()
    return service.name_for(product_id)
```

Use this endpoint in place of the earlier version. `.get()` is synchronous and
does not create resources. Repeated calls return the same instance within the
application lifespan. Two services depending on the catalog receive that same
catalog object.

Calls at module import time, outside an active application, or after shutdown
raise `RuntimeError`. An unregistered handle also raises an error. Calling a
resource handler without active lifespan state produces HTTP 500 and logs the
error. Keep the server's ASGI lifespan support enabled.

## Own cleanup in the factory

Use a generator when a resource needs cleanup. Karak keeps it open after its
single yield and exits it at shutdown. Put cleanup in `finally` or use a context
manager around the yield, so it also runs on failure or cancellation.

For a database driver, the factory would have this shape. `create_pool` and
`DatabasePool` below stand for your driver's factory and type, not Karak APIs:

```python
@resource
async def database() -> AsyncIterator[DatabasePool]:
    async with create_pool(database_url) as pool:
        yield pool
```

Do not add `@asynccontextmanager` to a resource generator. Karak enters the
generator as a context manager internally. Supported factory forms are:

| Factory | Annotation | Behavior |
| --- | --- | --- |
| `def` returning a value | `-> T` | Store the returned instance |
| `async def` returning a value | `-> T` | Await setup and store the instance |
| `def` yielding once | `-> Iterator[T]` | Enter at startup and exit at shutdown |
| `async def` yielding once | `-> AsyncIterator[T]` | Await entry and exit |

`Generator[T, None, None]` and `AsyncGenerator[T, None]` annotations also work.
Plain returned objects are not automatically closed, even if they have a `close`
method. Use a generator for resources that need release. Synchronous setup and
cleanup run on the event-loop thread, so avoid blocking work there.

Dependencies initialize before their consumers and clean up in reverse order.
If a service fails during startup, already-acquired resources are released.
If cleanup fails, remaining cleanup is still attempted. Karak reports setup and
cleanup errors through ASGI lifespan failure messages. A failed HTTP request
does not close shared application resources.

## Choose what to share

All registered resources currently have application scope. Each server worker
creates its own instances; they are not shared across processes. Separate
applications can register the same handles without sharing instances.

Shared objects must support concurrent use. Keep user identity, mutable request
state, borrowed database connections, and transactions out of shared services.
Services can hold a pool and borrow connections for individual operations.
Opening and committing transactions remains application code's responsibility.

If only one service needs a pool, its generator can create the pool and yield
the service directly. A separate pool registration is useful when multiple
independently registered services need the same pool.

## Combine resources with a startup hook

You can still pass an async context manager using `lifespan=` for additional
startup and shutdown work. Resources initialize before that hook enters, so
the hook can use `.get()`. The hook exits before resource cleanup begins.
See [application startup and shutdown](application.md#add-startup-and-shutdown-work).

## Test services and applications

Test ordinary service classes directly, without starting Karak:

```python
service = ProductService(Catalog(names={1: "Test tea"}))
assert service.name_for(1) == "Test tea"
```

To exercise a factory directly, call the handle's `.factory` with resolved
wrappers yourself. In the example, `products.factory(ResourceContext(catalog_value))`
constructs a service. This bypasses Karak's lifecycle management.

For ASGI integration tests, drive lifespan startup, keep it running while sending
requests, and send shutdown afterward. Give the lifespan scope a `state` dictionary
and copy that dictionary into each HTTP scope. Karak uses ASGI lifespan state to
select the correct application resource instances; running requests directly
without it does not initialize resources.

[Run your application →](application.md){: .next-link }
