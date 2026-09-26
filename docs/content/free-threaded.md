---
title: Free-threaded experiment
description: Try synchronous endpoints and explore how your workload behaves on free-threaded Python.
---

# Try another way to run Python.

<p class="lead">Explore synchronous endpoints and parallel work.</p>

If you want to experiment with ordinary `def` handlers and free-threaded
Python, Karak includes a separate HTTP implementation you can run locally.
Use it to explore how your own workload behaves with several worker threads.

It is research software with a different API from the main framework. For your
first Karak application, start with the [quickstart](index.md).

## Run the sample application

From your Karak checkout:

```sh
uv sync --group experiments --python 3.13t
uv run --group experiments --python 3.13t python -m experiments.free_threaded.examples.basic
```

Here `3.13t` selects a free-threaded Python build. Visit
[localhost:8000](http://127.0.0.1:8000) to see the sample application.

## Try your own endpoint

Save this as `threaded_example.py` in the repository root:

```python
from experiments.free_threaded import Karak

app = Karak()


@app.get("/")
def index():
    return {"message": "Hello from Karak"}


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, workers=4)
```

Stop the sample server with **Ctrl+C** first, then run:

```sh
uv run --group experiments --python 3.13t python threaded_example.py
```

The endpoint returns JSON. You can also explore typed request bodies and
shared dependencies using the [included example](https://github.com/grandimam/karak/blob/main/experiments/free_threaded/examples/basic.py).
Those features belong to this experiment, not the main ASGI API.

## Compare a workload

Stop any servers on ports 8001 and 8002 before running the comparison:

```sh
uv run --group experiments --python 3.13t python -m experiments.free_threaded.benchmarks.run_benchmark 1000 10
```

This sends 1,000 requests with 10 concurrent clients for each workload. It
compares the threaded experiment with a FastAPI example. The results depend on
your machine, Python build, and workload; they do not measure the main Karak
framework.

The [experiment guide](https://github.com/grandimam/karak/blob/main/experiments/free_threaded/README.md)
has more details and historical results.

## What this experiment is for

It helps investigate the [planned execution experience](design.md#use-more-of-your-machine):
ordinary Python that can take advantage of the machine it runs on. It is not a
production deployment option or a background-job system. Use it from the
repository; it is not included in the installed `karak` package.
