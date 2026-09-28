---
title: Quickstart
description: Install Karak, write an async endpoint, and run your first Python HTTP application.
---

<header class="docs-opening">
  <div class="opening-copy">
    <h1 id="start-with-a-little-python">Build your first<br>Karak application.</h1>
    <p class="lead">Learn to build Python backends, starting with one working endpoint.</p>
    <p class="page-status">Experimental · Python 3.13+</p>
  </div>
  <img class="opening-sphere" src="assets/share-card-sphere.png" width="1734" height="907" alt="" fetchpriority="high">
</header>

Karak's goal is to help you build production backend applications with one
coherent Python programming model. Start here with a running HTTP endpoint,
then follow [your first week](first-week.md) to learn routing, validation,
request context, resources, and testing through practical exercises.
Karak is experimental; today's examples are for local development and evaluation.

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

## What next?

[Add another endpoint](routing.md), then [accept values from a request](parameters.md).
Learn to [send responses](responses.md) and
[share services across requests](resources.md) as your application grows.
Use [request context](request-context.md) for headers, cookies, and body bytes.
For a guided sequence with daily checkpoints, follow [your first week](first-week.md).

[Define routes →](routing.md){: .next-link }
