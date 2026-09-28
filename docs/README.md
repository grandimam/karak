# Karak documentation

**Python backend development should be integrated, not assembled.** Karak is
being built as one coherent system for engineers who know Python and backend
fundamentals and want to learn one system deeply.

The direction spans HTTP, persistence, background work, scheduling,
observability, and operation, with one programming model, one configuration
model, one lifecycle, and one operational model. Today Karak is experimental
and provides the HTTP foundation. The practical guides describe that working
foundation; the broader production experience is planned.

## Get started

| I want to… | Read |
| --- | --- |
| Understand what Karak is for | [Introduction](content/introduction.md) |
| See my first endpoint respond | [Quickstart](content/index.md) |
| Set up my environment | [Installation](content/installation.md) |
| Start, edit, and stop my app | [Run an application](content/application.md) |
| Add an endpoint | [Define routes](content/routing.md) |
| Accept filters, page numbers, and other input | [Read request values](content/parameters.md) |
| Return a message or a status code | [Send responses](content/responses.md) |

## Look ahead

[Thesis and direction](content/design.md) explains the integrated backend
experience and the path from simple background execution to durable distributed
work within one mental model. It distinguishes current capabilities from plans.

## Work on Karak

The following documents are for contributors investigating the framework.
Design proposals may contain APIs that do not exist yet.

| Document | Focus |
| --- | --- |
| [ASGI implementation guide](asgi.md) | Current API details and boundaries |
| [Request handling](server.md) | How the implementation handles requests |
| [Load testing](load-testing.md) | Measuring the ASGI demo |
| [Architecture and design principles](design.md) | Shared models, capability boundaries, and criteria for the integrated backend |
| [Routing notes](../notes/route.md) | Early route and validation ideas |
| [Server notes](../notes/server.md) | Server and router exploration |
| [Worker notes](../notes/workers.md) | Background-task ideas |

## Maintain the website

The published guides live in `content/`. See [website development and GitHub
Pages setup](website.md) for local preview, editing, and deployment instructions.
