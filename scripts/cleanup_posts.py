#!/usr/bin/env python3
"""
Cleanup Hugo blog posts front matter and content.

Actions (configurable via flags):
- Remove rank_math_* keys from front matter
- Remove cover: blocks from front matter
- Lowercase and de-duplicate tags/categories in front matter
- Strip Gutenberg embed wrappers (<figure class="wp-block-..."><div class="wp-block-embed__wrapper"> ... </div></figure>)
- Replace <span style="text-decoration:underline;">text</span> with <u>text</u>

Usage:
  python scripts/cleanup_posts.py [--write] [--limit N] [--paths path1 path2 ...]

Defaults to processing all files under content/blog when no paths are given.
Dry-run by default (prints a summary of intended changes per file). Use --write to apply.
"""

import argparse
import pathlib
import re
import sys
from typing import List, Tuple


FRONT_MATTER_DELIM = "---\n"


def split_front_matter(text: str) -> Tuple[str, str, str]:
    if not text.startswith(FRONT_MATTER_DELIM):
        return "", "", text
    # find the second delimiter
    idx = text.find(FRONT_MATTER_DELIM, len(FRONT_MATTER_DELIM))
    if idx == -1:
        # malformed front matter
        return "", "", text
    fm = text[len(FRONT_MATTER_DELIM):idx]
    content = text[idx + len(FRONT_MATTER_DELIM):]
    return FRONT_MATTER_DELIM, fm, content


def remove_rank_math(fm: str) -> Tuple[str, int]:
    # Remove any rank_math_* key lines and their nested blocks (lists, mappings, folded scalars)
    lines = fm.splitlines(keepends=True)
    out: List[str] = []
    removed = 0
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        m = re.match(r"^(\s*)rank_math_[^:]+:\s*(.*)$", line)
        if m:
            base_indent_str = m.group(1)
            base_indent = len(base_indent_str.replace("\t", "    "))
            inline_value = m.group(2).strip()
            removed += 1  # remove the key line itself
            i += 1
            # If there is no inline scalar value, skip all subsequent lines indented deeper than the key
            if not inline_value:
                while i < n:
                    nxt = lines[i]
                    if nxt.strip() == "":
                        removed += 1
                        i += 1
                        continue
                    nxt_indent = len(nxt[: len(nxt) - len(nxt.lstrip(" \t"))].replace("\t", "    "))
                    if nxt_indent > base_indent:
                        removed += 1
                        i += 1
                        continue
                    break
            else:
                # Inline scalar present; nothing nested to skip
                pass
            continue
        else:
            out.append(line)
            i += 1
    return ("".join(out), removed)


def remove_cover_block(fm: str) -> Tuple[str, int]:
    lines = fm.splitlines(keepends=True)
    out: List[str] = []
    removed = 0
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        m = re.match(r"^(\s*)cover:\s*(.*)$", line)
        if m:
            indent = len(m.group(1).replace("\t", "    "))
            removed += 1
            # If scalar on same line, just drop this line
            scalar = m.group(2).strip()
            i += 1
            if scalar:
                continue
            # Otherwise, skip following indented block (> indent)
            while i < n:
                nxt = lines[i]
                if nxt.strip() == "":
                    # blank lines within block: skip
                    removed += 1
                    i += 1
                    continue
                nxt_indent = len(nxt[: len(nxt) - len(nxt.lstrip(" \t"))].replace("\t", "    "))
                if nxt_indent > indent:
                    removed += 1
                    i += 1
                else:
                    break
            continue
        else:
            out.append(line)
            i += 1
    return ("".join(out), removed)


def _lower_list_items_inline(value: str) -> str:
    # value is like "[foo, Bar, 'Baz Qux']"
    inner = value.strip()
    if not (inner.startswith("[") and inner.endswith("]")):
        return value
    inner = inner[1:-1]
    # naive split on commas respecting simple quotes
    parts: List[str] = []
    buf = ""
    in_quote = False
    quote_char = ''
    for ch in inner:
        if ch in ("'", '"'):
            if in_quote and ch == quote_char:
                in_quote = False
            elif not in_quote:
                in_quote = True
                quote_char = ch
            buf += ch
            continue
        if ch == "," and not in_quote:
            parts.append(buf.strip())
            buf = ""
        else:
            buf += ch
    if buf.strip():
        parts.append(buf.strip())

    def normalize_token(tok: str) -> str:
        t = tok.strip()
        quoted = False
        if len(t) >= 2 and ((t[0] == '"' and t[-1] == '"') or (t[0] == "'" and t[-1] == "'")):
            quoted = True
            t = t[1:-1]
        t = t.strip().lower()
        # re-quote if it originally was quoted or contains spaces
        if quoted or (" " in t):
            return f"\"{t}\""
        return t

    lowered = [normalize_token(p) for p in parts if p]
    return "[" + ", ".join(dict.fromkeys(lowered)) + "]"  # dedupe preserving order


def normalize_tags_categories(fm: str) -> Tuple[str, int]:
    lines = fm.splitlines(keepends=True)
    out: List[str] = []
    changed = 0
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        m_block = re.match(r"^(\s*)(tags|categories):\s*$", line)
        m_inline = re.match(r"^(\s*)(tags|categories):\s*(\[.*\])\s*$", line)
        if m_inline:
            indent, key, value = m_inline.group(1), m_inline.group(2), m_inline.group(3)
            new_value = _lower_list_items_inline(value)
            if new_value != value:
                changed += 1
            out.append(f"{indent}{key}: {new_value}\n")
            i += 1
            continue
        if m_block:
            indent, key = m_block.group(1), m_block.group(2)
            i += 1
            items: List[str] = []
            # capture subsequent lines that start with '- '
            while i < n:
                nxt = lines[i]
                if nxt.strip() == "":
                    break
                if not re.match(r"^\s*-\s*", nxt):
                    break
                # extract item text after '-'
                m_item = re.match(r"^\s*-\s*(.+?)\s*$", nxt)
                if m_item:
                    val = m_item.group(1).strip()
                    # strip quotes for normalization, lower, re-quote if spaces
                    if len(val) >= 2 and ((val[0] == '"' and val[-1] == '"') or (val[0] == "'" and val[-1] == "'")):
                        val = val[1:-1]
                    val = val.strip().lower()
                    if " " in val:
                        val = f"\"{val}\""
                    items.append(val)
                i += 1
            # dedupe preserving order
            seen = set()
            unique_items: List[str] = []
            for it in items:
                if it not in seen:
                    seen.add(it)
                    unique_items.append(it)
            out.append(f"{indent}{key}:\n")
            for it in unique_items:
                out.append(f"{indent}  - {it}\n")
            changed += 1 if items else 0
            continue
        out.append(line)
        i += 1
    return ("".join(out), changed)


def cleanup_orphan_list_items(fm: str) -> Tuple[str, int]:
    # Remove top-level list items that are not immediately under a list key
    allowed_list_keys = {"tags", "categories", "aliases", "series", "mf2_syndication"}
    lines = fm.splitlines(keepends=True)
    out: List[str] = []
    removed = 0
    prev_key_line: str = ""
    for line in lines:
        if re.match(r"^\s*[A-Za-z0-9_\-]+:\s*(\[.*\])?\s*$", line):
            # a key line (may be inline list or scalar)
            out.append(line)
            # Remember the key name (without value)
            key_match = re.match(r"^\s*([A-Za-z0-9_\-]+):", line)
            prev_key_line = key_match.group(1).lower() if key_match else ""
            continue
        if re.match(r"^\s*-\s+.+", line):
            if prev_key_line in allowed_list_keys:
                out.append(line)
            else:
                removed += 1
            continue
        # reset key context on other lines
        prev_key_line = prev_key_line if line.strip() == "" else ""
        out.append(line)
    return ("".join(out), removed)


def clean_mf2_syndication(fm: str) -> Tuple[str, int]:
    # Keep only valid http(s) URLs in mf2_syndication. Remove key if empty.
    lines = fm.splitlines(keepends=True)
    out: List[str] = []
    changed = 0
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        m_block = re.match(r"^(\s*)mf2_syndication:\s*$", line)
        m_inline = re.match(r"^(\s*)mf2_syndication:\s*(\[.*\])\s*$", line)
        if m_inline:
            indent, value = m_inline.group(1), m_inline.group(2)
            # Extract inline list items and filter to URLs
            items_str = value.strip()[1:-1]
            items = [p.strip().strip('"\'') for p in items_str.split(',')] if items_str else []
            kept: List[str] = []
            for it in items:
                if re.match(r"^https?://\S+$", it):
                    kept.append(it)
            if kept:
                changed += 1 if len(kept) != len(items) else 0
                pretty = ", ".join([f"\"{k}\"" for k in kept])
                out.append(f"{indent}mf2_syndication: [{pretty}]\n")
            else:
                # drop entire key
                changed += 1
            i += 1
            continue
        if m_block:
            indent = m_block.group(1)
            i += 1
            kept_urls: List[str] = []
            start_i = i
            while i < n:
                nxt = lines[i]
                if not re.match(r"^\s*-\s*", nxt):
                    break
                m_item = re.match(r"^\s*-\s*(.+?)\s*$", nxt)
                if m_item:
                    val = m_item.group(1).strip()
                    val = val.strip('"\'')
                    if re.match(r"^https?://\S+$", val):
                        kept_urls.append(val)
                i += 1
            if kept_urls:
                out.append(f"{indent}mf2_syndication:\n")
                for url in kept_urls:
                    out.append(f"{indent}  - \"{url}\"\n")
                changed += 1  # rewritten
            else:
                changed += 1  # removed
            continue
        out.append(line)
        i += 1
    return ("".join(out), changed)


RE_FIGURE_EMBED = re.compile(
    r"<figure\s+class=\"wp-block-[^\"]*\"[^>]*>\s*<div\s+class=\"wp-block-embed__wrapper\"[^>]*>(.*?)</div>\s*</figure>",
    re.IGNORECASE | re.DOTALL,
)

RE_SPAN_UNDERLINE = re.compile(
    r"<span\s+style=\"[^\"]*text-decoration\s*:\s*underline;?[^\"]*\">(.*?)</span>",
    re.IGNORECASE | re.DOTALL,
)


def cleanup_content(content: str) -> Tuple[str, int]:
    changed = 0
    def repl_embed(m):
        nonlocal changed
        changed += 1
        return m.group(1)

    content2 = RE_FIGURE_EMBED.sub(repl_embed, content)
    content3, n2 = RE_SPAN_UNDERLINE.subn(r"<u>\1</u>", content2)
    changed += n2
    return content3, changed


def process_file(path: pathlib.Path, write: bool = False) -> Tuple[int, List[str]]:
    text = path.read_text(encoding="utf-8")
    delim, fm, content = split_front_matter(text)
    changes: List[str] = []
    fm_changed_total = 0
    content_changed_total = 0

    if fm:
        new_fm = fm
        new_fm, removed_rank = remove_rank_math(new_fm)
        if removed_rank:
            fm_changed_total += removed_rank
            changes.append(f"front-matter: removed {removed_rank} rank_math_* keys")

        # Clean any orphaned list items that may remain after removing rank_math keys
        new_fm, removed_orphans = cleanup_orphan_list_items(new_fm)
        if removed_orphans:
            fm_changed_total += removed_orphans
            changes.append("front-matter: removed orphan list items")

        new_fm, removed_cover = remove_cover_block(new_fm)
        if removed_cover:
            fm_changed_total += removed_cover
            changes.append("front-matter: removed cover block")

        new_fm, normalized_tc = normalize_tags_categories(new_fm)
        if normalized_tc:
            fm_changed_total += normalized_tc
            changes.append("front-matter: normalized tags/categories")

        new_fm, cleaned_mf2 = clean_mf2_syndication(new_fm)
        if cleaned_mf2:
            fm_changed_total += cleaned_mf2
            changes.append("front-matter: cleaned mf2_syndication")
    else:
        new_fm = fm

    new_content, content_changes = cleanup_content(content)
    if content_changes:
        content_changed_total += content_changes
        changes.append(f"content: cleaned {content_changes} HTML wrapper(s)/underline span(s)")

    if not changes:
        return 0, []

    new_text = text
    if fm:
        new_text = f"{delim}{new_fm}{delim}{new_content}"
    else:
        new_text = new_content

    if write:
        path.write_text(new_text, encoding="utf-8")
    return 1, changes


def iter_target_files(paths: List[str], limit: int) -> List[pathlib.Path]:
    files: List[pathlib.Path] = []
    if paths:
        for p in paths:
            path = pathlib.Path(p)
            if path.is_dir():
                files.extend(sorted(path.rglob("*.md")))
            elif path.is_file() and path.suffix == ".md":
                files.append(path)
    else:
        base = pathlib.Path("content/blog")
        files = sorted(base.rglob("*.md"))
    if limit > 0:
        return files[:limit]
    return files


def main():
    parser = argparse.ArgumentParser(description="Cleanup Hugo blog posts.")
    parser.add_argument("--write", action="store_true", help="Apply changes (default is dry-run)")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of files processed")
    parser.add_argument("--paths", nargs="*", help="Specific file or directory paths to process")
    args = parser.parse_args()

    files = iter_target_files(args.paths or [], args.limit)
    total = 0
    changed_files = 0
    for f in files:
        total += 1
        changed, changes = process_file(f, write=args.write)
        if changed:
            changed_files += 1
            print(f"- {f}: " + "; ".join(changes))

    print(f"Processed {total} file(s). {changed_files} file(s) would be changed." + (" (applied)" if args.write else ""))


if __name__ == "__main__":
    sys.exit(main())
