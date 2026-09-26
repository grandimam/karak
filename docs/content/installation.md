---
title: Installation
description: Set up Karak from source with Python and uv.
---

# Make yourself at home.

<p class="lead">Set up Karak from the repository.</p>

## Requirements

Use Python 3.13+ and [uv](https://docs.astral.sh/uv/getting-started/installation/).
Standard Python is enough for the main ASGI framework. A free-threaded build is
only needed when exploring parallel execution in the experiment.

## Install from source

```sh
git clone https://github.com/grandimam/karak.git
cd karak
uv sync
```

This installs Karak in the project environment along with development tools,
including Uvicorn. Karak itself has no runtime dependencies.

## Run the included example

```sh
uv run uvicorn examples.basic:app --reload
```

In another terminal:

```sh
curl 'http://127.0.0.1:8000/users/42?active=true'
```

The response is `User 42 · active=True`.

## Run the tests

```sh
uv run python -m unittest discover -s tests
```

For the other implementation, follow the [free-threaded setup](free-threaded.md).
