<div align="center">

<img src="docs/content/assets/share-card-sphere.png" alt="A layered paper sphere in soft sage, blue, and cream" width="460">

# Karak

**Python backend development should be integrated, not assembled.**

One coherent system to learn deeply, build with, and operate.<br>
Learn the fundamentals. Learn Karak deeply. Build serious Python backends.

![Status: Experimental](https://img.shields.io/badge/status-experimental-bb9363?style=flat-square&labelColor=263e48)
![Python: 3.13+](https://img.shields.io/badge/python-3.13%2B-345f76?style=flat-square&labelColor=263e48&logo=python&logoColor=white)
![Runtime dependencies: 0](https://img.shields.io/badge/runtime_dependencies-0-657c62?style=flat-square&labelColor=263e48)
[![License: MIT](https://img.shields.io/badge/license-MIT-657c62?style=flat-square&labelColor=263e48)](LICENSE)

[The vision](#the-vision) &nbsp; · &nbsp; [Quick start](#quick-start) &nbsp; · &nbsp; [Documentation](docs/README.md) &nbsp; · &nbsp; [Contributing](#development)

</div>

> [!WARNING]
> **Experimental.** Today Karak provides a small HTTP foundation with async endpoints. Durable jobs, database-backed queues, scheduling, and job management are planned. Karak is not ready for production use; APIs and behavior may change without notice.

## The vision

Python backend development has become fragmented. Building a production
application often means assembling an ASGI framework, server, task queue,
broker, scheduler, migration tools, observability, and deployment tooling.
Each brings its own abstractions, configuration, lifecycle, and failure modes.

Karak's thesis is that backend engineering should be coherent. An engineer
should be able to learn Python, understand backend fundamentals, and learn
Karak deeply—then apply that knowledge across the production backend.
Karak should absorb the unnecessary integration and tooling complexity.

### Learn the fundamentals. Learn Karak deeply.

Karak is built for engineers. HTTP, databases, transactions, concurrency,
reliability, and distributed systems remain essential knowledge. The goal is
to let you apply those concepts through one coherent system without needing
to become an expert in a dozen unrelated tools.

The ambition is to make **“Karak engineer”** meaningful: someone who can build
and operate serious Python backends through deep knowledge of the fundamentals
and Karak.

### One model across the production backend

Karak should progressively own more of the backend experience:

**HTTP → persistence → background work → scheduling → observability → operation**

Across that progression, the design commitment is:

- **One programming model:** familiar Python functions, types, and shared resources.
- **One configuration model:** consistent settings across application capabilities.
- **One lifecycle:** defined resource setup, execution, cleanup, and shutdown.
- **One operational model:** consistent ways to run, inspect, diagnose, and recover work.

This is the product direction. Today Karak implements an early HTTP foundation;
the integrated production experience is still to be built.

### Background work shows why this matters

An application might begin by sending an email after a request, then need work
that survives restarts, retries failures, and runs across multiple workers.
That growth often means moving from framework background tasks to Celery,
Redis or RabbitMQ, workers, and a scheduler, with a new set of concepts and
configuration to learn.

Karak should provide a path from simple background execution to durable
distributed work while preserving the developer's mental model. Durability,
retry policies, duplicate execution, and transaction boundaries must remain
explicit as requirements grow. Engineers should gain stronger capabilities
within Karak, with the reliability guarantees clearly documented at each step.

Background work is one example of the broader thesis. Persistence, migrations,
scheduling, observability, and operation should follow the same principle:
new capabilities should build on what a Karak engineer already knows.

[Explore the thesis and direction →](docs/content/design.md) &nbsp; · &nbsp; [Read the architecture proposals →](docs/design.md)

## What you can try today

Karak starts with an HTTP foundation: an ASGI application, typed routes, input
validation, and text or byte responses. The current framework has **zero runtime
dependencies** and runs on **standard Python 3.13+**.

| Write a function | Let types do the parsing | Keep the setup small |
| :--- | :--- | :--- |
| Connect an async handler to a path and HTTP methods. | Turn path and query values into Python objects, with defaults and validation. | Run with an ASGI server. No free-threaded Python build required. |

## Quick start

You will need **Python 3.13+**, **Git**, and [uv](https://docs.astral.sh/uv/).

### 1. Set up the project

Start from a repository checkout. The development environment includes Uvicorn.

```bash
git clone https://github.com/grandimam/karak.git
cd karak
uv sync
```

### 2. Write an endpoint

Create `example.py` in the repository root:

```python
from karak import Karak
from karak import Router

router = Router()


@router.get("/users/{user_id}")
async def get_user(user_id: int, active: bool = True):
    return f"User {user_id} · active={active}"


app = Karak(router=router)
```

`user_id` comes from the path. `active` comes from the query string and defaults
to `True` when omitted. Karak converts both before calling your handler.

### 3. Bring it to life

```bash
uv run uvicorn example:app --reload
```

In another terminal, make a request:

```bash
curl 'http://127.0.0.1:8000/users/42?active=true'
```

```text
User 42 · active=True
```

Try `/users/not-a-number` and Karak responds with **HTTP 422**. Your handler only
runs after its inputs pass validation.

## Types do the parsing

Use Python annotations to describe the values your endpoint accepts. Named path
parameters come from the URL path; other parameters come from the query string.
Python defaults apply when a query parameter is omitted.

Add this route above `app = Karak(router=router)` in `example.py` to
combine repeated query values with a restricted set of choices:

```python
from typing import Literal


@router.get("/products")
async def products(tag: list[str], sort: Literal["price", "newest"] = "newest"):
    return f"Tags: {', '.join(tag)} · sort={sort}"
```

```bash
curl 'http://127.0.0.1:8000/products?tag=python&tag=backend&sort=price'
```

```text
Tags: python, backend · sort=price
```

<details>
<summary><strong>Explore the supported parameter types</strong></summary>

<br>

| Type | Example input | Handler receives |
| --- | --- | --- |
| `str` | `name=karak` | A string |
| `int` | `page=2` | An integer |
| `float` | `ratio=0.5` | A float |
| `bool` | `active=true` | A boolean; also accepts `1/0`, `yes/no`, and `on/off` |
| `UUID` | `id=12345678-1234-5678-1234-567812345678` | A UUID object |
| `date` | `day=2026-09-25` | An ISO date |
| `datetime` | `at=2026-09-25T12:30:00Z` | An ISO datetime |
| `Decimal` | `amount=19.99` | An exact decimal value |
| `Enum` | `status=shipped` | A matching enum member |
| `Literal["price", "newest"]` | `sort=price` | An allowed value |
| `list[int]` | `id=1&id=2` | `[1, 2]` — query parameters only |

Missing required parameters and invalid values produce **HTTP 422** responses.
Repeated query keys are accepted for lists and rejected for scalar parameters.
Unsupported annotations are rejected when the application is constructed.

</details>

[Read the parameter guide →](docs/content/parameters.md)

## Choose the response

Return a string or bytes directly, or use `Response` to set a status code. Add
this route before constructing the application:

```python
from karak import Response


@router.post("/greetings")
async def create_greeting(name: str):
    return Response(status_code=201, content=f"Hello, {name}")
```

```bash
curl -i -X POST 'http://127.0.0.1:8000/greetings?name=Karak'
```

This returns **HTTP 201** with the body `Hello, Karak`. Use `router.get` for
GET endpoints and `router.post` for POST endpoints. JSON responses are planned.

[Read the response guide →](docs/content/responses.md)

## Organize endpoints with routers

Declare each endpoint's full path with `@router.get(path)` or
`@router.post(path)`, then pass the router to `Karak(router=router)`.
The application builds and validates its routes during construction.
Give each module its own router and combine them with `router.include(child)`.

[See the routing guide →](docs/content/routing.md)

## Read request context

Use the same `ResourceContext[T]` convention in handlers and resource factories.
`ResourceContext[Request]` provides the current request without a factory:

```python
from karak import Request
from karak import ResourceContext


@router.get("/preferences")
async def preferences(context: ResourceContext[Request]):
    return context.value.cookies.get("theme", "light")
```

Register this endpoint before constructing the application. Request headers,
cookies, body bytes, and isolated state live on `context.value`. Registered
application services are available through `ResourceContext[ServiceType]`.

[Follow the complete request guide →](docs/content/request-context.md)

New to backend development? Follow the [curriculum](docs/content/curriculum.md):
Hello World → endpoints → requests → validation → responses → context → modules
→ resources → lifecycle → testing. The [first-week schedule](docs/content/first-week.md)
groups the lessons into seven practical sessions.

## Where we are

For reproducible local HTTP comparisons with FastAPI, see
[benchmarks](docs/content/benchmarks.md) and the [benchmark runner](benchmarks/README.md).

The HTTP foundation is available for experimentation. The broader system is
planned. Each capability should extend the same programming, configuration,
lifecycle, and operational models.

| Area | Today | Direction |
| :--- | :--- | :--- |
| **HTTP** | ASGI, composed routers, typed inputs, request and resource contexts, headers, cookies, text and bytes | JSON, generated API documentation |
| **Application lifecycle** | Typed resource dependencies, automatic setup and cleanup, optional `lifespan=` hook | Graceful shutdown coordination |
| **Persistence** | Planned | Database resources, explicit transactions, and migrations within the application model |
| **Background work** | Planned | A path from simple execution to durable distributed jobs, retries, and failure recovery |
| **Recurring work** | Planned | Scheduling with defined behavior for missed and overlapping runs |
| **Observability** | Planned | Connected request and job context, logs, metrics, and health information |
| **Operation** | Planned | Consistent configuration, process management, deployment, inspection, and recovery |
| **Webhooks and workflows** | Later | Reliable delivery and multistep work built on durable jobs |
| **Execution** | Async route handlers | Synchronous Python and free-threaded execution |

## Find your next step

| If you want to… | Start here |
| :--- | :--- |
| Learn the framework | [Documentation](docs/README.md) |
| Add endpoints and accept input | [Routing](docs/content/routing.md) · [Parameters](docs/content/parameters.md) |
| Share services and manage their dependencies | [Application resources](docs/content/resources.md) |
| Understand the current implementation | [ASGI guide](docs/asgi.md) · [Request handling](docs/server.md) |
| Measure a local application | [Load testing](docs/load-testing.md) |
| Work on the documentation site | [Website development](docs/website.md) |
| Report a bug or propose a workflow | [Issue tracker](https://github.com/grandimam/karak/issues) |

## Development

From your repository checkout, install dependencies and run the test suite:

```bash
uv sync
uv run python -m unittest discover -s tests
```

Contributions are welcome: try the examples, report a reproducible bug, improve
a guide, or share a workflow you would like Karak to support. For substantial
changes, start with an [issue](https://github.com/grandimam/karak/issues) so we can
discuss the direction together.

<details>
<summary><strong>A look around the repository</strong></summary>

<br>

```text
src/karak/
├── __init__.py             # Public exports
├── application.py         # Karak and ASGI lifecycle
├── request.py             # Request wrapper
├── response.py            # Response serialization
├── routing/
│   ├── __init__.py
│   ├── routes.py          # Route definitions and dispatch
│   ├── router.py          # Route selection
│   └── matching.py        # Path patterns and match results
├── parameters/
│   ├── __init__.py
│   ├── inspection.py      # Handler signatures and parameter validation
│   └── conversion.py      # Supported type converters
├── middleware/
│   ├── __init__.py
│   └── exceptions.py      # Request error handling
├── exceptions.py          # Framework exception types
├── types.py               # ASGI type aliases
└── py.typed
tests/                     # ASGI routing and validation tests
docs/                      # Guides, design proposals, and documentation site
```

</details>

## License

Open source under the [MIT License](LICENSE).
