#!/usr/bin/env python3
"""
Check for broken links to files in static directory from content files.
"""

import os
import re
from pathlib import Path
from collections import defaultdict
import json

# Directories to check
CONTENT_DIR = Path("content")
STATIC_DIR = Path("static")

# Patterns to find file references
PATTERNS = [
    # Markdown image syntax: ![alt](path)
    r'!\[([^\]]*)\]\(([^)]+\.(?:jpg|jpeg|png|gif|svg|webp|pdf|doc|docx|zip|mp3|mp4|ogg))\)',
    # Hugo figure shortcode: {{< figure src="path" >}}
    r'\{\{<\s*figure\s+src="([^"]+\.(?:jpg|jpeg|png|gif|svg|webp|pdf))"\s*[^>]*>\}\}',
    # HTML img tags: <img src="path">
    r'<img[^>]+src="([^"]+\.(?:jpg|jpeg|png|gif|svg|webp|pdf))"[^>]*>',
    # Markdown link syntax for files: [text](path.ext)
    r'\[([^\]]+)\]\(([^)]+\.(?:pdf|doc|docx|zip|mp3|mp4|ogg))\)',
    # HTML a tags for files: <a href="path.ext">
    r'<a[^>]+href="([^"]+\.(?:pdf|doc|docx|zip|mp3|mp4|ogg))"[^>]*>',
]

def normalize_path(path):
    """Normalize a file path from content to match static directory structure."""
    # Remove leading slashes
    path = path.lstrip('/')

    # Remove domain references
    path = re.sub(r'https?://[^/]+/', '', path)

    # Remove query strings and anchors
    path = re.sub(r'[?#].*$', '', path)

    return path

def find_file_references(content_file):
    """Find all file references in a content file."""
    references = []

    try:
        with open(content_file, 'r', encoding='utf-8') as f:
            content = f.read()

            for pattern in PATTERNS:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    # Extract the path (it might be in group 1 or 2 depending on pattern)
                    if len(match.groups()) == 1:
                        path = match.group(1)
                    else:
                        path = match.group(2)

                    references.append({
                        'original': path,
                        'normalized': normalize_path(path),
                        'match': match.group(0)
                    })
    except Exception as e:
        print(f"Error reading {content_file}: {e}")

    return references

def check_file_exists(normalized_path):
    """Check if a file exists in the static directory."""
    # Check exact path
    full_path = STATIC_DIR / normalized_path
    if full_path.exists():
        return True, str(full_path)

    # Check without wp-content/uploads prefix if present
    if normalized_path.startswith('wp-content/uploads/'):
        alt_path = normalized_path.replace('wp-content/uploads/', '')
        full_path = STATIC_DIR / alt_path
        if full_path.exists():
            return True, str(full_path)

    return False, None

def main():
    print("Scanning content files for file references...")

    all_references = defaultdict(list)
    broken_links = []
    working_links = []
    external_links = []

    # Find all markdown files
    md_files = list(CONTENT_DIR.rglob("*.md"))
    print(f"Found {len(md_files)} markdown files")

    for md_file in md_files:
        refs = find_file_references(md_file)
        if refs:
            all_references[str(md_file)] = refs

            for ref in refs:
                # Skip external URLs (http/https)
                if ref['original'].startswith(('http://', 'https://')):
                    # But check if it's a reference to joshuapsteele.com
                    if 'joshuapsteele.com' in ref['original']:
                        normalized = normalize_path(ref['original'])
                        exists, found_path = check_file_exists(normalized)

                        if not exists:
                            broken_links.append({
                                'file': str(md_file),
                                'original': ref['original'],
                                'normalized': normalized,
                                'match': ref['match']
                            })
                        else:
                            working_links.append({
                                'file': str(md_file),
                                'original': ref['original'],
                                'found_at': found_path
                            })
                    else:
                        external_links.append({
                            'file': str(md_file),
                            'url': ref['original']
                        })
                    continue

                # Check if file exists
                exists, found_path = check_file_exists(ref['normalized'])

                if not exists:
                    broken_links.append({
                        'file': str(md_file),
                        'original': ref['original'],
                        'normalized': ref['normalized'],
                        'match': ref['match']
                    })
                else:
                    working_links.append({
                        'file': str(md_file),
                        'original': ref['original'],
                        'found_at': found_path
                    })

    # Generate report
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Total content files scanned: {len(md_files)}")
    print(f"Files with references: {len(all_references)}")
    print(f"Working local links: {len(working_links)}")
    print(f"Broken local links: {len(broken_links)}")
    print(f"External links: {len(external_links)}")

    # Save broken links to JSON
    output_file = "broken-static-links.json"
    with open(output_file, 'w') as f:
        json.dump({
            'summary': {
                'total_files': len(md_files),
                'files_with_refs': len(all_references),
                'working_links': len(working_links),
                'broken_links': len(broken_links),
                'external_links': len(external_links)
            },
            'broken_links': broken_links,
            'working_links': working_links[:50],  # First 50 for reference
        }, f, indent=2)

    print(f"\nDetailed report saved to: {output_file}")

    # Print broken links by file type
    if broken_links:
        print("\n" + "="*80)
        print("BROKEN LINKS BY FILE TYPE")
        print("="*80)

        by_extension = defaultdict(list)
        for link in broken_links:
            ext = Path(link['normalized']).suffix.lower()
            by_extension[ext].append(link)

        for ext in sorted(by_extension.keys()):
            print(f"\n{ext.upper()} files ({len(by_extension[ext])} broken):")
            for link in by_extension[ext][:10]:  # Show first 10
                print(f"  - {link['file']}")
                print(f"    Looking for: {link['normalized']}")
                print(f"    Original: {link['original'][:80]}")

            if len(by_extension[ext]) > 10:
                print(f"  ... and {len(by_extension[ext]) - 10} more")

    # Print most affected files
    if broken_links:
        print("\n" + "="*80)
        print("MOST AFFECTED FILES (Top 20)")
        print("="*80)

        by_file = defaultdict(int)
        for link in broken_links:
            by_file[link['file']] += 1

        for file, count in sorted(by_file.items(), key=lambda x: x[1], reverse=True)[:20]:
            print(f"  {count:3d} broken links: {file}")

if __name__ == "__main__":
    main()
