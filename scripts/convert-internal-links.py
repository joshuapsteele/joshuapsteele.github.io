#!/usr/bin/env python3
"""
Convert absolute self-links (https://joshuapsteele.com/... and the old
joshuapsteele.github.io host) in post BODIES to root-relative internal links,
and flag any that don't resolve.

Why: internal references should be root-relative (`/some-post/`) so they work in
local dev and don't hard-code the production domain. Only actual link *targets*
are rewritten — markdown `](url)` targets and HTML `href="url"` — never bare
URLs shown as visible text and never anything inside the YAML front matter
(where `redirect_to`, `guid`, etc. legitimately use absolute URLs).

Validation uses the built site in public/ as ground truth (run `npm run build`
first). A converted target that resolves is rewritten; one that doesn't is left
untouched and reported so it can be fixed by hand.

Usage:
  python3 scripts/convert-internal-links.py          # dry run (default)
  python3 scripts/convert-internal-links.py --apply   # write changes
"""

import argparse
import os
import re
from collections import defaultdict

SELF_HOST = r'https?://(?:www\.)?joshuapsteele\.(?:com|github\.io)'
FRONT_MATTER = re.compile(r'^(---\r?\n.*?\r?\n---\r?\n)', re.DOTALL)

# Link target contexts only: markdown "](URL" and HTML href="URL".
MD_TARGET = re.compile(r'(\]\(\s*)(' + SELF_HOST + r'(/[^\s)"\']*)?)')
HREF_TARGET = re.compile(r'(href=["\'])(' + SELF_HOST + r'(/[^"\']*)?)')


def build_valid_urls(public_dir='public'):
    valid = set()
    for root, _dirs, files in os.walk(public_dir):
        rel = os.path.relpath(root, public_dir).replace(os.sep, '/')
        rel = '/' if rel == '.' else '/' + rel
        if 'index.html' in files:
            valid.add(rel.rstrip('/') or '/')
        for fn in files:
            if fn == 'index.html':
                continue
            valid.add((rel.rstrip('/') + '/' + fn) if rel != '/' else '/' + fn)
    return valid


def to_relative(absolute_url):
    """Strip the scheme+host, returning the root-relative path (with query/frag)."""
    rel = re.sub(r'^' + SELF_HOST, '', absolute_url)
    return rel if rel else '/'


def resolves(rel, valid):
    path = rel.split('?')[0].split('#')[0]
    key = path.rstrip('/') or '/'
    return key in valid or (key + '/') in valid or key == '/'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true',
                    help='write changes (default is a dry run)')
    args = ap.parse_args()

    if not os.path.isdir('public'):
        print("ERROR: public/ not found. Run `npm run build` first so links can "
              "be validated against the built site.")
        return

    valid = build_valid_urls()
    converted = []   # (file, absolute_url, relative)
    failed = []      # (file, absolute_url, attempted_relative)
    files_changed = 0

    for root, _dirs, files in os.walk('content'):
        for filename in files:
            if not filename.endswith('.md'):
                continue
            path = os.path.join(root, filename)
            rel_file = os.path.relpath(path, 'content')
            text = open(path, encoding='utf-8', errors='ignore').read()

            # Protect the front matter: only operate on the body.
            m = FRONT_MATTER.match(text)
            fm, body = (m.group(1), text[m.end():]) if m else ('', text)

            def repl(match):
                pre, absolute = match.group(1), match.group(2)
                relative = to_relative(absolute)
                if resolves(relative, valid):
                    converted.append((rel_file, absolute, relative))
                    return pre + relative
                failed.append((rel_file, absolute, relative))
                return match.group(0)  # leave untouched

            new_body = MD_TARGET.sub(repl, body)
            new_body = HREF_TARGET.sub(repl, new_body)

            if new_body != body:
                files_changed += 1
                if args.apply:
                    open(path, 'w', encoding='utf-8').write(fm + new_body)

    mode = "APPLIED" if args.apply else "DRY RUN (no files written)"
    print("=" * 70)
    print(f"Self-link converter — {mode}")
    print("=" * 70)
    print(f"Converted (resolved -> rewritten): {len(converted)} links "
          f"in {files_changed} files")
    print(f"Flagged (do NOT resolve, left as-is): {len(failed)} links\n")

    if converted:
        by_file = defaultdict(int)
        for f, _a, _r in converted:
            by_file[f] += 1
        print("Files with conversions:")
        for f in sorted(by_file):
            print(f"  {by_file[f]:3d}  {f}")

    if failed:
        print("\n⚠️  Flagged links that do not resolve (fix manually):")
        for f, absolute, attempted in failed:
            print(f"  {f}\n      {absolute}\n      (would be {attempted}; not found in public/)")

    if not args.apply and (converted or failed):
        print("\nRe-run with --apply to write the conversions.")


if __name__ == "__main__":
    main()
