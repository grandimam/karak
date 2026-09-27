import asyncio
import unittest

from karak.application import Karak
from karak import Router


def make_request(app, path: str, query_string: bytes = b"", *, method: str = "GET"):
    messages = []

    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message):
        messages.append(message)

    scope = {
        "type": "http",
        "method": method,
        "path": path,
        "query_string": query_string,
    }
    asyncio.run(app(scope, receive, send))
    return messages


class RouteValidationTests(unittest.TestCase):
    def test_path_contract_is_checked_during_app_initialization(self):
        router = Router()

        @router.get("/users/{user_id}")
        async def user():
            return "unreachable"

        with self.assertRaisesRegex(
            ValueError,
            "Path parameters missing from handler signature: user_id",
        ):

            Karak(routes=[router])

    def test_path_and_query_parameters_are_converted(self):
        router = Router()

        @router.get("/users/{user_id}")
        async def user(user_id: int, active: bool):
            return f"{user_id}:{active}"

        app = Karak(routes=[router])
        messages = make_request(app, "/users/42", b"active=true")

        self.assertEqual(messages[0]["status"], 200)
        self.assertEqual(messages[1]["body"], b"42:True")

    def test_default_is_used_for_missing_optional_query_parameter(self):
        router = Router()

        @router.get("/users/{user_id}")
        async def user(user_id: int, page: int = 1):
            return f"{user_id}:{page}"

        app = Karak(routes=[router])
        messages = make_request(app, "/users/42")

        self.assertEqual(messages[0]["status"], 200)
        self.assertEqual(messages[1]["body"], b"42:1")

    def test_invalid_path_parameter_becomes_validation_response(self):
        router = Router()

        @router.get("/users/{user_id}")
        async def user(user_id: int):
            return str(user_id)

        app = Karak(routes=[router])
        messages = make_request(app, "/users/not-an-int")

        self.assertEqual(messages[0]["status"], 422)
        self.assertIn(b"Invalid path parameter 'user_id'", messages[1]["body"])

    def test_missing_query_parameter_becomes_validation_response(self):
        router = Router()

        @router.get("/users")
        async def users(limit: int):
            return str(limit)

        app = Karak(routes=[router])
        messages = make_request(app, "/users")

        self.assertEqual(messages[0]["status"], 422)
        self.assertIn(b"Invalid query parameter 'limit'", messages[1]["body"])

    def test_unhandled_handler_exception_becomes_internal_error(self):
        router = Router()

        @router.get("/users")
        async def users():
            raise RuntimeError("database unavailable")

        app = Karak(routes=[router])
        with self.assertLogs("karak.errors", level="ERROR"):
            messages = make_request(app, "/users")

        self.assertEqual(messages[0]["status"], 500)
        self.assertEqual(messages[1]["body"], b"Internal Server Error")


if __name__ == "__main__":
    unittest.main()
