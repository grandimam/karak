# Karak documentation

Learn Karak by building a small application and adding the capabilities you need.
The guides introduce concepts in a useful order and remain readable individually.
Karak is experimental and requires Python 3.13+.

## Get started

Start with [Hello World](content/index.md), then add
[endpoints](content/endpoints.md) and see [how requests work](content/introduction.md).
Use [installation](content/installation.md) for environment setup.

## Explore the capabilities

| What you need | Guide |
| --- | --- |
| Choose a layout that can grow | [Project layout](content/project-layout.md) |
| Accept and validate caller input | [Path and query parameters](content/parameters.md) |
| Choose status codes, headers, and cookies | [Responses and errors](content/responses.md) |
| Read headers, cookies, body bytes, and request state | [Request context](content/request-context.md) |
| Split endpoints across files | [Routers and modules](content/routing.md) |
| Share a service or client across handlers | [Shared resources](content/resources.md) |
| Run setup and cleanup | [Application lifecycle](content/application.md) |
| Verify application behavior | [Testing](content/testing.md) |

Each guide explains the feature, shows working code and expected results, and
links to related capabilities. Complete examples state when to replace a file;
smaller snippets explain where they fit.

## Reference and direction

[Benchmarks](content/benchmarks.md) explains the local FastAPI comparison.
[Mission](content/design.md) describes Karak's broader production-backend goals.

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
