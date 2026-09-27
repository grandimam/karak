---
title: Define routes
description: Give your application endpoints and read values from their URLs.
---

# Give your application another endpoint.

<p class="lead">Choose the URL someone visits and the function that answers it.</p>

A route connects a URL to your code. In the [quickstart](index.md), `/` returned
a greeting. Define endpoints on your `router`, then pass `router.routes` into
`Karak` when constructing the application. Add this before that constructor:

```python
@router.get("/users/{user_id}")
async def user(user_id: int):
    return f"User {user_id}"
```

Start the server and visit
[localhost:8000/users/42](http://127.0.0.1:8000/users/42). The response is:

```text
User 42
```

## Accept a value in the URL

`{user_id}` marks the part of the URL that can change. Name the function
parameter `user_id` too, and use `int` to ask for an integer.

Visit `/users/7` to receive `User 7`. Visit `/users/alex` and Karak returns an
HTTP 422 validation response because `alex` cannot be converted to an integer.

## Add optional controls

Use query parameters for values such as filters or page numbers. Add this
parameter to the same user endpoint:

```python
@router.get("/users/{user_id}")
async def user(user_id: int, active: bool = True):
    return f"User {user_id} · active={active}"
```

Replace the earlier `user` endpoint with this version rather than registering
both. `/users/42?active=false` responds with `User 42 · active=False`. If you
leave `active` out, the default `True` applies.

Continue to [read request values](parameters.md) for lists, defaults, and
other supported types.

## Choose an HTTP method

Use `@router.get(path)` for GET endpoints and `@router.post(path)` for POST
endpoints. The decorator selects the HTTP method; there is no `methods=`
argument. Other method decorators and automatic JSON request-body handling are
still planned.

```python
@router.post("/users")
async def create_user(name: str):
    return f"Created {name}"
```

## Construct the application

After defining your endpoints, pass the router's routes into the application:

```python
app = Karak(routes=[router])
```

The application copies that list during initialization. Finish decorating your
router before constructing the app. There is no routing compilation or freeze
step at startup, and the router remains editable. Later additions to the
original router are not added to an already constructed application's copy.

## Mount declarations

`Mount` currently holds a path prefix and a child router:

```python
from karak import Mount
from karak import Router

users = Router()
api = Router(routes=[Mount(path="/users", router=users)])
```

**Mount dispatch is not implemented.** The declaration is available for the
routing design; nested paths and inherited parameters are not resolved yet.
Attempting to dispatch through a mount raises `NotImplementedError`.

## Prototype limitations

Keep these limitations in mind when trying routes:

- Use matching names for path placeholders and function parameters, and
  annotate every parameter. Mistakes here prevent the endpoint from being added.
- An unknown URL currently returns HTTP 500 with `Route Not Found`, rather
  than HTTP 404. Check the URL and the routes you have defined.
- Routes are checked in registration order. Put static paths before overlapping
  parameterized paths. A method mismatch continues searching for a matching
  endpoint before returning HTTP 405.
- Literal characters such as `.` and `+` match exactly; `{name}` introduces a
  path parameter.
