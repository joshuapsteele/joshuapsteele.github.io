#!/usr/bin/env python3
"""
Check Amazon links (amazon.com, amzn.to, a.co) with a best effort to avoid
being bot-blocked. Amazon aggressively fingerprints automated traffic, so this
will NOT achieve a clean pass — the goal is to maximize the chance of a real
answer and to clearly separate "genuinely dead" from "blocked, can't tell."

Tactics used (none defeat Amazon's CAPTCHA, but they help):
- A realistic desktop-browser User-Agent and full header set.
- A persistent cookie jar reused across requests (Amazon sets a session cookie
  on first contact; sending it back looks more like a real browser).
- Strictly sequential requests with a randomized human-ish delay between them.
- GET with redirect-following so amzn.to / a.co short links resolve to the
  product page, which is what actually gets validated.
- Body inspection to tell apart a live product, Amazon's "we couldn't find that
  page" soft-404, and a CAPTCHA / "Robot Check" interstitial.

Usage:
  python3 scripts/check-amazon-links.py [--delay 2.5] [--jitter 1.5] [--limit N]

Output:
  docs/AUDIT-amazon-links.md
  scripts/data/audit-amazon-links.json
"""

import argparse
import json
import os
import re
import random
import time
from collections import defaultdict
from datetime import date
from http.cookiejar import CookieJar
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, build_opener, HTTPCookieProcessor
from urllib.parse import urlparse

AMAZON_SUBSTRINGS = ('amazon.', 'amzn.to', 'amzn.com', '://a.co/')

USER_AGENTS = [
    ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
     '(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'),
    ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 '
     '(KHTML, like Gecko) Version/17.4 Safari/605.1.15'),
    ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
     '(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'),
]

def base_headers():
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': ('text/html,application/xhtml+xml,application/xml;q=0.9,'
                   'image/avif,image/webp,*/*;q=0.8'),
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'identity',  # keep body uncompressed so we can scan it
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Referer': 'https://www.google.com/',
    }

BLOCK_MARKERS = (
    'robot check', 'type the characters you see in this image',
    'to discuss automated access', 'api-services-support@amazon.com',
    'enter the characters as they are shown', 'sorry, we just need to make sure',
)
NOTFOUND_MARKERS = (
    "we couldn't find that page", 'looking for something?',
    'the web address you entered is not a functioning page',
    'page not found', "we're sorry. the web address you entered",
)


def extract_amazon_links(content_dir):
    links = defaultdict(list)
    for root, _dirs, files in os.walk(content_dir):
        for filename in files:
            if not filename.endswith('.md'):
                continue
            filepath = os.path.join(root, filename)
            rel = os.path.relpath(filepath, content_dir)
            try:
                content = open(filepath, encoding='utf-8', errors='ignore').read()
            except Exception as e:
                print(f"Error reading {filepath}: {e}")
                continue
            urls = re.findall(r'\[([^\]]*)\]\((https?://[^)\s]+)', content)
            hrefs = re.findall(r'href=["\'](https?://[^"\']+)["\']', content)
            for text, url in urls:
                if any(s in url for s in AMAZON_SUBSTRINGS):
                    links[rel].append((text, url.rstrip('.,;')))
            for url in hrefs:
                if any(s in url for s in AMAZON_SUBSTRINGS):
                    links[rel].append(('', url))
    return links


def check_amazon_url(opener, url, timeout=20):
    """Return (status, final_url, category, note)."""
    req = Request(url, method='GET', headers=base_headers())
    try:
        with opener.open(req, timeout=timeout) as resp:
            status = resp.status
            final = resp.geturl()
            body = resp.read(40000).decode('utf-8', errors='ignore').lower()
    except HTTPError as e:
        code = e.code
        if code in (404, 410):
            return code, url, 'dead', 'HTTP 404/410'
        if code in (503, 429) or code >= 500:
            return code, url, 'blocked', 'rate-limited / server error'
        if code in (403, 401):
            return code, url, 'blocked', 'forbidden (likely bot defense)'
        return code, url, 'dead', f'HTTP {code}'
    except TimeoutError:
        return None, url, 'blocked', 'timeout'
    except URLError as e:
        reason = str(getattr(e, 'reason', e))
        low = reason.lower()
        if any(s in low for s in ('not known', 'no address', 'refused', 'getaddrinfo')):
            return None, url, 'dead', reason[:100]
        return None, url, 'blocked', reason[:100]
    except Exception as e:  # noqa: BLE001
        return None, url, 'blocked', str(e)[:100]

    if any(m in body for m in BLOCK_MARKERS):
        return status, final, 'blocked', 'CAPTCHA / Robot Check'
    if any(m in body for m in NOTFOUND_MARKERS):
        return status, final, 'dead', 'Amazon soft-404 (product page gone)'
    if status == 200:
        return status, final, 'working', 'product page loaded'
    return status, final, 'blocked', f'unexpected status {status}'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--delay', type=float, default=2.5,
                    help='base seconds between requests (default 2.5)')
    ap.add_argument('--jitter', type=float, default=1.5,
                    help='added random 0..jitter seconds per request (default 1.5)')
    ap.add_argument('--limit', type=int, default=0,
                    help='only check the first N unique URLs (0 = all)')
    args = ap.parse_args()

    print("=" * 70)
    print("AMAZON LINKS CHECKER")
    print("=" * 70)

    links = extract_amazon_links('content/')
    total = sum(len(v) for v in links.values())
    unique = sorted({url for v in links.values() for _t, url in v})
    if args.limit:
        unique = unique[:args.limit]
    est = len(unique) * (args.delay + args.jitter / 2) / 60
    print(f"Found {total} Amazon links across {len(links)} files; "
          f"{len(unique)} unique to check.")
    print(f"Sequential with ~{args.delay}s (+0..{args.jitter}s) delay "
          f"=> roughly {est:.0f} min.\n")

    opener = build_opener(HTTPCookieProcessor(CookieJar()))
    # Warm up the cookie jar with a homepage hit so later requests carry a session.
    try:
        opener.open(Request('https://www.amazon.com/', headers=base_headers()),
                    timeout=20).read(1000)
    except Exception:
        pass

    status_map = {}
    for i, url in enumerate(unique, 1):
        status_map[url] = check_amazon_url(opener, url)
        if i % 10 == 0 or i == len(unique):
            print(f"  Progress: {i}/{len(unique)}")
        time.sleep(args.delay + random.random() * args.jitter)

    buckets = {'working': [], 'dead': [], 'blocked': []}
    for filepath, items in links.items():
        for text, url in items:
            if url not in status_map:
                continue
            status, final, cat, note = status_map[url]
            buckets[cat].append({
                'file': filepath, 'text': text, 'url': url,
                'final_url': final, 'status': status, 'note': note,
            })

    report_path = Path('docs/AUDIT-amazon-links.md')
    data_path = Path('scripts/data/audit-amazon-links.json')
    report_path.parent.mkdir(parents=True, exist_ok=True)
    data_path.parent.mkdir(parents=True, exist_ok=True)

    with report_path.open('w') as f:
        f.write('# Amazon Links Audit Report\n\n')
        f.write(f'**Audit Date:** {date.today().isoformat()}\n\n')
        f.write('Amazon blocks automated checkers aggressively, so treat results '
                'with caution. **Blocked** means we could not tell (CAPTCHA, 503, '
                'timeout) — the product is probably fine. **Dead** means a 404/410 '
                'or an Amazon "we couldn\'t find that page" soft-404, which is worth '
                'fixing.\n\n')
        f.write('---\n\n## Summary\n\n')
        f.write(f'- Unique Amazon URLs checked: {len(unique)}\n')
        f.write(f'- Working: {len(buckets["working"])}\n')
        f.write(f'- **Dead (verify & fix): {len(buckets["dead"])}**\n')
        f.write(f'- Blocked / could-not-determine: {len(buckets["blocked"])}\n\n')
        for title, key, blurb in [
            ('Dead links (verify & fix)', 'dead',
             'A 404/410 or Amazon soft-404. Confirm in a browser, then update the '
             'ASIN or remove the link.'),
            ('Blocked / could-not-determine', 'blocked',
             'CAPTCHA, 503, 403, or timeout. Most are fine; re-run later or '
             'spot-check a sample manually.'),
        ]:
            f.write('---\n\n')
            f.write(f'## {title}\n\n{blurb}\n\n**Count:** {len(buckets[key])}\n\n')
            by_file = defaultdict(list)
            for it in buckets[key]:
                by_file[it['file']].append(it)
            for filepath in sorted(by_file):
                f.write(f'\n### {filepath}\n\n')
                for it in by_file[filepath]:
                    label = f"Status {it['status']}" if it['status'] else 'ERROR'
                    link = (f"`[{it['text']}]({it['url']})`" if it['text']
                            else f"`{it['url']}`")
                    f.write(f"- **{label}** ({it['note']}): {link}\n")
            f.write('\n')

    json.dump({
        'date': date.today().isoformat(),
        'unique_checked': len(unique),
        'working': len(buckets['working']),
        'dead': len(buckets['dead']),
        'blocked': len(buckets['blocked']),
        'dead_details': buckets['dead'],
        'blocked_details': buckets['blocked'],
    }, data_path.open('w'), indent=2)

    print("\n" + "=" * 70)
    print(f"Working: {len(buckets['working'])} | DEAD: {len(buckets['dead'])} | "
          f"Blocked: {len(buckets['blocked'])}")
    print(f"Report: {report_path}")
    print(f"Data:   {data_path}")


if __name__ == "__main__":
    main()
