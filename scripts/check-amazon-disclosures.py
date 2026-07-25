#!/usr/bin/env python3
"""Verify disclosure coverage for Amazon affiliate links in the built Hugo site."""

from __future__ import annotations

import re
import sys
from html import unescape
from pathlib import Path
from urllib.parse import parse_qs, urlsplit


PUBLIC_DIR = Path(__file__).resolve().parents[1] / "public"
REQUIRED_DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases."
AMAZON_HOST = r"(?:[a-z0-9-]+\.)*amazon\.com|amzn\.to|a\.co"
AMAZON_LINK_RE = re.compile(
    rf'<a\b[^>]*\bhref=(?:'
    rf'["\']https?://(?:{AMAZON_HOST})(?:[/:?][^"\']*)?["\']'
    rf'|https?://(?:{AMAZON_HOST})(?:[/:?][^\s>]*)?'
    rf')[^>]*>.*?</a>',
    re.IGNORECASE | re.DOTALL,
)
HREF_RE = re.compile(
    r'\bhref=(?:"([^"]*)"|\'([^\']*)\'|([^\s>]+))', re.IGNORECASE
)
LINK_DISCLOSURE_RE = re.compile(
    r'^\s*<span\b[^>]*\bclass=(?:["\'][^"\']*\bamazon-paid-link\b[^"\']*["\']|amazon-paid-link)[^>]*>'
    r"\s*\(paid link\)\s*</span>",
    re.IGNORECASE | re.DOTALL,
)


def is_affiliate_link(anchor_html: str) -> bool:
    match = HREF_RE.search(anchor_html)
    if not match:
        return False

    url = unescape(next(group for group in match.groups() if group is not None))
    parsed = urlsplit(url)
    hostname = (parsed.hostname or "").lower()

    if hostname in {"amzn.to", "a.co"}:
        return True

    return (hostname == "amazon.com" or hostname.endswith(".amazon.com")) and (
        "tag" in parse_qs(parsed.query)
    )


def main() -> int:
    if not PUBLIC_DIR.is_dir():
        print("Build output not found. Run `npm run build` first.", file=sys.stderr)
        return 2

    pages_with_links = 0
    amazon_links = 0
    failures: list[str] = []

    for path in sorted(PUBLIC_DIR.rglob("*.html")):
        html = path.read_text(encoding="utf-8")
        links = [
            match
            for match in AMAZON_LINK_RE.finditer(html)
            if is_affiliate_link(match.group(0))
        ]
        if not links:
            continue

        pages_with_links += 1
        amazon_links += len(links)
        relative_path = path.relative_to(PUBLIC_DIR)

        if REQUIRED_DISCLOSURE not in html:
            failures.append(f"{relative_path}: missing required Associate statement")

        for index, link in enumerate(links, start=1):
            following_html = html[link.end() :]
            if not LINK_DISCLOSURE_RE.match(following_html):
                failures.append(
                    f"{relative_path}: Amazon affiliate link {index} is missing an adjacent (paid link) disclosure"
                )

    if failures:
        print(
            f"FAIL: {len(failures)} disclosure issue(s) across "
            f"{pages_with_links} page(s) and {amazon_links} Amazon affiliate link(s):"
        )
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(
        f"PASS: {pages_with_links} page(s) with {amazon_links} Amazon affiliate link(s) "
        "have page-level and adjacent disclosures."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
