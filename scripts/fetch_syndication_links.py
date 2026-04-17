#!/usr/bin/env python3
"""
Fetch Micro.blog syndication links and generate data/syndication.json for Hugo.

Micro.blog cross-posts after it reads the site's feeds, so the canonical Hugo
source does not know Mastodon or Threads URLs at publish time. This script asks
Micro.blog for recent posts, finds items whose canonical URL lives on
joshuapsteele.com, and maps those URLs to their syndicated copies.
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse, urlunparse
from urllib.request import Request, urlopen


DEFAULT_SOURCE_URL = "https://micro.blog/posts/joshuapsteele"
DEFAULT_OUTPUT_FILE = Path(__file__).resolve().parent.parent / "data" / "syndication.json"
CANONICAL_HOSTS = {"joshuapsteele.com", "www.joshuapsteele.com"}
MICROBLOG_USERNAME = "joshuapsteele"


def fetch_json(url):
    req = Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "joshuapsteele-hugo-site/1.0",
        },
    )
    with urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def normalize_url(url):
    if not url:
        return ""

    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        return ""

    host = parsed.netloc.lower()
    if host.startswith("www."):
        host = host[4:]

    path = parsed.path or "/"
    if not path.endswith("/"):
        path = f"{path}/"

    return urlunparse(("https", host, path, "", "", ""))


def normalized_path(url):
    normalized = normalize_url(url)
    if not normalized:
        return ""
    return urlparse(normalized).path


def is_canonical_site_url(url):
    parsed = urlparse(url or "")
    return parsed.netloc.lower() in CANONICAL_HOSTS


def service_for_url(url):
    host = urlparse(url).netloc.lower()
    if "threads.com" in host:
        return "threads"
    if "mastodon" in host:
        return "mastodon"
    if "micro.blog" in host:
        return "microblog"
    return "other"


def microblog_url_for_item(item):
    item_id = str(item.get("id", "")).strip()
    if item_id.isdigit():
        return f"https://micro.blog/{MICROBLOG_USERNAME}/{item_id}"
    return ""


def build_entry(item):
    canonical = normalize_url(item.get("url", ""))
    links = []

    microblog_url = microblog_url_for_item(item)
    if microblog_url:
        links.append({"service": "microblog", "url": microblog_url})

    microblog = item.get("_microblog") or {}
    for url in microblog.get("syndication") or []:
        if not isinstance(url, str) or not url.startswith("http"):
            continue
        links.append({"service": service_for_url(url), "url": url})

    # Dedupe while preserving order.
    seen = set()
    deduped = []
    for link in links:
        key = (link["service"], link["url"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(link)

    entry = {
        "canonical": canonical,
        "microblog_id": str(item.get("id", "")),
        "published": item.get("date_published", ""),
        "links": deduped,
    }

    for link in deduped:
        if link["service"] != "other" and link["service"] not in entry:
            entry[link["service"]] = link["url"]

    return entry


def generate(data):
    by_path = {}
    by_url = {}

    for item in data.get("items", []):
        item_url = item.get("url", "")
        if not is_canonical_site_url(item_url):
            continue

        path = normalized_path(item_url)
        canonical = normalize_url(item_url)
        if not path or not canonical:
            continue

        entry = build_entry(item)
        by_path[path] = entry
        by_url[canonical] = entry

    return {
        "generated": datetime.now(timezone.utc).isoformat(),
        "source": DEFAULT_SOURCE_URL,
        "count": len(by_path),
        "by_path": by_path,
        "by_url": by_url,
    }


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-url", default=DEFAULT_SOURCE_URL)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_FILE)
    return parser.parse_args()


def main():
    args = parse_args()

    try:
        data = fetch_json(args.source_url)
    except HTTPError as exc:
        print(f"HTTP error fetching Micro.blog posts: {exc.code} {exc.reason}", file=sys.stderr)
        return 1
    except (URLError, TimeoutError) as exc:
        print(f"Network error fetching Micro.blog posts: {exc}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"Could not parse Micro.blog JSON: {exc}", file=sys.stderr)
        return 1

    output = generate(data)
    output["source"] = args.source_url

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2, sort_keys=True)
        handle.write("\n")

    print(f"Generated {args.output} with {output['count']} syndicated canonical post(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
