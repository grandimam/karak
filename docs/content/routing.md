---
title: Define routes
description: Give your application endpoints and read values from their URLs.
---

# Give your application another endpoint.

<p class="lead">Choose the URL someone visits and the function that answers it.</p>

A route connects a URL to your code. In the [quickstart](index.md), `/` returned
a greeting. To add a user endpoint, put this below your existing `app = Karak()`:

```python
@app.get(path="/users/{user_id}", methods=["GET"])
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
@app.get(path="/users/{user_id}", methods=["GET"])
async def user(user_id: int, active: bool = True):
    return f"User {user_id} · active={active}"
```

Replace the earlier `user` endpoint with this version rather than registering
both. `/users/42?active=false` responds with `User 42 · active=False`. If you
leave `active` out, the default `True` applies.

Continue to [read request values](parameters.md) for lists, defaults, and
other supported types.

## Choose an HTTP method

The current decorator takes both `path=` and `methods=`. Although it is named
`app.get`, the list supplied in `methods` determines which methods it accepts.
Separate `app.post`, `app.put`, and `app.delete` helpers are not available yet.

The current guides focus on GET endpoints. Automatic JSON request-body
handling is still planned.

## Prototype limitations

Keep these limitations in mind when trying routes:

- Use matching names for path placeholders and function parameters, and
  annotate every parameter. Mistakes here prevent the endpoint from being added.
- Avoid registering different method-specific handlers for the same path.
  A request can receive HTTP 405 before reaching the intended handler.
- An unknown URL currently returns HTTP 500 with `Route Not Found`, rather
  than HTTP 404. Check the URL and the routes you have defined.
- Keep literal paths simple. Characters such as `.` and `+` can be interpreted
  as patterns instead of matching exactly as written.
