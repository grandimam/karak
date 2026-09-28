---
title: Quickstart
description: Start learning Karak with its HTTP foundation—the first step toward one integrated Python backend system.
---

<header class="docs-opening">
  <div class="opening-copy">
    <h1 id="start-with-a-little-python">Python backends.<br>One coherent system.</h1>
    <p class="lead">Integrated, not assembled. Learn the fundamentals. Learn Karak deeply. Build and operate serious Python backends.</p>
    <p class="page-status">Experimental · Python 3.13+</p>
  </div>
  <img class="opening-sphere" src="assets/share-card-sphere.png" width="1734" height="907" alt="" fetchpriority="high">
</header>

Karak's thesis is that [Python backend development should be integrated, not
assembled](introduction.md). The goal is one system to learn deeply across
HTTP, persistence, background work, scheduling, observability, and operation.
This guide starts with the HTTP foundation available today. Karak is
experimental; the broader production system is planned.

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
For the shared programming, configuration, lifecycle, and operational models
we are building toward, read [the thesis and direction](design.md).

[Define routes →](routing.md){: .next-link }
