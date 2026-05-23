#!/usr/bin/env python3
"""
Check external HTTP(S) links in markdown files for breakage.

Designed to minimize false positives:
- Sends realistic browser headers (a bare bot User-Agent gets 403'd by many WAFs).
- Throttles per-domain (one request at a time per host, with a minimum interval)
  so we don't trip rate limiters; different domains are still checked in parallel.
- Retries transient failures (timeouts, 429/503) with backoff before giving up.
- Falls back from HEAD to GET when a host mishandles HEAD (403/405/network error).
- Classifies results as DEAD (high-confidence, fix it) vs. BLOCKED/MANUAL
  (403/429/503/999/SSL/timeout — the site probably exists but blocks bots).

Amazon links and self-links (joshuapsteele.com) are skipped here; they have
dedicated scripts (check-amazon-links.py, convert-internal-links.py).
"""

import os
import re
import time
import json
import random
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from pathlib import Path
from threading import Lock
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from urllib.parse import urlparse

# Domains handled by other scripts (excluded from this run).
EXCLUDE_SUBSTRINGS = (
    'amazon.', 'amzn.to', 'amzn.com', '://a.co/',
    'joshuapsteele.com', 'joshuapsteele.github.io',
)

BROWSER_HEADERS = {
    'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                   'AppleWebKit/537.36 (KHTML, like Gecko) '
                   'Chrome/124.0.0.0 Safari/537.36'),
    'Accept': ('text/html,application/xhtml+xml,application/xml;q=0.9,'
               'image/avif,image/webp,image/apng,*/*;q=0.8'),
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate',  # body is never read, so this is harmless
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

MIN_DOMAIN_INTERVAL = 1.5   # seconds between requests to the same host
DEFAULT_TIMEOUT = 15
DEFAULT_RETRIES = 2

# Per-domain locks/timestamps for polite throttling across worker threads.
_locks_guard = Lock()
_domain_locks = {}
_domain_last = {}


def _get_domain_lock(domain):
    with _locks_guard:
        if domain not in _domain_locks:
            _domain_locks[domain] = Lock()
        return _domain_locks[domain]


def _is_dns_failure(error):
    if not error:
        return False
    e = error.lower()
    return any(s in e for s in (
        'name or service not known', 'nodename nor servname',
        'no address associated', 'getaddrinfo failed',
        'name resolution', 'temporary failure in name resolution',
    ))


def extract_external_links(content_dir):
    """Extract external HTTP(S) links from markdown files."""
    external_links = defaultdict(list)
    for root, _dirs, files in os.walk(content_dir):
        for filename in files:
            if not filename.endswith('.md'):
                continue
            filepath = os.path.join(root, filename)
            rel_path = os.path.relpath(filepath, content_dir)
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            except Exception as e:
                print(f"Error reading {filepath}: {e}")
                continue

            md_links = re.findall(r'\[([^\]]*)\]\((https?://[^)\s]+)', content)
            html_links = re.findall(r'href=["\'](https?://[^"\']+)["\']', content)
            for text, url in md_links:
                external_links[rel_path].append(('markdown', text, url.rstrip('.,;')))
            for url in html_links:
                external_links[rel_path].append(('html', '', url))
    return external_links


def _open(url, method, timeout):
    """Single request. Returns (status, error)."""
    req = Request(url, method=method, headers=BROWSER_HEADERS)
    try:
        with urlopen(req, timeout=timeout) as response:
            return response.status, None
    except HTTPError as e:
        return e.code, None
    except TimeoutError:
        return None, "Timeout"
    except URLError as e:
        return None, str(getattr(e, 'reason', e))[:120]
    except Exception as e:  # noqa: BLE001 - report anything else as an error string
        return None, str(e)[:120]


def check_url(url, timeout=DEFAULT_TIMEOUT, retries=DEFAULT_RETRIES):
    """Check one URL with per-domain throttling, HEAD->GET fallback, and retries."""
    domain = urlparse(url).netloc.lower()
    lock = _get_domain_lock(domain)
    with lock:
        wait = MIN_DOMAIN_INTERVAL - (time.time() - _domain_last.get(domain, 0))
        if wait > 0:
            time.sleep(wait)
        try:
            status, error = None, None
            for attempt in range(retries + 1):
                status, error = _open(url, 'HEAD', timeout)
                # Some hosts block or mishandle HEAD; retry the same URL with GET.
                if status in (403, 405, 406, 501) or status is None:
                    g_status, g_error = _open(url, 'GET', timeout)
                    if g_status is not None or status is None:
                        status, error = g_status, g_error
                # Decide whether to retry.
                if status is not None and status not in (429, 503):
                    break
                if status in (429, 503) and attempt < retries:
                    time.sleep(2 * (attempt + 1) + random.random())
                    continue
                if status is None and not _is_dns_failure(error) and attempt < retries:
                    time.sleep(1.5 * (attempt + 1) + random.random())
                    continue
                break
            return url, status, error
        finally:
            _domain_last[domain] = time.time()


def classify(status, error):
    """Bucket a result as 'working', 'dead', or 'blocked' (manual verify).

    Only 404/410 and hard network failures (DNS/refused/no-route) count as
    'dead'. Every other non-2xx/3xx status is 'blocked' (manual verify): 400,
    401, 403, 405, 429, 451, 503, 999, etc. are overwhelmingly bot defense or
    transient rather than a genuinely missing page, so flagging them as dead
    produces false positives (e.g. Harbor Freight/Wikipedia/Facebook return 400
    to non-browser clients).
    """
    if status is not None and 200 <= status < 400:
        return 'working'
    if status in (404, 410):
        return 'dead'
    if status is not None:
        return 'blocked'  # all other 4xx/5xx -> ambiguous, verify manually
    # No HTTP status -> network-level error
    e = (error or '').lower()
    if _is_dns_failure(error) or 'refused' in e or 'no route' in e:
        return 'dead'
    return 'blocked'  # SSL errors, timeouts, unknown errors -> manual verify


def check_links_parallel(unique_urls, max_workers=10):
    print(f"\nChecking {len(unique_urls)} unique URLs "
          f"(per-domain throttled; this can take a while)...\n")
    results = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(check_url, url): url for url in unique_urls}
        done = 0
        for future in as_completed(futures):
            url, status, error = future.result()
            results[url] = (status, error)
            done += 1
            if done % 25 == 0 or done == len(unique_urls):
                print(f"  Progress: {done}/{len(unique_urls)} "
                      f"({done / len(unique_urls) * 100:.0f}%)")
    return results


REPORT_PATH = Path('docs/AUDIT-06-external-links.md')
DATA_PATH = Path('scripts/data/audit-external-links.json')


def _write_section(f, title, items, blurb):
    f.write(f'## {title}\n\n{blurb}\n\n**Count:** {len(items)}\n\n')
    by_file = defaultdict(list)
    for it in items:
        by_file[it['file']].append(it)
    for filepath in sorted(by_file):
        f.write(f'\n### {filepath}\n\n')
        for it in by_file[filepath]:
            label = f"Status {it['status']}" if it['status'] else "ERROR"
            link = (f"`[{it['text']}]({it['url']})`" if it['text']
                    else f"`{it['url']}`")
            f.write(f"- **{label}**: {link}")
            if it['error']:
                f.write(f"\n  - {it['error']}")
            f.write('\n')
    f.write('\n')


def write_outputs(meta, buckets, skipped_urls):
    """Write the markdown report and JSON data from classified buckets."""
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    with REPORT_PATH.open('w') as f:
        f.write('# External Links Audit Report\n')
        f.write('## joshuapsteele.com Hugo Site\n\n')
        f.write(f'**Audit Date:** {meta["date"]}\n\n')
        f.write('Amazon and self (joshuapsteele.com) links are checked by '
                '`check-amazon-links.py` and `convert-internal-links.py`.\n\n')
        f.write('---\n\n## Summary\n\n')
        f.write(f'- Total external links: {meta["total_links"]}\n')
        f.write(f'- Unique URLs checked: {meta["unique_urls_checked"]}\n')
        f.write(f'- Skipped (Amazon/self): {meta["skipped_count"]}\n')
        f.write(f'- Working: {len(buckets["working"])}\n')
        f.write(f'- **Dead (action needed): {len(buckets["dead"])}**\n')
        f.write(f'- Blocked / manual-verify: {len(buckets["blocked"])}\n\n')
        f.write('---\n\n')
        _write_section(
            f, 'Dead links (action needed)', buckets['dead'],
            'High-confidence breakage: a 404/410, or a hard network failure '
            '(DNS does not resolve / connection refused). Fix these: update the '
            'URL, swap in an Internet Archive snapshot, or remove the link.')
        f.write('---\n\n')
        _write_section(
            f, 'Blocked / manual-verify', buckets['blocked'],
            'Ambiguous: a 4xx other than 404/410 (often bot defense, e.g. 400/403/'
            '429), a 5xx, an SSL error, or a timeout. The page very likely still '
            'exists but blocks automated checkers. Spot-check in a real browser '
            'before changing anything.')

    json.dump({
        **meta,
        'working': len(buckets['working']),
        'dead': len(buckets['dead']),
        'blocked': len(buckets['blocked']),
        'dead_details': buckets['dead'],
        'blocked_details': buckets['blocked'],
        'skipped_urls': sorted(skipped_urls),
    }, DATA_PATH.open('w'), indent=2)


def reclassify_existing():
    """Re-bucket the previously saved results with the current classify() rules,
    without re-hitting the network. 'working' count is preserved from the prior
    run (only dead/blocked details were stored)."""
    prior = json.load(DATA_PATH.open())
    buckets = {'working': [], 'dead': [], 'blocked': []}
    moved = 0
    for it in prior.get('dead_details', []) + prior.get('blocked_details', []):
        cat = classify(it.get('status'), it.get('error'))
        buckets[cat].append(it)
    # Reconstruct working as a placeholder list of the right length.
    buckets['working'] = [None] * prior.get('working', 0)
    meta = {
        'date': date.today().isoformat(),
        'total_files': prior.get('total_files', 0),
        'total_links': prior.get('total_links', 0),
        'unique_urls_checked': prior.get('unique_urls_checked', 0),
        'skipped_count': prior.get('skipped_count', 0),
    }
    write_outputs(meta, buckets, prior.get('skipped_urls', []))
    print(f"Reclassified from saved data -> Working: {prior.get('working',0)} | "
          f"DEAD: {len(buckets['dead'])} | Blocked/manual: {len(buckets['blocked'])}")
    print(f"Report: {REPORT_PATH}\nData:   {DATA_PATH}")


def main():
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--reclassify', action='store_true',
                    help='re-bucket the saved results with current rules; no network')
    args = ap.parse_args()

    if args.reclassify:
        reclassify_existing()
        return

    print("=" * 70)
    print("EXTERNAL LINKS CHECKER")
    print("=" * 70)

    print("\nExtracting external links from content...")
    external_links = extract_external_links('content/')
    total_links = sum(len(v) for v in external_links.values())

    all_urls = set()
    for links in external_links.values():
        for _t, _text, url in links:
            all_urls.add(url)

    skipped = {u for u in all_urls if any(s in u for s in EXCLUDE_SUBSTRINGS)}
    to_check = sorted(all_urls - skipped)
    print(f"Found {total_links} external links across {len(external_links)} files")
    print(f"Unique URLs: {len(all_urls)} | checking: {len(to_check)} | "
          f"skipped (Amazon/self, handled elsewhere): {len(skipped)}")

    url_status = check_links_parallel(to_check)

    buckets = {'working': [], 'dead': [], 'blocked': []}
    for filepath, links in external_links.items():
        for link_type, text, url in links:
            if url in skipped:
                continue
            status, error = url_status.get(url, (None, "Not checked"))
            buckets[classify(status, error)].append({
                'file': filepath, 'type': link_type, 'text': text,
                'url': url, 'status': status, 'error': error,
            })

    meta = {
        'date': date.today().isoformat(),
        'total_files': len(external_links),
        'total_links': total_links,
        'unique_urls_checked': len(to_check),
        'skipped_count': len(skipped),
    }
    write_outputs(meta, buckets, skipped)

    print("\n" + "=" * 70)
    print(f"Working: {len(buckets['working'])} | DEAD: {len(buckets['dead'])} | "
          f"Blocked/manual: {len(buckets['blocked'])} | Skipped: {len(skipped)}")
    print(f"Report: {REPORT_PATH}\nData:   {DATA_PATH}")


if __name__ == "__main__":
    main()
