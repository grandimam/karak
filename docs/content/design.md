---
title: Mission
description: Python backend development should be integrated, not assembled. Karak's thesis and path toward one coherent production backend system.
---

# Our mission: one coherent Python backend system.

<p class="lead">Learn the fundamentals. Learn Karak deeply. Build and operate serious Python backends.</p>

## The thesis

Python backend development has become too fragmented. A production application
often requires a collection of independent tools: an ASGI framework, server,
task queue, broker, scheduler, migrations, observability, deployment tooling,
and more. Each brings its own abstractions, configuration, operational model,
and failure modes. Engineers spend substantial effort learning how those
pieces fit together and maintaining their connections.

**Python backend development should be integrated, not assembled.**

Karak should give engineers one coherent system to learn deeply. A developer
should be able to learn Python, understand the fundamentals of backend
engineering, and learn Karak. Karak should absorb the unnecessary integration
and tooling complexity around those fundamentals.

**This is the direction, not today's feature set.** Karak currently provides
an experimental HTTP foundation with async endpoints, typed URL inputs,
validation, text or byte responses, and shared application resources. The broader capabilities below are
planned, and Karak is not production-ready.

## Built for engineers who understand their systems

A Karak engineer should understand HTTP, databases, transactions, concurrency,
reliability, and distributed systems. Those concepts explain whether an
application behaves correctly under load, during failures, and through change.

Karak should make those concepts easier to apply. It must expose transaction
boundaries, resource lifetimes, retry policies, and failure behavior clearly.
Engineers still decide what consistency their application needs, whether an
operation is safe to retry, and how to handle partial failure.

The ambition is to make “Karak engineer” meaningful: deep knowledge of Karak
and backend fundamentals should be enough to build and operate serious Python
backends without becoming an expert in a dozen unrelated tools.

## Four commitments across the backend

| Commitment | What an engineer should be able to rely on |
| --- | --- |
| One programming model | Familiar Python functions and types, with consistent ways to use shared application resources across requests and work |
| One configuration model | Settings with consistent naming, validation, and override rules across the application |
| One lifecycle | Defined setup, resource ownership, execution, cleanup, and graceful shutdown across process roles |
| One operational model | Consistent ways to run, inspect, diagnose, deploy, and recover the application |

One system can run in multiple processes and on multiple machines. Coherence
means those processes share an application model and understandable contracts.
It does not require every workload to run in one process or every component
to be implemented from scratch. Karak should own the integration and document
the behavior engineers depend on, including the boundaries of external systems.

## Progressively own the production backend

**HTTP → persistence → background work → scheduling → observability → operation**

This progression describes the scope Karak should grow to own. Observability
and operational behavior need to develop alongside each capability. It is a
direction, not a release calendar.

| Area | Intended experience | Today |
| --- | --- | --- |
| HTTP | Define endpoints, validate input, return structured responses, and share services | Async endpoints, typed path and query inputs, validation, text and bytes, application resources |
| Persistence | Manage database resources, transactions, and schema migrations within Karak's application model | Planned |
| Background work | Grow from simple background execution to durable distributed work using the same concepts | Planned |
| Scheduling | Schedule the same work with explicit behavior for missed runs, overlaps, and time zones | Planned |
| Observability | Follow requests and jobs through logs, metrics, failures, and health information | Planned |
| Operation | Configure, start, deploy, stop, inspect, and recover application processes consistently | Planned |

Persistence is part of the thesis because data, transactions, and schema
changes shape application correctness. The specific database APIs and migration
interfaces are still to be designed. Similarly, operation is a product
responsibility; the exact deployment commands and supported environments remain
open decisions.

## Background work is the test case

An application first needs to send an email after a request. Later, the email
must survive an application restart. Then it needs retries, more workers, and
a recurring schedule.

Today that progression often means graduating from framework background tasks
to Celery plus Redis or RabbitMQ, worker configuration, a scheduler, and tools
to inspect failures. The engineer must learn a new programming and operational
model to continue solving the same application problem.

Karak should support that growth within one system:

1. Define background work using familiar Python and application resources.
2. Choose durable execution when work must survive a process restart.
3. Configure retries, timeouts, concurrency, and recovery through Karak.
4. Run workers independently as capacity and isolation requirements grow.
5. Schedule and inspect that same work through the shared operational model.

The mental model should carry forward. The guarantees must be explicit at each
stage: in-process work can be lost, durable work needs persisted state, and
retries can cause duplicate execution. Engineers must understand idempotency,
transaction boundaries, and failures between systems. A familiar API must never
imply guarantees the selected execution mode cannot provide.

No background execution or durable job system is available in Karak today.

## One application from request to recovery

Consider a customer report. An endpoint validates a request, saves the report
record, and submits work. A worker loads the data and generates the report.
The customer can inspect its status, and the same work can run every Monday.

In the intended Karak experience, the endpoint, database resources, job, and
schedule belong to one application model. The engineer can trace a failure
back to the request, understand whether retrying is safe, and deploy with
defined behavior for work already running.

Making the database update and job submission atomic is an engineering
requirement to design and verify. Sharing a framework alone cannot guarantee
it. Karak's responsibility is to provide an explicit, supported way to express
that relationship and explain its limits.

## How we judge progress

A feature should deepen what an engineer can do with Karak while reusing what
they already know. Adding a wrapper around another tool is insufficient if
engineers still have to learn and reconcile its separate configuration,
lifecycle, and failure handling for ordinary use.

We should evaluate new capabilities against the four commitments, document
their guarantees, and verify behavior through failures and restarts. Performance
work, including exploration of synchronous and free-threaded execution, serves
this larger objective. Current handlers use `async def`; standard Python is
supported today.

Production readiness must be earned through reliable behavior, testing,
documentation, and real use. Try the [HTTP quickstart](index.md) to explore the
foundation, or [share a backend workflow](https://github.com/grandimam/karak/issues)
that Karak should make coherent.
