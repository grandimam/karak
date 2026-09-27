<div align="center">

<img src="docs/content/assets/share-card-sphere.png" alt="A layered paper sphere in soft sage, blue, and cream" width="460">

# Karak

**Your Python application. Less infrastructure.**

Building a Python application runtime for APIs, durable jobs, and schedules.<br>
One application. Fewer services to operate.

![Status: Experimental](https://img.shields.io/badge/status-experimental-bb9363?style=flat-square&labelColor=263e48)
![Python: 3.13+](https://img.shields.io/badge/python-3.13%2B-345f76?style=flat-square&labelColor=263e48&logo=python&logoColor=white)
![Runtime dependencies: 0](https://img.shields.io/badge/runtime_dependencies-0-657c62?style=flat-square&labelColor=263e48)
[![License: MIT](https://img.shields.io/badge/license-MIT-657c62?style=flat-square&labelColor=263e48)](LICENSE)

[The vision](#the-vision) &nbsp; · &nbsp; [Quick start](#quick-start) &nbsp; · &nbsp; [Documentation](docs/README.md) &nbsp; · &nbsp; [Contributing](#development)

</div>

> [!WARNING]
> **Experimental.** Today Karak provides a small HTTP foundation with async endpoints. Durable jobs, database-backed queues, scheduling, and job management are planned. Karak is not ready for production use; APIs and behavior may change without notice.

## The vision

A Python application grows beyond its first endpoint. It sends email, generates
reports, delivers webhooks, and runs work every night. Supporting that work can
mean adding a task queue, a message broker, a scheduler, a job dashboard, and
the configuration that connects them.

Karak aims to bring **APIs, durable background jobs, and scheduled work** into
one application, with shared configuration, resources, and visibility. The goal
is to let you remove the extra services you would otherwise assemble to run
that work reliably.

**The deployment target: your application and its database.** We plan to store
jobs, schedules, and execution history in the application's existing database,
with PostgreSQL as the initial target. API and worker processes should be able
to run together on one machine or scale independently from the same codebase.

### What we aim to replace

These are planned replacement targets; they are not available in Karak today.

| What you could remove | What Karak aims to provide |
| :--- | :--- |
| **Celery, RQ, or a separate task library** | Durable jobs, retries, timeouts, concurrency controls, and recovery after worker crashes |
| **Redis or RabbitMQ used only for jobs** | A queue backed by your existing database, without a dedicated message broker |
| **Celery Beat and application cron scripts** | Delayed and recurring jobs, with policies for missed and overlapping runs |
| **A separate job result backend** | Persistent job status, progress, results, and failure history |
| **Flower or a custom job dashboard** | Built-in job inspection, manual retries, queue controls, and worker health |
| **Custom webhook and workflow glue** | Reliable webhook delivery and multistep work with persisted progress |

The first focus is reliable jobs, scheduling, and the tools to operate them.
Webhook delivery and workflows would build on that foundation. Removing a
dedicated broker depends on what else your application uses it for; database
storage, backups, hosting, and worker compute remain part of operating the app.

### One application, from request to completion

Imagine a customer requesting a report. Your API saves the request and queues
the work in the same database transaction. A worker generates the report,
recovers after an interruption, and delivers a completion webhook. You can
inspect failures, retry work, and schedule the same report for next Monday.

That is the experience we are building toward: one application definition,
shared services, and a clear view of the work from request to completion.

[Explore the vision →](docs/content/design.md) &nbsp; · &nbsp; [Read the architecture proposals →](docs/design.md)

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


app = Karak(routes=router.routes)
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

Add this route above `app = Karak(routes=router.routes)` in `example.py` to
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
Unsupported annotations are rejected when the route is registered.

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

## Where we are

The HTTP foundation is available for experimentation. The rest of the runtime
is planned, with reliable jobs and scheduling as the first infrastructure
replacement goals.

| Area | Today | Direction |
| :--- | :--- | :--- |
| **HTTP** | ASGI, router decorators, typed inputs, validation, text and bytes | Mount routing, JSON, shared dependencies, generated API documentation |
| **Application lifecycle** | Startup and shutdown acknowledgements | Resource setup, cleanup, and graceful shutdown |
| **Background work** | Planned | Database-backed jobs, workers, retries, and failure recovery |
| **Recurring work** | Planned | Scheduling with defined behavior for missed and overlapping runs |
| **Operations** | Planned | Job inspection and retries, shared configuration, logs, metrics, and health information |
| **Webhooks and workflows** | Later | Reliable delivery and multistep work built on durable jobs |
| **Execution** | Async route handlers | Synchronous Python and free-threaded execution |

## Find your next step

| If you want to… | Start here |
| :--- | :--- |
| Learn the framework | [Documentation](docs/README.md) |
| Add endpoints and accept input | [Routing](docs/content/routing.md) · [Parameters](docs/content/parameters.md) |
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
│   ├── mount.py           # Router mount declarations
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
