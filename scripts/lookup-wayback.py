#!/usr/bin/env python3
"""
Look up Internet Archive (Wayback Machine) snapshots for the dead external
links found by check-external-links.py.

Reads the dead URLs from scripts/data/audit-external-links.json, queries the
Wayback availability API for the closest usable (HTTP 2xx) snapshot of each,
and writes a mapping to scripts/data/wayback-map.json:

    { "<dead url>": {"wayback": "<snapshot url>"|null,
                     "timestamp": "...", "snap_status": "..."} }

This is the input to the dead-link fixer: URLs with a snapshot get rewritten to
the archived copy; URLs without one get unlinked and marked.

Usage: python3 scripts/lookup-wayback.py
"""

import json
import time
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen
from urllib.error import URLError

AUDIT = Path('scripts/data/audit-external-links.json')
OUT = Path('scripts/data/wayback-map.json')
API = 'https://archive.org/wayback/available?url='
HEADERS = {'User-Agent': 'joshuapsteele.com link maintenance (Wayback lookup)'}


def closest_snapshot(url, timeout=20):
    """Return (wayback_url|None, timestamp, snap_status)."""
    try:
        req = Request(API + quote(url, safe=''), headers=HEADERS)
        with urlopen(req, timeout=timeout) as resp:
            data = json.load(resp)
    except (URLError, TimeoutError, ValueError, Exception):  # noqa: BLE001
        return None, None, 'lookup-error'
    snap = (data.get('archived_snapshots') or {}).get('closest') or {}
    if not snap.get('available'):
        return None, None, 'none'
    status = str(snap.get('status', ''))
    wb = snap.get('url')
    if wb and wb.startswith('http://'):
        wb = 'https://' + wb[len('http://'):]  # prefer https for the archive link
    # Only treat a 2xx capture as usable; a snapshot that archived a 404/redirect
    # is no better than the dead link.
    if status.startswith('2'):
        return wb, snap.get('timestamp'), status
    return None, snap.get('timestamp'), status or 'non-2xx'


def main():
    data = json.load(AUDIT.open())
    dead_urls = sorted({it['url'] for it in data.get('dead_details', [])})
    print(f"Looking up Wayback snapshots for {len(dead_urls)} dead URLs...\n")

    mapping = {}
    have = 0
    for i, url in enumerate(dead_urls, 1):
        wb, ts, status = closest_snapshot(url)
        mapping[url] = {'wayback': wb, 'timestamp': ts, 'snap_status': status}
        if wb:
            have += 1
        if i % 20 == 0 or i == len(dead_urls):
            print(f"  {i}/{len(dead_urls)} (snapshots found so far: {have})")
        time.sleep(0.5)  # be polite to archive.org

    OUT.write_text(json.dumps(mapping, indent=2))
    print(f"\nSnapshots found: {have}/{len(dead_urls)} "
          f"({len(dead_urls) - have} will need unlink + marker)")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
