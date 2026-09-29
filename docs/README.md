# Karak documentation

A curriculum for learning modern Python backend development through Karak.
Start with a working endpoint, then build toward a modular, tested application.
Karak is experimental and requires Python 3.13+.

## Learn in order

Start with the [curriculum map](content/curriculum.md), use
[installation](content/installation.md) for setup, and optionally follow the
[first-week schedule](content/first-week.md).

| Part | Chapters |
| --- | --- |
| Your first HTTP app | [1. Hello World](content/index.md) · [2. Endpoints and methods](content/endpoints.md) · [3. Follow a request](content/introduction.md) |
| Requests and responses | [4. Parameters](content/parameters.md) · [5. Responses and errors](content/responses.md) · [6. Request context](content/request-context.md) |
| Structure and reliability | [7. Routers and modules](content/routing.md) · [8. Shared resources](content/resources.md) · [9. Lifecycle](content/application.md) · [10. Testing](content/testing.md) |

Each chapter has a concrete example, practice, and a next lesson. The curriculum
ends with a small catalog project that combines the concepts. Planned subjects
are identified separately so readers know what is available today.

## Reference and direction

[Benchmarks](content/benchmarks.md) explains the local FastAPI comparison.
[Mission](content/design.md) describes Karak's broader production-backend goals.
These pages are outside the numbered learning path.

## Work on Karak

The following documents are for contributors investigating the framework.
Design proposals may contain APIs that do not exist yet.

| Document | Focus |
| --- | --- |
| [ASGI implementation guide](asgi.md) | Current API details and boundaries |
| [Request handling](server.md) | How the implementation handles requests |
| [Load testing](load-testing.md) | Reproducing the local HTTP comparison |
| [Architecture and design principles](design.md) | Shared models, capability boundaries, and criteria for the integrated backend |
| [Routing notes](../notes/route.md) | Early route and validation ideas |
| [Server notes](../notes/server.md) | Server and router exploration |
| [Worker notes](../notes/workers.md) | Background-task ideas |

## Maintain the website

The published guides live in `content/`. See [website development and GitHub
Pages setup](website.md) for local preview, editing, and deployment instructions.
