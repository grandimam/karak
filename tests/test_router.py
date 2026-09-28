import asyncio
import unittest

from unittest.mock import patch

from karak import Karak
from karak import Response
from karak import Router
from karak.parameters import inspect_handler
from tests.test_route_validation import make_request


class RouterDecoratorTests(unittest.TestCase):
    def test_included_routers_dispatch_in_registration_order(self):
        users = Router()
        orders = Router()
        router = Router()

        @router.get("/users/me")
        async def current_user():
            return "current user"

        @users.get("/users/{user_id}")
        async def user(user_id: int):
            return f"user:{user_id}"

        @orders.post("/orders/{order_id}")
        async def order(order_id: int):
            return f"order:{order_id}"

        router.include(users)
        router.include(orders)
        app = Karak(router=router)

        self.assertEqual(make_request(app, "/users/me")[1]["body"], b"current user")
        self.assertEqual(make_request(app, "/users/42")[1]["body"], b"user:42")
        self.assertEqual(
            make_request(app, "/orders/7", method="POST")[1]["body"], b"order:7"
        )

    def test_inclusion_snapshots_definitions_and_allows_child_reuse(self):
        child = Router()
        first = Router()
        second = Router()

        @child.get("/original")
        async def original():
            return "original"

        first.include(child)
        second.include(child)

        @child.get("/later")
        async def later():
            return "later"

        next(iter(child)).path = "/changed"
        for parent in (first, second):
            app = Karak(router=parent)
            self.assertEqual(make_request(app, "/original")[1]["body"], b"original")
            self.assertEqual(
                make_request(app, "/later")[1]["body"], b"Route Not Found"
            )

    def test_nested_and_empty_routers_can_be_included(self):
        child = Router()
        parent = Router()
        root = Router()

        @child.get("/nested")
        async def nested():
            return "nested"

        parent.include(Router())
        parent.include(child)
        root.include(parent)
        self.assertEqual(
            make_request(Karak(router=root), "/nested")[1]["body"], b"nested"
        )

    def test_duplicate_method_and_path_are_rejected_at_construction(self):
        for included in (False, True):
            with self.subTest(included=included):
                router = Router()
                other = Router() if included else router

                @router.get("/users")
                async def first():
                    return "first"

                @other.get("/users")
                async def second():
                    return "second"

                if included:
                    router.include(other)
                with self.assertRaisesRegex(ValueError, "Duplicate route: GET /users"):
                    Karak(router=router)

    def test_app_snapshots_routes_at_construction(self):
        router = Router()

        @router.get("/first")
        async def first():
            return "first"

        app = Karak(router=router)

        @router.get("/later")
        async def later():
            return "later"

        updated = Karak(router=router)
        self.assertEqual(make_request(app, "/first")[1]["body"], b"first")
        self.assertEqual(make_request(app, "/later")[1]["body"], b"Route Not Found")
        self.assertEqual(make_request(updated, "/later")[1]["body"], b"later")

    def test_full_paths_convert_parameters_and_inspect_handlers_once(self):
        with patch(
            "karak.routing.route.inspect_handler", wraps=inspect_handler
        ) as inspect:
            router = Router()

            @router.get("/api/users/{user_id}/posts/{post_id}")
            async def post(user_id: int, post_id: int, preview: bool = False):
                return f"{user_id}:{post_id}:{preview}"

            inspect.assert_not_called()
            app = Karak(router=router)
            inspect.assert_called_once_with(post, {"user_id", "post_id"})
            for _ in range(2):
                response = make_request(
                    app, "/api/users/42/posts/7", b"preview=true&user_id=999"
                )
                self.assertEqual(response[1]["body"], b"42:7:True")
            inspect.assert_called_once_with(post, {"user_id", "post_id"})

    def test_literal_paths_and_trailing_slashes_match_exactly(self):
        router = Router()

        @router.get("/")
        @router.get("/api.v1/a+b")
        @router.get("/users/")
        async def handler():
            return "ok"

        app = Karak(router=router)
        for path in ("/", "/api.v1/a+b", "/users/"):
            with self.subTest(path=path):
                self.assertEqual(make_request(app, path)[1]["body"], b"ok")
        for path in ("/apiXv1/a+b", "/api.v1/aaab", "/users"):
            with self.subTest(path=path):
                self.assertEqual(make_request(app, path)[1]["body"], b"Route Not Found")

    def test_route_paths_require_a_leading_slash(self):
        router = Router()

        async def handler():
            return "ok"

        for decorator in (router.get, router.post):
            for path in ("", "users"):
                with self.subTest(method=decorator.__name__, path=path):
                    with self.assertRaisesRegex(ValueError, "must start with"):
                        decorator(path)(handler)

    def test_duplicate_path_parameters_are_rejected_at_construction(self):
        router = Router()

        @router.get("/users/{user_id}/posts/{user_id}")
        async def post(user_id: int):
            return str(user_id)

        with self.assertRaisesRegex(ValueError, "Duplicate path parameter"):
            Karak(router=router)

    def test_get_and_post_on_the_same_path_dispatch_to_their_handlers(self):
        router = Router()

        @router.post("/users")
        async def create_user(name: str):
            return Response(status_code=201, content=f"created:{name}")

        @router.get(path="/users")
        async def list_users():
            return "users"

        app = Karak(router=router)
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
        app = Karak(router=router)
        for method in ("GET", "POST"):
            with self.subTest(method=method):
                messages = make_request(app, "/greeting", method=method)
                self.assertEqual(messages[1]["body"], b"Hello Sam")

    def test_routes_can_be_registered_after_a_request(self):
        router = Router()

        @router.get("/first")
        async def first():
            return "first"

        self.assertEqual(
            make_request(Karak(router=router), "/first")[1]["body"], b"first"
        )

        @router.get("/later")
        async def later():
            return "later"

        self.assertEqual(
            make_request(Karak(router=router), "/later")[1]["body"], b"later"
        )
