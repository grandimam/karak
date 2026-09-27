import asyncio
import unittest

from karak import Karak
from karak import Response
from karak import Router
from tests.test_route_validation import make_request


class RouterDecoratorTests(unittest.TestCase):
    def test_get_and_post_on_the_same_path_dispatch_to_their_handlers(self):
        router = Router()

        @router.post("/users")
        async def create_user(name: str):
            return Response(status_code=201, content=f"created:{name}")

        @router.get(path="/users")
        async def list_users():
            return "users"

        app = Karak(routes=[router])
        created = make_request(app, "/users", b"name=Sam", method="POST")
        listed = make_request(app, "/users")
        rejected = make_request(app, "/users", method="DELETE")

        self.assertEqual(created[0]["status"], 201)
        self.assertEqual(created[1]["body"], b"created:Sam")
        self.assertEqual(listed[0]["status"], 200)
        self.assertEqual(listed[1]["body"], b"users")
        self.assertEqual(rejected[0]["status"], 405)

    def test_decorators_can_stack_and_preserve_the_callable_handler(self):
        router = Router()

        @router.get("/greeting")
        @router.post("/greeting")
        async def greeting(name: str = "Sam"):
            return f"Hello {name}"

        self.assertEqual(asyncio.run(greeting("Alex")), "Hello Alex")
        app = Karak(routes=[router])
        for method in ("GET", "POST"):
            with self.subTest(method=method):
                messages = make_request(app, "/greeting", method=method)
                self.assertEqual(messages[1]["body"], b"Hello Sam")

    def test_routes_can_be_registered_after_a_request(self):
        router = Router()

        @router.get("/first")
        async def first():
            return "first"

        self.assertEqual(make_request(Karak(routes=[router]), "/first")[1]["body"], b"first")

        @router.get("/later")
        async def later():
            return "later"

        self.assertEqual(make_request(Karak(routes=[router]), "/later")[1]["body"], b"later")
