from collections.abc import Mapping
from datetime import datetime
from email.utils import format_datetime
from http.cookies import SimpleCookie

from karak.request import MutableHeaders
from karak.types import Scope
from karak.types import Receive
from karak.types import Send


class Response:
    charset = "utf-8"

    def __init__(
        self,
        status_code: int = 200,
        content: str | bytes | None = None,
        *,
        headers: Mapping[str, str] | None = None,
    ):
        self._content = content
        self._status_code = status_code
        self.headers = MutableHeaders()
        self.headers.update(headers or {})

    def set_cookie(
        self,
        name: str,
        value: str = "",
        *,
        max_age: int | None = None,
        expires: datetime | str | None = None,
        path: str = "/",
        domain: str | None = None,
        secure: bool = False,
        httponly: bool = False,
        samesite: str = "lax",
    ) -> None:
        if samesite.lower() not in ("lax", "strict", "none"):
            raise ValueError("samesite must be 'lax', 'strict', or 'none'")
        cookie: SimpleCookie = SimpleCookie()
        cookie[name] = value
        morsel = cookie[name]
        if isinstance(max_age, int):
            morsel["max-age"] = max_age
        if expires:
            morsel["expires"] = (
                format_datetime(expires, usegmt=True)
                if isinstance(expires, datetime) else expires
            )
        morsel["path"] = path
        if domain:
            morsel["domain"] = domain
        morsel["secure"] = secure
        morsel["httponly"] = httponly
        morsel["samesite"] = samesite.lower()
        self.headers.append("set-cookie", morsel.OutputString())

    def delete_cookie(
        self,
        name: str,
        *,
        path: str = "/",
        domain: str | None = None,
    ) -> None:
        self.set_cookie(
            name, max_age=0, expires="Thu, 01 Jan 1970 00:00:00 GMT",
            path=path, domain=domain,
        )

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        content = self._content or b""
        if isinstance(content, str):
            content = content.encode(self.charset)
        await send({
            "type": "http.response.start", "status": self._status_code,
            "headers": self.headers.raw,
        })
        await send({"type": "http.response.body", "body": content})
