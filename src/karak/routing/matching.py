import re

from enum import Enum


class Match(Enum):
    NONE = 0
    PARTIAL = 1
    FULL = 2


PARAM_RE = re.compile(r"{([a-zA-Z_][a-zA-Z0-9_]*)}")


def compile_path(path: str) -> re.Pattern:
    names = PARAM_RE.findall(path)
    if len(names) != len(set(names)):
        raise ValueError(f"Duplicate path parameter names in route: {path}")
    parts = []
    position = 0
    for match in PARAM_RE.finditer(path):
        parts.append(re.escape(path[position : match.start()]))
        parts.append(f"(?P<{match.group(1)}>[^/]+)")
        position = match.end()
    parts.append(re.escape(path[position:]))
    pattern = "".join(parts)

    return re.compile(f"^{pattern}$")
