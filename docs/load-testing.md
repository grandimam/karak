# Load Testing

This guide covers Karak’s ASGI implementation (`karak`). The thing you should load test is the full
request path:

1. ASGI server
2. `Karak.__call__`
3. `Request` creation
4. route matching
5. handler execution
6. response serialization

For this repository, the cleanest setup is:

- run the app with `uvicorn`
- drive traffic with `hey` first
- start with one server worker to measure framework overhead
- increase concurrency gradually and record latency/error rates

## 1. Run the app

Install the development dependencies from the repository root:

```bash
uv sync
```

Then run the app:

```bash
uv run uvicorn examples.basic:app --host 127.0.0.1 --port 8000 --workers 1
```

Use `--workers 1` first. That isolates the performance of the framework path
inside a single process. If you later want to measure multi-process scaling,
repeat the same test with `--workers 2`, `--workers 4`, and so on.

## 2. Install hey

On macOS:

```bash
brew install hey
```

## 3. Run a baseline test

From the repository root:

```bash
hey -n 10000 -c 100 http://127.0.0.1:8000/users/123
```

This command uses:

- URL: `http://127.0.0.1:8000/users/123`
- total requests: `10000`
- concurrency: `100`

This hits the current demo endpoint:

```text
GET /users/123
```

## 4. Run progressively harder tests

```bash
hey -n 20000 -c 200 http://127.0.0.1:8000/users/123
hey -n 50000 -c 500 http://127.0.0.1:8000/users/123
```

This gives you a quick view of:

- throughput at each load level
- p95 and p99 latency
- when error rates begin to rise

Vary `-n` for total requests and `-c` for concurrency.

## 5. What to measure

For each run, record:

- requests/second
- average latency
- p95 latency
- p99 latency
- error rate
- CPU usage
- memory usage

If you are testing the framework itself, compare:

- static route vs parameterized route
- small response vs larger response
- one worker vs multiple workers

## 6. Suggested test matrix

Run these separately so results stay interpretable:

1. `GET /users/123` with current demo handler
2. same route with a handler that returns a larger payload
3. typed query parameters, including repeated list values, using a custom demo route
4. valid input vs a validation failure, recording expected HTTP 422 responses separately
5. one process vs multiple `uvicorn` workers

Handlers can receive `ResourceContext[Request]` and read cached body bytes with
`await context.value.body()`. Automatic body binding and `Request.json()` are
not implemented. Body-parsing benchmarks must explicitly parse these bytes.

## 7. Important caveat for this repo

Right now the repository is still early-stage alpha, so a load test here is
best used for relative comparison while developing the framework, not for
production capacity planning.

Examples:

- compare router changes before/after an optimization
- compare GIL vs free-threaded Python builds
- compare path-matching approaches

## 8. Interpreting results

If throughput is low and CPU is also low, you likely have blocking or request
handling overhead outside raw compute.

If CPU is high and latency rises smoothly with concurrency, you are probably
CPU-bound in routing, request parsing, or response generation.

If p99 jumps far earlier than p50, you likely have queueing contention under
load.
