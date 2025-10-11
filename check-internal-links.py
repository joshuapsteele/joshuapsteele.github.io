#!/usr/bin/env python3
"""
Check for broken internal links in markdown files.
Analyzes both markdown-style and HTML-style links.
"""

import os
import re
import frontmatter
from pathlib import Path
from collections import defaultdict
from urllib.parse import urlparse, unquote

def get_all_urls_and_paths(content_dir):
    """Build a map of all valid URLs and file paths in the site"""
    valid_urls = set()
    valid_paths = set()

    for root, dirs, files in os.walk(content_dir):
        for filename in files:
            if filename.endswith('.md'):
                filepath = os.path.join(root, filename)

                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        post = frontmatter.load(f)

                    # Add the file's URL if it has one
                    if 'url' in post:
                        url = post['url'].strip()
                        valid_urls.add(url)
                        valid_urls.add(url.rstrip('/'))  # Both with and without trailing slash
                        if not url.endswith('/'):
                            valid_urls.add(url + '/')

                    # Add aliases
                    if 'aliases' in post:
                        aliases = post['aliases']
                        if isinstance(aliases, str):
                            aliases = [aliases]
                        for alias in aliases:
                            alias = alias.strip()
                            valid_urls.add(alias)
                            valid_urls.add(alias.rstrip('/'))
                            if not alias.endswith('/'):
                                valid_urls.add(alias + '/')

                    # Add the relative file path
                    rel_path = os.path.relpath(filepath, content_dir)
                    valid_paths.add(rel_path)

                except Exception as e:
                    pass

    return valid_urls, valid_paths

def extract_links(content):
    """Extract all markdown and HTML links from content"""
    links = []

    # Markdown links: [text](url)
    md_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    for match in re.finditer(md_pattern, content):
        text = match.group(1)
        url = match.group(2)
        links.append({'type': 'markdown', 'text': text, 'url': url})

    # HTML links: <a href="url">
    html_pattern = r'<a\s+(?:[^>]*?\s+)?href=["\']([^"\']+)["\']'
    for match in re.finditer(html_pattern, content, re.IGNORECASE):
        url = match.group(1)
        links.append({'type': 'html', 'text': '', 'url': url})

    return links

def is_internal_link(url):
    """Check if a URL is an internal link"""
    # Skip external URLs
    if url.startswith(('http://', 'https://', '//')):
        parsed = urlparse(url)
        # Only consider it internal if it's explicitly joshuapsteele.com
        if 'joshuapsteele.com' in parsed.netloc or 'joshuapsteele.github.io' in parsed.netloc:
            return True
        return False

    # Skip anchors, mailto, and other special protocols
    if url.startswith(('#', 'mailto:', 'tel:', 'javascript:')):
        return False

    # Everything else starting with / or relative is internal
    if url.startswith('/') or not url.startswith(('http', '//')):
        return True

    return False

def normalize_url(url):
    """Normalize a URL for comparison"""
    # Remove query strings and fragments
    url = url.split('?')[0].split('#')[0]
    # URL decode
    url = unquote(url)
    # Normalize trailing slashes
    return url.rstrip('/')

def check_internal_links(content_dir):
    """Check all internal links in markdown files"""
    results = {
        'total_files': 0,
        'total_links': 0,
        'internal_links': 0,
        'broken_links': defaultdict(list),
        'working_links': 0,
        'files_with_broken_links': set(),
    }

    print("Building site URL map...")
    valid_urls, valid_paths = get_all_urls_and_paths(content_dir)
    print(f"Found {len(valid_urls)} valid URLs and {len(valid_paths)} valid paths")

    print("\nChecking internal links...")

    for root, dirs, files in os.walk(content_dir):
        for filename in files:
            if filename.endswith('.md'):
                filepath = os.path.join(root, filename)
                results['total_files'] += 1

                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    links = extract_links(content)

                    for link in links:
                        url = link['url']
                        results['total_links'] += 1

                        if not is_internal_link(url):
                            continue

                        results['internal_links'] += 1

                        # Normalize the URL
                        normalized = normalize_url(url)

                        # Check if it exists
                        is_valid = False

                        # Check against valid URLs
                        if normalized in valid_urls or (normalized + '/') in valid_urls:
                            is_valid = True

                        # Check for relative paths
                        if not is_valid and not url.startswith('/'):
                            # Try to resolve relative path
                            current_dir = os.path.dirname(filepath)
                            target_path = os.path.normpath(os.path.join(current_dir, url))
                            if os.path.exists(target_path):
                                is_valid = True

                        # Check for common patterns
                        if not is_valid:
                            # Remove leading slash for checking
                            check_url = normalized.lstrip('/')

                            # Check if it's a valid file reference
                            possible_paths = [
                                f"blog/{check_url}.md",
                                f"pages/{check_url}.md",
                                f"{check_url}.md",
                                check_url,
                            ]

                            for path in possible_paths:
                                full_path = os.path.join(content_dir, path)
                                if os.path.exists(full_path):
                                    is_valid = True
                                    break

                        if is_valid:
                            results['working_links'] += 1
                        else:
                            rel_filepath = os.path.relpath(filepath, content_dir)
                            results['broken_links'][rel_filepath].append({
                                'type': link['type'],
                                'text': link['text'],
                                'url': url,
                                'normalized': normalized
                            })
                            results['files_with_broken_links'].add(rel_filepath)

                except Exception as e:
                    print(f"Error processing {filepath}: {e}")

    return results

def main():
    print("=" * 80)
    print("INTERNAL LINK CHECK")
    print("=" * 80)
    print()

    results = check_internal_links('content/')

    # Print summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"\n📊 Files Analyzed: {results['total_files']}")
    print(f"🔗 Total Links Found: {results['total_links']}")
    print(f"🏠 Internal Links: {results['internal_links']}")
    print(f"✅ Working Internal Links: {results['working_links']}")
    print(f"❌ Broken Internal Links: {sum(len(v) for v in results['broken_links'].values())}")
    print(f"📄 Files with Broken Links: {len(results['files_with_broken_links'])}")

    # Save detailed results
    import json
    with open('audit-internal-links.json', 'w') as f:
        # Convert set to list for JSON serialization
        output = dict(results)
        output['files_with_broken_links'] = sorted(list(results['files_with_broken_links']))
        json.dump(output, f, indent=2, default=str)

    print(f"\n✅ Detailed results saved to: audit-internal-links.json")

    # Print broken links
    if results['broken_links']:
        print("\n" + "=" * 80)
        print("BROKEN LINKS BY FILE")
        print("=" * 80)

        for filepath in sorted(results['broken_links'].keys()):
            print(f"\n📄 {filepath}")
            for link in results['broken_links'][filepath]:
                print(f"   ❌ [{link['text']}]({link['url']})")
                if link['normalized'] != link['url']:
                    print(f"      (normalized: {link['normalized']})")

    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
