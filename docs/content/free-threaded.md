---
title: Free-threaded experiment
description: Explore Karak’s separate synchronous HTTP implementation on free-threaded Python.
---

# A little room to experiment.

<p class="lead">Synchronous handlers. A thread pool. Another way to run Python.</p>

The repository includes a separate free-threaded HTTP implementation in
`experiments/free_threaded/`. It explores parallel execution with a built-in
socket server. The main `karak` package remains the ASGI framework.

## Run the example

From the repository root, use a free-threaded Python build:

```sh
uv sync --group experiments --python 3.13t
uv run --group experiments --python 3.13t python -m experiments.free_threaded.examples.basic
```

The demo listens at [localhost:8000](http://127.0.0.1:8000).

## A synchronous application

```python
from experiments.free_threaded import Karak

app = Karak()


@app.get("/")
def index():
    return {"message": "Hello from Karak"}


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, workers=4)
```

This API includes dependency injection, Pydantic body models, JSON responses,
and HTTP keep-alive. Those capabilities belong to this experiment and are not
yet part of the main ASGI implementation.

## Benchmarks

```sh
uv run --group experiments --python 3.13t python -m experiments.free_threaded.benchmarks.run_benchmark 1000 10
```

The runner starts the threaded server on port 8001 and its FastAPI comparison
on port 8002. It does not measure the Karak ASGI implementation. Historical
measurements describe their original setup; rerun them for your environment.

Read the [experiment guide and recorded results](https://github.com/grandimam/karak/blob/main/experiments/free_threaded/README.md).

## Boundaries

The experiment is repository-only research code and is excluded from the
installed `karak` wheel. It handles HTTP/1.1 and does not provide WebSockets,
HTTP/2, or a middleware system. Neither implementation currently provides a
durable job queue or a production-ready application platform.
