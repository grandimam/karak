---
title: Routing
description: Register async routes and bind named path parameters.
---

# Give your code a route.

<p class="lead">Connect a path and an HTTP method to an async function.</p>

```python
from karak import Karak

app = Karak()


@app.get(path="/users/{user_id}", methods=["GET"])
async def user(user_id: int):
    return f"User {user_id}"
```

`/users/42` passes the integer `42` to the handler. Every named placeholder in
the path must have a corresponding handler parameter.

## Registration

The decorator currently requires keyword arguments: `path=` and `methods=`.
Despite its name, `app.get(...)` registers the methods supplied in the list.
Separate `app.post(...)`, `app.put(...)`, and `app.delete(...)` helpers do not
exist in this implementation yet.

Annotations are inspected when a route is registered. Missing path parameters,
unsupported annotations, and unannotated handler parameters fail at registration.

## Query values

A parameter whose name is absent from the route path comes from the query
string. A default makes it optional:

```python
@app.get(path="/users/{user_id}", methods=["GET"])
async def user(user_id: int, active: bool = True):
    return f"User {user_id} · active={active}"
```

Read [parameters](parameters.md) for supported types and validation behavior.

## Prototype limitations

Routes are checked in registration order. The router currently returns HTTP
405 as soon as it finds a matching path with a different method. Avoid separate
method-specific registrations for the same path until this selection is improved.

An unmatched path currently returns HTTP 500 with `Route Not Found`; it does not
yet return HTTP 404. Route patterns use regular expressions internally, so
literal regex characters in paths are not currently escaped.
