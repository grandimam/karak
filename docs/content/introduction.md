---
title: Introduction
description: Learn the fundamentals. Learn Karak deeply. One coherent system for Python backend engineering.
---

# Python backend development should be integrated, not assembled.

<p class="lead">Karak is being built to give Python backend engineers one coherent system to learn deeply, build with, and operate.</p>

Building a production Python backend often means assembling a framework,
server, task queue, broker, scheduler, migration tools, observability, and
deployment tooling. Each adds its own abstractions and operational model.
Karak aims to absorb that integration complexity so knowledge of one system
carries across the application.

## Built for engineers

Learn Python. Understand HTTP, databases, transactions, concurrency,
reliability, and distributed systems. Learn Karak deeply and apply those
fundamentals to serious backends.

That is the ambition behind “Karak engineer.” You should understand how your
application behaves, including how it fails. You should also have the comfort
of working within a system whose configuration, lifecycle, and operations are
consistent as your application grows.

## One system, progressively more of the backend

**HTTP → persistence → background work → scheduling → observability → operation**

Karak should extend one programming model, one configuration model, one
lifecycle, and one operational model across these capabilities. For example,
moving from a simple background task to durable distributed work should build
on the Karak model you already know. Reliability requirements become more
explicit as work grows; the surrounding toolchain should not need to be
relearned at each stage.

Read [the thesis and direction](design.md) for what this means in practice.

## What can I use today?

Today Karak provides an experimental HTTP foundation: async endpoints, typed
path and query values, validation, and text or byte responses. It runs on
standard Python 3.13+ with an external ASGI server such as Uvicorn.

Karak is not ready for production use. Integrated persistence, background
execution, durable jobs, scheduling, observability, and production operation
are planned. These guides teach the working HTTP foundation and label future
capabilities separately.

## Start with the HTTP foundation

1. [Run your first endpoint](index.md).
2. [Add URLs to your application](routing.md).
3. [Accept and validate request values](parameters.md).
4. [Choose what to send back](responses.md).

If you need help setting up your environment, begin with
[installation](installation.md).
