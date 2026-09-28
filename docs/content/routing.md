---
title: Define routes
description: Give your application endpoints and read values from their URLs.
---

# Give your application another endpoint.

<p class="lead">Choose the URL someone visits and the function that answers it.</p>

A route connects a URL to your code. In the [quickstart](index.md), `/` returned
a greeting. Define endpoints on your `router`, then pass it in the application's
`routes` list. Add this before constructing `Karak(routes=[router])`:

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

After defining your endpoints, pass the router into the application:

```python
app = Karak(routes=[router])
```

`Router` and `Mount` both implement `BaseRouter.flatten(prefix="")`. This method
produces endpoint definitions with complete paths. `Karak` uses those definitions
to create executable routes and validate handler signatures during initialization.
The application then matches those routes directly when serving requests.

Finish decorating your routers before constructing the app. Routers remain
editable, but later additions are only included when a new application is
constructed. There is no separate startup compilation or freezing step.

## Mount a router

Use `Mount` to give a router a shared prefix. Mounts can wrap any `BaseRouter`,
including another mount. Prefixes and endpoint paths can both contain parameters:

```python
from karak import Karak
from karak import Mount
from karak import Router

posts = Router()


@posts.get("/{post_id}")
async def post(user_id: int, post_id: int, preview: bool = False):
    return f"User {user_id}, post {post_id}, preview={preview}"


users = Mount(path="/users/{user_id}/posts", router=posts)
app = Karak(routes=[Mount(path="/api", router=users)])
```

`GET /api/users/42/posts/7?preview=true` passes `user_id=42`, `post_id=7`, and
`preview=True` to `post`. Each handler must declare all parameters inherited
from its mounts. A query value with the same name cannot override a path value.

To group several routers, pass them in another router's constructor, for example
`Router(routes=[Mount(path="/users", router=users_router), other_router])`.
Endpoint decorators on that parent add its own routes after those child groups.

Mounts only carry prefixes and references to children. The complete tree is
flattened when `Karak` is constructed, so additions made to a child before then
are included. Reusing a router in different mounts or applications leaves its
original paths unchanged.

Mount prefixes must start with `/`; a trailing slash is ignored when joining
them to child paths. Mounting at `/` adds no prefix. Under `/api`, an endpoint
path of `""` matches `/api`, while `"/"` matches `/api/`. There are no automatic
slash redirects. Duplicate parameter names in a complete path are rejected
when the application is constructed.

## Prototype limitations

Keep these limitations in mind when trying routes:

- Use matching names for path placeholders and function parameters, and
  annotate every parameter. Mistakes here prevent application construction.
- An unknown URL currently returns HTTP 500 with `Route Not Found`, rather
  than HTTP 404. Check the URL and the routes you have defined.
- Routes are checked in registration order. Put static paths before overlapping
  parameterized paths. A method mismatch continues searching for a matching
  endpoint before returning HTTP 405.
- Literal characters such as `.` and `+` match exactly; `{name}` introduces a
  path parameter.
