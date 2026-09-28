---
title: Benchmarks
description: Compare Karak and FastAPI on reproducible local HTTP workloads, and learn what throughput and latency measurements mean.
---

# Measure a backend with a repeatable workload.

<p class="lead">Compare matching requests and record the conditions behind the results.</p>

This section compares Karak and FastAPI through real HTTP requests to Uvicorn.
It measures the small HTTP operations both frameworks support today. It does
not measure a complete production backend or establish feature parity.

## Understand the numbers

**Throughput**, expressed as requests per second, counts how much work completes
in a second. Higher is better when the requests and available resources are the
same. **Latency** is how long one request takes. Lower is better.

**p95 latency** means 95% of measured requests finished within that duration.
It helps reveal delays hidden by an average. **Concurrency** is how many client
requests can be in flight at once. A concurrency of 32 does not mean 32 users
of your whole application; it is a load-generator setting for this test.

## What we compare

| Workload | Request | Handler work |
| --- | --- | --- |
| Small text | GET `/text` | Return 13 text bytes |
| Typed inputs | GET `/users/42?active=false&limit=20` | Convert an integer path and boolean/integer query values |
| Request context | GET `/context` | Read a header and cookie from the current request |
| Body echo | POST `/body` | Read and return 1 KiB of bytes |

Both applications have the same four routes in the same order. All handlers
are async, construct fresh responses, and produce matching bytes, content type,
and content length. Before each measurement, the runner verifies these outputs.
FastAPI returns a response object directly, which bypasses automatic response
conversion as described in its [response documentation](https://fastapi.tiangolo.com/advanced/custom-response/).

Both use one Uvicorn worker with `asyncio` and `h11`, lifespan enabled, keep-alive
connections, and access logs disabled. The load generator is `hey`, using two Go
CPUs. Client and server run on the same host over loopback. No database, TLS,
authentication, custom middleware, JSON conversion, or external network is involved.

## Local results: 29 September 2026

Measured on an Apple M2 Pro (12 logical CPUs), macOS 26.5.2 arm64,
Python 3.13.3. Dependency versions: FastAPI 0.141.1, Starlette 1.7.0,
Pydantic 2.13.5, Uvicorn 0.54.0, h11 0.16.0; load generator hey 0.1.5.
The measurement date uses Dubai time.

All **2,307,584 measured requests returned HTTP 200**, with zero client errors
across 48 measurements. Warmup requests are excluded from this count. CPU usage
and memory consumption were not measured.

At concurrency 32, Karak's median throughput was 1.18× FastAPI for text,
1.47× for typed inputs, 1.04× for request context, and 1.17× for body echo.
At concurrency 1, the ratios were smaller: 1.08×, 1.22×, 1.01×, and 1.07×
respectively. The context result is close; three short repetitions do not
establish statistical significance. These ratios apply to these workloads and
this machine, not to every application built with either framework.
Karak's reported p99 latency was higher in all four single-client workloads,
despite its higher throughput; throughput alone does not describe tail behavior.

### Concurrency 1

| Workload | Karak req/s (min–max) | FastAPI req/s (min–max) | Karak / FastAPI | Karak p95 / p99 ms | FastAPI p95 / p99 ms |
| --- | ---: | ---: | ---: | ---: | ---: |
| text | 8,059 (7,963–8,069) | 7,477 (7,448–7,523) | 1.08× | 0.1 / 0.3 | 0.2 / 0.2 |
| typed | 7,705 (7,582–7,750) | 6,290 (6,270–6,291) | 1.22× | 0.1 / 0.3 | 0.2 / 0.2 |
| context | 7,473 (7,221–7,477) | 7,363 (7,204–7,385) | 1.01× | 0.1 / 0.4 | 0.2 / 0.2 |
| body | 7,425 (7,334–7,434) | 6,939 (6,892–6,982) | 1.07× | 0.1 / 0.3 | 0.2 / 0.2 |

### Concurrency 32

| Workload | Karak req/s (min–max) | FastAPI req/s (min–max) | Karak / FastAPI | Karak p95 / p99 ms | FastAPI p95 / p99 ms |
| --- | ---: | ---: | ---: | ---: | ---: |
| text | 14,265 (14,207–14,395) | 12,085 (11,961–12,206) | 1.18× | 2.5 / 2.7 | 2.8 / 3.0 |
| typed | 13,132 (13,115–13,159) | 8,921 (8,843–9,101) | 1.47× | 2.7 / 2.9 | 3.8 / 3.9 |
| context | 12,186 (12,161–12,241) | 11,674 (11,597–11,778) | 1.04× | 2.9 / 3.1 | 2.9 / 3.1 |
| body | 12,332 (12,284–12,464) | 10,583 (10,510–10,611) | 1.17× | 2.9 / 3.1 | 3.2 / 3.5 |

The tables retain the measured summary. Generated reports and logs are not
stored in the repository; rerun the suite to produce local results.

## Reproduce the comparison

The [benchmark source and instructions](https://github.com/grandimam/karak/tree/main/benchmarks)
include both apps, the runner, and a lockfile for the comparison dependencies.

From a repository checkout, install `hey` if needed (`brew install hey` on macOS),
then run:

```sh
uv sync --project benchmarks --frozen
benchmarks/.venv/bin/python benchmarks/run.py \
  --seconds 5 --warmup 1 --repeats 3 --concurrency 1 32 \
  --output benchmarks/results/my-run
```

This uses a separate environment with locked benchmark dependencies. Choose a
new output directory for each run. Expect roughly five to six minutes for the
default suite; avoid other heavy work on the machine while it runs.

Each measurement starts a fresh server, warms it up for one second, and measures
for five seconds. Three repetitions are taken at each concurrency, alternating
which framework runs first between repetitions. Each server is stopped before
the next measurement. The runner saves raw hey reports, environment details,
source hashes, and a JSON summary. Errors stop the run rather than being counted
as successful throughput.

## Interpret the results carefully

The tables report median throughput across repetitions, with minimum and maximum
throughput to show variation. Reported p95 and p99 are medians of each run's
percentiles, not pooled percentiles. hey's latency display rounds to 0.1 ms.

The client uses a closed loop: it sends the next request after the previous one
finishes. This does not model requests arriving independently during overload.
Client and server share CPU and scheduling resources. These measurements cannot
isolate Python framework execution time from network and server overhead.

Small handlers expose HTTP overhead. A production endpoint may spend most of
its time waiting for a database, checking permissions, or calling another service.
Use this comparison as a local baseline and rerun with your application's work
before making a capacity decision. FastAPI and Karak also provide different
feature sets; Karak remains experimental.
