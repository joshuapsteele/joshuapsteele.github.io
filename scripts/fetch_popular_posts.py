#!/usr/bin/env python3
"""
Fetch popular posts from Tinylytics API and generate data/popular.json for Hugo.

Usage:
    python3 fetch_popular_posts.py

Environment variables:
    TINYLYTICS_API_KEY: Your Tinylytics API key (required)
    TINYLYTICS_SITE_ID: Your Tinylytics site ID (optional, will be auto-detected)

The script fetches the top pages from the last 30 days and outputs them
in a format suitable for Hugo's data templates.
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

# Configuration
API_BASE = "https://tinylytics.app/api/v1"
DEFAULT_DAYS = 30
TOP_N = 10  # Fetch more than needed to filter out non-blog posts
OUTPUT_FILE = Path(__file__).parent / "data" / "popular.json"


def get_api_key():
    """Get API key from environment or fallback."""
    key = os.environ.get("TINYLYTICS_API_KEY")
    if not key:
        print("Error: TINYLYTICS_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)
    return key


def api_request(endpoint, api_key):
    """Make an authenticated API request."""
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
    except HTTPError as e:
        print(f"HTTP Error {e.code}: {e.reason}", file=sys.stderr)
        if e.code == 401:
            print("Check your API key is correct", file=sys.stderr)
        sys.exit(1)
    except URLError as e:
        print(f"URL Error: {e.reason}", file=sys.stderr)
        sys.exit(1)


def get_site_id(api_key):
    """Get the first site ID from the account."""
    site_id = os.environ.get("TINYLYTICS_SITE_ID")
    if site_id:
        return site_id

    data = api_request("/sites", api_key)
    if not data or "sites" not in data or len(data["sites"]) == 0:
        print("Error: No sites found in Tinylytics account", file=sys.stderr)
        sys.exit(1)

    return data["sites"][0]["id"]


def fetch_hits_by_path(api_key, site_id, days=DEFAULT_DAYS):
    """Fetch hits grouped by path for the last N days."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    endpoint = (
        f"/sites/{site_id}/hits"
        f"?start_date={start_date.strftime('%Y-%m-%d')}"
        f"&end_date={end_date.strftime('%Y-%m-%d')}"
        f"&grouped=true"
        f"&group_by=path"
    )

    return api_request(endpoint, api_key)


def fetch_leaderboard(api_key, site_id):
    """Fetch the all-time leaderboard (fallback if hits endpoint doesn't work well)."""
    endpoint = f"/sites/{site_id}/leaderboard"
    return api_request(endpoint, api_key)


def is_blog_post(path):
    """Check if a path is a blog post (not a page or other content)."""
    # Skip common non-blog paths
    skip_prefixes = [
        "/tags/",
        "/categories/",
        "/page/",
        "/search",
        "/about",
        "/contact",
        "/cv",
        "/now",
        "/uses",
        "/resources",
        "/blogroll",
        "/bookmarks",
        "/carry",
        "/chipotle",
        "/defaults",
        "/follow",
        "/ideas",
        "/interests",
        "/lists",
        "/nope",
        "/slashes",
        "/posse",
        "/questions",
        "/resist",
        "/save",
        "/someday",
        "/til",
        "/why",
        "/wish-list",
        "/yep",
        "/popular",
    ]

    # Skip root and empty paths
    if path in ["/", ""]:
        return False

    # Skip paths that match skip prefixes
    path_lower = path.lower().rstrip("/")
    for prefix in skip_prefixes:
        if path_lower.startswith(prefix.rstrip("/")):
            return False

    # Must be a blog post path (starts with /blog/ or is a root-level post)
    # Your site structure: /blog/post-slug/ or legacy /post-slug/
    if path_lower.startswith("/blog/"):
        return True

    # For legacy posts at root level, they should have a slug pattern
    # and not be a known page
    return True  # Be inclusive, filter by skip_prefixes


def process_hits_data(data, top_n=5):
    """Process hits data and return top blog posts."""
    posts = []

    # Handle different response formats
    if "grouped_hits" in data:
        items = data["grouped_hits"]
    elif "hits" in data:
        items = data["hits"]
    elif "data" in data:
        items = data["data"]
    else:
        items = data if isinstance(data, list) else []

    for item in items:
        path = item.get("path") or item.get("url", "")

        # Skip non-blog content
        if not is_blog_post(path):
            continue

        # Handle different field names for hit count
        hits = (
            item.get("views") or
            item.get("hit_count") or
            item.get("hits") or
            item.get("total_hits") or
            item.get("count", 0)
        )
        unique = item.get("unique_views") or item.get("unique") or item.get("unique_hits") or hits

        posts.append({
            "path": path,
            "hits": hits,
            "unique": unique,
        })

    # Sort by hits descending
    posts.sort(key=lambda x: x["hits"], reverse=True)

    return posts[:top_n]


def generate_output(posts, days):
    """Generate the output data structure."""
    return {
        "generated": datetime.now().isoformat(),
        "period_days": days,
        "posts": posts,
    }


def main():
    """Main entry point."""
    print("Fetching popular posts from Tinylytics...")

    api_key = get_api_key()
    site_id = get_site_id(api_key)

    print(f"Using site ID: {site_id}")
    print(f"Fetching data for last {DEFAULT_DAYS} days...")

    # Try hits endpoint first (more accurate for time period)
    try:
        data = fetch_hits_by_path(api_key, site_id, DEFAULT_DAYS)
        posts = process_hits_data(data, top_n=5)
    except Exception as e:
        print(f"Hits endpoint failed: {e}, trying leaderboard...", file=sys.stderr)
        data = fetch_leaderboard(api_key, site_id)
        posts = process_hits_data(data, top_n=5)

    if not posts:
        print("Warning: No blog posts found in analytics data", file=sys.stderr)
        posts = []

    # Generate output
    output = generate_output(posts, DEFAULT_DAYS)

    # Ensure data directory exists
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Write output
    with open(OUTPUT_FILE, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Generated {OUTPUT_FILE} with {len(posts)} posts")

    # Print summary
    for i, post in enumerate(posts, 1):
        print(f"  {i}. {post['path']} ({post['hits']} hits)")


if __name__ == "__main__":
    main()
