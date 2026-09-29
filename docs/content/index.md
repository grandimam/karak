---
title: Hello World
guide: true
description: Install Karak, write an async endpoint, and run your first Python HTTP application.
---

<header class="docs-opening">
  <div class="opening-copy">
    <h1 id="start-with-a-little-python">Hello, world.<br>Your first backend.</h1>
    <p class="lead">Learn to build Python backends, starting with one working endpoint.</p>
    <p class="page-status">Experimental · Python 3.13+</p>
  </div>
  <img class="opening-sphere" src="assets/share-card-sphere.png" width="1734" height="907" alt="" fetchpriority="high">
</header>

Karak is a Python framework for building async HTTP applications. Define
endpoints with Python functions, validate inputs with type annotations, and
share services through typed resource contexts.

Start with a small application that returns a greeting. You can add the
capabilities your backend needs as you go. Karak is experimental and currently
suited to local development and evaluation.

## Install

You will need Python 3.13+ and [uv](https://docs.astral.sh/uv/getting-started/installation/).
Open a terminal and run:

```sh
git clone https://github.com/grandimam/karak.git
cd karak
uv sync
```

Stay in the `karak` directory for the steps below. See
[installation](installation.md) if you need more help with setup.

## Create an application

Create a file called `main.py` in that directory:

```python
from karak import Karak
from karak import Router

router = Router()


@router.get("/")
async def index():
    return "Hello from Karak"


app = Karak(router=router)
```

This tells Karak to run `index()` when someone visits `/`. The text you return
becomes the response. Use `async def` for your endpoints in the current version.

## Run it

```sh
uv run uvicorn main:app --reload
```

Open [localhost:8000](http://127.0.0.1:8000) in your browser. You should see:

```text
Hello from Karak
```

Change the returned text, save `main.py`, and refresh the browser. The
`--reload` option restarts the development server when you edit a file.
Press **Ctrl+C** in the terminal when you want to stop it.

## Add to your application

[Add another endpoint](endpoints.md) to give the application a second URL, then
[accept path and query values](parameters.md) to make its response depend on
caller input. For the request's headers, cookies, and body, use
[request context](request-context.md).

As the application grows, start with the [recommended project layout](project-layout.md),
[split routes into modules](routing.md), and
[share services](resources.md) across handlers. Each guide includes examples
you can run independently; complete `main.py` examples replace the previous
file, while smaller snippets explain where to add them.
