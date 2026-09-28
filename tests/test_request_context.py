from __future__ import annotations

import asyncio
import unittest

from typing import Any

from karak import Karak
from karak import Request
from karak import ResourceContext
from karak import Response
from karak import Router
from karak import resource
from karak.headers import Headers
from tests.test_resources import Pool
from tests.test_resources import request
from tests.test_resources import running
from tests.test_route_validation import make_request


class ContextTests(unittest.IsolatedAsyncioTestCase):
    async def test_contexts_share_one_request_and_isolate_concurrent_state(self):
        router = Router()
        seen = []

        @router.get("/users/{user_id}")
        async def user(user_id: int, ctx: ResourceContext[Request], other: ResourceContext[Request], active: bool = True):
            self.assertIs(ctx.value, other.value)
            req = ctx.value
            self.assertEqual(req.state, {})
            req.state["user"] = user_id
            seen.append(req)
            await asyncio.sleep(0)
            self.assertEqual(req.state["user"], user_id)
            self.assertEqual(req.path_params, {"user_id": str(user_id)})
            self.assertEqual(req.headers.getlist("X-TAG"), ["one", "two"])
            self.assertEqual(req.cookies, {"theme": "dark", "language": "en"})
            return f"{user_id}:{active}"

        app = Karak(router=router)

        async def call(user_id):
            messages = []
            scope = {
                "type": "http", "method": "GET", "path": f"/users/{user_id}",
                "query_string": b"active=false&ctx=untrusted",
                "headers": [(b"X-Tag", b"one"), (b"x-tag", b"two"),
                            (b"cookie", b"theme=dark"), (b"cookie", b"language=en")],
            }

            async def receive():
                return {"type": "http.request"}

            async def send(message):
                messages.append(message)

            await app(scope, receive, send)
            return messages

        results = await asyncio.gather(call(1), call(2))
        self.assertEqual([result[1]["body"] for result in results], [b"1:False", b"2:False"])
        self.assertIsNot(seen[0], seen[1])

    async def test_handler_resources_use_active_app_and_lifespan(self):
        created = []

        @resource
        def pool() -> Pool:
            value = Pool(str(len(created)))
            created.append(value)
            return value

        @resource
        def enabled() -> bool:
            return False

        router = Router()

        @router.get("/")
        async def index(db: ResourceContext[Pool], flag: ResourceContext[bool], ctx: ResourceContext[Request]):
            self.assertIs(db.value, pool.get())
            self.assertFalse(flag.value)
            self.assertEqual(ctx.value.path, "/")
            await asyncio.sleep(0)
            return db.value.name

        first = Karak(router=router, resources=[pool, enabled])
        second = Karak(router=router, resources=[pool, enabled])
        async with running(first) as first_state:
            async with running(second) as second_state:
                results = await asyncio.gather(request(first, first_state), request(second, second_state))
                self.assertEqual([result[1]["body"] for result in results], [b"0", b"1"])
                with self.assertLogs("karak.errors", level="ERROR"):
                    self.assertEqual((await request(second, first_state))[0]["status"], 500)
        with self.assertLogs("karak.errors", level="ERROR"):
            self.assertEqual((await request(first, first_state))[0]["status"], 500)

    async def test_body_is_cached_for_empty_chunked_and_concurrent_reads(self):
        for chunks, expected in (([{}], b""), ([{"body": b"ab", "more_body": True}, {"body": b"cd"}], b"abcd")):
            events = iter(chunks)
            calls = []

            async def receive():
                calls.append(True)
                await asyncio.sleep(0)
                return {"type": "http.request", **next(events)}

            req = Request({}, receive)
            self.assertEqual(await asyncio.gather(req.body(), req.body()), [expected, expected])
            self.assertEqual(await req.body(), expected)
            self.assertEqual(len(calls), len(chunks))

    async def test_disconnected_body_raises(self):
        async def receive():
            return {"type": "http.disconnect"}

        with self.assertRaisesRegex(RuntimeError, "disconnected"):
            await Request({}, receive).body()


class ContextValidationTests(unittest.TestCase):
    def test_missing_provider_and_invalid_contexts_fail_at_construction(self):
        async def missing(value: ResourceContext[Pool]): pass
        async def bare(value: ResourceContext): pass
        async def any_type(value: ResourceContext[Any]): pass
        async def default(value: ResourceContext[Request] = None): pass
        async def path(value: ResourceContext[Request]): pass
        async def positional(value: ResourceContext[Request], /): pass

        for handler, url, error, message in (
            (missing, "/", ValueError, "No registered provider"),
            (bare, "/", TypeError, "concrete type"),
            (any_type, "/", TypeError, "concrete type"),
            (default, "/", TypeError, "default"),
            (path, "/{value}", TypeError, "path parameter"),
            (positional, "/", TypeError, "keyword"),
        ):
            with self.subTest(handler=handler.__name__):
                router = Router()
                router.get(url)(handler)
                with self.assertRaisesRegex(error, message):
                    Karak(router=router)

    def test_request_cannot_be_registered_or_used_by_application_factory(self):
        @resource
        def invalid() -> Request:
            raise AssertionError("must not run")

        @resource
        def dependent(ctx: ResourceContext[Request]) -> Pool:
            raise AssertionError("must not run")

        for provider, message in ((invalid, "built-in"), (dependent, "cannot depend")):
            with self.assertRaisesRegex(ValueError, message):
                Karak(router=Router(), resources=[provider])

    def test_request_headers_are_read_only_and_preserve_raw_values(self):
        headers = Headers([(b"X-Test", b"one"), (b"x-test", b"two")])
        self.assertEqual(headers["X-TEST"], "one")
        self.assertEqual(list(headers), ["x-test"])
        self.assertEqual(len(headers), 1)
        self.assertIsNone(headers.get("missing"))
        with self.assertRaises(TypeError):
            headers["x-test"] = "changed"
        raw = headers.raw
        raw.clear()
        self.assertEqual(headers.getlist("x-test"), ["one", "two"])

    def test_response_headers_and_cookies_reach_asgi(self):
        router = Router()

        @router.get("/")
        async def index():
            response = Response(headers={"X-Test": "first"})
            response.headers.append("X-Test", "second")
            response.headers["X-Test"] = "replaced"
            response.set_cookie("theme", "dark", httponly=True, secure=True)
            response.set_cookie("language", "en")
            response.delete_cookie("old", path="/account", domain="example.com")
            return response

        messages = make_request(Karak(router=router), "/")
        headers = Headers(messages[0]["headers"])
        self.assertEqual(headers.getlist("x-test"), ["replaced"])
        cookies = headers.getlist("set-cookie")
        self.assertEqual(len(cookies), 3)
        self.assertIn("HttpOnly", cookies[0])
        self.assertIn("Secure", cookies[0])
        self.assertIn("SameSite=lax", cookies[0])
        self.assertIn("Max-Age=0", cookies[2])
        self.assertIn("Path=/account", cookies[2])
        self.assertIn("Domain=example.com", cookies[2])
        self.assertEqual(messages[1]["body"], b"")

    def test_response_rejects_header_injection_and_invalid_samesite(self):
        response = Response()
        for name, value in (("bad name", "ok"), ("x-test", "ok\r\nx-other: bad")):
            with self.assertRaises(ValueError):
                response.headers[name] = value
        with self.assertRaises(ValueError):
            response.set_cookie("theme", "dark", samesite="invalid")
        with self.assertRaises(ValueError):
            response.set_cookie("theme", "dark", path="/\r\nx-other: bad")
