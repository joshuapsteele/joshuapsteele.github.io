#!/usr/bin/env python3
"""
Display batches of posts needing better descriptions for manual review.
"""

import sys
import yaml
import re
from pathlib import Path


def extract_frontmatter_and_body(content: str):
    """Extract YAML front matter and body content."""
    pattern = r'^---\s*\n(.*?\n)---\s*\n(.*)$'
    match = re.match(pattern, content, re.DOTALL)

    if not match:
        return {}, content

    yaml_str = match.group(1)
    body = match.group(2)

    try:
        frontmatter = yaml.safe_load(yaml_str)
        if frontmatter is None:
            frontmatter = {}
    except yaml.YAMLError:
        frontmatter = {}

    return frontmatter, body


def clean_text(text: str, max_chars: int = 400) -> str:
    """Clean markdown text for preview."""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    # Remove markdown links but keep text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    # Remove markdown images
    text = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', '', text)
    # Remove markdown headings markers
    text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
    # Remove code blocks
    text = re.sub(r'```.*?```', ' ', text, flags=re.DOTALL)
    text = re.sub(r'`[^`]+`', ' ', text)
    # Remove multiple spaces/newlines
    text = re.sub(r'\s+', ' ', text)

    return text.strip()[:max_chars]


def show_batch(filenames: list, start_idx: int, batch_size: int = 10):
    """Show a batch of posts."""
    content_dir = Path('content/blog')
    end_idx = min(start_idx + batch_size, len(filenames))

    print(f"\n{'='*80}")
    print(f"BATCH {start_idx//batch_size + 1}: Posts {start_idx+1}-{end_idx} of {len(filenames)}")
    print(f"{'='*80}\n")

    for i in range(start_idx, end_idx):
        filename = filenames[i]
        filepath = content_dir / filename

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            frontmatter, body = extract_frontmatter_and_body(content)

            title = frontmatter.get('title', 'Untitled')
            current_desc = frontmatter.get('description', '')
            categories = frontmatter.get('categories', [])
            tags = frontmatter.get('tags', [])

            preview = clean_text(body, max_chars=300)

            print(f"{i+1}. {filename}")
            print(f"   Title: {title}")
            print(f"   Categories: {', '.join(categories) if categories else 'None'}")
            if tags:
                print(f"   Tags: {', '.join(tags[:5])}{'...' if len(tags) > 5 else ''}")
            print(f"   Current: {current_desc}")
            print(f"   Preview: {preview}...")
            print()

        except Exception as e:
            print(f"{i+1}. {filename} - ERROR: {e}\n")


def main():
    # Read the list of files
    with open('/tmp/generic_desc_posts.txt', 'r') as f:
        filenames = [line.strip() for line in f if line.strip()]

    if len(sys.argv) > 1:
        batch_num = int(sys.argv[1])
        start_idx = (batch_num - 1) * 10
    else:
        start_idx = 0

    show_batch(filenames, start_idx, batch_size=10)

    total_batches = (len(filenames) + 9) // 10
    print(f"\n{'='*80}")
    print(f"To see next batch, run: python3 show_posts_batch.py {(start_idx//10) + 2}")
    print(f"Total batches: {total_batches} ({len(filenames)} posts)")
    print(f"{'='*80}\n")


if __name__ == '__main__':
    main()
