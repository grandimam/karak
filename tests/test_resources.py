from __future__ import annotations

import asyncio
import unittest

from unittest.mock import patch

from collections.abc import AsyncIterator
from collections.abc import Iterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

from karak import Karak
from karak import ResourceContext
from karak import Router
from karak import resource


@dataclass
class Pool:
    name: str
    closed: bool = False


@dataclass
class UserService:
    pool: Pool


@dataclass
class AuditService:
    pool: Pool


@asynccontextmanager
async def running(app):
    incoming = asyncio.Queue()
    outgoing = asyncio.Queue()
    state = {}
    task = asyncio.create_task(
        app({"type": "lifespan", "state": state}, incoming.get, outgoing.put)
    )
    try:
        await incoming.put({"type": "lifespan.startup"})
        startup = await asyncio.wait_for(outgoing.get(), timeout=2)
        if startup["type"] != "lifespan.startup.complete":
            raise AssertionError(startup)
        yield state
        await incoming.put({"type": "lifespan.shutdown"})
        shutdown = await asyncio.wait_for(outgoing.get(), timeout=2)
        if shutdown["type"] != "lifespan.shutdown.complete":
            raise AssertionError(shutdown)
        await task
    finally:
        if not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass


async def request(app, state):
    messages = []

    async def receive():
        return {"type": "http.request", "body": b""}

    async def send(message):
        messages.append(message)

    await app(
        {
            "type": "http", "method": "GET", "path": "/",
            "query_string": b"", "state": state.copy(),
        },
        receive,
        send,
    )
    return messages


async def lifecycle_messages(app):
    incoming = iter([
        {"type": "lifespan.startup"},
        {"type": "lifespan.shutdown"},
    ])
    messages = []

    async def receive():
        return next(incoming)

    async def send(message):
        messages.append(message)

    await app({"type": "lifespan", "state": {}}, receive, send)
    return messages


class ResourceTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        registration = patch("karak.resources._registered_resources", [])
        registration.start()
        self.addCleanup(registration.stop)

    async def test_nested_factories_share_dependencies_and_cleanup_in_reverse_order(self):
        events = []
        pools = []
        seen_services = []

        @resource
        def users(pool: ResourceContext[Pool]) -> Iterator[UserService]:
            events.append("open service")
            try:
                yield UserService(pool.value)
            finally:
                self.assertFalse(pool.value.closed)
                events.append("close service")

        @resource
        async def audit(pool: ResourceContext[Pool]) -> AuditService:
            return AuditService(pool.value)

        @resource
        async def database() -> AsyncIterator[Pool]:
            pool = Pool("shared")
            pools.append(pool)
            events.append("open pool")
            try:
                yield pool
            finally:
                pool.closed = True
                events.append("close pool")

        router = Router()

        @router.get("/")
        async def index():
            seen_services.append(users.get())
            self.assertIs(users.get().pool, audit.get().pool)
            await asyncio.sleep(0)
            return users.get().pool.name

        app = Karak(router=router)
        self.assertEqual(events, [])
        async with running(app) as state:
            first, second = await asyncio.gather(request(app, state), request(app, state))
            self.assertEqual(first[1]["body"], b"shared")
            self.assertEqual(second[1]["body"], b"shared")
            self.assertIs(seen_services[0], seen_services[1])
            self.assertEqual(len(pools), 1)
            with self.assertRaisesRegex(RuntimeError, "active application lifespan"):
                database.get()
        self.assertEqual(events, ["open pool", "open service", "close service", "close pool"])
        self.assertTrue(pools[0].closed)
        with self.assertLogs("karak.errors", level="ERROR"):
            self.assertEqual((await request(app, state))[0]["status"], 500)

    async def test_resource_handles_are_isolated_between_apps_and_lifespans(self):
        created = []

        @resource
        def database() -> Pool:
            pool = Pool(str(len(created)))
            created.append(pool)
            return pool

        router = Router()

        @router.get("/")
        async def index():
            await asyncio.sleep(0)
            return database.get().name

        first_app = Karak(router=router)
        second_app = Karak(router=router)
        async with running(first_app) as first:
            async with running(second_app) as second:
                a, b = await asyncio.gather(request(first_app, first), request(second_app, second))
                self.assertEqual(a[1]["body"], b"0")
                self.assertEqual(b[1]["body"], b"1")
                with self.assertLogs("karak.errors", level="ERROR"):
                    self.assertEqual((await request(second_app, first))[0]["status"], 500)
        async with running(first_app) as restarted:
            self.assertEqual((await request(first_app, restarted))[1]["body"], b"2")

    async def test_later_declarations_do_not_change_existing_applications(self):
        created = []

        @resource
        def database() -> Pool:
            return Pool("shared")

        first = Karak(router=Router())

        @resource
        def audit(pool: ResourceContext[Pool]) -> AuditService:
            created.append(pool.value)
            return AuditService(pool.value)

        router = Router()

        @router.get("/")
        async def index(service: ResourceContext[AuditService]):
            self.assertIs(service.value, audit.get())
            return service.value.pool.name

        second = Karak(router=router)
        async with running(first):
            self.assertEqual(created, [])
            async with running(second) as state:
                self.assertEqual((await request(second, state))[1]["body"], b"shared")
                self.assertEqual(len(created), 1)

    async def test_falsey_values_and_plain_sync_factory(self):
        @resource
        def enabled() -> bool:
            return False

        @resource
        def description(flag: ResourceContext[bool]) -> str:
            return str(flag.value)

        router = Router()

        @router.get("/")
        async def index():
            return description.get()

        app = Karak(router=router)
        async with running(app) as state:
            self.assertEqual((await request(app, state))[1]["body"], b"False")

    async def test_lifespan_hook_can_use_resources_before_they_are_cleaned_up(self):
        events = []

        @resource
        def database() -> Iterator[Pool]:
            events.append("pool setup")
            try:
                yield Pool("ready")
            finally:
                events.append("pool cleanup")

        @asynccontextmanager
        async def lifespan():
            self.assertEqual(database.get().name, "ready")
            events.append("hook setup")
            try:
                yield
            finally:
                self.assertEqual(database.get().name, "ready")
                events.append("hook cleanup")

        app = Karak(router=Router(), lifespan=lifespan)
        await lifecycle_messages(app)
        self.assertEqual(events, ["pool setup", "hook setup", "hook cleanup", "pool cleanup"])

    async def test_failed_startup_cleans_up_dependencies(self):
        closed = []

        @resource
        async def database() -> AsyncIterator[Pool]:
            try:
                yield Pool("ready")
            finally:
                closed.append(True)

        @resource
        def users(pool: ResourceContext[Pool]) -> UserService:
            raise RuntimeError("service setup failed")

        messages = await lifecycle_messages(Karak(router=Router()))
        self.assertEqual(messages, [
            {"type": "lifespan.startup.failed", "message": "service setup failed"},
        ])
        self.assertEqual(closed, [True])

    async def test_cleanup_failure_still_closes_dependencies(self):
        closed = []

        @resource
        def database() -> Iterator[Pool]:
            try:
                yield Pool("ready")
            finally:
                closed.append(True)

        @resource
        def users(pool: ResourceContext[Pool]) -> Iterator[UserService]:
            yield UserService(pool.value)
            raise RuntimeError("service cleanup failed")

        messages = await lifecycle_messages(Karak(router=Router()))
        self.assertEqual(messages[-1], {
            "type": "lifespan.shutdown.failed", "message": "service cleanup failed",
        })
        self.assertEqual(closed, [True])

    async def test_cancellation_closes_resources(self):
        closed = []

        @resource
        async def database() -> AsyncIterator[Pool]:
            try:
                yield Pool("ready")
            finally:
                closed.append(True)

        incoming = asyncio.Queue()
        outgoing = asyncio.Queue()
        app = Karak(router=Router())
        task = asyncio.create_task(app({"type": "lifespan"}, incoming.get, outgoing.put))
        try:
            await incoming.put({"type": "lifespan.startup"})
            self.assertEqual(
                (await asyncio.wait_for(outgoing.get(), timeout=2))["type"],
                "lifespan.startup.complete",
            )
        finally:
            task.cancel()
            with self.assertRaises(asyncio.CancelledError):
                await task
        self.assertEqual(closed, [True])

    def test_missing_dependency_is_rejected_before_execution(self):
        @resource
        def users(pool: ResourceContext[Pool]) -> UserService:
            self.fail("factory must not run during validation")

        with self.assertRaisesRegex(ValueError, "no registered provider"):
            Karak(router=Router())

    def test_ambiguous_type_is_rejected(self):
        @resource
        def first() -> Pool:
            return Pool("first")

        @resource
        def second() -> Pool:
            return Pool("second")

        with self.assertRaisesRegex(ValueError, "Ambiguous resource type"):
            Karak(router=Router())

    def test_cycles_are_rejected(self):
        @resource
        def database(service: ResourceContext[UserService]) -> Pool:
            return service.value.pool

        @resource
        def users(pool: ResourceContext[Pool]) -> UserService:
            return UserService(pool.value)

        with self.assertRaisesRegex(ValueError, "database -> users -> database"):
            Karak(router=Router())

    def test_invalid_annotations_are_rejected(self):
        def missing_return():
            return Pool("ready")

        def missing_context(pool: Pool) -> UserService:
            return UserService(pool)

        async def wrong_yield_type() -> Pool:
            yield Pool("ready")

        for factory, message in (
            (missing_return, "concrete return type"),
            (missing_context, r"ResourceContext\[T\]"),
            (wrong_yield_type, r"AsyncIterator\[T\]"),
        ):
            with self.subTest(factory=factory):
                with patch("karak.resources._registered_resources", []):
                    resource(factory)
                    with self.assertRaisesRegex(TypeError, message):
                        Karak(router=Router())
