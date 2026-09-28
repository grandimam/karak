from asyncio import Lock
from dataclasses import dataclass
from dataclasses import field
from functools import cached_property
from http.cookies import CookieError
from http.cookies import SimpleCookie
from typing import Any
from urllib.parse import parse_qs

from karak.headers import Headers
from karak.types import Receive
from karak.types import Scope


REQUEST_SCOPE_KEY = "karak.request"


@dataclass
class Request:
    scope: Scope
    receive: Receive
    state: dict[str, Any] = field(default_factory=dict, init=False)
    _body: bytes = field(default=b"", init=False, repr=False)
    _body_loaded: bool = field(default=False, init=False, repr=False)
    _body_lock: Lock = field(default_factory=Lock, init=False, repr=False)

    @cached_property
    def path(self) -> str:
        return self.scope["path"]

    @cached_property
    def method(self) -> str:
        return self.scope["method"]

    @property
    def path_params(self) -> dict[str, str]:
        return self.scope.get("path_params", {})

    @cached_property
    def headers(self) -> Headers:
        return Headers(self.scope.get("headers", ()))

    @cached_property
    def cookies(self) -> dict[str, str]:
        parsed: SimpleCookie = SimpleCookie()
        try:
            parsed.load("; ".join(self.headers.getlist("cookie")))
        except CookieError:
            return {}
        return {name: morsel.value for name, morsel in parsed.items()}

    @cached_property
    def params(self) -> dict[str, list[str]]:
        query_str = self.scope.get("query_string", b"")
        if isinstance(query_str, bytes):
            query_str = query_str.decode("utf-8")
        return parse_qs(query_str, keep_blank_values=True)

    async def body(self) -> bytes:
        async with self._body_lock:
            if self._body_loaded:
                return self._body
            chunks: list[bytes] = []
            while True:
                payload = await self.receive()
                if payload["type"] == "http.disconnect":
                    raise RuntimeError("HTTP connection disconnected")
                if payload["type"] == "http.request":
                    chunks.append(payload.get("body", b""))
                    if not payload.get("more_body", False):
                        break
            self._body = b"".join(chunks)
            self._body_loaded = True
            return self._body
