#!/usr/bin/env python3
"""Dependency-free boundary and local-link checks for Tom / Jerry Tennis."""

from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
MEDIA = {".aac", ".m4a", ".mov", ".mp3", ".mp4", ".wav"}
PRIVATE = ("/Users/", "/private/tmp/", "Personal/playground/")
CHOE_PAYLOAD = re.compile(r"(?:data/catalog\.json|vimeo-dirty-hands|saga1-episode-|saga2-saga-)", re.I)


class Links(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.values: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for name, value in attrs:
            if name in {"href", "src"} and value:
                self.values.append(value)


def target(source: Path, value: str) -> Path | None:
    parsed = urlsplit(value)
    if parsed.scheme or parsed.netloc or value.startswith(("#", "mailto:", "tel:", "data:")):
        return None
    raw = unquote(parsed.path)
    if not raw:
        return None
    found = ROOT / raw.lstrip("/") if raw.startswith("/") else source.parent / raw
    found = found.resolve()
    return found / "index.html" if found.is_dir() else found


def main() -> int:
    errors: list[str] = []
    files = [path for path in ROOT.rglob("*") if path.is_file() and ".git" not in path.parts]
    for path in files:
        rel = path.relative_to(ROOT)
        if path.suffix.lower() in MEDIA:
            errors.append(f"downloaded audio/video is not allowed: {rel}")
        if path.suffix.lower() not in {".css", ".html", ".js", ".json", ".md", ".mjs", ".py", ".txt", ".yml", ".yaml"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if path.resolve() != Path(__file__).resolve():
            for marker in PRIVATE:
                if marker in text:
                    errors.append(f"private machine path `{marker}` in {rel}")
        if rel.parts and rel.parts[0] not in {".git"} and CHOE_PAYLOAD.search(str(rel)):
            errors.append(f"David Choe archive payload crossed repository boundary: {rel}")

    for html in sorted(ROOT.rglob("*.html")):
        if ".git" in html.parts:
            continue
        parser = Links()
        parser.feed(html.read_text(encoding="utf-8"))
        for value in parser.values:
            resolved = target(html, value)
            if resolved is not None and not resolved.exists():
                errors.append(f"missing local target in {html.relative_to(ROOT)}: {value}")

    for required in (ROOT / "tennis-culture/index.html", ROOT / "tom-handoff/index.html"):
        if not required.exists():
            errors.append(f"missing owned surface: {required.relative_to(ROOT)}")

    if errors:
        print("Tom / Jerry validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Tom / Jerry validation passed: {len(files)} files checked.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
