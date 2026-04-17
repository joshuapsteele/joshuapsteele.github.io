#!/usr/bin/env python3
"""Check conversation sources for a joshuapsteele.com page.

This mirrors the client-side sources used by layouts/partials/webmention_display.html.
It is intentionally read-only and safe to run against any public page URL.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Optional


SOURCES = (
    (
        "webmention.io",
        "https://webmention.io/api/mentions.jf2?target={target}&per-page=50",
    ),
    (
        "micro.blog",
        "https://micro.blog/webmention?target={target}&format=jf2",
    ),
)


@dataclass
class SourceResult:
    name: str
    status: Optional[int]
    ok: bool
    count: int
    note: str = ""


def fetch_json(url: str) -> tuple[int, dict]:
    request = urllib.request.Request(url, headers={"User-Agent": "joshuapsteele.com-conversation-check/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            body = response.read().decode("utf-8")
            return response.status, json.loads(body)
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        if error.code == 404 and "Post not found" in body:
            return error.code, {"type": "feed", "children": [], "_not_found": True}
        raise


def count_mentions(data: dict) -> int:
    children = data.get("children")
    if isinstance(children, list):
        return len(children)
    items = data.get("items")
    if isinstance(items, list):
        return len(items)
    return 0


def check_source(name: str, template: str, target_url: str) -> SourceResult:
    encoded = urllib.parse.quote(target_url, safe="")
    url = template.format(target=encoded)

    try:
        status, data = fetch_json(url)
    except Exception as error:  # noqa: BLE001 - command-line diagnostic should report any failure.
        return SourceResult(name=name, status=None, ok=False, count=0, note=str(error))

    if data.get("_not_found"):
        return SourceResult(
            name=name,
            status=status,
            ok=True,
            count=0,
            note="no Micro.blog conversation for this URL yet",
        )

    return SourceResult(name=name, status=status, ok=True, count=count_mentions(data))


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Webmention.io and Micro.blog conversation sources.")
    parser.add_argument("url", help="Canonical post/note URL to test")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    args = parser.parse_args()

    results = [check_source(name, template, args.url) for name, template in SOURCES]

    if args.json:
        print(json.dumps([result.__dict__ for result in results], indent=2, sort_keys=True))
        return 0 if all(result.ok for result in results) else 1

    print(f"Conversation source check for {args.url}")
    print()
    for result in results:
        status = result.status if result.status is not None else "error"
        state = "ok" if result.ok else "failed"
        line = f"- {result.name}: {state}, status {status}, {result.count} item(s)"
        if result.note:
            line += f" ({result.note})"
        print(line)

    total = sum(result.count for result in results if result.ok)
    print()
    print(f"Total raw source items: {total}")

    if not all(result.ok for result in results):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
