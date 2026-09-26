"""Check built documentation assets, internal links, and search records."""

import json

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote
from urllib.parse import urlsplit


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.ids = set()
        self.links = []
        self.has_title = False
        self.has_main = False
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            self.ids.add(attrs["id"])
        if tag == "title":
            self.has_title = True
        if tag == "main":
            self.has_main = True
        if tag in {"a", "link", "script", "img"}:
            target = attrs.get("href") or attrs.get("src")
            if target:
                self.links.append(target)


def main():
    root = Path(__file__).resolve().parent / "dist"
    pages = {path.resolve(): Page(path.read_text()) for path in root.rglob("*.html")}
    errors = []

    def check_link(source, value):
        link = urlsplit(value)
        if link.scheme or link.netloc:
            return
        target = (root / unquote(link.path).lstrip("/") if link.path.startswith("/")
                  else source.parent / unquote(link.path)) if link.path else source
        if target.is_dir():
            target /= "index.html"
        target = target.resolve()
        if not target.is_relative_to(root.resolve()) or not target.exists():
            errors.append(f"{source.relative_to(root)}: missing target {value}")
        elif link.fragment and target in pages and unquote(link.fragment) not in pages[target].ids:
            errors.append(f"{source.relative_to(root)}: missing anchor {value}")

    assert root.joinpath("index.html").exists(), "Build the site first."
    for path, page in pages.items():
        if not page.has_title or not page.has_main:
            errors.append(f"{path.name}: missing title or main content")
        for link in page.links:
            check_link(path, link)
    index = json.loads(root.joinpath("search/search_index.json").read_text())
    assert index["docs"], "The search index is empty."
    for document in index["docs"]:
        check_link(root / "index.html", document["location"])
    assert not errors, "\n".join(errors)
    print(f"Checked {len(pages)} pages, local links, assets, and {len(index['docs'])} search records.")


if __name__ == "__main__":
    main()
