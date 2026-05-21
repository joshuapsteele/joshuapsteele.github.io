#!/usr/bin/env python3
"""
Apply taxonomy consolidation based on scripts/data/taxonomy_map.yaml.

This intentionally avoids third-party Python packages so the documented cleanup
command works on a fresh checkout.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MAP = Path(__file__).resolve().parent / "data" / "taxonomy_map.yaml"


def parse_scalar(raw: str) -> Optional[str]:
    value = raw.split("#", 1)[0].strip()
    if value in {"", "null", "None", "~"}:
        return None
    return value.strip("'\"")


def load_taxonomy_map(filename: Path = DEFAULT_MAP) -> Tuple[Dict[str, Optional[str]], Dict[str, Optional[str]]]:
    """Load category_mapping and tag_cleanup sections from the taxonomy map."""
    category_mapping: Dict[str, Optional[str]] = {}
    tag_cleanup: Dict[str, Optional[str]] = {}
    section = None

    with filename.open("r", encoding="utf-8") as f:
        for raw in f:
            line = raw.rstrip("\n")
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            if not line.startswith((" ", "\t")) and stripped.endswith(":"):
                section = stripped[:-1]
                continue

            if section not in {"category_mapping", "tag_cleanup"}:
                continue

            match = re.match(r"^\s+(.+?):\s*(.*?)\s*$", line)
            if not match:
                continue

            key = match.group(1).strip().strip("'\"")
            value = parse_scalar(match.group(2))
            if section == "category_mapping":
                category_mapping[key] = value
            else:
                tag_cleanup[key] = value

    return category_mapping, tag_cleanup


def split_front_matter(text: str) -> Tuple[str, str, str]:
    match = re.match(r"^(---\r?\n)(.*?)(\r?\n---\r?\n.*)$", text, flags=re.DOTALL)
    if not match:
        return "", "", text
    return match.group(1), match.group(2), match.group(3)


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


def parse_list_from_fm(fm: str, key: str) -> Tuple[List[str], str]:
    inline = re.search(rf"(?m)^({re.escape(key)}:\s*)(\[.*\])\s*$", fm)
    if inline:
        return parse_inline_list(inline.group(2)), "inline"

    scalar = re.search(rf"(?m)^{re.escape(key)}:[^\S\r\n]+(.+?)\s*$", fm)
    if scalar:
        return [scalar.group(1).strip().strip("'\"")], "inline"

    block = re.search(rf"(?m)^{re.escape(key)}:\s*$", fm)
    if not block:
        return [], "absent"

    items: List[str] = []
    after = fm[block.end() :]
    for line in after.splitlines():
        if line.strip() == "" and not items:
            continue
        match = re.match(r"^\s*-\s+(.*?)\s*$", line)
        if not match:
            break
        items.append(match.group(1).strip().strip("'\""))
    return items, "block"


def quote_inline(value: str) -> str:
    if re.match(r"^[A-Za-z0-9_-]+$", value):
        return value
    return '"' + value.replace('"', '\\"') + '"'


def render_list(key: str, values: List[str], style: str) -> List[str]:
    if style == "inline":
        return [f"{key}: [{', '.join(quote_inline(v) for v in values)}]\n"]
    return [f"{key}:\n", *[f"  - {value}\n" for value in values]]


def replace_list_in_fm(fm: str, key: str, values: List[str], style: str) -> str:
    lines = fm.splitlines(keepends=True)
    out: List[str] = []
    i = 0

    while i < len(lines):
        line = lines[i]
        if re.match(rf"^{re.escape(key)}:\s*(\[.*\])?\s*$", line):
            if values:
                out.extend(render_list(key, values, style))
            i += 1
            if style == "block":
                while i < len(lines) and re.match(r"^\s*-\s+", lines[i]):
                    i += 1
            continue

        out.append(line)
        i += 1

    return "".join(out)


def apply_mapping(items: List[str], mapping: Dict[str, Optional[str]]) -> List[str]:
    result: List[str] = []
    for item in items:
        mapped = mapping.get(item, item)
        if mapped and mapped not in result:
            result.append(mapped)
    return result


def apply_taxonomy(content_dir: Path, category_mapping: Dict[str, Optional[str]], tag_cleanup: Dict[str, Optional[str]], dry_run: bool = True):
    changes = []
    stats = {
        "total_files": 0,
        "files_changed": 0,
        "categories_updated": 0,
        "tags_updated": 0,
        "errors": [],
    }

    for root, _, files in os.walk(content_dir):
        for filename in files:
            if not filename.endswith(".md"):
                continue

            filepath = Path(root) / filename
            rel_path = filepath.relative_to(REPO_ROOT).as_posix()
            stats["total_files"] += 1

            try:
                text = filepath.read_text(encoding="utf-8")
                prefix, fm, suffix = split_front_matter(text)
                if not fm:
                    continue

                new_fm = fm
                file_changes = []

                old_cats, cat_style = parse_list_from_fm(new_fm, "categories")
                if old_cats:
                    new_cats = apply_mapping(old_cats, category_mapping)
                    if new_cats != old_cats:
                        new_fm = replace_list_in_fm(new_fm, "categories", new_cats, cat_style)
                        file_changes.append(("categories", old_cats, new_cats))
                        stats["categories_updated"] += 1

                old_tags, tag_style = parse_list_from_fm(new_fm, "tags")
                if old_tags and tag_cleanup:
                    new_tags = apply_mapping(old_tags, tag_cleanup)
                    if new_tags != old_tags:
                        new_fm = replace_list_in_fm(new_fm, "tags", new_tags, tag_style)
                        file_changes.append(("tags", old_tags, new_tags))
                        stats["tags_updated"] += 1

                if file_changes:
                    changes.append({"file": rel_path, "changes": file_changes})
                    stats["files_changed"] += 1
                    if not dry_run:
                        filepath.write_text(f"{prefix}{new_fm}{suffix}", encoding="utf-8")

            except Exception as exc:
                stats["errors"].append(f"{rel_path}: {exc}")

    return changes, stats


def main() -> int:
    dry_run = "--apply" not in sys.argv
    map_path = DEFAULT_MAP

    if "--map" in sys.argv:
        try:
            map_path = Path(sys.argv[sys.argv.index("--map") + 1])
        except IndexError:
            print("ERROR: --map requires a path", file=sys.stderr)
            return 2

    print("=" * 70)
    print("DRY RUN MODE - No files will be modified" if dry_run else "APPLYING TAXONOMY CHANGES")
    print("=" * 70)

    print(f"\nLoading taxonomy map: {map_path.relative_to(REPO_ROOT) if map_path.is_absolute() else map_path}")
    category_mapping, tag_cleanup = load_taxonomy_map(map_path)

    unique_targets = {value for value in category_mapping.values() if value}
    print(f"Category mappings loaded: {len(category_mapping)} -> {len(unique_targets)} target categories")
    print(f"Tag cleanup rules loaded: {len(tag_cleanup)}")

    print("\nProcessing content files...")
    changes, stats = apply_taxonomy(REPO_ROOT / "content", category_mapping, tag_cleanup, dry_run)

    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"Total files processed: {stats['total_files']}")
    print(f"Files with changes: {stats['files_changed']}")
    print(f"Categories updated: {stats['categories_updated']}")
    print(f"Tags updated: {stats['tags_updated']}")

    if stats["errors"]:
        print(f"\nErrors: {len(stats['errors'])}")
        for error in stats["errors"][:5]:
            print(f"  - {error}")

    if changes:
        print("\nChanges:")
        for change in changes[:10]:
            print(f"\n  {change['file']}:")
            for field, old, new in change["changes"]:
                print(f"    {field}: {old} -> {new}")
        if len(changes) > 10:
            print(f"\n  ... and {len(changes) - 10} more files")

    if dry_run:
        print("\nTo apply these changes, run: python3 scripts/apply-taxonomy.py --apply")
    else:
        print("\nChanges applied successfully.")

    return 1 if stats["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
