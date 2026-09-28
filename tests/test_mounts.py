import unittest

from unittest.mock import patch
from uuid import UUID

from karak import BaseRouter
from karak import Karak
from karak import Mount
from karak import Response
from karak import Router
from karak.parameters import inspect_handler
from tests.test_route_validation import make_request


class MountTests(unittest.TestCase):
    def test_mount_serves_prefixed_routes_without_changing_the_child(self):
        users = Router()

        @users.get("/{user_id}")
        async def user(user_id: int):
            return str(user_id)

        mount = Mount(path="/users", router=users)
        app = Karak(routes=[mount])

        self.assertEqual(mount.path, "/users")
        self.assertIs(mount.router, users)
        self.assertEqual(make_request(app, "/users/42")[1]["body"], b"42")
        self.assertEqual(make_request(Karak(routes=[users]), "/42")[1]["body"], b"42")

    def test_nested_mounts_convert_inherited_parameters_and_preserve_query_values(self):
        received = []
        posts = Router()

        @posts.get("/{post_id}")
        async def post(
            tenant_id: UUID, user_id: int, post_id: int, preview: bool = False
        ):
            received.append((tenant_id, user_id, post_id, preview))
            return "post"

        users = Router(routes=[Mount(path="/users/{user_id}/posts", router=posts)])
        api = Router(routes=[Mount(path="/tenants/{tenant_id}", router=users)])
        app = Karak(routes=[Mount(path="/api", router=api)])
        tenant_id = UUID("12345678-1234-5678-1234-567812345678")

        response = make_request(
            app,
            f"/api/tenants/{tenant_id}/users/42/posts/7",
            b"preview=true&user_id=999&post_id=999",
        )

        self.assertEqual(response[0]["status"], 200)
        self.assertEqual(received, [(tenant_id, 42, 7, True)])

    def test_invalid_inherited_parameter_returns_422(self):
        received = []
        users = Router()

        @users.get("/profile")
        async def profile(user_id: int):
            received.append(user_id)
            return "profile"

        app = Karak(routes=[Mount(path="/users/{user_id}", router=users)])
        response = make_request(app, "/users/invalid/profile")

        self.assertEqual(response[0]["status"], 422)
        self.assertIn(b"Invalid path parameter 'user_id'", response[1]["body"])
        self.assertEqual(received, [])

    def test_app_validates_inherited_handler_contracts_during_initialization(self):
        missing = Router()

        @missing.get("/profile")
        async def profile():
            return "profile"

        with self.assertRaisesRegex(
            ValueError, "missing from handler signature: user_id"
        ):
            Karak(routes=[Mount(path="/users/{user_id}", router=missing)])

        lists = Router()

        @lists.get("/profile")
        async def profile_list(user_id: list[int]):
            return "profile"

        with self.assertRaisesRegex(TypeError, "must be a query parameter"):
            Karak(routes=[Mount(path="/users/{user_id}", router=lists)])

        repeated = Router()

        @repeated.get("/posts/{user_id}")
        async def post(user_id: int):
            return str(user_id)

        with self.assertRaisesRegex(ValueError, "Duplicate path parameter"):
            Karak(routes=[Mount(path="/users/{user_id}", router=repeated)])

    def test_app_snapshots_child_routes_while_routers_remain_editable(self):
        child = Router()

        @child.get("/first")
        async def first():
            return "first"

        original = Mount(path="/old", router=child)

        @child.get("/later")
        async def later():
            return "later"

        app = Karak(routes=[original])

        @child.get("/new")
        async def new():
            return "new"

        updated = Karak(routes=[original])

        self.assertEqual(make_request(app, "/old/first")[1]["body"], b"first")
        self.assertEqual(make_request(app, "/old/later")[1]["body"], b"later")
        self.assertEqual(make_request(app, "/old/new")[1]["body"], b"Route Not Found")
        self.assertEqual(make_request(updated, "/old/new")[1]["body"], b"new")
        self.assertEqual(
            make_request(Karak(routes=[child]), "/later")[1]["body"], b"later"
        )

    def test_nested_mounts_inspect_handlers_once_with_the_complete_path(self):
        with patch(
            "karak.routing.routes.inspect_handler", wraps=inspect_handler
        ) as inspect:
            posts = Router()

            @posts.get("/{post_id}")
            async def post(user_id: int, post_id: int):
                return f"{user_id}:{post_id}"

            users = Mount(path="/users/{user_id}/posts", router=posts)
            api = Mount(path="/api", router=users)
            definitions = list(api.flatten())
            self.assertEqual(
                definitions[0].path, "/api/users/{user_id}/posts/{post_id}"
            )
            inspect.assert_not_called()

            app = Karak(routes=[api])
            inspect.assert_called_once_with(post, {"user_id", "post_id"})
            for _ in range(2):
                self.assertEqual(
                    make_request(app, "/api/users/42/posts/7")[1]["body"], b"42:7"
                )
            inspect.assert_called_once_with(post, {"user_id", "post_id"})

    def test_mount_and_app_accept_the_base_router_contract(self):
        users = Router()

        @users.get("/{user_id}")
        async def user(user_id: int):
            return str(user_id)

        class UserRouter(BaseRouter):
            def flatten(self, prefix=""):
                yield from users.flatten(f"{prefix}/users")

        app = Karak(routes=[Mount(path="/api", router=UserRouter())])
        self.assertEqual(make_request(app, "/api/users/42")[1]["body"], b"42")

    def test_router_can_be_reused_under_different_prefixes(self):
        users = Router()

        @users.get("/profile")
        async def profile(user_id: int):
            return str(user_id)

        first = Karak(
            routes=[
                Mount(path="/v1/users/{user_id}", router=users),
                Mount(path="/v2/users/{user_id}", router=users),
            ]
        )
        second = Karak(routes=[Mount(path="/members/{user_id}", router=users)])

        for app, path in (
            (first, "/v1/users/42/profile"),
            (first, "/v2/users/42/profile"),
            (second, "/members/42/profile"),
        ):
            with self.subTest(path=path):
                self.assertEqual(make_request(app, path)[1]["body"], b"42")
        self.assertEqual(
            make_request(Karak(routes=[users]), "/profile", b"user_id=99")[1]["body"],
            b"99",
        )

    def test_path_joining_handles_root_and_trailing_slashes(self):
        cases = (
            ("/api", "/users", "/api/users"),
            ("/api/", "/users", "/api/users"),
            ("/", "/users", "/users"),
            ("/api", "", "/api"),
            ("/api", "/", "/api/"),
            ("/", "", "/"),
        )
        for prefix, suffix, expected in cases:
            with self.subTest(prefix=prefix, suffix=suffix):
                child = Router()

                @child.get(suffix)
                async def handler():
                    return "ok"

                app = Karak(routes=[Mount(path=prefix, router=child)])
                self.assertEqual(make_request(app, expected)[0]["status"], 200)

    def test_literal_prefix_and_sibling_route_matching(self):
        users = Router()

        @users.get("/a+b")
        async def user():
            return "user"

        router = Router(routes=[Mount(path="/api.v1", router=users)])

        @router.get("/health")
        async def health():
            return "healthy"

        app = Karak(routes=[router])
        self.assertEqual(make_request(app, "/api.v1/a+b")[1]["body"], b"user")
        self.assertEqual(make_request(app, "/health")[1]["body"], b"healthy")
        for path in ("/apiXv1/a+b", "/api.v1/aaab", "/api.v1extra/a+b"):
            with self.subTest(path=path):
                self.assertEqual(make_request(app, path)[1]["body"], b"Route Not Found")

    def test_mounted_get_and_post_keep_their_methods(self):
        users = Router()

        @users.post("/profile")
        async def create(user_id: int):
            return Response(status_code=201, content=f"created:{user_id}")

        @users.get("/profile")
        async def profile(user_id: int):
            return f"profile:{user_id}"

        app = Karak(routes=[Mount(path="/users/{user_id}", router=users)])
        self.assertEqual(
            make_request(app, "/users/42/profile")[1]["body"], b"profile:42"
        )
        created = make_request(app, "/users/42/profile", method="POST")
        self.assertEqual(created[0]["status"], 201)
        self.assertEqual(created[1]["body"], b"created:42")
        self.assertEqual(
            make_request(app, "/users/42/profile", method="DELETE")[0]["status"], 405
        )

    def test_mount_paths_require_a_leading_slash(self):
        for path in ("", "api"):
            with self.subTest(path=path):
                with self.assertRaisesRegex(ValueError, "must start with"):
                    Mount(path=path, router=Router())
