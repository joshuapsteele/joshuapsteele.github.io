#!/usr/bin/env python3
"""
Generate data/popular.json for Hugo from Tinylytics analytics.

By default, this fetches Tinylytics API data for the last 30 days. It can also
read a manual Tinylytics CSV export, which is useful for validating or refreshing
the popular-posts data locally.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse
from urllib.request import Request, urlopen


REPO_ROOT = Path(__file__).resolve().parents[1]
API_BASE = "https://tinylytics.app/api/v1"
DEFAULT_DAYS = 30
DEFAULT_TOP_N = 10
DEFAULT_SITE_DOMAIN = "joshuapsteele.com"
DEFAULT_SITE_HOSTS = {
    "joshuapsteele.com",
    "www.joshuapsteele.com",
    "joshuapsteele.github.io",
}
OUTPUT_FILE = REPO_ROOT / "data" / "popular.json"


class TinylyticsAPIError(Exception):
    """Raised when a Tinylytics API request fails."""


def split_front_matter(text: str) -> tuple[str, str]:
    match = re.match(r"^---\s*\r?\n(.*?)\r?\n---\s*\r?\n(.*)$", text, flags=re.DOTALL)
    if not match:
        return "", text
    return match.group(1), match.group(2)


def parse_frontmatter_scalar(fm: str, key: str) -> str | None:
    match = re.search(rf"(?m)^{re.escape(key)}:\s*(.*?)\s*$", fm)
    if not match:
        return None
    value = match.group(1).strip()
    if not value or value.startswith("["):
        return None
    return value.strip("'\"")


def parse_frontmatter_list(fm: str, key: str) -> list[str]:
    match = re.search(rf"(?m)^{re.escape(key)}:\s*(.*?)\s*$", fm)
    if not match:
        return []

    value = match.group(1).strip()
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1]
        return [item.strip().strip("'\"") for item in inner.split(",") if item.strip()]

    if value:
        return [value.strip("'\"")]

    items = []
    for line in fm[match.end() :].splitlines():
        item = re.match(r"^\s*-\s+(.*?)\s*$", line)
        if not item:
            break
        items.append(item.group(1).strip().strip("'\""))
    return items


def normalize_path(raw_path: str) -> str:
    if not raw_path:
        return ""

    parsed = urlparse(raw_path)
    path = parsed.path if parsed.scheme or parsed.netloc else raw_path.split("?", 1)[0].split("#", 1)[0]
    path = "/" + path.lstrip("/")
    if path != "/" and not path.endswith("/"):
        path += "/"
    return path


def build_blog_path_map(content_dir: Path = REPO_ROOT / "content" / "blog") -> dict[str, str]:
    """Map every known blog URL variant to its canonical served URL."""
    path_map: dict[str, str] = {}

    for post_path in sorted(content_dir.glob("*.md")):
        if post_path.name == "_index.md":
            continue

        fm, _ = split_front_matter(post_path.read_text(encoding="utf-8", errors="ignore"))
        frontmatter_url = parse_frontmatter_scalar(fm, "url")
        canonical = normalize_path(frontmatter_url or f"/{post_path.stem}/")

        variants = {
            canonical,
            f"/{post_path.stem}/",
            f"/blog/{post_path.stem}/",
        }
        variants.update(normalize_path(alias) for alias in parse_frontmatter_list(fm, "aliases"))

        for variant in variants:
            if variant:
                path_map[variant] = canonical

    return path_map


def get_api_key() -> str:
    key = os.environ.get("TINYLYTICS_API_KEY")
    if not key:
        raise SystemExit("Error: TINYLYTICS_API_KEY environment variable not set")
    return key


def api_request(endpoint: str, api_key: str):
    url = f"{API_BASE}{endpoint}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
        "User-Agent": "joshuapsteele-hugo-site/1.0",
    }

    try:
        req = Request(url, headers=headers)
        with urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode())
    except HTTPError as exc:
        hint = " (check your API key is correct)" if exc.code == 401 else ""
        raise TinylyticsAPIError(f"HTTP Error {exc.code}: {exc.reason}{hint}") from exc
    except URLError as exc:
        raise TinylyticsAPIError(f"URL Error: {exc.reason}") from exc


def site_matches_domain(site: dict, domain: str) -> bool:
    needle = domain.lower()
    for key in ("domain", "host", "hostname", "name", "url"):
        value = str(site.get(key, "")).lower()
        if not value:
            continue
        parsed_host = urlparse(value).netloc.lower() if value.startswith(("http://", "https://")) else value
        if parsed_host == needle or value == needle or needle in value:
            return True
    return False


def get_site_id(api_key: str, preferred_domain: str) -> str:
    site_id = os.environ.get("TINYLYTICS_SITE_ID")
    if site_id:
        return site_id

    data = api_request("/sites", api_key)
    sites = data.get("sites", []) if isinstance(data, dict) else []
    if not sites:
        raise SystemExit("Error: No sites found in Tinylytics account")

    for site in sites:
        if site_matches_domain(site, preferred_domain):
            return str(site["id"])

    print(
        f"Warning: no Tinylytics site matched {preferred_domain}; using first returned site.",
        file=sys.stderr,
    )
    return str(sites[0]["id"])


def with_query(endpoint: str, params: dict[str, str]) -> str:
    parsed = urlparse(endpoint)
    query = dict(parse_qsl(parsed.query))
    query.update(params)
    return urlunparse(parsed._replace(query=urlencode(query)))


def fetch_paginated_items(api_key: str, endpoint: str, params: dict[str, str], per_page: int = 1000) -> list[dict]:
    """Fetch every page of a Tinylytics list endpoint and return the combined items."""
    items: list[dict] = []
    page = 1
    while True:
        page_endpoint = with_query(endpoint, {**params, "page": str(page), "per_page": str(per_page)})
        data = api_request(page_endpoint, api_key)
        page_items = extract_items(data)
        items.extend(page_items)

        pagination = data.get("pagination", {}) if isinstance(data, dict) else {}
        total_pages = parse_count(pagination.get("total_pages"))
        if not page_items or not total_pages or page >= total_pages:
            break
        page += 1
    return items


def fetch_hits_by_path(api_key: str, site_id: str, days: int) -> list[dict]:
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    return fetch_paginated_items(
        api_key,
        f"/sites/{site_id}/hits",
        {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "grouped": "true",
            "group_by": "path",
        },
    )


def fetch_leaderboard(api_key: str, site_id: str) -> list[dict]:
    return fetch_paginated_items(api_key, f"/sites/{site_id}/leaderboard", {})


def extract_items(data) -> list[dict]:
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    if not isinstance(data, dict):
        return []

    for key in ("grouped_hits", "hits", "data", "results", "leaderboard"):
        items = data.get(key)
        if isinstance(items, list):
            return [item for item in items if isinstance(item, dict)]
    return []


def parse_count(value) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        try:
            return int(float(value))
        except (TypeError, ValueError):
            return None


def item_hit_count(item: dict) -> int | None:
    for key in ("views", "hit_count", "hits", "total_hits", "count", "pageviews"):
        count = parse_count(item.get(key))
        if count is not None:
            return count
    return None


def item_unique_count(item: dict, fallback: int) -> int:
    for key in ("unique_views", "unique", "unique_hits", "visitors"):
        count = parse_count(item.get(key))
        if count is not None:
            return count
    return fallback


def should_count_row(item: dict, allowed_hosts: set[str]) -> bool:
    event = str(item.get("event", "")).strip()
    if event:
        return False

    raw_url = str(item.get("url", "")).strip()
    if raw_url:
        parsed = urlparse(raw_url)
        host = parsed.netloc.lower().rstrip(".")
        if host and allowed_hosts and host not in allowed_hosts:
            return False

    return True


def process_hits_data(data, path_map: dict[str, str], allowed_hosts: set[str], top_n: int) -> list[dict]:
    """Process API or CSV-shaped data and return top canonical blog posts."""
    totals: Counter[str] = Counter()
    unique_ids: defaultdict[str, set[str]] = defaultdict(set)
    unique_totals: Counter[str] = Counter()

    for item in extract_items(data):
        if not should_count_row(item, allowed_hosts):
            continue

        raw_path = str(item.get("path") or item.get("url") or "")
        path = normalize_path(raw_path)
        canonical = path_map.get(path)
        if not canonical:
            continue

        hit_count = item_hit_count(item)
        if hit_count is None:
            hit_count = 1

        totals[canonical] += hit_count

        unique_id = str(item.get("unique_id", "")).strip()
        if unique_id:
            unique_ids[canonical].add(unique_id)
        else:
            unique_totals[canonical] += item_unique_count(item, hit_count)

    posts = []
    for path, hits in totals.most_common():
        unique = len(unique_ids[path]) if unique_ids[path] else unique_totals[path]
        posts.append({"path": path, "hits": hits, "unique": unique or hits})

    return posts[:top_n]


def log_unmatched_diagnostics(data, path_map: dict[str, str], allowed_hosts: set[str], limit: int = 15) -> None:
    """Explain why no posts matched, to make a zero-match failure actionable."""
    items = extract_items(data)
    counted = [item for item in items if should_count_row(item, allowed_hosts)]
    print(
        f"Diagnostic: extracted {len(items)} item(s); {len(counted)} passed the event/host filter; "
        f"path_map has {len(path_map)} known blog URL variants.",
        file=sys.stderr,
    )
    if items and not counted:
        print(f"Diagnostic: allowed hosts = {sorted(allowed_hosts)}", file=sys.stderr)
    print("Diagnostic: sample of returned paths (raw -> normalized -> matched?):", file=sys.stderr)
    for item in (counted or items)[:limit]:
        raw_path = str(item.get("path") or item.get("url") or "")
        norm = normalize_path(raw_path)
        print(f"  {raw_path!r} -> {norm!r} -> {norm in path_map}", file=sys.stderr)
    print("Diagnostic: sample of known blog paths: " + ", ".join(sorted(path_map)[:5]), file=sys.stderr)


def read_csv_export(csv_path: Path, days: int) -> list[dict]:
    with csv_path.open(newline="", encoding="utf-8-sig") as file:
        rows = list(csv.DictReader(file))

    dated_rows = []
    for row in rows:
        created_at = row.get("created_at", "")
        try:
            row_date = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S %z")
        except ValueError:
            continue
        dated_rows.append((row_date, row))

    if not dated_rows:
        return rows

    end_date = max(row_date for row_date, _ in dated_rows)
    start_date = end_date - timedelta(days=days)
    return [row for row_date, row in dated_rows if start_date <= row_date <= end_date]


def generate_output(posts: list[dict], days: int, source: str) -> dict:
    return {
        "generated": datetime.now().isoformat(),
        "period_days": days,
        "source": source,
        "posts": posts,
    }


def write_output(output: dict, output_file: Path, allow_empty: bool) -> None:
    posts = output.get("posts", [])
    if not posts and not allow_empty:
        raise SystemExit(
            "Error: no matching Hugo blog posts found in Tinylytics data; "
            "leaving existing popular data untouched."
        )

    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")


def parse_allowed_hosts(value: str | None) -> set[str]:
    if not value:
        return set(DEFAULT_SITE_HOSTS)
    return {host.strip().lower().rstrip(".") for host in value.split(",") if host.strip()}


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Hugo popular-post data from Tinylytics")
    parser.add_argument("--csv", dest="csv_path", type=Path, help="Tinylytics CSV export to use instead of the API")
    parser.add_argument("--days", type=int, default=DEFAULT_DAYS, help="Number of recent days to include")
    parser.add_argument("--top-n", type=int, default=DEFAULT_TOP_N, help="Number of popular posts to write")
    parser.add_argument("--output", type=Path, default=OUTPUT_FILE, help="Output JSON path")
    parser.add_argument("--allow-empty", action="store_true", help="Allow writing an empty posts list")
    parser.add_argument(
        "--site-domain",
        default=os.environ.get("TINYLYTICS_SITE_DOMAIN", DEFAULT_SITE_DOMAIN),
        help="Preferred Tinylytics site domain for API auto-detection",
    )
    parser.add_argument(
        "--site-hosts",
        default=os.environ.get("TINYLYTICS_SITE_HOSTS"),
        help="Comma-separated hosts to count from CSV/API URL fields",
    )
    args = parser.parse_args()

    path_map = build_blog_path_map()
    allowed_hosts = parse_allowed_hosts(args.site_hosts)

    if args.csv_path:
        print(f"Reading Tinylytics CSV export: {args.csv_path}")
        raw_data = read_csv_export(args.csv_path, args.days)
        posts = process_hits_data(raw_data, path_map, allowed_hosts, args.top_n)
        source = f"csv:{args.csv_path.name}"
    else:
        print("Fetching popular posts from Tinylytics...")
        api_key = get_api_key()
        site_id = get_site_id(api_key, args.site_domain)
        print(f"Using site ID: {site_id}")
        print(f"Fetching data for last {args.days} days...")

        try:
            raw_data = fetch_hits_by_path(api_key, site_id, args.days)
            posts = process_hits_data(raw_data, path_map, allowed_hosts, args.top_n)
        except TinylyticsAPIError as exc:
            print(f"Hits endpoint failed: {exc}; trying leaderboard...", file=sys.stderr)
            raw_data = fetch_leaderboard(api_key, site_id)
            posts = process_hits_data(raw_data, path_map, allowed_hosts, args.top_n)
        source = "tinylytics-api"

    if not posts and not args.allow_empty:
        log_unmatched_diagnostics(raw_data, path_map, allowed_hosts)

    output = generate_output(posts, args.days, source)
    write_output(output, args.output, args.allow_empty)

    print(f"Generated {args.output} with {len(posts)} posts")
    for index, post in enumerate(posts, 1):
        print(f"  {index}. {post['path']} ({post['hits']} hits)")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except TinylyticsAPIError as exc:
        print(f"Tinylytics API error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
