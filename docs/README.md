# Karak documentation

Build an HTTP application with async routes, typed inputs, responses, and shared
application resources. Start with a working example, then add the capabilities
your application needs. Karak is experimental and requires Python 3.13+.

## Get started

| I want to… | Read |
| --- | --- |
| Follow a week of beginner exercises | [Your first week](content/first-week.md) |
| Understand routers, handlers, and resources | [How Karak works](content/introduction.md) |
| See my first endpoint respond | [Quickstart](content/index.md) |
| Set up my environment | [Installation](content/installation.md) |
| Start, edit, and stop my app | [Run an application](content/application.md) |
| Add an endpoint | [Define routes](content/routing.md) |
| Accept filters, page numbers, and other input | [Read request values](content/parameters.md) |
| Read headers, cookies, bodies, and request state | [Request context](content/request-context.md) |
| Return a message or a status code | [Send responses](content/responses.md) |
| Share a service or client across requests | [Application resources](content/resources.md) |
| Compare measured HTTP performance | [Benchmarks](content/benchmarks.md) |

## Mission

[Mission](content/design.md) is the site's one page about Karak's goals and
future direction. All other website pages explain how to build with the
features available today.

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
