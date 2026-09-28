from collections.abc import Iterable
from collections.abc import Iterator
from collections.abc import Mapping
from collections.abc import MutableMapping
import re


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
