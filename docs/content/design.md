---
title: Our vision
description: What we plan to build with Karak—APIs, durable jobs, scheduling, and the tools to operate them together.
---

# Build the application. Bring it to production.

<p class="lead">APIs, jobs, workers, and scheduled tasks—with one way to run them.</p>

Getting an endpoint to respond is the beginning. The work grows when it needs
to call other services, process something later, retry after a failure, and
keep running through a deployment.

We are building toward a Karak experience that covers that whole journey.
You should be able to stay focused on your Python application as it grows
beyond its first API.

**This page describes our plans.** Today you can try basic HTTP endpoints,
typed URL inputs, validation, and text or byte responses. Durable jobs,
scheduling, and the production tools below are not available yet.

## What we want you to be able to build

Imagine an application that generates customer reports. The experience we
want Karak to support looks like this:

1. A customer requests a report through your API.
2. You validate the request and queue the report without making the customer
   wait for it to finish.
3. A worker generates the report using the same configuration and services as
   the API.
4. If a temporary failure occurs, the job can retry according to your policy.
   If it still fails, you can find out why and decide what to do next.
5. The customer can check whether the report is waiting, running, finished, or
   failed.
6. You can schedule the same work to run each week, and deploy updates with
   defined behavior for work already in progress.

That is one application from the developer’s point of view. Our goal is to
make it feel like one when you build and operate it, too.

## Build useful APIs

You should be able to describe the data an endpoint accepts, return structured
responses, and give callers clear errors. Shared services such as database
connections should be straightforward to use across endpoints.

We plan to extend the current HTTP foundation with JSON bodies and responses,
shared dependencies, application setup and cleanup, middleware, and generated
API documentation. You should spend less time repeating input parsing and
wiring up the same service in different places.

## Move work out of the request

Some work takes longer than a caller should wait: sending email, processing
uploads, generating reports, or contacting an unreliable external service.
You should be able to submit that work and return a useful response promptly.

We want Karak to cover background-job workflows you might otherwise use a
separate task queue such as Celery for. The plan includes durable jobs,
retries, timeouts, job status, and a way to inspect and retry failures.

Durable means the work must have defined behavior when a worker crashes or
restarts. Delivery guarantees, duplicate execution, and recovery need an
explicit design before this can be relied on. There is no durable job system
in Karak today.

## Schedule recurring work

Daily summaries, weekly reports, and regular cleanup should belong to the same
application as your on-demand jobs. You should be able to express a schedule
and see whether the expected work actually ran.

Scheduling is planned. We still need to define how missed runs, overlapping
runs, time zones, and retries behave. These decisions matter as much as the
syntax for creating a schedule.

## Operate with confidence

You should be able to answer everyday questions without piecing together a
new set of tools for each part of your application:

- What is running, waiting, or failing?
- Which request started this job?
- Why did a task fail, and is it safe to retry?
- Is the application healthy, or are its workers falling behind?
- What happens to in-flight work when I deploy or stop a worker?

The planned production experience includes consistent configuration, shared
resource lifetimes, useful logs and metrics, health information, and graceful
shutdown. The exact commands and interfaces are still being designed; we are
not promising a particular dashboard, hosting service, or deployment platform.

## Use more of your machine

We want ordinary Python code to work well for both concurrent requests and
parallel computation. You should be able to benefit from free-threaded Python
where it fits your workload, with understandable controls over workers and
resource use.

A unified synchronous experience is a
longer-term goal; the main framework currently uses `async def` endpoints.

## The path we plan to take

| Area | What it should let you do | Status |
| --- | --- | --- |
| HTTP foundation | Run endpoints, accept typed URL values, and return text or bytes | Available for experimentation |
| Complete API workflows | Accept JSON, share services, and generate API documentation | Planned |
| Reliable background jobs | Submit work, track it, retry failures, and recover after interruptions | Planned |
| Recurring work | Schedule jobs and understand missed or overlapping runs | Planned |
| Production operations | Configure, observe, and shut down APIs and workers consistently | Planned |
| Free-threaded execution | Explore synchronous Python and parallel workloads | Planned |

The intended progression is to strengthen the API experience, establish shared
configuration and resource management, then build reliable jobs and scheduling
on those foundations. Observability and shutdown behavior need to develop
alongside each capability. This is a direction, not a release calendar; the
order can change as we learn.

## What will stay simple

You should be able to begin with a small application and add capabilities as
you need them. We want familiar Python functions, types, defaults, and modules
to do as much of the explaining as possible. Where behavior needs a choice—such
as a retry policy or a job’s lifetime—that choice should be explicit.

Production readiness is something we have to earn through reliable behavior,
testing, documentation, and real use. Karak is not there yet.

Try the [quickstart](index.md) to explore what exists today. If you want to
help shape the project, [open a discussion in the issue tracker](https://github.com/grandimam/karak/issues)
with a workflow you would like Karak to make easier.
