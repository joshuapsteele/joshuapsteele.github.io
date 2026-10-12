#!/usr/bin/env python3
"""Validate production links, assets, social metadata, and feeds without network access.

Run after a clean production build. Deliberately never accepts source Markdown
as evidence that a URL is published. Fragments and CSS URLs are not checked.
"""
import argparse
from collections import Counter
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit
import xml.etree.ElementTree as ET

HOSTS = {'joshuapsteele.com', 'www.joshuapsteele.com', 'joshuapsteele.github.io'}
SINGLE_META = {'og:title', 'og:url', 'og:type', 'og:description', 'og:site_name',
               'twitter:card', 'twitter:title', 'twitter:description', 'twitter:image'}

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs = []
        self.meta = Counter()
        self.styles = []
        self.preloads = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'meta':
            self.meta[a.get('property', a.get('name', ''))] += 1
        if tag == 'link':
            rel = a.get('rel', '').split()
            if 'stylesheet' in rel:
                self.styles.append(a.get('href', ''))
            if 'preload' in rel and a.get('as') == 'image':
                self.preloads.append(a.get('href', ''))
            if any(x in rel for x in ['stylesheet', 'icon', 'preload']):
                self.refs.append(a.get('href', ''))
        if tag == 'a':
            self.refs.append(a.get('href', ''))
        if tag in {'img', 'script', 'audio', 'video', 'source', 'iframe'}:
            self.refs.append(a.get('src', ''))
        if tag == 'video':
            self.refs.append(a.get('poster', ''))
        # Data URLs may contain commas; leave those srcsets to a browser validator.
        if tag in {'img', 'source'} and 'data:' not in a.get('srcset', ''):
            self.refs.extend(item.strip().split()[0] for item in a.get('srcset', '').split(',') if item.strip())


def check(root):
    errors = []
    html_files = sorted(root.rglob('*.html'))
    if not (root / 'index.html').is_file():
        return ['Missing production index.html; run npm run build first.']
    for file in html_files:
        page = Page()
        page.feed(file.read_text(encoding='utf-8'))
        source = file.relative_to(root).as_posix()
        # index.html is served at its parent directory URL.
        base = 'https://joshuapsteele.com/' + source.removesuffix('index.html')
        for ref in page.refs:
            if not ref or ref.startswith('#'):
                continue
            url = urlsplit(urljoin(base, ref))
            if url.scheme not in {'http', 'https'} or url.hostname not in HOSTS:
                continue
            target = root / unquote(url.path).lstrip('/')
            if not target.is_file() and not (target / 'index.html').is_file():
                errors.append(f'{source}: missing destination {ref}')
        for key in SINGLE_META:
            if page.meta[key] > 1:
                errors.append(f'{source}: duplicate {key}')
        if any('/css/extended/' in href for href in page.styles):
            errors.append(f'{source}: extended CSS loaded separately from theme bundle')
        if any('/images/default-social.png' in href for href in page.preloads):
            errors.append(f'{source}: unnecessary social-image preload')
    for file in sorted(root.rglob('*.json')):
        try:
            data = json.loads(file.read_text())
            if file.name == 'feed.json' and not isinstance(data.get('items'), list):
                errors.append(f'{file}: feed must have an items array')
        except (ValueError, AttributeError) as exc:
            errors.append(f'{file}: invalid JSON/feed: {exc}')
    for file in sorted(root.rglob('*.xml')):
        try:
            ET.parse(file)
        except ET.ParseError as exc:
            errors.append(f'{file}: invalid XML: {exc}')
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--public-dir', type=Path, default=Path('public'))
    args = parser.parse_args()
    errors = check(args.public_dir)
    for error in errors[:30]:
        print(error)
    if errors:
        print(f'FAIL: {len(errors)} rendered-site errors (first 30 shown).')
        return 1
    print('PASS: rendered internal links, assets, metadata, JSON and XML feeds.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
