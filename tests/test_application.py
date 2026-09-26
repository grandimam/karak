import asyncio
import unittest

from karak import Karak
from karak import Response
from tests.test_route_validation import make_request


class ApplicationTests(unittest.TestCase):
    def test_public_application_exports_serve_asgi_response(self):
        app = Karak()

        @app.get(path="/", methods=["GET"])
        async def index():
            return Response(status_code=201, content=b"created")

        messages = make_request(app, "/")
        self.assertEqual(messages[0]["status"], 201)
        self.assertEqual(messages[1]["body"], b"created")

    def test_lifespan_acknowledges_startup_and_shutdown(self):
        app = Karak()
        events = iter([
            {"type": "lifespan.startup"},
            {"type": "lifespan.shutdown"},
        ])
        messages = []

        async def receive():
            return next(events)

        async def send(message):
            messages.append(message)

        asyncio.run(app({"type": "lifespan"}, receive, send))
        self.assertEqual(messages, [
            {"type": "lifespan.startup.complete"},
            {"type": "lifespan.shutdown.complete"},
        ])
