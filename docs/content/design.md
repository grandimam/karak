---
title: Design notes
description: The principles and longer-term direction behind Karak.
---

# Beyond the request handler.

<p class="lead">A simpler path from Python to production.</p>

An application needs to manage resources, run background work, recover from
failures, shut down cleanly, and make its behavior visible. Karak’s goal is to
bring that work into one application model.

## Say each thing once

Python already has packages, functions, annotations, defaults, imports, and
context managers. Where those structures communicate intent clearly, the
framework should use them. Where information is missing, it should ask for
that information explicitly.

## Make execution understandable

The long-term direction includes ordinary synchronous application code,
concurrent execution, and parallel execution on free-threaded Python. Resource
lifetimes, cancellation, failure handling, and shutdown should have clear
semantics.

The ASGI implementation uses async handlers today. The free-threaded HTTP
experiment explores a separate synchronous approach.

## Take background work seriously

Durable jobs need persistence, delivery semantics, retries, timeouts, and
visibility into failures. A thread pool alone does not provide those
guarantees. Jobs, workers, scheduling, and operational tooling are future work.

## Read the proposals

These are working design documents, not a reference for implemented APIs:

- [Production goals and execution model](https://github.com/grandimam/karak/blob/main/docs/design.md)
- [Framework and resource model](https://github.com/grandimam/karak/blob/main/docs/framework.md)
- [ASGI load-testing guide](https://github.com/grandimam/karak/blob/main/docs/load-testing.md)

For what works today, use the [quickstart](index.md) and the framework pages.
