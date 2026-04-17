#!/usr/bin/env python3
"""
Send outgoing Webmentions for recently built Hugo posts.

The deploy workflow runs this after Hugo has rendered `public/`. By default it
only sends Webmentions to explicit IndieWeb reply targets (`u-in-reply-to`) so
regular links in a post do not become surprise notifications. Pass
`--content-links` when you intentionally want to notify every linked page that
advertises a Webmention endpoint.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urljoin, urlparse, urlunparse
from urllib.request import Request, urlopen


USER_AGENT = "joshuapsteele-webmention-sender/1.0 (+https://joshuapsteele.com/)"
DEFAULT_FEEDS = ("public/notes/feed.json", "public/blog/feed.json")
DEFAULT_EXCLUDE_HOSTS = {"joshuapsteele.com", "www.joshuapsteele.com"}
MAX_RESPONSE_BYTES = 1024 * 1024


@dataclass(frozen=True)
class FeedItem:
    source_url: str
    published: datetime | None
    feed_path: Path


class OutboundLinkParser(HTMLParser):
    def __init__(self, base_url: str, include_content_links: bool):
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.include_content_links = include_content_links
        self.links: list[str] = []
        self._capture_stack: list[bool] = []
        self._capture_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = {name.lower(): value or "" for name, value in attrs}
        classes = set(attr.get("class", "").split())
        is_reply_link = tag == "a" and "u-in-reply-to" in classes
        starts_capture = False

        if self.include_content_links:
            starts_capture = bool(classes.intersection({"e-content", "reply-context"}))

        self._capture_stack.append(starts_capture)
        if starts_capture:
            self._capture_depth += 1

        if tag == "a" and attr.get("href") and (is_reply_link or self._capture_depth > 0):
            self.links.append(urljoin(self.base_url, attr["href"]))

    def handle_endtag(self, tag: str) -> None:
        if not self._capture_stack:
            return
        started_capture = self._capture_stack.pop()
        if started_capture:
            self._capture_depth = max(0, self._capture_depth - 1)


class WebmentionEndpointParser(HTMLParser):
    def __init__(self, base_url: str):
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.endpoint: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if self.endpoint or tag not in {"link", "a"}:
            return
        attr = {name.lower(): value or "" for name, value in attrs}
        rels = set(attr.get("rel", "").lower().split())
        href = attr.get("href")
        if "webmention" in rels and href:
            self.endpoint = urljoin(self.base_url, href)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--public-dir", default="public", help="Rendered Hugo output directory.")
    parser.add_argument(
        "--feed",
        action="append",
        dest="feeds",
        help="JSON Feed path to scan. Repeatable. Defaults to notes and blog feeds.",
    )
    parser.add_argument("--limit", type=int, default=5, help="Maximum items to inspect per feed.")
    parser.add_argument("--since-days", type=int, default=14, help="Ignore feed items older than this.")
    parser.add_argument("--max-targets-per-source", type=int, default=20)
    parser.add_argument("--timeout", type=int, default=10)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--content-links",
        action="store_true",
        help="Also notify normal links inside e-content, not just u-in-reply-to links.",
    )
    parser.add_argument(
        "--exclude-host",
        action="append",
        default=[],
        help="Host to skip as a target. Repeatable.",
    )
    return parser.parse_args()


def parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def load_feed_items(feed_path: Path, limit: int) -> list[FeedItem]:
    if not feed_path.exists():
        print(f"Skipping missing feed: {feed_path}", file=sys.stderr)
        return []

    with feed_path.open(encoding="utf-8") as fh:
        data = json.load(fh)

    items = data.get("items", [])
    loaded: list[FeedItem] = []
    for item in items[:limit]:
        source_url = item.get("url") or item.get("id")
        if not source_url:
            continue
        loaded.append(
            FeedItem(
                source_url=source_url,
                published=parse_datetime(item.get("date_published")),
                feed_path=feed_path,
            )
        )
    return loaded


def should_include_item(item: FeedItem, since: datetime) -> bool:
    return item.published is None or item.published >= since


def public_file_for_url(source_url: str, public_dir: Path) -> Path | None:
    parsed = urlparse(source_url)
    path = parsed.path.lstrip("/")
    if not path:
        candidates = [public_dir / "index.html"]
    elif Path(path).suffix:
        candidates = [public_dir / path]
    else:
        candidates = [public_dir / path / "index.html"]

    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def canonicalize_url(value: str) -> str | None:
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return None
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path or "/", parsed.params, parsed.query, ""))


def collect_targets(
    source_url: str,
    source_file: Path,
    include_content_links: bool,
    exclude_hosts: set[str],
    max_targets: int,
) -> list[str]:
    html = source_file.read_text(encoding="utf-8", errors="ignore")
    parser = OutboundLinkParser(source_url, include_content_links=include_content_links)
    parser.feed(html)

    source_host = urlparse(source_url).netloc.lower()
    excluded = {host.lower() for host in exclude_hosts}
    excluded.add(source_host)

    seen: set[str] = set()
    targets: list[str] = []
    for raw_url in parser.links:
        target_url = canonicalize_url(raw_url)
        if not target_url:
            continue
        host = urlparse(target_url).netloc.lower()
        if host in excluded:
            continue
        if target_url in seen:
            continue
        seen.add(target_url)
        targets.append(target_url)
        if len(targets) >= max_targets:
            break
    return targets


def read_url(url: str, timeout: int) -> tuple[str, list[str]]:
    req = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml"})
    with urlopen(req, timeout=timeout) as response:
        link_headers = response.headers.get_all("Link") or []
        body = response.read(MAX_RESPONSE_BYTES).decode("utf-8", errors="replace")
        return body, link_headers


def endpoint_from_link_header(target_url: str, headers: Iterable[str]) -> str | None:
    for header in headers:
        for part in header.split(","):
            part = part.strip()
            if not part.startswith("<") or ">" not in part:
                continue
            href, params = part[1:].split(">", 1)
            rel_match = re.search(r'rel=(?:"([^"]+)"|([^;\s]+))', params, flags=re.IGNORECASE)
            rels = set((rel_match.group(1) or rel_match.group(2) or "").lower().split()) if rel_match else set()
            if "webmention" in rels:
                return urljoin(target_url, href)
    return None


def discover_endpoint(target_url: str, timeout: int) -> str | None:
    try:
        body, link_headers = read_url(target_url, timeout)
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        print(f"  discover failed for {target_url}: {exc}", file=sys.stderr)
        return None

    endpoint = endpoint_from_link_header(target_url, link_headers)
    if endpoint:
        return endpoint

    parser = WebmentionEndpointParser(target_url)
    parser.feed(body)
    return parser.endpoint


def send_webmention(source_url: str, target_url: str, endpoint: str, timeout: int, dry_run: bool) -> bool:
    if dry_run:
        print(f"  DRY {source_url} -> {target_url} via {endpoint}")
        return True

    data = urlencode({"source": source_url, "target": target_url}).encode("utf-8")
    req = Request(
        endpoint,
        data=data,
        headers={
            "User-Agent": USER_AGENT,
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json,text/plain,*/*",
        },
        method="POST",
    )

    try:
        with urlopen(req, timeout=timeout) as response:
            print(f"  sent {response.status} {source_url} -> {target_url}")
            return 200 <= response.status < 300
    except HTTPError as exc:
        print(f"  send failed {exc.code} {source_url} -> {target_url}: {exc.reason}", file=sys.stderr)
    except (URLError, TimeoutError, OSError) as exc:
        print(f"  send failed {source_url} -> {target_url}: {exc}", file=sys.stderr)
    return False


def main() -> int:
    args = parse_args()
    public_dir = Path(args.public_dir)
    feed_paths = [Path(path) for path in (args.feeds or DEFAULT_FEEDS)]
    exclude_hosts = DEFAULT_EXCLUDE_HOSTS.union(set(args.exclude_host))
    since = datetime.now(timezone.utc) - timedelta(days=args.since_days)

    items: list[FeedItem] = []
    for feed_path in feed_paths:
        items.extend(load_feed_items(feed_path, args.limit))

    inspected = sent = skipped = 0
    seen_pairs: set[tuple[str, str]] = set()

    for item in items:
        if not should_include_item(item, since):
            skipped += 1
            continue

        source_file = public_file_for_url(item.source_url, public_dir)
        if not source_file:
            print(f"No rendered file for {item.source_url}", file=sys.stderr)
            skipped += 1
            continue

        inspected += 1
        targets = collect_targets(
            item.source_url,
            source_file,
            include_content_links=args.content_links,
            exclude_hosts=exclude_hosts,
            max_targets=args.max_targets_per_source,
        )
        if not targets:
            continue

        print(f"{item.source_url}")
        for target_url in targets:
            pair = (item.source_url, target_url)
            if pair in seen_pairs:
                continue
            seen_pairs.add(pair)

            if args.dry_run:
                print(f"  DRY {item.source_url} -> {target_url}")
                sent += 1
                continue

            endpoint = discover_endpoint(target_url, args.timeout)
            if not endpoint:
                print(f"  no endpoint for {target_url}")
                continue

            if send_webmention(item.source_url, target_url, endpoint, args.timeout, args.dry_run):
                sent += 1

    print(f"Inspected {inspected} source item(s), sent {sent} Webmention(s), skipped {skipped}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
