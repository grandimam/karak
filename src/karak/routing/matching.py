import re

from enum import Enum


class Match(Enum):
    NONE = 0
    PARTIAL = 1
    FULL = 2


PARAM_RE = re.compile(r"{([a-zA-Z_][a-zA-Z0-9_]*)}")


def compile_path(path: str) -> re.Pattern:
    pattern = PARAM_RE.sub(
        lambda match: f"(?P<{match.group(1)}>[^/]+)",
        path,
    )

    return re.compile(f"^{pattern}$")
