#!/usr/bin/env python3
"""
Hugo Blog Front Matter Cleanup Script

Removes legacy WordPress/Avada theme front matter from markdown files
while preserving essential Hugo metadata.

Usage:
    python cleanup_frontmatter.py --dry-run  # Test mode (no changes)
    python cleanup_frontmatter.py            # Apply changes
"""

import os
import re
import yaml
from pathlib import Path
from typing import Dict, List, Any, Tuple
import argparse


# Fields to remove (legacy WordPress/Avada fields)
FIELDS_TO_REMOVE = [
    # Prefixes - remove all fields starting with these
    'pyre_', 'avada_', 'fusion_', 'kd_',
    # Specific standalone fields
    'guid', 'id', 'custom_permalink', 'total_sidebar_layout', 'enclosure'
]

# Fields to keep (Hugo essentials)
FIELDS_TO_KEEP = [
    'title', 'date', 'author', 'categories', 'tags',
    'description', 'url', 'draft'
]

# Special files to exclude
EXCLUDE_FILES = ['_index.md', 'archives.md', 'search.md']


def should_remove_field(field_name: str) -> bool:
    """Check if a field should be removed."""
    # Check exact matches
    if field_name in ['guid', 'id', 'custom_permalink', 'total_sidebar_layout', 'enclosure']:
        return True

    # Check prefixes
    for prefix in ['pyre_', 'avada_', 'fusion_', 'kd_']:
        if field_name.startswith(prefix):
            return True

    return False


def extract_frontmatter(content: str) -> Tuple[Dict[str, Any], str, int, int]:
    """
    Extract YAML front matter from markdown content.

    Returns:
        tuple: (frontmatter_dict, body_content, start_line, end_line)
    """
    # Match YAML front matter between --- delimiters
    pattern = r'^---\s*\n(.*?\n)---\s*\n(.*)$'
    match = re.match(pattern, content, re.DOTALL)

    if not match:
        return {}, content, 0, 0

    yaml_content = match.group(1)
    body_content = match.group(2)

    # Parse YAML
    try:
        frontmatter = yaml.safe_load(yaml_content)
        if frontmatter is None:
            frontmatter = {}
    except yaml.YAMLError as e:
        print(f"Warning: YAML parsing error: {e}")
        frontmatter = {}

    # Count lines
    start_line = 0
    end_line = yaml_content.count('\n') + 2  # +2 for the two --- lines

    return frontmatter, body_content, start_line, end_line


def clean_frontmatter(frontmatter: Dict[str, Any]) -> Dict[str, Any]:
    """Clean and standardize front matter."""
    cleaned = {}

    # Process each field
    for key, value in frontmatter.items():
        if should_remove_field(key):
            continue  # Skip legacy fields

        # Skip fields with None or empty string values (except description which we add later)
        if value is None or value == '':
            continue

        # Keep this field
        cleaned[key] = value

    # Ensure required fields exist
    if 'description' not in cleaned:
        cleaned['description'] = ""

    # Ensure categories and tags are lists
    if 'categories' in cleaned:
        if isinstance(cleaned['categories'], str):
            cleaned['categories'] = [cleaned['categories']]
        elif cleaned['categories'] is None:
            cleaned['categories'] = []

    if 'tags' in cleaned:
        if isinstance(cleaned['tags'], str):
            cleaned['tags'] = [cleaned['tags']]
        elif cleaned['tags'] is None:
            cleaned['tags'] = []

    return cleaned


def order_frontmatter(frontmatter: Dict[str, Any]) -> Dict[str, Any]:
    """Order front matter fields in a standardized way."""
    ordered = {}

    # Define the order
    field_order = ['title', 'date', 'author', 'categories', 'tags', 'description', 'url', 'draft']

    # Add fields in order
    for field in field_order:
        if field in frontmatter:
            ordered[field] = frontmatter[field]

    # Add any remaining fields
    for key, value in frontmatter.items():
        if key not in ordered:
            ordered[key] = value

    return ordered


def format_yaml(data: Dict[str, Any]) -> str:
    """Format dictionary as YAML with proper styling."""
    # Use PyYAML to dump with proper formatting
    yaml_str = yaml.dump(
        data,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,
        width=1000  # Prevent line wrapping
    )

    # Clean up empty values
    yaml_str = re.sub(r'^(\w+):\s*null\s*$', r'\1:', yaml_str, flags=re.MULTILINE)

    return yaml_str


def process_file(filepath: Path, dry_run: bool = False) -> Dict[str, Any]:
    """
    Process a single markdown file.

    Returns:
        dict: Statistics about the processing
    """
    stats = {
        'file': str(filepath),
        'processed': False,
        'fields_removed': 0,
        'fields_kept': 0,
        'description_added': False,
        'error': None
    }

    try:
        # Read file
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract front matter
        frontmatter, body, _, _ = extract_frontmatter(content)

        if not frontmatter:
            stats['error'] = "No front matter found"
            return stats

        original_field_count = len(frontmatter)

        # Clean front matter
        cleaned = clean_frontmatter(frontmatter)
        ordered = order_frontmatter(cleaned)

        # Calculate stats
        stats['fields_removed'] = original_field_count - len(cleaned)
        stats['fields_kept'] = len(cleaned)
        stats['description_added'] = 'description' not in frontmatter and 'description' in cleaned
        stats['processed'] = True

        # Write back if not dry run
        if not dry_run and stats['fields_removed'] > 0:
            # Format new content
            yaml_str = format_yaml(ordered)
            new_content = f"---\n{yaml_str}---\n{body}"

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)

    except Exception as e:
        stats['error'] = str(e)

    return stats


def find_markdown_files(content_dir: Path) -> List[Path]:
    """Find all markdown files in content directory, excluding special files."""
    md_files = []

    for root, dirs, files in os.walk(content_dir):
        for file in files:
            if file.endswith('.md') and file not in EXCLUDE_FILES:
                md_files.append(Path(root) / file)

    return md_files


def main():
    parser = argparse.ArgumentParser(description='Clean Hugo blog front matter')
    parser.add_argument('--dry-run', action='store_true',
                       help='Run in test mode without making changes')
    parser.add_argument('--content-dir', default='content',
                       help='Content directory to process (default: content)')
    args = parser.parse_args()

    content_dir = Path(args.content_dir)

    if not content_dir.exists():
        print(f"Error: Content directory '{content_dir}' not found")
        return

    print(f"{'='*60}")
    print(f"Hugo Front Matter Cleanup Script")
    print(f"Mode: {'DRY RUN (no changes)' if args.dry_run else 'LIVE (making changes)'}")
    print(f"Directory: {content_dir}")
    print(f"{'='*60}\n")

    # Find all markdown files
    md_files = find_markdown_files(content_dir)
    print(f"Found {len(md_files)} markdown files\n")

    # Process files
    all_stats = []
    files_with_changes = []
    files_with_errors = []
    files_needing_descriptions = []

    for filepath in md_files:
        stats = process_file(filepath, dry_run=args.dry_run)
        all_stats.append(stats)

        if stats['error']:
            files_with_errors.append(stats)
        elif stats['fields_removed'] > 0:
            files_with_changes.append(stats)
            if stats['description_added']:
                files_needing_descriptions.append(stats)

    # Print summary
    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"Total files processed: {len(md_files)}")
    print(f"Files with changes: {len(files_with_changes)}")
    print(f"Files with errors: {len(files_with_errors)}")
    print(f"Files needing description text: {len(files_needing_descriptions)}")

    if files_with_changes:
        total_removed = sum(s['fields_removed'] for s in files_with_changes)
        avg_removed = total_removed / len(files_with_changes)
        print(f"\nTotal fields removed: {total_removed}")
        print(f"Average fields removed per file: {avg_removed:.1f}")

    # Show files with most cleanup
    if files_with_changes:
        print(f"\n{'='*60}")
        print(f"Top 10 files with most cleanup:")
        print(f"{'='*60}")
        sorted_changes = sorted(files_with_changes,
                               key=lambda x: x['fields_removed'],
                               reverse=True)[:10]
        for stat in sorted_changes:
            filename = Path(stat['file']).name
            print(f"  {filename}: {stat['fields_removed']} fields removed")

    # Show errors
    if files_with_errors:
        print(f"\n{'='*60}")
        print(f"Files with errors:")
        print(f"{'='*60}")
        for stat in files_with_errors:
            filename = Path(stat['file']).name
            print(f"  {filename}: {stat['error']}")

    # Show files needing descriptions
    if files_needing_descriptions and not args.dry_run:
        print(f"\n{'='*60}")
        print(f"Files needing manual description (empty added):")
        print(f"{'='*60}")
        for stat in files_needing_descriptions[:20]:  # Show first 20
            filename = Path(stat['file']).name
            print(f"  {filename}")
        if len(files_needing_descriptions) > 20:
            print(f"  ... and {len(files_needing_descriptions) - 20} more")

    if args.dry_run:
        print(f"\n{'='*60}")
        print(f"DRY RUN COMPLETE - No changes were made")
        print(f"Run without --dry-run to apply changes")
        print(f"{'='*60}")
    else:
        print(f"\n{'='*60}")
        print(f"CLEANUP COMPLETE")
        print(f"{'='*60}")


if __name__ == '__main__':
    main()
