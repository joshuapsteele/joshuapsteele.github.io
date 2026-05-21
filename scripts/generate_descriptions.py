#!/usr/bin/env python3
"""
Generate simple descriptions for blog posts missing them.

Uses only the Python standard library and preserves existing front matter
formatting instead of reserializing YAML.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Dict, List, Tuple


def split_front_matter(content: str) -> Tuple[str, str, str]:
    match = re.match(r"^(---\s*\r?\n)(.*?)(\r?\n---\s*\r?\n)(.*)$", content, re.DOTALL)
    if not match:
        return "", "", "", content
    return match.group(1), match.group(2), match.group(3), match.group(4)


def parse_inline_list(raw: str) -> List[str]:
    inner = raw.strip()[1:-1]
    return [part.strip().strip("'\"") for part in inner.split(",") if part.strip()]


def get_frontmatter_value(fm: str, key: str):
    match = re.search(rf"(?m)^{re.escape(key)}:\s*(.*?)\s*$", fm)
    if not match:
        return None
    value = match.group(1).strip()
    if value.startswith("[") and value.endswith("]"):
        return parse_inline_list(value)
    if value:
        return value.strip("'\"")

    items = []
    for line in fm[match.end() :].splitlines():
        item_match = re.match(r"^\s*-\s+(.*?)\s*$", line)
        if not item_match:
            break
        items.append(item_match.group(1).strip().strip("'\""))
    return items or None


def needs_description(fm: str) -> bool:
    value = get_frontmatter_value(fm, "description")
    return value is None or str(value).strip() == ""


def extract_text_content(body: str, max_chars: int = 1000) -> str:
    text = re.sub(r"{{<.*?>}}", " ", body, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"!\[[^\]]*\]\([^\)]+\)", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"`[^`]+`", " ", text)
    text = re.sub(r"^#+\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"[*_>#-]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()[:max_chars]


def generate_simple_description(title: str, content_preview: str, categories: List[str] | None = None) -> str:
    sentences = re.split(r"(?<=[.!?])\s+", content_preview)
    parts: List[str] = []
    char_count = 0

    for sentence in sentences[:4]:
        sentence = sentence.strip().strip('"')
        if len(sentence) < 25:
            continue
        if char_count + len(sentence) + 1 > 155:
            break
        parts.append(sentence)
        char_count += len(sentence) + 1

    description = " ".join(parts).strip()
    if description and description[-1] not in ".!?":
        description += "."
    if len(description) > 160:
        description = description[:157].rstrip() + "..."
    if not description or len(description) < 30:
        category = categories[0] if categories else "blog"
        description = f"A {category} post by Joshua P. Steele."
    return description


def insert_description(fm: str, description: str) -> str:
    line = f'description: "{description.replace(chr(34), chr(39))}"\n'
    for key in ("tags", "categories", "date", "title"):
        match = re.search(rf"(?m)^{key}:\s*(.*?)\s*$", fm)
        if not match:
            continue
        insert_at = match.end() + 1
        if not match.group(1).strip():
            rest = fm[match.end() + 1 :]
            offset = 0
            for rest_line in rest.splitlines(keepends=True):
                if not re.match(r"^\s*-\s+", rest_line):
                    break
                offset += len(rest_line)
            insert_at += offset
        return fm[:insert_at] + line + fm[insert_at:]
    return fm + line


def find_posts_needing_descriptions(content_dir: Path) -> List[Path]:
    posts: List[Path] = []
    for md_file in sorted(content_dir.rglob("*.md")):
        if md_file.name == "_index.md":
            continue
        prefix, fm, suffix, _ = split_front_matter(md_file.read_text(encoding="utf-8"))
        if prefix and suffix and needs_description(fm):
            posts.append(md_file)
    return posts


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate simple descriptions for missing blog front matter")
    parser.add_argument("--content-dir", default="content/blog")
    parser.add_argument("--dry-run", action="store_true", help="Print generated descriptions without writing files")
    args = parser.parse_args()

    content_dir = Path(args.content_dir)
    posts = find_posts_needing_descriptions(content_dir)
    print(f"Found {len(posts)} posts needing descriptions")

    for index, post_path in enumerate(posts, 1):
        content = post_path.read_text(encoding="utf-8")
        prefix, fm, suffix, body = split_front_matter(content)
        title = str(get_frontmatter_value(fm, "title") or "Untitled")
        categories = get_frontmatter_value(fm, "categories")
        if isinstance(categories, str):
            categories = [categories]
        description = generate_simple_description(title, extract_text_content(body), categories)
        print(f"[{index}/{len(posts)}] {post_path}: {description}")

        if not args.dry_run:
            new_fm = insert_description(fm, description)
            post_path.write_text(f"{prefix}{new_fm}{suffix}{body}", encoding="utf-8")

    if not posts:
        print("All blog posts have descriptions.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
