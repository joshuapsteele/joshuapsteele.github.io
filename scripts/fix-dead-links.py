#!/usr/bin/env python3
"""
Fix the dead external links found by check-external-links.py, using the strategy:

  * If the Internet Archive has a usable snapshot (see lookup-wayback.py),
    rewrite the dead URL to that snapshot (link text/alt preserved).
  * Otherwise UNLINK it: keep the visible text and append a marker —
      [text](deadurl)        -> text (old, broken link)
      ![alt](deadimg)        -> alt (old, broken image)
      <a href="deadurl">t</a> -> t (old, broken link)

Operates on post BODIES only (never the YAML front matter). Dry-run by default.

Inputs:  scripts/data/audit-external-links.json, scripts/data/wayback-map.json
Usage:   python3 scripts/fix-dead-links.py [--apply]
"""

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

AUDIT = Path('scripts/data/audit-external-links.json')
WAYBACK = Path('scripts/data/wayback-map.json')
FRONT_MATTER = re.compile(r'^(---\r?\n.*?\r?\n---\r?\n)', re.DOTALL)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true', help='write changes (default: dry run)')
    args = ap.parse_args()

    audit = json.load(AUDIT.open())
    wb = json.load(WAYBACK.open())

    # dead URLs grouped by file. Skip URLs with unbalanced parentheses: the link
    # extractor truncates URLs like .../300_(film) at the inner ")", so the
    # "dead" result is a false positive and the real link works fine.
    by_file = defaultdict(set)
    skipped_fp = []
    for it in audit.get('dead_details', []):
        if it['url'].count('(') > it['url'].count(')'):
            skipped_fp.append(it['url'])
            continue
        by_file[it['file']].add(it['url'])

    stats = defaultdict(int)
    archived_examples, unlinked_examples = [], []
    files_changed = 0

    for rel_file, urls in by_file.items():
        path = Path('content') / rel_file
        text = path.read_text(encoding='utf-8', errors='ignore')
        m = FRONT_MATTER.match(text)
        fm, body = (m.group(1), text[m.end():]) if m else ('', text)
        new = body

        for url in urls:
            esc = re.escape(url)
            snapshot = (wb.get(url) or {}).get('wayback')
            if snapshot:
                # Swap just the URL token (boundary lookahead avoids prefix clashes).
                new2, n = re.subn(esc + r'(?=[)"\s]|$)', snapshot.replace('\\', r'\\'), new)
                if n:
                    stats['archived'] += n
                    if len(archived_examples) < 6:
                        archived_examples.append((rel_file, url, snapshot))
                new = new2
            else:
                # Image first (![alt](url)), then link ([text](url)), then href.
                new, ni = re.subn(r'!\[([^\]]*)\]\(' + esc + r'(?:\s+"[^"]*")?\)',
                                  r'\1 (old, broken image)', new)
                new, nl = re.subn(r'\[([^\]]*)\]\(' + esc + r'(?:\s+"[^"]*")?\)',
                                  r'\1 (old, broken link)', new)
                new, nh = re.subn(r'<a\s+[^>]*href=["\']' + esc + r'["\'][^>]*>(.*?)</a>',
                                  r'\1 (old, broken link)', new, flags=re.IGNORECASE | re.DOTALL)
                stats['unlinked'] += ni + nl + nh
                if (ni + nl + nh) and len(unlinked_examples) < 8:
                    unlinked_examples.append((rel_file, url))

        if new != body:
            files_changed += 1
            if args.apply:
                path.write_text(fm + new, encoding='utf-8')

    mode = "APPLIED" if args.apply else "DRY RUN (no files written)"
    print("=" * 70)
    print(f"Dead-link fixer — {mode}")
    print("=" * 70)
    print(f"Files affected: {files_changed}")
    print(f"Rewritten to Wayback snapshot: {stats['archived']}")
    print(f"Unlinked + marked (no snapshot): {stats['unlinked']}")
    print(f"Skipped (unbalanced-paren false positives, left untouched): "
          f"{len(set(skipped_fp))}\n")
    if archived_examples:
        print("Sample Wayback rewrites:")
        for f, u, s in archived_examples:
            print(f"  {f}\n     {u}\n  -> {s}")
    if unlinked_examples:
        print("\nSample unlinks (text kept, marked):")
        for f, u in unlinked_examples:
            print(f"  {f}  ::  {u}")
    if not args.apply:
        print("\nRe-run with --apply to write the changes.")


if __name__ == "__main__":
    main()
