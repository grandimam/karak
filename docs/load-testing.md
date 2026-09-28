# Run reproducible HTTP benchmarks

The [benchmark guide](content/benchmarks.md) explains Karak's measured comparison
with FastAPI and the meaning of throughput, latency, and concurrency.
The [runner instructions](../benchmarks/README.md) document the workloads,
environment, raw output, and reproducibility controls.

From the repository root, install `hey` (`brew install hey` on macOS), then:

```sh
uv sync --project benchmarks --frozen
benchmarks/.venv/bin/python benchmarks/run.py \
  --seconds 5 --warmup 1 --repeats 3 --concurrency 1 32 \
  --output benchmarks/results/my-run
```

This starts each server, checks equivalent responses, warms up, measures,
and shuts down. Each output directory must be new. Completed reports contain
`metadata.finished_at_utc`, all individual measurements, and `summary`.
Partial reports from failed runs are retained for diagnosis.

## Extend the matrix

The initial suite covers text, typed path/query inputs, request context, and a
1 KiB body echo. Add realistic application workloads separately:

- Actual database reads/writes, with identical data and pool configuration.
- Registered service access and application business operations.
- Validation failures, tracked separately from successful responses.
- Larger route tables and payload sizes.
- Multiple workers and alternative event loops, labeled as separate configurations.

Always verify response equivalence before comparing speeds. Keep Python, server,
client, concurrency, response format, and dependency versions fixed. If features
differ, state exactly which work each framework performs.

## Before capacity planning

Move the load generator to another machine, run longer trials, and measure CPU,
RSS memory, database timings, and errors. Use an arrival-rate-controlled tool to
study overload; the included hey comparison uses fixed concurrent clients.
Match the deployment's proxy, TLS, worker count, data, and authorization paths.
These local microbenchmarks are a development baseline, not a production sizing
recommendation.
