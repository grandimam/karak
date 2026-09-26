---
title: Introduction
description: Karak’s direction, current capabilities, and free-threaded experiment.
---

# A simpler path from Python to production.

<p class="lead">One application model for the work around your Python code.</p>

Karak aims to make APIs, background jobs, workers, and scheduled tasks easier to
build, run, and operate together. The goal is a consistent approach to
configuration, dependencies, lifecycle, and observability.

## Where we are today

The main implementation is an experimental ASGI framework. It provides async
route handlers, typed path and query parameters, validation, text and byte
responses, and startup and shutdown acknowledgements. It runs on standard
Python 3.13+ and has no runtime dependencies.

Karak is early-stage software. APIs can change, and it is not ready for
production use.

## Where we want to go

Durable jobs, scheduling, worker management, and production tooling are future
goals. Reliable background work needs clear delivery guarantees, persistence,
retries, and visibility into failures. Those capabilities are not implemented
in the current framework.

The [design notes](design.md) explore that direction.

## A free-threaded experiment

The repository also includes a [separate HTTP experiment](free-threaded.md)
with synchronous handlers, a socket server, and a thread pool. It explores
parallel execution with free-threaded Python. Its API and capabilities are
separate from the main ASGI framework.

## Begin here

Follow the [quickstart](index.md) to serve your first response, then explore
[routing](routing.md) and [parameters](parameters.md).
