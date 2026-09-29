---
title: Endpoints and HTTP methods
lesson: 2
description: Add a second endpoint, distinguish a URL from a handler, and try GET and POST requests.
---

# Give your backend another endpoint.

<p class="lead">An endpoint connects an HTTP method and a path to a Python function.</p>

In [Hello World](index.md), visiting `/` returned a greeting. Now make the same
application answer more than one kind of request. Keep everything in `main.py`
for this lesson; splitting files comes later.

## Name the pieces

In `http://127.0.0.1:8000/health`, `127.0.0.1:8000` identifies your local server
and `/health` is the path. A request also has a method: GET asks to read a
representation; POST submits work or data for the server to process.

An **endpoint** is the method and path your application exposes. A **handler**
is the Python function that answers it. A **route** records how to connect the
two. Naming a function `health` does not create `/health`; the decorator does.

## Add a health endpoint

Replace `main.py` with this complete version:

```python
from karak import Karak
from karak import Router

router = Router()


@router.get("/")
async def index():
    return "Hello from Karak"


@router.get("/health")
async def health():
    return "ok"


@router.post("/greetings")
async def create_greeting():
    return "Greeting received"


app = Karak(router=router)
```

The line `@router.get("/health")` registers the function below it. This syntax is
called a **decorator**. Here it records the handler; it does not call the handler
while the module is imported.

All route declarations come before `Karak(router=router)`. Karak captures the
registered routes when constructing the application. A route added afterward
will not appear in that application.

## Make each request

Run `uv run uvicorn main:app --reload`. In another terminal:

```sh
curl -i http://127.0.0.1:8000/health
curl -i -X POST http://127.0.0.1:8000/greetings
```

`curl` is a command-line HTTP client. `-i` includes response headers and status;
`-X POST` selects the method. The first command returns HTTP 200 with `ok`.
The second returns HTTP 200 with `Greeting received`.

This POST endpoint only acknowledges the request. It does not store anything,
read a body, or automatically choose a creation status. Later lessons add
inputs and explicit response status codes.

## Predict a method mismatch

Opening a URL in a browser's address bar normally makes a GET request. Try:

```sh
curl -i http://127.0.0.1:8000/greetings
```

The path exists, but the registered method is POST. Karak returns HTTP 405,
`Method Not Allowed`. GET and POST may share a path if you register a separate
handler for each method. Registering the same method and path twice is an error.

Karak currently provides GET and POST decorators. Unknown paths currently
return HTTP 500 with `Route Not Found`; this is a framework limitation, not the
HTTP status an application should normally use for a missing resource.

## Add one endpoint yourself

Before `app = Karak(...)`, add GET `/version` and return `"0.1.0"`. Call it with
curl, then try POST on the same path. Predict both responses before running the
commands. Rename the handler without changing its decorator and check that the
URL still works.

You now have multiple endpoints. Next, trace how a request reaches one of them.
