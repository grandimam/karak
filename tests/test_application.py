import asyncio
import unittest
from contextlib import asynccontextmanager

from karak import Karak
from karak import Response
from karak import Router
from tests.test_route_validation import make_request


class ApplicationTests(unittest.TestCase):
    def test_public_application_exports_serve_asgi_response(self):
        router = Router()

        @router.get("/")
        async def index():
            return Response(status_code=201, content=b"created")

        app = Karak(router=router)
        messages = make_request(app, "/")
        self.assertEqual(messages[0]["status"], 201)
        self.assertEqual(messages[1]["body"], b"created")

    def test_lifespan_acknowledges_startup_and_shutdown(self):
        app = Karak(router=Router())
        events = iter(
            [
                {"type": "lifespan.startup"},
                {"type": "lifespan.shutdown"},
            ]
        )
        messages = []

        async def receive():
            return next(events)

        async def send(message):
            messages.append(message)

        asyncio.run(app({"type": "lifespan"}, receive, send))
        self.assertEqual(
            messages,
            [
                {"type": "lifespan.startup.complete"},
                {"type": "lifespan.shutdown.complete"},
            ],
        )


class LifespanTests(unittest.IsolatedAsyncioTestCase):
    async def test_resources_are_available_between_startup_and_shutdown(self):
        resources = {}
        events = []
        router = Router()

        @asynccontextmanager
        async def lifespan():
            resources["greeting"] = "hello"
            events.append("setup")
            try:
                yield
            finally:
                resources.clear()
                events.append("cleanup")

        @router.get("/")
        async def index():
            return resources["greeting"]

        app = Karak(router=router, lifespan=lifespan)
        incoming = iter([
            {"type": "lifespan.startup"},
            {"type": "lifespan.shutdown"},
        ])

        async def receive():
            return next(incoming)

        async def send(message):
            events.append(message["type"])
            if message["type"] == "lifespan.startup.complete":
                responses = []

                async def receive_request():
                    return {"type": "http.request", "body": b""}

                async def send_response(response):
                    responses.append(response)

                await app(
                    {"type": "http", "method": "GET", "path": "/", "query_string": b""},
                    receive_request,
                    send_response,
                )
                self.assertEqual(responses[1]["body"], b"hello")

        await app({"type": "lifespan"}, receive, send)
        self.assertEqual(events, [
            "setup", "lifespan.startup.complete", "cleanup", "lifespan.shutdown.complete",
        ])
        self.assertEqual(resources, {})

    async def test_setup_and_cleanup_failures_are_reported(self):
        for phase in ("startup", "shutdown"):
            with self.subTest(phase=phase):
                @asynccontextmanager
                async def lifespan():
                    if phase == "startup":
                        raise RuntimeError("setup failed")
                    yield
                    raise RuntimeError("cleanup failed")

                incoming = iter([
                    {"type": "lifespan.startup"},
                    {"type": "lifespan.shutdown"},
                ])
                messages = []

                async def receive():
                    return next(incoming)

                async def send(message):
                    messages.append(message)

                app = Karak(router=Router(), lifespan=lifespan)
                await app({"type": "lifespan"}, receive, send)
                expected = [] if phase == "startup" else ["lifespan.startup.complete"]
                expected.append(f"lifespan.{phase}.failed")
                self.assertEqual([message["type"] for message in messages], expected)
                self.assertIn("failed", messages[-1]["message"])

    async def test_cancellation_runs_cleanup(self):
        started = asyncio.Event()
        closed = []

        @asynccontextmanager
        async def lifespan():
            try:
                yield
            finally:
                closed.append(True)

        incoming = asyncio.Queue()
        await incoming.put({"type": "lifespan.startup"})

        async def send(message):
            started.set()

        app = Karak(router=Router(), lifespan=lifespan)
        task = asyncio.create_task(app({"type": "lifespan"}, incoming.get, send))
        try:
            await asyncio.wait_for(started.wait(), timeout=2)
        finally:
            task.cancel()
            with self.assertRaises(asyncio.CancelledError):
                await task
        self.assertEqual(closed, [True])
