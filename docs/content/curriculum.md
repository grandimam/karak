---
title: Learn modern Python backend development
description: A practical curriculum from Hello World to endpoints, validation, request context, modular applications, resources, and tests.
---

# Learn modern Python backend development.

<p class="lead">Start with Hello World. Build up to a backend you can explain, organize, and test.</p>

A backend receives requests, runs application logic, and sends responses.
This curriculum teaches those responsibilities with Python and Karak. Each
chapter adds a concept you can use immediately: first an endpoint, then typed
inputs, responses, request context, and services with a defined lifetime.

The goal is to develop the skills needed to build production backend applications.
The chapters available today cover Karak's HTTP foundation. Karak is experimental;
persistence, authentication, deployment, and operational tooling are still future
work, not capabilities assumed by these lessons.

## Before you begin

You should be able to write a Python function, import a name, and use a dictionary.
Later chapters introduce classes, type annotations, `async`/`await`, and resource
cleanup as they become useful. You do not need prior web-framework experience.
Use [installation](installation.md) if your environment is not ready.

Each complete `main.py` example is a new snapshot: replace the previous version
instead of pasting multiple applications together. Smaller snippets say where
to put them. Run the example, change it, and complete the closing practice before
moving on. Keep your work in local lesson files; the documentation examples do
not require changing Karak's source.

## Part 1: Make an HTTP application

First make something work, then explain what happened between the client and
Python. Keep one file until you understand endpoints and requests.

| Lesson | What you will be able to do |
| --- | --- |
| [1. Hello World](index.md) | Create `main.py`, start the server, and see a response |
| [2. Endpoints and HTTP methods](endpoints.md) | Connect GET and POST requests to different Python functions |
| [3. Follow a request](introduction.md) | Explain the client, server, router, handler, and `async`/`await` |

## Part 2: Handle caller input and produce responses

Turn a fixed greeting into an application that accepts values. Learn where data
comes from, which values Karak converts, and how the caller sees the result.

| Lesson | What you will be able to do |
| --- | --- |
| [4. Path and query parameters](parameters.md) | Declare required values, defaults, and valid input types |
| [5. Responses and errors](responses.md) | Choose status codes, body content, headers, and outgoing cookies |
| [6. Request context](request-context.md) | Read headers, cookies, and body bytes through `ResourceContext[Request]` |

## Part 3: Grow and verify the application

Once individual endpoints work, organize them into modules and move shared
behavior into services. Give each object an appropriate lifetime and prove
important behavior with tests.

| Lesson | What you will be able to do |
| --- | --- |
| [7. Routers and modules](routing.md) | Compose feature routers and understand route order |
| [8. Shared resources](resources.md) | Supply a service through `ResourceContext[T]` and clean it up |
| [9. Application lifecycle](application.md) | Run the app and explain startup, shutdown, and reload behavior |
| [10. Test your backend](testing.md) | Test successful requests, validation failures, and resource cleanup |

## Put the chapters together

Build a small in-memory product catalog. It is complete for this stage when:

- A product endpoint accepts an integer ID and returns a name or an explicit 404.
- A preference endpoint sets a theme cookie and another request reads it back.
- Product and preference endpoints live in separate modules combined by a root router.
- A catalog service is registered once and supplied to handlers with `ResourceContext`.
- Tests cover a successful lookup, invalid input, a missing product, and cleanup.

The [resource lesson](resources.md) supplies a working catalog to build on;
[testing](testing.md) shows how to verify it. This catalog is in memory, so its
contents reset when the process restarts. That gives a concrete reason to learn
persistence next.

## Choose a pace

The [first-week schedule](first-week.md) groups these chapters into seven sessions.
Treat it as a suggested pace, not a deadline. Repeat a chapter if you can run its
example but cannot yet explain what it does.

## Where the curriculum will grow

These are future subjects, not published lessons or implemented framework features:

| Next subject | Question it should answer |
| --- | --- |
| Databases and transactions | How does data survive restarts, and which changes must succeed together? |
| Authentication and authorization | Who is making a request, and what are they allowed to do? |
| Background work | Which work can finish after the HTTP response, and how is failure recovered? |
| Observability and performance | How do logs, metrics, and traces explain behavior under real load? |
| Deployment and operations | How do configuration, migrations, shutdown, and recovery work in a running service? |

The [benchmark reference](benchmarks.md) is available now for interpreting a local
HTTP comparison. It is optional reading after the core lessons. See
[Karak's direction](design.md) for the broader framework goals.

[Start lesson 1: Hello World →](index.md){: .next-link }
