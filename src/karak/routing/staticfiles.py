import asyncio
import mimetypes
import os
import stat

from pathlib import Path

from karak.types import Receive
from karak.types import Scope
from karak.types import Send


class StaticFiles:
    """Serve a directory at /static/ without loading its contents at startup."""

    chunk_size = 64 * 1024

    def __init__(self, directory: str | Path) -> None:
        self.directory = Path(directory).resolve()
        if not self.directory.is_dir():
            raise ValueError(f"Static directory does not exist: {directory}")

    def matches(self, path: str) -> bool:
        return path == "/static" or path.startswith("/static/")

    def _open(self, path: str):
        relative = path.removeprefix("/static/")
        if path == "/static" or ".." in Path(relative).parts:
            raise FileNotFoundError(path)
        target = (self.directory / relative).resolve()
        if not target.is_relative_to(self.directory) or not target.is_file():
            raise FileNotFoundError(path)
        file = target.open("rb")
        try:
            info = os.fstat(file.fileno())
            if not stat.S_ISREG(info.st_mode):
                raise FileNotFoundError(path)
            content_type, encoding = mimetypes.guess_type(target.name)
            if encoding or not content_type:
                content_type = "application/octet-stream"
            return file, info.st_size, content_type
        except BaseException:
            file.close()
            raise

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        method = scope["method"]
        if method not in ("GET", "HEAD"):
            await self._error(send, 405, b"Method Not Allowed", method)
            return
        try:
            file, size, content_type = await asyncio.to_thread(self._open, scope["path"])
        except (OSError, ValueError, RuntimeError):
            await self._error(send, 404, b"Not Found", method)
            return

        try:
            await send({
                "type": "http.response.start",
                "status": 200,
                "headers": [
                    (b"content-type", content_type.encode("ascii")),
                    (b"content-length", str(size).encode("ascii")),
                ],
            })
            if method == "GET":
                remaining = size
                while remaining:
                    chunk = await asyncio.to_thread(
                        file.read, min(self.chunk_size, remaining)
                    )
                    if not chunk:
                        raise OSError("Static file was truncated while being served")
                    remaining -= len(chunk)
                    await send({
                        "type": "http.response.body",
                        "body": chunk,
                        "more_body": True,
                    })
            await send({"type": "http.response.body", "body": b"", "more_body": False})
        finally:
            file.close()

    async def _error(self, send: Send, status: int, body: bytes, method: str):
        headers = [
            (b"content-type", b"text/plain; charset=utf-8"),
            (b"content-length", str(len(body)).encode("ascii")),
        ]
        if status == 405:
            headers.append((b"allow", b"GET, HEAD"))
        await send({"type": "http.response.start", "status": status, "headers": headers})
        await send({
            "type": "http.response.body",
            "body": b"" if method == "HEAD" else body,
        })
