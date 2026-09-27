---
title: Quickstart
description: Install Karak, create an endpoint, and see your first response in a browser.
---

<header class="docs-opening">
  <div class="opening-copy">
    <h1 id="start-with-a-little-python">Start with a little Python.</h1>
    <p class="lead">Create an endpoint and see it respond in your browser.</p>
    <p class="page-status">Experimental · Python 3.13+</p>
  </div>
  <img class="opening-sphere" src="assets/share-card-sphere.png" width="1734" height="907" alt="" fetchpriority="high">
</header>

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


app = Karak(routes=[router])
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
For the bigger picture—APIs, jobs, workers, and operating them together—read
[our vision](design.md).

[Define routes →](routing.md){: .next-link }
