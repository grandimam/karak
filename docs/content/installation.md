---
title: Installation
description: Set up Python and Karak, run the included example, and resolve common setup problems.
---

# Get ready to try Karak.

<p class="lead">A local Python environment and a small application to start with.</p>

## What you need

Use Python 3.13 or newer and
[install uv](https://docs.astral.sh/uv/getting-started/installation/) to manage the
project environment. You will also need Git to download the repository.

You can use standard Python. The free-threaded build is only needed when
exploring parallel execution in the [separate experiment](free-threaded.md).

## Set up the project

```sh
git clone https://github.com/grandimam/karak.git
cd karak
uv sync
```

For now, these guides use a checkout of the repository. `uv sync` prepares its
Python environment and installs Karak and the tools needed to run the examples.
Use `uv run` for subsequent commands so they use that environment.

## Check that it works

You can run an included example before writing any code:

```sh
uv run uvicorn examples.basic:app --reload
```

Visit [localhost:8000/users/42?active=true](http://127.0.0.1:8000/users/42?active=true).
You should see:

```text
User 42 · active=True
```

Stop the server with **Ctrl+C**, then follow the [quickstart](index.md) to create
your own `main.py`.

## If setup gets stuck

| What you see | What to check |
| --- | --- |
| `uv` is not found | Install uv and reopen your terminal if it was just installed. |
| The project or configuration cannot be found | Run the commands from the cloned `karak` directory. |
| `No module named karak` | Run `uv sync`, then start the server with `uv run`. |
| The server cannot import `main` | Save `main.py` in the project root, and name the application `app`. |
| Port 8000 is already in use | Stop the other server, or add `--port 8001` and open port 8001 in the browser. |

For everyday editing and running, continue to [run an application](application.md).
