#!/usr/bin/env python3
"""
Taxonomy tools for Hugo posts (tags/categories).

Commands:
- inventory: list all unique tags and categories with counts
- apply-map: apply a consolidation mapping from taxonomy_map.yaml

Mapping file format (no external deps required):

tags:
  old-term: new-term
  "Old With Spaces": "new with spaces"
categories:
  old-cat: new-cat

Usage examples:
  python scripts/taxonomy_tools.py inventory
  python scripts/taxonomy_tools.py apply-map taxonomy_map.yaml  # dry-run
  python scripts/taxonomy_tools.py apply-map taxonomy_map.yaml --write

Notes:
- Preserves url/aliases/guid/id.
- Dedupes and lowercases results after mapping.
- Writes block-style lists for consistency.
"""

import argparse
import collections
import pathlib
import re
import sys
from typing import Dict, List, Tuple


FRONT_MATTER_DELIM = "---\n"


def split_front_matter(text: str) -> Tuple[str, str, str]:
    # Support both LF and CRLF newlines for YAML front matter
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n(.*)$", text, flags=re.DOTALL)
    if not m:
        return "", "", text
    fm = m.group(1)
    content = m.group(2)
    return FRONT_MATTER_DELIM, fm, content


def parse_list_from_fm(fm: str, key: str) -> Tuple[List[str], str]:
    # Returns (items, style) where style is 'block'|'inline'|'absent'
    items: List[str] = []
    style = 'absent'
    # inline
    m_inline = re.search(rf"(?m)^\s*{re.escape(key)}:\s*(\[.*\])\s*$", fm)
    if m_inline:
        style = 'inline'
        raw = m_inline.group(1).strip()[1:-1]
        if raw.strip():
            parts = []
            buf = ""
            in_quote = False
            quote = ''
            for ch in raw:
                if ch in ('"', "'"):
                    if in_quote and ch == quote:
                        in_quote = False
                    elif not in_quote:
                        in_quote = True
                        quote = ch
                    buf += ch
                    continue
                if ch == ',' and not in_quote:
                    parts.append(buf.strip())
                    buf = ""
                else:
                    buf += ch
            if buf.strip():
                parts.append(buf.strip())
            for p in parts:
                t = p.strip().strip('"\'')
                if t:
                    items.append(t)
        return items, style
    # block
    m_block = re.search(rf"(?m)^\s*{re.escape(key)}:\s*$", fm)
    if m_block:
        style = 'block'
        # collect following - items; allow initial blank lines
        start = m_block.end()
        after = fm[start:]
        seen_any = False
        for line in after.splitlines():
            if line.strip() == "" and not seen_any:
                # skip leading blanks between key and list
                continue
            if re.match(r"^\s*-\s+", line):
                val = re.sub(r"^\s*-\s+", "", line).strip()
                val = val.strip('"\'')
                if val:
                    items.append(val)
                    seen_any = True
                continue
            # stop at first non-list or blank after items
            break
        return items, style
    return items, style


def render_block_list(key: str, values: List[str]) -> str:
    out = [f"{key}:\n"]
    for v in values:
        # quote values with spaces
        vq = f'"{v}"' if ' ' in v else v
        out.append(f"  - {vq}\n")
    return "".join(out)


def set_list_in_fm(fm: str, key: str, values: List[str]) -> str:
    # Remove existing key and write block-style list at same approximate position.
    lines = fm.splitlines(keepends=True)
    out: List[str] = []
    i = 0
    n = len(lines)
    removed = False
    while i < n:
        line = lines[i]
        if re.match(rf"^\s*{re.escape(key)}:\s*(\[.*\])?\s*$", line):
            removed = True
            i += 1
            # skip any following - items
            while i < n and re.match(r"^\s*-\s+", lines[i]):
                i += 1
            continue
        out.append(line)
        i += 1
    # Append at end of fm if not found; otherwise, keep as is and append at end for simplicity
    rendered = render_block_list(key, values) if values else ""
    # If no values, just return fm without the key
    if not rendered:
        return "".join(out)
    # Ensure fm ends with newline
    if out and not out[-1].endswith("\n"):
        out[-1] = out[-1] + "\n"
    out.append(rendered)
    return "".join(out)


def inventory_content(base: pathlib.Path) -> Tuple[Dict[str, int], Dict[str, int]]:
    tag_counts: Dict[str, int] = collections.Counter()
    cat_counts: Dict[str, int] = collections.Counter()
    for md in sorted(base.rglob("*.md")):
        text = md.read_text(encoding="utf-8")
        _, fm, _ = split_front_matter(text)
        if not fm:
            continue
        tags, _ = parse_list_from_fm(fm, "tags")
        cats, _ = parse_list_from_fm(fm, "categories")
        for t in tags:
            tag_counts[t] += 1
        for c in cats:
            cat_counts[c] += 1
    return tag_counts, cat_counts


def load_mapping(path: pathlib.Path) -> Tuple[Dict[str, str], Dict[str, str]]:
    # Minimal parser for mapping yaml (no nesting beyond tags:/categories: key: value)
    tags: Dict[str, str] = {}
    cats: Dict[str, str] = {}
    current = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith('#'):
            continue
        if line.lower() == 'tags:':
            current = 'tags'
            continue
        if line.lower() == 'categories:':
            current = 'categories'
            continue
        m = re.match(r"^(.+?):\s*(.+)$", line)
        if m and current in ('tags', 'categories'):
            k = m.group(1).strip().strip('"\'')
            v = m.group(2).strip().strip('"\'')
            if current == 'tags':
                tags[k] = v
            else:
                cats[k] = v
    return tags, cats


def apply_mapping_to_list(items: List[str], mapping: Dict[str, str]) -> List[str]:
    result: List[str] = []
    seen = set()
    for it in items:
        new = mapping.get(it, it)
        new = new.strip().lower()
        if new not in seen and new:
            seen.add(new)
            result.append(new)
    return result


def apply_mapping(base: pathlib.Path, map_path: pathlib.Path, write: bool) -> None:
    tag_map, cat_map = load_mapping(map_path)
    changed_files = 0
    total = 0
    for md in sorted(base.rglob("*.md")):
        total += 1
        text = md.read_text(encoding="utf-8")
        delim, fm, content = split_front_matter(text)
        if not fm:
            continue
        tags, _ = parse_list_from_fm(fm, "tags")
        cats, _ = parse_list_from_fm(fm, "categories")
        new_tags = apply_mapping_to_list(tags, tag_map)
        new_cats = apply_mapping_to_list(cats, cat_map)
        changed = False
        new_fm = fm
        if new_tags != tags:
            new_fm = set_list_in_fm(new_fm, "tags", new_tags)
            changed = True
        if new_cats != cats:
            new_fm = set_list_in_fm(new_fm, "categories", new_cats)
            changed = True
        if changed:
            changed_files += 1
            new_text = f"{delim}{new_fm}{delim}{content}"
            if write:
                md.write_text(new_text, encoding="utf-8")
            rel = md.as_posix()
            print(f"- {rel}: updated tags/categories")
    print(f"Processed {total} file(s). {changed_files} file(s) {'updated' if write else 'would be updated'}.")


def main():
    parser = argparse.ArgumentParser(description="Taxonomy tools for Hugo posts")
    sub = parser.add_subparsers(dest='cmd', required=True)

    p_inv = sub.add_parser('inventory', help='List all tags and categories with counts')
    p_inv.add_argument('--limit', type=int, default=0, help='Limit rows shown per taxonomy')

    p_app = sub.add_parser('apply-map', help='Apply mapping file to consolidate terms')
    p_app.add_argument('map', help='Path to taxonomy_map.yaml')
    p_app.add_argument('--write', action='store_true', help='Apply changes (dry-run by default)')

    p_exp = sub.add_parser('export-map', help='Export current terms into a skeleton mapping file')
    p_exp.add_argument('out', help='Path to write mapping YAML')

    p_sug = sub.add_parser('suggest-map', help='Export mapping with similarity suggestions as comments')
    p_sug.add_argument('out', help='Path to write suggested mapping YAML')

    args = parser.parse_args()
    # Operate across the whole site content, not just blog
    base = pathlib.Path('content')

    if args.cmd == 'inventory':
        tags, cats = inventory_content(base)
        print("Categories (count):")
        for k, v in sorted(cats.items(), key=lambda kv: (-kv[1], kv[0]))[: args.limit or None]:
            print(f"- {k}: {v}")
        print("\nTags (count):")
        for k, v in sorted(tags.items(), key=lambda kv: (-kv[1], kv[0]))[: args.limit or None]:
            print(f"- {k}: {v}")
        return

    if args.cmd == 'apply-map':
        apply_mapping(base, pathlib.Path(args.map), write=args.write)
        return

    if args.cmd == 'export-map':
        tags, cats = inventory_content(base)
        out_path = pathlib.Path(args.out)
        with out_path.open('w', encoding='utf-8') as f:
            f.write("# Auto-generated taxonomy map skeleton. Fill values to consolidate terms.\n")
            f.write("# Keys are existing terms; set value to the desired canonical term.\n\n")
            f.write("tags:\n")
            for term in sorted(tags.keys(), key=str.lower):
                f.write(f"  '{term}': '{term}'\n")
            f.write("\ncategories:\n")
            for term in sorted(cats.keys(), key=str.lower):
                f.write(f"  '{term}': '{term}'\n")
        print(f"Wrote skeleton mapping to {out_path}")
        return

    if args.cmd == 'suggest-map':
        tags, cats = inventory_content(base)
        def simkey(s: str) -> str:
            s2 = s.lower()
            s2 = s2.replace('&', 'and')
            s2 = re.sub(r"[\s_\-]+", "", s2)
            s2 = re.sub(r"[^a-z0-9]", "", s2)
            # crude singular: drop trailing 's' for words > 3 chars
            if len(s2) > 3 and s2.endswith('s') and not s2.endswith('ss'):
                s2 = s2[:-1]
            return s2
        def groups(terms: List[str]) -> Dict[str, List[str]]:
            g: Dict[str, List[str]] = {}
            for t in terms:
                k = simkey(t)
                g.setdefault(k, []).append(t)
            return g
        tag_groups = groups(list(tags.keys()))
        cat_groups = groups(list(cats.keys()))
        out_path = pathlib.Path(args.out)
        with out_path.open('w', encoding='utf-8') as f:
            f.write("# Suggested taxonomy mapping.\n")
            f.write("# For each term, set the value to your canonical term.\n")
            f.write("# Candidates hints list similar terms (by punctuation/spacing/plural heuristics).\n\n")
            f.write("tags:\n")
            for term in sorted(tags.keys(), key=str.lower):
                cands = [c for c in tag_groups.get(simkey(term), []) if c != term]
                hint = f"  # candidates: {', '.join(sorted(cands, key=str.lower))}" if cands else ""
                f.write(f"  '{term}': '{term}'{hint}\n")
            f.write("\ncategories:\n")
            for term in sorted(cats.keys(), key=str.lower):
                cands = [c for c in cat_groups.get(simkey(term), []) if c != term]
                hint = f"  # candidates: {', '.join(sorted(cands, key=str.lower))}" if cands else ""
                f.write(f"  '{term}': '{term}'{hint}\n")
        print(f"Wrote suggested mapping to {out_path}")
        return


if __name__ == '__main__':
    sys.exit(main())
