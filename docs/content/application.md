---
title: Application lifecycle
guide: true
description: Start your Karak application, edit it locally, and understand the current deployment limits.
---

# Own startup and shutdown.

<p class="lead">Know when shared objects are created, used, and released.</p>

[Shared resources](resources.md) live across requests. The application
lifecycle determines when they are created and released. Use a lifespan hook
for additional startup and shutdown work, and the server settings below when
editing or changing ports.

To try a lifespan hook, start by replacing `main.py` with a small application so startup and
shutdown messages are easy to observe:

```python
from karak import Karak
from karak import Router

router = Router()


@router.get("/")
async def index():
    return "Hello from Karak"


app = Karak(router=router)
```

## Share services and clients

Use `@resource` factories for objects shared across requests. The decorator
registers each factory globally; define or import them before constructing `Karak`. Karak initializes their dependencies before serving requests and runs
generator cleanup at shutdown. Start with the complete example in
[share application resources](resources.md).

## Add startup and shutdown work

Pass an async context manager as `lifespan=` when you need application-specific
setup or cleanup beyond registered resource factories:

```python
from contextlib import asynccontextmanager

from karak import Karak
from karak import Router

router = Router()


@asynccontextmanager
async def lifespan():
    print("Application starting")
    try:
        yield
    finally:
        print("Application stopping")


@router.get("/")
async def index():
    return "Hello from Karak"


app = Karak(router=router, lifespan=lifespan)
```

Karak enters this context manager before acknowledging startup and exits it
before acknowledging shutdown. If you also register resources, they initialize
before the hook enters and remain available until after it exits. The hook can
access their handles through `.get()`; Karak does not use its yielded value.

Keep ASGI lifespan enabled when running hooks or resources. Startup errors stop
initialization and release resources already acquired. Cleanup errors are
reported to the server. The server is responsible for finishing active requests
before sending shutdown. Without resources or a hook, Karak simply acknowledges
the server's startup and shutdown events.

## Start the development server

From the directory containing `main.py`, run:

```sh
uv run uvicorn main:app --reload
```

Uvicorn is the server that listens for web requests and runs your application.
`main:app` means “use the object named `app` in `main.py`.” If you rename the
file to `example.py`, use `example:app` instead.

Open [localhost:8000](http://127.0.0.1:8000) to try the endpoint. Keep the terminal
open while you use it; **Ctrl+C** stops the server.

## Edit and try again

With `--reload`, the server restarts when you save changes. Edit the text
returned by `index()`, save, and refresh your browser.

You can add more endpoints to the same `router` before constructing the app. Each endpoint currently needs an
`async def` function. See [define routes](routing.md) for an example you can add
to this file.

## Use a different port

If another application already uses port 8000:

```sh
uv run uvicorn main:app --reload --port 8001
```

Open [localhost:8001](http://127.0.0.1:8001) for this server.

## Understand a failed request

An HTTP 422 response means a supplied value is missing or invalid. Check the
response message and the endpoint’s [expected inputs](parameters.md).

An `Internal Server Error` response means the endpoint encountered an
unexpected error. Look at the traceback in the server terminal to find the
cause. See [send responses](responses.md#understand-error-responses) for more.

## Can I deploy it to production?

Karak is currently for local experimentation and development. The framework
is not production-ready, and `--reload` is a development convenience.

For local development, run the Uvicorn command above. Do not use `--reload`
when evaluating behavior across a long-running process: each reload creates a
new application lifespan and new resource instances. Configure and manage the
ASGI server yourself; Karak does not include a deployment command.

## Recognize startup and shutdown in the terminal

With the `lifespan` example, `Application starting` appears before requests are
served and `Application stopping` appears during shutdown. These messages occur
per application lifetime. Making another request does not repeat startup;
editing a file with `--reload` starts a new lifetime.

The [testing guide](testing.md) shows how to exercise this lifecycle and make
requests without starting a network server.
