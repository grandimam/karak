---
title: Installation
guide: true
description: Set up Python and Karak, verify your environment, and resolve common setup problems before Hello World.
---

# Get ready to try Karak.

<p class="lead">A local Python environment and a small application to start with.</p>

## What you need

Use Python 3.13 or newer and
[install uv](https://docs.astral.sh/uv/getting-started/installation/) to manage the
project environment. You will also need Git to download the repository.

You can use standard Python.

## Set up the project

```sh
git clone https://github.com/grandimam/karak.git
cd karak
uv sync
```

For now, these guides use a checkout of the repository. `uv sync` prepares its
Python environment and installs Karak and the tools needed to run the examples.
Use `uv run` for subsequent commands so they use that environment.

## Check that Python can import Karak

Run this from the repository root:

```sh
uv run python -c "from karak import Karak; print('Karak is ready')"
```

You should see `Karak is ready`. This checks the environment without requiring
an example file. Continue to [Hello World](index.md) to create your
own `main.py` and start a server.

## If setup gets stuck

| What you see | What to check |
| --- | --- |
| `uv` is not found | Install uv and reopen your terminal if it was just installed. |
| The project or configuration cannot be found | Run the commands from the cloned `karak` directory. |
| `No module named karak` | Run `uv sync`, then start the server with `uv run`. |
| The server cannot import `main` | Save `main.py` in the project root, and name the application `app`. |
| Port 8000 is already in use | Stop the other server, or add `--port 8001` and open port 8001 in the browser. |

Start with [Hello World](index.md). The
[application lifecycle guide](application.md) covers startup, shutdown, and server settings.
