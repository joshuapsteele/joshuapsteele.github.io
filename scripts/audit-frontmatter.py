#!/usr/bin/env python3
"""
Analyze front matter across blog markdown files.

This script intentionally uses only the Python standard library so audit checks
work on a fresh checkout.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List


def split_front_matter(text: str) -> str:
    match = re.match(r"^---\s*\r?\n(.*?)\r?\n---\s*\r?\n", text, flags=re.DOTALL)
    return match.group(1) if match else ""


def parse_inline_list(raw: str) -> List[str]:
    inner = raw.strip()[1:-1]
    items: List[str] = []
    buf = ""
    in_quote = False
    quote = ""

    for ch in inner:
        if ch in {"'", '"'}:
            if in_quote and ch == quote:
                in_quote = False
            elif not in_quote:
                in_quote = True
                quote = ch
            buf += ch
            continue
        if ch == "," and not in_quote:
            item = buf.strip().strip("'\"")
            if item:
                items.append(item)
            buf = ""
            continue
        buf += ch

    item = buf.strip().strip("'\"")
    if item:
        items.append(item)
    return items


def parse_scalar(raw: str) -> Any:
    value = raw.strip()
    if value in {"", "null", "Null", "NULL", "~"}:
        return None
    if value in {"true", "True", "TRUE"}:
        return True
    if value in {"false", "False", "FALSE"}:
        return False
    if value.startswith("[") and value.endswith("]"):
        return parse_inline_list(value)
    return value.strip("'\"")


def parse_front_matter(fm: str) -> Dict[str, Any]:
    data: Dict[str, Any] = {}
    lines = fm.splitlines()
    i = 0

    while i < len(lines):
        line = lines[i]
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*?)\s*$", line)
        if not match:
            i += 1
            continue

        key = match.group(1)
        raw_value = match.group(2)
        if raw_value:
            data[key] = parse_scalar(raw_value)
            i += 1
            continue

        items: List[str] = []
        j = i + 1
        while j < len(lines):
            item_match = re.match(r"^\s*-\s+(.*?)\s*$", lines[j])
            if not item_match:
                break
            items.append(item_match.group(1).strip().strip("'\""))
            j += 1

        data[key] = items if items else None
        i = j

    return data


def as_list(value: Any) -> List[str]:
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [str(value).strip()]


def has_value(post: Dict[str, Any], field: str) -> bool:
    if field not in post:
        return False
    value = post[field]
    if isinstance(value, list):
        return len(as_list(value)) > 0
    return value is not None and str(value).strip() != ""


def analyze_frontmatter(content_dir: Path) -> Dict[str, Any]:
    results: Dict[str, Any] = {
        "total_posts": 0,
        "missing_fields": defaultdict(list),
        "field_usage": Counter(),
        "posts_by_category": defaultdict(list),
        "posts_by_tag": defaultdict(list),
        "posts_without_categories": [],
        "posts_without_tags": [],
        "posts_without_description": [],
        "posts_without_url": [],
        "date_issues": [],
        "all_categories": set(),
        "all_tags": set(),
        "author_variants": set(),
        "draft_posts": [],
        "posts_with_aliases": [],
        "field_type_issues": [],
    }

    for root, _, files in os.walk(content_dir):
        for filename in sorted(files):
            if not filename.endswith(".md") or filename == "_index.md":
                continue

            filepath = Path(root) / filename
            results["total_posts"] += 1

            try:
                text = filepath.read_text(encoding="utf-8", errors="ignore")
                post = parse_front_matter(split_front_matter(text))
                path = filepath.as_posix()

                for key in post:
                    results["field_usage"][key] += 1

                if has_value(post, "author"):
                    results["author_variants"].add(str(post["author"]))

                if post.get("draft") is True:
                    results["draft_posts"].append(path)

                if has_value(post, "aliases"):
                    results["posts_with_aliases"].append(path)

                categories = as_list(post.get("categories"))
                if not categories:
                    results["posts_without_categories"].append(path)
                for cat in categories:
                    results["all_categories"].add(cat)
                    results["posts_by_category"][cat].append(path)

                tags = as_list(post.get("tags"))
                if not tags:
                    results["posts_without_tags"].append(path)
                for tag in tags:
                    results["all_tags"].add(tag)
                    results["posts_by_tag"][tag].append(path)

                if not has_value(post, "description"):
                    results["posts_without_description"].append(path)

                if not has_value(post, "url"):
                    results["posts_without_url"].append(path)

                if not has_value(post, "date"):
                    results["date_issues"].append(f"{path}: Missing or empty date")

                for field in ["title", "date", "author", "categories", "tags", "description", "url"]:
                    if field not in post:
                        results["missing_fields"][field].append(path)

            except Exception as exc:
                results["date_issues"].append(f"{filepath.as_posix()}: Error parsing - {exc}")

    return results


def serializable(results: Dict[str, Any]) -> Dict[str, Any]:
    output = {}
    for key, value in results.items():
        if isinstance(value, defaultdict):
            output[key] = {k: sorted(v) for k, v in value.items()}
        elif isinstance(value, Counter):
            output[key] = dict(value)
        elif isinstance(value, set):
            output[key] = sorted(value)
        else:
            output[key] = value
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze Hugo blog front matter")
    parser.add_argument("--content-dir", default="content/blog", help="Directory of markdown files to audit")
    parser.add_argument("--output", default="scripts/data/audit-frontmatter.json", help="JSON output path")
    args = parser.parse_args()

    content_dir = Path(args.content_dir)
    output_path = Path(args.output)

    print(f"Analyzing front matter in {content_dir}...")
    results = analyze_frontmatter(content_dir)
    output = serializable(results)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2, default=str), encoding="utf-8")

    print("=" * 80)
    print("FRONT MATTER AUDIT SUMMARY")
    print("=" * 80)
    print(f"\nFiles analyzed: {results['total_posts']}")
    print("\nMissing critical fields:")
    print(f"   - Without categories: {len(results['posts_without_categories'])} posts")
    print(f"   - Without tags: {len(results['posts_without_tags'])} posts")
    print(f"   - Without description: {len(results['posts_without_description'])} posts")
    print(f"   - Without url: {len(results['posts_without_url'])} posts")
    print(f"   - Date issues: {len(results['date_issues'])} posts")
    print("\nTaxonomy overview:")
    print(f"   - Total unique categories: {len(output['all_categories'])}")
    print(f"   - Total unique tags: {len(output['all_tags'])}")
    print("\nField usage (top 15):")
    for field, count in results["field_usage"].most_common(15):
        pct = count / max(results["total_posts"], 1) * 100
        print(f"   - {field:<20} {count:>4} ({pct:>5.1f}%)")
    print(f"\nAuthor variants: {', '.join(output['author_variants']) or 'None'}")
    print(f"Draft posts: {len(results['draft_posts'])}")
    print(f"Posts with aliases: {len(results['posts_with_aliases'])}")
    print(f"\nAnalysis complete. Raw data: {output_path}")
    print("=" * 80)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
