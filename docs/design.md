# Karak architecture: one coherent backend system

> **Design proposal.** This document describes intended architecture and design
> criteria. Today the main `karak` package provides an experimental async ASGI
> foundation. Persistence, background work, scheduling, and integrated production
> operation are planned. See the [ASGI guide](asgi.md) for current behavior.

## The thesis

**Python backend development should be integrated, not assembled.**

Karak should give Python backend engineers one coherent system to learn deeply,
build with, and operate. Engineers should learn Python and the fundamentals of
HTTP, databases, transactions, concurrency, reliability, and distributed
systems, then apply that knowledge through Karak. The framework should absorb
unnecessary integration and tooling complexity around those fundamentals.

The product ambition is to make “Karak engineer” meaningful. Architecture
choices should support that ambition across the production backend:

**HTTP → persistence → background work → scheduling → observability → operation**

The [public thesis and direction](content/design.md) describes the intended
experience. This document establishes how contributors should evaluate designs
that make it possible. It supersedes the earlier execution-centered roadmap;
synchronous and free-threaded execution remain possibilities within the broader
system, rather than the test of the product thesis.

## Four architectural commitments

| Commitment | Design responsibility |
| --- | --- |
| One programming model | Use consistent Python interfaces for application definitions, resources, requests, and work. New capabilities should extend concepts an engineer already knows. |
| One configuration model | Define consistent setting names, validation, overrides, and error reporting across process roles. |
| One lifecycle | Define who owns resources, when they are acquired and released, and how startup, cancellation, failure, and shutdown behave. |
| One operational model | Provide consistent ways to run, inspect, diagnose, deploy, and recover requests, jobs, and schedules. |

These are commitments for the planned system. Current lifespan handling accepts
an application-defined async context manager for setup and cleanup. Registered
resource factories support typed dependencies and application-scoped sharing;
request connections and transactions remain the application's responsibility.

Integration does not require implementing every underlying component ourselves.
ASGI servers, database drivers, and other infrastructure can sit behind explicit
boundaries. Karak should own supported integration paths and their behavior.
For normal application work, engineers should not have to reconcile independent
configuration systems and lifecycles themselves.

A single application model can span multiple processes and machines. Shared
configuration does not imply shared memory, and a consistent lifecycle does
not imply that every process starts or stops simultaneously.

## Architecture boundaries

The proposed responsibilities are:

| Boundary | Responsibility |
| --- | --- |
| Application definition | Routes, work definitions, schedules, settings, and resource declarations |
| Protocol handling | ASGI request and response handling, with protocol-specific behavior kept explicit |
| Resource and persistence management | Database connections, transaction scopes, migrations, and cleanup |
| Execution | Dispatch, concurrency limits, cancellation, timeouts, and worker ownership |
| Durable work and scheduling | Persisted job state, claiming work, retry policy, recovery, and schedule decisions |
| Observability and operation | Connected context, health, inspection, process control, and deployment behavior |

These are internal boundaries within one product. Each subsystem must carry the
same application identity, configuration conventions, and lifecycle contracts.
The exact module layout and public APIs remain open design decisions.

## HTTP foundation

The current implementation establishes ASGI handling, router composition, typed
path and query inputs, validation, and text or byte responses. It prepares
routes and inspects handler signatures during application construction.

Planned HTTP work includes structured bodies and responses, shared resources,
middleware interfaces, and generated API documentation. Routing, validation,
and API documentation should derive from the same definitions so their behavior
cannot drift. Protocol features such as streaming and WebSockets need explicit
resource and cancellation behavior when introduced.

Keep protocol compatibility and errors understandable. Validate inputs before
calling application code, avoid repeating reflection for each request, and
avoid exposing internal exception details in production responses.

## Persistence and resource ownership

Persistence belongs in the application model because transactions and schema
changes affect requests, workers, and deployments together. A persistence design
should cover:

- Resource acquisition, pooling, scope, and cleanup across process roles.
- Explicit transaction boundaries, commit and rollback behavior, and failures.
- Schema migrations and compatibility with running application versions.
- A supported relationship between application writes and durable job submission.

Database APIs, migration interfaces, and the need for an ORM are undecided.
Owning the persistence experience does not commit Karak to a custom database
engine or to hiding SQL and transaction concepts.

Dependencies should have explicit scopes. Request-scoped state must not silently
outlive its request or be passed to another process. A worker must acquire its
own resources under the same application rules. Any future dependency graph
should be prepared where possible and must respect declared resource ownership.

## Background work: preserve the model as guarantees grow

The intended progression is simple background execution, durable execution,
then distributed workers and scheduled work. Engineers should keep familiar
work definitions, configuration conventions, resource rules, and inspection
concepts throughout that progression.

Each mode needs a clear contract. Before exposing a mode, define and verify:

| Concern | Required design decision |
| --- | --- |
| Submission | When work is accepted, and what survives process failure |
| Transactions | Whether application writes and submission can commit atomically, and under which conditions |
| Delivery | When duplicate execution is possible and what application idempotency is required |
| Retries | Eligible failures, limits, delays, and how attempts are recorded |
| Ownership | How workers claim work and recover abandoned claims |
| Cancellation and timeouts | What can be interrupted and what happens to external side effects |
| Capacity | Concurrency limits, queue pressure, and resource isolation |
| Compatibility | How persisted inputs and work definitions behave across deployments |
| Results | Retention, status, failure history, and inspection |

A familiar interface must not conceal a change in reliability guarantees.
Moving work to another process also introduces serialization and resource
boundaries; these must be visible and documented.

A queue stored in the application's database, with PostgreSQL as an initial
candidate, is a proposed integration strategy. It could support transactional
submission and reduce the need for a separate broker. This is not an implemented
storage contract. Contention, polling or notification, claiming, recovery,
retention, and capacity must be evaluated before choosing it.

Replacing Celery or eliminating a broker can be a consequence of the design.
The product objective is a coherent backend experience across capabilities.

## Scheduling

Schedules should invoke the same work definitions and use the same resources,
configuration, retry policies, and operational interfaces as on-demand work.

A scheduling design must define time zones, missed runs, overlapping runs,
duplicate triggers, coordination between schedulers, and how schedule changes
interact with work already submitted. Engineers should be able to inspect why
a run happened or was skipped. Scheduling has no implementation today.

## Observability and operation

Observability should grow alongside each capability. Requests, database work,
job submissions, attempts, and scheduled runs need connected context so an
engineer can follow a single application operation across process boundaries.
Logs, metrics, health information, and failure inspection should use consistent
terms and identifiers.

Operation should cover process roles, configuration, startup readiness,
deployment, graceful shutdown, and recovery. Shutdown contracts must explain
when a process stops accepting work, how long active work may finish, what
happens when that deadline expires, and how resources are released. Durable
queued work must have a defined recovery path.

A deployment model must account for schema changes and old and new workers
running together. Hosting environments, commands, dashboards, and integration
interfaces remain to be designed. One operational model does not remove the
engineer's responsibility for capacity, database backups, or incident response.

## Execution serves the application model

Current route handlers use `async def` on standard Python 3.13+. Synchronous
handlers and free-threaded execution are future exploration areas. Thread,
process, and async execution strategies should be evaluated against application
semantics and lifecycle requirements.

Concurrency, parallelism, thread safety, blocking calls, cancellation, and
resource isolation remain engineering concepts users must understand. Karak
should provide clear controls and defaults for applying them. It must not
silently move work between execution strategies when doing so changes behavior.

Performance claims require measurements. Benchmark framework overhead, I/O
workloads, CPU workloads where relevant, and behavior under overload. A faster
executor is useful when it supports reliable application behavior and the
shared model.

## Development direction

The progression describes expanding responsibility, not fixed release numbers:

1. Strengthen the existing HTTP foundation and its documented behavior.
2. Establish shared configuration, resource ownership, and lifecycle contracts.
3. Bring persistence, transaction handling, and migrations into that model.
4. Introduce background execution with explicit guarantees, then durable work
   and independent workers using the same concepts.
5. Add scheduling over the established work model.
6. Deepen observability and operation across the whole system.

Observability, diagnostics, shutdown behavior, and validation belong in every
stage. Existing HTTP features are a foundation; they do not yet demonstrate the
full thesis or production readiness. Release scope should follow verified
capabilities rather than the earlier speculative version roadmap.

## Review criteria

For each proposed capability, contributors should explain:

- Which backend concept it lets an engineer apply and which integration burden
  Karak takes responsibility for.
- How it reuses the programming, configuration, lifecycle, and operational models.
- What guarantees it provides and what happens during failure, restart, and upgrade.
- Which choices remain explicit and which underlying tools users must understand.
- How its behavior will be verified and taught through a complete application workflow.

Production readiness requires demonstrated reliability, stable documented
contracts, appropriate security behavior, and operational experience. The
standard is whether deep knowledge of Karak and backend fundamentals lets an
engineer confidently build and operate the supported system.
