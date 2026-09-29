---
title: Hello World
lesson: 1
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

This is lesson 1 of [Learn modern Python backend development](curriculum.md).
Start with a program that answers one HTTP request. You will run it, change its
response, and explain what the client sees. Later chapters add inputs, cookies,
modules, and shared services. Karak is experimental; use this course for local
learning and development.

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

## Make the greeting your own

Change the response to `"Hello from my backend"`, refresh the browser, and check
that it changed. Stop the server and start it again without referring to the
commands above. You should be able to identify the file, application object,
and address you are opening.

Next, add a second endpoint and make a POST request. Follow the lesson links
below to continue in order, or return to the [curriculum map](curriculum.md).
