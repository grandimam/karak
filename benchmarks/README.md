# Karak vs FastAPI HTTP benchmark

This suite measures four small HTTP workloads through a real Uvicorn server.
It checks response status, bytes, content type, and content length before loading
each endpoint. It is a local framework baseline, not a production capacity test.

## Reproduce

From the repository root, with Python 3.13+ and `hey` on PATH:

```sh
# macOS, if hey is not installed:
brew install hey
uv sync --project benchmarks --frozen
benchmarks/.venv/bin/python benchmarks/run.py \
  --seconds 5 --warmup 1 --repeats 3 --concurrency 1 32 \
  --output benchmarks/results/my-run
```

Use a new output directory for every run. The runner refuses to overwrite results.
Generated results are ignored by Git; keep published summaries in the benchmark guide.
The environment is separate from Karak's runtime and development dependencies;
`benchmarks/uv.lock` pins the comparison dependencies. Karak is imported from
this checkout's `src` directory. Close other heavy applications before running.

Each framework runs alone in a fresh server process for each measurement.
The runner alternates which framework runs first between repetitions, runs
one second of warmup, then five seconds of measurement. It shuts down every
server it starts, including after failures. The default suite takes about five
to six minutes. Client and server share the same machine.

## Workloads

| Name | Request | Work |
| --- | --- | --- |
| `text` | GET `/text` | Construct a fresh 13-byte text response |
| `typed` | GET `/users/42?active=false&limit=20` | Convert integer path, boolean query, and integer query inputs |
| `context` | GET `/context` | Inject request access, read `X-Client` and a theme cookie |
| `body` | POST `/body` | Read and echo 1,024 bytes |

Each app has the same four routes in the same order, with async handlers.
Both produce identical body bytes and explicit content type/content length.
FastAPI returns a response object directly to avoid automatic JSON serialization.
The request access idioms differ: Karak uses `ResourceContext[Request]`, and
FastAPI injects `Request`. No database, auth, custom middleware, response model,
resource factory, or artificial sleep is included. FastAPI's docs routes are off.

Both servers use one Uvicorn worker, `asyncio`, `h11`, lifespan enabled, HTTP/1.1
keep-alive, and no access logs. Uvicorn server/date headers are disabled on both.
`hey -cpus 2` fixes the client's Go CPU setting, not OS CPU affinity. There is
no CPU pinning, TLS, separate load-generator machine, or uvloop in this baseline.

## Read the output

- `results.json`: environment, source hashes, commands, all measurements, and summaries.
- `*.txt`: original measured hey reports, including status counts and latency distributions.
- `*.server.log`: server warnings/errors, normally empty.

Generate Markdown tables from a finished run:

```sh
benchmarks/.venv/bin/python benchmarks/report.py benchmarks/results/my-run/results.json
```

Summary throughput is the median requests/second across repetitions. Min/max
show run-to-run variation. Summary p95/p99 are medians of per-run percentiles,
not percentiles pooled over all requests. hey rounds latency output to 0.0001
seconds, so the displayed precision is 0.1 ms.

The run aborts on non-200 responses, client errors, response mismatch, or source
changes during measurement. Earlier completed measurements remain on disk for
diagnosis; a complete report has `finished_at_utc` and `summary` fields.

These are closed-loop tests: when one request finishes, a client sends another.
They do not simulate an independently arriving traffic stream. Throughput and
tail latency include local client, socket, server, and OS scheduling overhead.
Measure your actual database and business operations before capacity planning.
