#!/usr/bin/env python3
"""
Migrate a Micro.Blog archive export into the Hugo /notes/ section.

Usage:
    1. In Micro.Blog, go to Account → Export and choose "Markdown archive".
       You'll get a .zip with one .md per post, each with frontmatter.
    2. Unzip it somewhere, e.g. ~/Downloads/microblog-archive/.
    3. Run this script:

        python3 migrate-microblog-archive.py \\
            --archive ~/Downloads/microblog-archive/ \\
            --hugo-repo ~/git/joshuapsteele.github.io \\
            --download-images

    4. Review the result with `git status` in the Hugo repo,
       then commit and push.

What it does:
    - Reads each Micro.Blog post and converts to the `content/notes/` shape
      the new Hugo section expects.
    - Filenames become YYYY-MM-DD-HHMM.md based on the post's original date.
    - Rewrites Micro.Blog-hosted image URLs (social.joshuapsteele.com/uploads/…)
      to local /notes/images/{filename} paths, and optionally downloads them
      into static/notes/images/.
    - Preserves original dates so Hugo's chronological ordering matches
      what's visible today at social.joshuapsteele.com.
    - Marks imported posts `syndicate: false` by default so they are visible
      on joshuapsteele.com but omitted from /notes/feed.json.
    - Idempotent: re-running skips posts that already exist in content/notes/.

Requires: Python 3.8+, `pyyaml`, `requests`.
    pip install --break-system-packages pyyaml requests
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse

try:
    import yaml
except ImportError:
    sys.exit("pyyaml not installed. Run: pip install --break-system-packages pyyaml requests")

try:
    import requests
except ImportError:
    sys.exit("requests not installed. Run: pip install --break-system-packages pyyaml requests")


IMG_URL_RE = re.compile(
    r'(?P<full>!\[[^\]]*\]\()(?P<url>https?://[^\s)]+)(?P<rest>\))',
)
HTML_IMG_RE = re.compile(
    r'<img\s+[^>]*src="(?P<url>https?://[^"]+)"[^>]*>',
    re.IGNORECASE,
)


@dataclass
class PostFrontmatter:
    title: str | None
    date: datetime
    tags: list[str]
    raw: dict


def parse_frontmatter(text: str) -> tuple[PostFrontmatter, str]:
    """Split a Micro.Blog markdown file into frontmatter + body."""
    if not text.startswith("---"):
        raise ValueError("Post missing frontmatter")
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.DOTALL)
    if not m:
        raise ValueError("Post frontmatter malformed")
    raw = yaml.safe_load(m.group(1)) or {}
    body = m.group(2).lstrip("\n")

    # Title handling: Micro.Blog often uses empty string for title-less posts.
    title = raw.get("title")
    if isinstance(title, str) and not title.strip():
        title = None

    # Date parsing: Micro.Blog emits RFC 3339 usually, but sometimes plain.
    date_val = raw.get("date")
    if isinstance(date_val, datetime):
        date = date_val
    elif isinstance(date_val, str):
        try:
            date = datetime.fromisoformat(date_val.replace("Z", "+00:00"))
        except ValueError:
            date = datetime.now(timezone.utc)
    else:
        date = datetime.now(timezone.utc)
    if date.tzinfo is None:
        date = date.replace(tzinfo=timezone.utc)

    # Tags
    tags = raw.get("tags") or raw.get("categories") or []
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",") if t.strip()]
    tags = [str(t).strip().lower().replace(" ", "-") for t in tags if t]

    return PostFrontmatter(title=title, date=date, tags=tags, raw=raw), body


def image_filename_from_url(url: str) -> str:
    """Produce a stable local filename from a remote image URL."""
    parsed = urlparse(url)
    base = Path(parsed.path).name or hashlib.sha1(url.encode()).hexdigest()[:12]
    # Prefix with a short hash so collisions across posts can't overwrite.
    if "." in base:
        stem, ext = base.rsplit(".", 1)
        stem = stem[:60]
        h = hashlib.sha1(url.encode()).hexdigest()[:8]
        return f"{stem}-{h}.{ext}"
    h = hashlib.sha1(url.encode()).hexdigest()[:8]
    return f"{base}-{h}"


def rewrite_images(body: str, images_dir: Path, download: bool) -> tuple[str, list[tuple[str, Path]]]:
    """Rewrite Micro.Blog image URLs → /notes/images/…, and collect downloads to do."""
    downloads: list[tuple[str, Path]] = []

    def _rewrite_markdown(m: re.Match[str]) -> str:
        url = m.group("url")
        if _is_own_microblog_upload(url):
            fn = image_filename_from_url(url)
            downloads.append((url, images_dir / fn))
            return f"{m.group('full')}/notes/images/{fn}{m.group('rest')}"
        return m.group(0)

    def _rewrite_html(m: re.Match[str]) -> str:
        url = m.group("url")
        if _is_own_microblog_upload(url):
            fn = image_filename_from_url(url)
            downloads.append((url, images_dir / fn))
            return m.group(0).replace(url, f"/notes/images/{fn}")
        return m.group(0)

    body = IMG_URL_RE.sub(_rewrite_markdown, body)
    body = HTML_IMG_RE.sub(_rewrite_html, body)

    if download:
        for url, dest in downloads:
            if dest.exists():
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            try:
                r = requests.get(url, timeout=30)
                r.raise_for_status()
                dest.write_bytes(r.content)
                print(f"  ↓ {url} → {dest.name}")
                time.sleep(0.1)  # be polite to Micro.Blog
            except requests.RequestException as e:
                print(f"  ✗ failed to fetch {url}: {e}", file=sys.stderr)

    return body, downloads


def _is_own_microblog_upload(url: str) -> bool:
    host = urlparse(url).netloc
    return host.endswith("social.joshuapsteele.com") or host.endswith("joshuapsteele.micro.blog")


def filename_for_post(date: datetime) -> str:
    return date.astimezone().strftime("%Y-%m-%d-%H%M") + ".md"


def render_hugo_note(fm: PostFrontmatter, body: str, syndicate: bool) -> str:
    """Emit the Hugo frontmatter + body for content/notes/*.md."""
    lines = ["---"]
    if fm.title:
        lines.append(f"title: {yaml.safe_dump(fm.title, default_flow_style=False).strip()}")
    lines.append(f"date: {fm.date.strftime('%Y-%m-%dT%H:%M:%S%z')[:-2]}:00")
    lines.append("draft: false")
    if not syndicate:
        lines.append("syndicate: false")
    tags_yaml = "[" + ", ".join(f'"{t}"' for t in fm.tags) + "]"
    lines.append(f"tags: {tags_yaml}")
    # Preserve the original Micro.Blog URL so webmentions + existing links still resolve.
    if "url" in fm.raw and isinstance(fm.raw["url"], str):
        lines.append(f"aliases: [{yaml.safe_dump(fm.raw['url'], default_flow_style=False).strip()}]")
    lines.append("---")
    lines.append("")
    lines.append(body.rstrip() + "\n")
    return "\n".join(lines)


def iter_archive_posts(archive_dir: Path) -> Iterable[Path]:
    for p in sorted(archive_dir.rglob("*.md")):
        if p.name.startswith("_"):
            continue
        yield p


def migrate(archive: Path, hugo_repo: Path, download_images: bool, dry_run: bool, syndicate: bool) -> None:
    notes_dir = hugo_repo / "content" / "notes"
    images_dir = hugo_repo / "static" / "notes" / "images"
    notes_dir.mkdir(parents=True, exist_ok=True)
    if download_images:
        images_dir.mkdir(parents=True, exist_ok=True)

    seen = {p.name for p in notes_dir.glob("*.md")}
    written = 0
    skipped = 0
    errors = 0

    for src in iter_archive_posts(archive):
        try:
            text = src.read_text(encoding="utf-8")
            fm, body = parse_frontmatter(text)
        except Exception as e:
            print(f"! {src.name}: parse error — {e}", file=sys.stderr)
            errors += 1
            continue

        body, _ = rewrite_images(body, images_dir, download=download_images and not dry_run)
        fname = filename_for_post(fm.date)

        # If collision on filename, disambiguate with a second counter.
        base_stem = fname.removesuffix(".md")
        counter = 1
        while fname in seen:
            counter += 1
            fname = f"{base_stem}-{counter}.md"

        if fname in seen:
            skipped += 1
            continue
        seen.add(fname)

        rendered = render_hugo_note(fm, body, syndicate=syndicate)
        dest = notes_dir / fname
        if dry_run:
            print(f"DRY {src.name} → content/notes/{fname}")
        else:
            dest.write_text(rendered, encoding="utf-8")
            print(f"+ {src.name} → content/notes/{fname}")
        written += 1

    print()
    print(f"Wrote   {written}")
    print(f"Skipped {skipped} (already existed)")
    print(f"Errors  {errors}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--archive", required=True, type=Path, help="Path to unzipped Micro.Blog archive")
    ap.add_argument("--hugo-repo", required=True, type=Path, help="Path to joshuapsteele.github.io repo")
    ap.add_argument("--download-images", action="store_true", help="Download Micro.Blog-hosted images into static/notes/images/")
    ap.add_argument(
        "--syndicate",
        action="store_true",
        help="Allow imported posts into /notes/feed.json. Default is to write syndicate: false.",
    )
    ap.add_argument("--dry-run", action="store_true", help="Print actions without writing files")
    args = ap.parse_args()

    if not args.archive.is_dir():
        sys.exit(f"--archive not a directory: {args.archive}")
    if not (args.hugo_repo / "hugo.yaml").is_file() and not (args.hugo_repo / "config.yaml").is_file():
        sys.exit(f"--hugo-repo does not look like a Hugo site: {args.hugo_repo}")

    migrate(args.archive, args.hugo_repo, args.download_images, args.dry_run, args.syndicate)
    return 0


if __name__ == "__main__":
    sys.exit(main())
