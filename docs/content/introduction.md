---
title: Introduction
description: What you can do with Karak today and the Python application experience we are building toward.
---

# From your first endpoint to a running application.

<p class="lead">Karak is being built to make Python applications easier to take to production.</p>

You start with an API. Then you need to send an email after a request, generate
a report in the background, run something every night, and find out why a job
failed. Those are all parts of the same application.

We want Karak to give you one way to build and operate that application, from
handling a request to running the work that follows it.

## What can I use today?

You can try an early API framework: create endpoints, read typed values from a
URL, reject invalid input, and return text or bytes. The guides walk you through
those tasks with examples you can run locally.

Karak is experimental and not ready for production use. Background jobs,
scheduling, and the broader production experience described in the
[vision](design.md) are still planned.

## Start with a small application

You need Python 3.13+ and uv. Standard Python works; you do not need a
free-threaded build to get started.

1. [Run your first endpoint](index.md).
2. [Add URLs to your application](routing.md).
3. [Accept and validate request values](parameters.md).
4. [Choose what to send back](responses.md).

If you need help setting up your environment, begin with
[installation](installation.md).

## Where is Karak going?

The goal is to let you build an API, hand work to a worker, schedule recurring
jobs, and operate them together. You should be able to see what is running,
understand failures, and deploy changes with predictable behavior.

Read [what we plan to build](design.md) for the intended experience and the
steps toward it.

## Curious about free-threaded Python?

There is also a [separate experiment](free-threaded.md) for trying synchronous
handlers and parallel execution. It has a different API and is intended for
exploration. Start with the main guides if you want to learn Karak’s current
API.
