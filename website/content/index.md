---
title: Quickstart
description: Create and run your first Karak ASGI application.
summary: Create and run your first Karak application.
---

# Start with a little Python.

<p class="lead">Create and run your first Karak application.</p>

<p class="page-status">Experimental · Python 3.13+</p>

## Install

Clone the repository and install the development dependencies.

```sh
git clone https://github.com/grandimam/karak.git
cd karak
uv sync
```

## Create an application

Save the following as `main.py` in the project root.

```python
from karak import Karak

app = Karak()


@app.get(path="/", methods=["GET"])
async def index():
    return "Hello from Karak"
```

## Run it

```sh
uv run uvicorn main:app --reload
```

Open [localhost:8000](http://127.0.0.1:8000) in your browser.

[Routing →](routing.md){: .next-link }
