# Karak documentation

Karak aims to make Python applications easier to take to production, bringing
APIs, background jobs, workers, and scheduled tasks into one application model.

The current implementation is the ASGI framework in `src/karak/`. A separate
free-threaded HTTP experiment lives in `experiments/free_threaded/`. Background
job processing, scheduling, and broader production tooling remain design goals.

## Using Karak

| Guide | Contents |
| --- | --- |
| [Quick start](../README.md#quick-start) | Install and run the main ASGI framework |
| [ASGI guide](asgi.md) | Register routes, bind parameters, and return responses |
| [Request handling](server.md) | Application, router, request, and response internals |
| [Load testing](load-testing.md) | Measure the current ASGI demo |
| [Free-threaded experiment](../experiments/free_threaded/README.md) | Run the synchronous server and its benchmarks |

## Design proposals and working notes

These documents record proposed capabilities and development ideas. Their
example APIs may not exist in the current implementation.

| Document | Focus |
| --- | --- |
| [Design and execution model](design.md) | Long-term goals, synchronous application code, and parallel execution |
| [Framework design](framework.md) | Python package structure, resource routing, and dependency lifetimes |
| [Routing notes](../notes/route.md) | Early reasoning about route registration and validation |
| [Server notes](../notes/server.md) | Original exploration of the server and router abstractions |
| [Worker notes](../notes/workers.md) | Background-task ideas |

The ASGI framework currently uses async handlers. The free-threaded experiment
uses synchronous handlers and its own socket server. A unified synchronous ASGI
execution model remains a design goal.

## Documentation website

The [website source](content/index.md), theme, and build configuration live in
this directory. See [website development and GitHub Pages setup](website.md)
for preview commands, editing instructions, and deployment configuration.
