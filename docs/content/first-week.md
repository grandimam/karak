---
title: First-week schedule
description: Follow the backend curriculum over seven practical sessions, with concrete checkpoints and time to repeat difficult lessons.
---

# A suggested first week.

<p class="lead">Use the curriculum in order, at a pace that leaves time to build and explain.</p>

The [curriculum map](curriculum.md) is the full chapter sequence. This page groups
it into seven sessions, assuming basic Python and roughly one to two hours per
session. Take longer when a concept is new. The goal is a small, tested local
backend and a clear understanding of how it works.

## Day 1: Hello World

Complete [installation](installation.md) and [lesson 1](index.md). Create
`main.py`, start Uvicorn, change the greeting, and restart the server.

**Checkpoint:** Run the app from a stopped terminal and identify its module,
application object, address, and returned body.

## Day 2: Endpoints and the request path

Complete [lesson 2: endpoints](endpoints.md) and [lesson 3: follow a request](introduction.md).
Try GET and POST, then trace the request through client, server, router, and handler.

**Checkpoint:** Explain a 405 response and why renaming a handler does not change
its URL. Distinguish import-time setup from per-request execution.

## Day 3: Inputs and outcomes

Complete [lesson 4: parameters](parameters.md) and [lesson 5: responses](responses.md).
Try valid values, missing values, invalid values, and a valid ID that does not exist.

**Checkpoint:** Explain why the examples return 200, 422, or an explicit 404.
Show the difference between a response header and the response body.

## Day 4: Request context

Complete [lesson 6](request-context.md). Save a preference cookie, send it on a
later request, delete it, and read raw body bytes with `await`.

**Checkpoint:** Explain `.value`, why request state is temporary, and why a
client-provided cookie is not proof of identity.

## Day 5: Modules and routers

Complete [lesson 7](routing.md). Create the application package, include each
module's router, and run the new entry point.

**Checkpoint:** Add a module without editing another feature's handlers. Explain
why child routes must exist before inclusion and why duplicate paths fail.

## Day 6: Resources and lifetime

Complete [lesson 8: shared resources](resources.md) and [lesson 9: lifecycle](application.md).
Run the catalog example and observe its setup and cleanup.

**Checkpoint:** Contrast an application service with the current request, and
explain what a development reload does to both.

## Day 7: Test and assemble

Complete [lesson 10: testing](testing.md), including the intentional failing
assertion. Start combining the examples into the
[course project](curriculum.md#put-the-chapters-together).

**Checkpoint:** Show passing tests for a successful lookup, invalid input,
a missing product, and factory cleanup. Trace one request without looking at
the guide, and list what your backend would still need before production use.

Continue the project if it takes another session. The current course covers HTTP
and application structure; databases, authentication, deployment, and operations
will require further lessons and implementation. Read the
[benchmark reference](benchmarks.md) afterward if you want to investigate local
HTTP performance.
