---
title: Run an application
description: Start your Karak application, edit it locally, and understand the current deployment limits.
---

# Run your application.

<p class="lead">Start a server, make changes, and try your endpoints.</p>

A Karak application collects the endpoints you want to make available. Create
one in `main.py` and add your first endpoint:

```python
from karak import Karak
from karak import Router

router = Router()


@router.get("/")
async def index():
    return "Hello from Karak"


app = Karak(router=router)
```

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

The intended [operational model](design.md) spans HTTP, persistence, background
work, and schedules with consistent configuration, resource ownership,
inspection, and shutdown. Today's explicit Uvicorn command is how you run the
HTTP foundation while that integrated experience is being built. There is no
Karak deployment command or managed background-job system to use yet.
