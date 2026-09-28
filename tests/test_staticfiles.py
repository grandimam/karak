import asyncio
import unittest

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from karak import Karak
from karak import Router
from karak.routing.staticfiles import StaticFiles
from tests.test_route_validation import make_request


class StaticFilesTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.directory = self.root / "static"
        self.directory.mkdir()
        self.router = Router()
        self.app = Karak(router=self.router, static_dir=self.directory)

    def body(self, messages):
        return b"".join(message["body"] for message in messages[1:])

    def test_reads_nested_files_on_request_and_sends_headers(self):
        nested = self.directory / "css"
        nested.mkdir()
        path = nested / "style.css"
        path.write_bytes(b"body {}")
        response = make_request(self.app, "/static/css/style.css")
        self.assertEqual(response[0]["status"], 200)
        headers = dict(response[0]["headers"])
        self.assertEqual(headers[b"content-type"], b"text/css")
        self.assertEqual(headers[b"content-length"], b"7")
        self.assertEqual(self.body(response), b"body {}")
        path.write_bytes(b"updated")
        self.assertEqual(
            self.body(make_request(self.app, "/static/css/style.css")), b"updated"
        )
        path.unlink()
        self.assertEqual(make_request(self.app, "/static/css/style.css")[0]["status"], 404)

    def test_streams_large_and_empty_files(self):
        for content in (b"", b"x" * (StaticFiles.chunk_size * 2 + 3)):
            with self.subTest(size=len(content)):
                (self.directory / "file.bin").write_bytes(content)
                response = make_request(self.app, "/static/file.bin")
                self.assertEqual(self.body(response), content)
                self.assertFalse(response[-1]["more_body"])
                for message in response[1:]:
                    self.assertLessEqual(len(message["body"]), StaticFiles.chunk_size)

    def test_head_sends_headers_without_reading_body(self):
        (self.directory / "file.txt").write_bytes(b"hello")
        opened = (self.directory / "file.txt").open("rb")
        with patch.object(StaticFiles, "_open", return_value=(opened, 5, "text/plain")):
            with patch.object(opened, "read", side_effect=AssertionError("body read")):
                response = make_request(self.app, "/static/file.txt", method="HEAD")
        self.assertTrue(opened.closed)
        self.assertEqual(response[0]["status"], 200)
        self.assertEqual(dict(response[0]["headers"])[b"content-length"], b"5")
        self.assertEqual(self.body(response), b"")

    def test_rejects_missing_files_directories_and_directory_escape(self):
        (self.root / "secret.txt").write_text("secret")
        (self.directory / "outside").symlink_to(self.root, target_is_directory=True)
        (self.directory / "folder").mkdir()
        for path in (
            "/static", "/static/", "/static/missing", "/static/folder",
            "/static/../secret.txt", "/static/outside/secret.txt",
            "/static//etc/passwd", "/static/bad\x00name",
        ):
            with self.subTest(path=path):
                self.assertEqual(make_request(self.app, path)[0]["status"], 404)

    def test_static_prefix_takes_priority_and_does_not_fall_through(self):
        @self.router.get("/{category}/{name}")
        async def fallback(category: str, name: str):
            return "decorated"

        app = Karak(router=self.router, static_dir=self.directory)
        self.assertEqual(make_request(app, "/static/missing")[0]["status"], 404)
        self.assertEqual(
            self.body(make_request(app, "/staticish/file.png")), b"decorated"
        )
        disabled = Karak(router=self.router)
        self.assertEqual(self.body(make_request(disabled, "/static/file.png")), b"decorated")

    def test_only_get_and_head_are_allowed(self):
        response = make_request(self.app, "/static/file.txt", method="POST")
        self.assertEqual(response[0]["status"], 405)
        self.assertEqual(dict(response[0]["headers"])[b"allow"], b"GET, HEAD")
        missing = make_request(self.app, "/static/missing", method="HEAD")
        self.assertEqual(missing[0]["status"], 404)
        self.assertEqual(self.body(missing), b"")

    def test_invalid_directory_fails_at_startup(self):
        with self.assertRaisesRegex(ValueError, "Static directory"):
            Karak(router=self.router, static_dir=self.root / "missing")
        file = self.root / "file"
        file.write_text("not a directory")
        with self.assertRaisesRegex(ValueError, "Static directory"):
            Karak(router=self.router, static_dir=file)

    def test_send_failure_closes_file_without_starting_another_response(self):
        path = self.directory / "file.txt"
        path.write_bytes(b"hello")
        opened = path.open("rb")
        messages = []

        async def receive():
            return {"type": "http.request"}

        async def send(message):
            messages.append(message)
            if message["type"] == "http.response.body":
                raise OSError("connection closed")

        with patch.object(StaticFiles, "_open", return_value=(opened, 5, "text/plain")):
            with self.assertRaisesRegex(OSError, "connection closed"):
                asyncio.run(self.app(
                    {"type": "http", "method": "GET", "path": "/static/file.txt"},
                    receive,
                    send,
                ))
        self.assertTrue(opened.closed)
        self.assertEqual(
            [message["status"] for message in messages if "status" in message], [200]
        )
