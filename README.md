<div align="center">

# Karak

**A simpler path from Python to production.**

Karak aims to make APIs, background jobs, workers, and scheduled tasks easier to build, run, and operate together in Python.

![Status: Experimental](https://img.shields.io/badge/status-experimental-orange)
![Python: 3.13+](https://img.shields.io/badge/python-3.13%2B-3776AB?logo=python&logoColor=white)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

[Quick start](#quick-start) · [Documentation](docs/README.md) · [Development](#development)

</div>

> [!WARNING]
> **Experimental — under active development.**
> Karak is an early prototype. APIs and behavior can change without notice, and it is not ready for production use. The synchronous execution model is a design goal; the current implementation uses async route handlers.

## The idea

A Python application needs more than request handlers. It needs to run work in
the background, manage resources, recover from failures, shut down cleanly, and
make its behavior visible in production.

Karak’s goal is to let you build an API, hand longer work to a worker, schedule
recurring jobs, and operate them together. You should be able to see what is
running, understand failures, retry work, and deploy changes with predictable
behavior—all within one Python application model.

For example, a report request should be able to become a background job, retry
after a temporary failure, and run on a weekly schedule using the same
application services. We want the configuration, resource management, and
visibility into that work to feel consistent from start to finish.

The current implementation starts with the HTTP foundation: an ASGI application,
typed routing, validation, and error handling. Durable jobs, scheduling, worker
management, and production tooling are goals for future development.

Read [our vision and plans](docs/content/design.md) for the experience we want
to build and the current status of each area.

## Quick start

Requires **Python 3.13+** and [uv](https://docs.astral.sh/uv/). The main ASGI implementation runs on standard Python; a free-threaded build is not required. The framework itself has no runtime dependencies; the development setup includes Uvicorn.

```bash
git clone https://github.com/grandimam/karak.git
cd karak
uv sync
```

Create `example.py` in the repository root:

```python
from karak import Karak

app = Karak()


@app.get(path="/users/{user_id}", methods=["GET"])
async def get_user(user_id: int, active: bool = True):
    return f"User {user_id} · active={active}"
```

Start the server:

```bash
uv run uvicorn example:app --reload
```

Try your route:

```bash
curl 'http://127.0.0.1:8000/users/42?active=true'
```

```text
User 42 · active=True
```

## Parameter types

Handler annotations drive path and query conversion. Parameters named in the route come from the path; other parameters come from the query string. Python defaults apply when a query parameter is omitted.

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

For example, combine restricted choices with repeated query parameters:

```python
from typing import Literal


@app.get(path="/products", methods=["GET"])
async def products(tag: list[str], sort: Literal["price", "newest"] = "newest"):
    return f"Tags: {', '.join(tag)} · sort={sort}"
```

```bash
curl 'http://127.0.0.1:8000/products?tag=python&tag=backend&sort=price'
```

Missing required parameters and invalid values produce **HTTP 422** responses. Repeated query keys are accepted for lists and rejected for scalar parameters. Unsupported annotations are rejected when the route is registered.

## Built so far

- **ASGI application** with HTTP handling and startup/shutdown acknowledgements.
- **Routing** with method matching and named path parameters.
- **Typed parameters** with conversion, defaults, and validation.
- **Responses** for text and bytes, with custom status codes through `Response`.
- **Error handling** for validation failures and unexpected handler exceptions.

The [design document](docs/design.md) describes planned work, including synchronous execution, dependency injection, JSON responses, and a thread-based executor.

## Development

Install dependencies and run the test suite:

```bash
uv sync
uv run python -m unittest discover -s tests
```

| Resource | What you'll find |
| --- | --- |
| [Documentation](docs/README.md) | Current guides and design proposals |
| [Documentation website](docs/website.md) | Local preview, editing, and GitHub Pages deployment |
| [ASGI guide](docs/asgi.md) | Routes, parameters, responses, and current limitations |
| [Request handling](docs/server.md) | How the ASGI implementation handles requests |
| [Design](docs/design.md) | Goals, execution model, and planned architecture |
| [Routing notes](notes/route.md) | Handler inspection and parameter validation |
| [Load testing](docs/load-testing.md) | Uvicorn + hey setup and measurement guidance |
| [Issues](https://github.com/grandimam/karak/issues) | Bug reports and discussions |

## Repository layout

```text
src/karak/                  # Main ASGI implementation
examples/basic.py           # Runnable ASGI demo
examples/exploration.py     # Exploratory demo and development notes
tests/                     # ASGI routing and validation tests
docs/                      # Design proposals and load-testing guide
notes/                     # Development notes
```

Run the included demo with `uv run uvicorn examples.basic:app --reload`.

## License

[MIT](LICENSE).
