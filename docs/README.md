# Karak documentation

Start with a small application, then learn to accept requests and send useful
responses. These guides describe what you can try today. Karak is experimental;
background jobs, scheduling, and production operations are still planned.

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

[Our vision](content/design.md) describes the application experience we want to
build: APIs, durable background jobs, workers, recurring work, and the tools to
operate them together. It distinguishes current capabilities from future plans.

## Work on Karak

The following documents are for contributors investigating the framework.
Design proposals may contain APIs that do not exist yet.

| Document | Focus |
| --- | --- |
| [ASGI implementation guide](asgi.md) | Current API details and boundaries |
| [Request handling](server.md) | How the implementation handles requests |
| [Load testing](load-testing.md) | Measuring the ASGI demo |
| [Production goals and execution design](design.md) | Architecture proposals behind the product direction |
| [Framework design](framework.md) | Resource routing and dependency proposals |
| [Routing notes](../notes/route.md) | Early route and validation ideas |
| [Server notes](../notes/server.md) | Server and router exploration |
| [Worker notes](../notes/workers.md) | Background-task ideas |

## Maintain the website

The published guides live in `content/`. See [website development and GitHub
Pages setup](website.md) for local preview, editing, and deployment instructions.
