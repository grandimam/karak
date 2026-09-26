# Free-threaded HTTP experiment

This experiment explores synchronous Python handlers and parallel execution with a built-in HTTP server. The main `karak` package provides the ASGI framework. The benchmark results below are historical measurements of this experiment, not of the ASGI implementation. Run commands from the repository root. For the main framework, see the [ASGI guide](../../docs/asgi.md). This experiment is available from the repository and is excluded from the installed `karak` wheel.

> **⚠️ Experimental**: This project is a proof-of-concept exploring free-threaded Python (PEP 703) for HTTP frameworks. Not production-ready.

A pure-Python HTTP framework built for free-threaded Python 3.13+. No async/await — just threads with true parallelism.

The [historical benchmarks](#benchmarks) below record results from the original prototype. They are not a performance guarantee for either implementation.

Website: [karak.dev](https://karak.dev)

## Requirements

- Python 3.13+ with free-threading enabled (`python3.13t`)
- [uv](https://github.com/astral-sh/uv) package manager

## Installation

```bash
uv sync --group experiments --python 3.13t
```

## Development Setup

```bash
git clone https://github.com/grandimam/karak.git
cd karak

# Install
uv sync --group experiments --python 3.13t

# Run
uv run --group experiments --python 3.13t python -m experiments.free_threaded.examples.basic

# Test
curl http://localhost:8000/
curl http://localhost:8000/items/1
curl -X POST http://localhost:8000/items -H "Content-Type: application/json" -d '{"name":"Widget","price":9.99}'
```

## Running Benchmarks

```bash
# Install dev dependencies
uv sync --group experiments --python 3.13t

# Run benchmark
uv run --group experiments --python 3.13t python -m experiments.free_threaded.benchmarks.run_benchmark 1000 10
```

## Quick Start

```python
from typing import Annotated
from pydantic import BaseModel
from experiments.free_threaded import Karak
from experiments.free_threaded import Depends

app = Karak()

class Item(BaseModel):
    name: str
    price: float

@app.get("/")
def index() -> dict:
    return {"message": "Hello, World!"}

@app.get("/items/{item_id}")
def get_item(item_id: int) -> dict:
    return {"id": item_id}

@app.post("/items")
def create_item(body: Item) -> Item:
    return body

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, workers=4)
```

## Features

- **Pure Python**: No C extensions, no Rust, no Cython
- **Free-threaded**: True parallelism without the GIL (Python 3.13t)
- **Type-driven**: Pydantic models auto-parsed from request body
- **Dependency injection**: `Depends()` with request-scoped caching
- **HTTP Keep-alive**: Connection reuse for high throughput
- **Radix tree router**: Routes organized by path segment
- **orjson support**: Optional 3-5x faster JSON serialization
- **Small implementation**: Application, routing, request/response types, HTTP parsing, and server modules

## Benchmarks

### System

| Component | Value                  |
| --------- | ---------------------- |
| CPU       | Apple M2 Pro           |
| Cores     | 12                     |
| Python    | 3.13.0 (free-threaded) |
| Platform  | Darwin arm64           |

### High Concurrency (2000 requests, 100 concurrent clients)

| Scenario      | Free Threaded (16 threads) | FastAPI (async) | Difference           |
| ------------- | -------------------------- | --------------- | -------------------- |
| **JSON**      | 8,418 req/s                | 4,509 req/s     | Free Threaded: +87%  |
| **CPU Bound** | 1,425 req/s                | 266 req/s       | Free Threaded: +435% |

### Standard Load (1000 requests, 20 concurrent clients)

| Scenario      | Free Threaded (4 threads) | FastAPI (async) | Difference           |
| ------------- | ------------------------- | --------------- | -------------------- |
| **JSON**      | 9,287 req/s               | 4,377 req/s     | Free Threaded: +112% |
| **DB Query**  | 8,284 req/s               | 2,302 req/s     | Free Threaded: +260% |
| **CPU Bound** | 880 req/s                 | 264 req/s       | Free Threaded: +233% |

### Thread Scaling (CPU-bound workload)

| Workers | req/s | Scaling |
| ------- | ----- | ------- |
| 4       | 608   | 1.0x    |
| 8       | 1,172 | 1.9x    |
| 16      | 1,297 | 2.1x    |
| 32      | 1,391 | 2.3x    |

### Interpreting the recorded results

The tables record higher throughput for the threaded prototype in the listed
workloads and increased CPU-bound throughput as workers were added. These
measurements describe that setup only. Rerun the benchmarks for the interpreter,
dependencies, hardware, and workload you intend to evaluate; the results do not
establish the performance of the main ASGI framework.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                       Karak App                         │
│              (app.py: DI, validation, handlers)         │
├─────────────────────────────────────────────────────────┤
│                     Radix Router                        │
│              (router.py: path-segment matching)           │
├─────────────────────────────────────────────────────────┤
│                    Request / Response                   │
│               (types.py: dataclasses)                   │
├─────────────────────────────────────────────────────────┤
│                      HTTP Parser                        │
│            (http.py: parse/write HTTP/1.1)              │
├─────────────────────────────────────────────────────────┤
│                   ThreadPoolExecutor                    │
│         (server.py: sockets, keep-alive, workers)       │
└─────────────────────────────────────────────────────────┘
```

## Project Structure

```
experiments/free_threaded/
├── __init__.py   # exports
├── app.py        # Karak, Depends, DI resolution
├── router.py     # RadixRouter, path-segment matching
├── types.py      # Request, Response, HTTPException
├── server.py     # Server, ThreadPool, keep-alive
├── http.py       # HTTPParser, write_response
├── examples/     # Synchronous demo application
└── benchmarks/   # Benchmark applications, runner, and profiling scripts
```

## Why Free-Threaded Python?

Traditional Python has the GIL (Global Interpreter Lock), which prevents true parallelism in threads. Web frameworks work around this using:

- **Async/await** (FastAPI, Starlette): Cooperative multitasking
- **Multiprocessing** (Gunicorn, uvicorn): Separate processes with IPC overhead

Free-threaded Python (PEP 703) removes the GIL, enabling:

- **Simple synchronous code** that runs in parallel
- **Shared memory** between threads (no serialization)
- **Lower overhead** than multiprocessing

## Limitations

- Experimental and not battle-tested
- HTTP/1.1 only (no HTTP/2, no WebSocket)
- No middleware system (yet)
- C extensions with internal locks don't parallelize

## License

[MIT](../../LICENSE).
