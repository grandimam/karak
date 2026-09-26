from typing import Any

from collections.abc import Awaitable
from collections.abc import Callable

Scope = dict[str, Any]
Message = dict[str, Any]

Receive = Callable[[], Awaitable[dict]]
Send = Callable[[Message], Awaitable[None]]

KarakApp = Callable[[Scope, Receive, Send], Awaitable[None]]
