<div align="center">

<img src="docs/content/assets/share-card-sphere.png" alt="A layered paper sphere in soft sage, blue, and cream" width="360">

# Karak

**Build Python backends with async functions, typed inputs, and shared resources.**

![Status: Experimental](https://img.shields.io/badge/status-experimental-bb9363?style=flat-square&labelColor=263e48)
![Python: 3.13+](https://img.shields.io/badge/python-3.13%2B-345f76?style=flat-square&labelColor=263e48&logo=python&logoColor=white)
![Runtime dependencies: 0](https://img.shields.io/badge/runtime_dependencies-0-657c62?style=flat-square&labelColor=263e48)
[![License: MIT](https://img.shields.io/badge/license-MIT-657c62?style=flat-square&labelColor=263e48)](LICENSE)

[Get started](#hello-world) &nbsp; · &nbsp; [Documentation](docs/README.md) &nbsp; · &nbsp; [Benchmarks](docs/content/benchmarks.md)

</div>

## How to use Karak

| I want to… | Start here |
| --- | --- |
| Run my first endpoint | [Hello World](#hello-world) |
| Accept values from a URL | [Path and query parameters](#read-path-and-query-parameters) |
| Handle a POST and choose a status code | [POST requests](#handle-a-post-request) |
| Read the current request | [Headers and cookies](#read-headers-and-cookies) |
| Send a cookie or custom header | [Response headers and cookies](#set-a-cookie-and-response-header) |
| Initialize a service once and reuse it | [Shared resources](#share-a-service-across-requests) |
| Split my app into feature files | [Project layout](#organize-a-growing-application) |

[Testing](docs/content/testing.md) · [Startup and shutdown](docs/content/application.md) · [Contributing](#development)

## Hello World

Install from a repository checkout. The development environment includes Uvicorn:

```sh
git clone https://github.com/grandimam/karak.git
cd karak
uv sync
```

Create `main.py`:

```python
from karak import Karak
from karak import Router

router = Router()


@router.get("/")
async def hello():
    return "Hello, world!"


app = Karak(router=router)
```

Run it:

```sh
uv run uvicorn main:app --reload
```

Open [localhost:8000](http://127.0.0.1:8000). You should see `Hello, world!`.

For the next examples, add imports at the top of `main.py` and handlers **before**
`app = Karak(router=router)`.

## Read path and query parameters

```python
@router.get("/users/{user_id}")
async def user(user_id: int, active: bool = True):
    return f"User {user_id}, active={active}"
```

```sh
curl 'http://127.0.0.1:8000/users/42?active=false'
# User 42, active=False
```

`user_id` comes from the path; `active` comes from the query string. Karak
converts them using the annotations. Missing required values and invalid inputs
return HTTP 422.

[More parameter types →](docs/content/parameters.md)

## Handle a POST request

```python
from karak import Response


@router.post("/greetings")
async def greet(name: str):
    return Response(status_code=201, content=f"Hello, {name}!")
```

```sh
curl -i -X POST 'http://127.0.0.1:8000/greetings?name=Sam'
# HTTP 201, with the body: Hello, Sam!
```

Here `name` is a query parameter. JSON bodies are not automatically bound to
handler parameters.

## Read headers and cookies

```python
from karak import Request
from karak import ResourceContext


@router.get("/preferences")
async def preferences(context: ResourceContext[Request]):
    request = context.value
    client = request.headers.get("x-client", "unknown")
    theme = request.cookies.get("theme", "light")
    return f"Client: {client}, theme: {theme}"
```

```sh
curl -H 'X-Client: web' -b 'theme=dark' http://127.0.0.1:8000/preferences
# Client: web, theme: dark
```

Karak supplies the current request through `ResourceContext[Request]`.
Use `await context.value.body()` to read body bytes, or `context.value.state`
to keep data for the current request.

[Request context →](docs/content/request-context.md)

## Set a cookie and response header

```python
@router.post("/preferences")
async def save_preferences():
    response = Response(content="Preference saved")
    response.headers["content-type"] = "text/plain; charset=utf-8"
    response.set_cookie("theme", "dark", httponly=True, samesite="lax")
    return response
```

```sh
curl -i -X POST http://127.0.0.1:8000/preferences
```

The response includes `Content-Type` and `Set-Cookie` headers.
Use `response.delete_cookie("theme")` to expire the cookie.

[Responses and cookies →](docs/content/responses.md)

## Share a service across requests

Replace `main.py` with this complete example:

```python
from dataclasses import dataclass

from karak import Karak
from karak import ResourceContext
from karak import Router
from karak import resource


@dataclass
class Catalog:
    names: dict[int, str]


@resource
def catalog() -> Catalog:
    return Catalog({1: "Tea", 2: "Coffee"})


router = Router()


@router.get("/products/{product_id}")
async def product(product_id: int, data: ResourceContext[Catalog]):
    return data.value.names.get(product_id, "Unknown product")


app = Karak(router=router)
```

```sh
curl http://127.0.0.1:8000/products/1
# Tea
```

Karak creates the catalog at startup and shares it across requests.
Use a generator factory when a resource needs cleanup at shutdown.

[Resource dependencies and cleanup →](docs/content/resources.md)

## Organize a growing application

Start with one file per feature and one test file per feature:

```text
app/
├── __init__.py
├── main.py
├── resources.py
├── users.py
└── orders.py
tests/
├── __init__.py
├── test_users.py
└── test_orders.py
```

Export a `router` from `users.py` and `orders.py`, then combine them in
`app/main.py`:

```python
from karak import Karak
from karak import Router

from app.users import router as users_router
from app.orders import router as orders_router

router = Router()
router.include(users_router)
router.include(orders_router)

app = Karak(router=router)
```

Run this layout with `uv run uvicorn app.main:app --reload`. Expand a feature
or its tests into a package when it needs several files.

[Router examples →](docs/content/routing.md) · [Project layout →](docs/content/project-layout.md)

## Documentation

[All guides](docs/README.md) · [Testing](docs/content/testing.md) ·
[Application lifecycle](docs/content/application.md) · [Benchmarks](docs/content/benchmarks.md)

Karak is experimental and not ready for production use. It currently supports
async GET/POST handlers, typed path/query inputs, text/byte responses, headers,
cookies, static files, and shared resources. Automatic JSON binding and responses
are not implemented. Unknown URLs currently return 500 rather than 404.
See [the project direction](docs/content/design.md) for planned capabilities.

## Development

```sh
uv sync
uv run python -m unittest discover -s tests
```

[Report an issue](https://github.com/grandimam/karak/issues) · [MIT License](LICENSE)
