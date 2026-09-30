from asyncio import Lock
from collections.abc import Iterable
from collections.abc import Iterator
from collections.abc import Mapping
from collections.abc import MutableMapping
from dataclasses import dataclass
from dataclasses import field
from functools import cached_property
from http.cookies import CookieError
from http.cookies import SimpleCookie
from typing import Any
from urllib.parse import parse_qs
import re

from karak.types import Receive
from karak.types import Scope


REQUEST_SCOPE_KEY = "karak.request"


class Headers(Mapping[str, str]):
    """Case-insensitive headers preserving repeated fields and their order."""

    def __init__(self, raw: Iterable[tuple[bytes, bytes]] = ()) -> None:
        self._raw = [(name.lower(), value) for name, value in raw]

    @property
    def raw(self) -> list[tuple[bytes, bytes]]:
        return list(self._raw)

    def getlist(self, name: str) -> list[str]:
        key = name.lower().encode("ascii")
        return [value.decode("latin-1") for header, value in self._raw if header == key]

    def __getitem__(self, name: str) -> str:
        values = self.getlist(name)
        if not values:
            raise KeyError(name)
        return values[0]

    def __iter__(self) -> Iterator[str]:
        return iter(dict.fromkeys(name.decode("ascii") for name, _ in self._raw))

    def __len__(self) -> int:
        return len(set(name for name, _ in self._raw))


class MutableHeaders(Headers, MutableMapping[str, str]):
    @staticmethod
    def _encode(name: str, value: str) -> tuple[bytes, bytes]:
        if not re.fullmatch(r"[!#$%&'*+.^_`|~0-9A-Za-z-]+", name):
            raise ValueError("Invalid header name")
        if any(ord(character) < 32 and character != "\t" or ord(character) == 127 for character in value):
            raise ValueError("Invalid header value")
        return name.lower().encode("ascii"), value.encode("latin-1")

    def __setitem__(self, name: str, value: str) -> None:
        key, encoded = self._encode(name, value)
        self._raw = [(header, item) for header, item in self._raw if header != key]
        self._raw.append((key, encoded))

    def __delitem__(self, name: str) -> None:
        key = name.lower().encode("ascii")
        if name not in self:
            raise KeyError(name)
        self._raw = [(header, value) for header, value in self._raw if header != key]

    def append(self, name: str, value: str) -> None:
        self._raw.append(self._encode(name, value))


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
