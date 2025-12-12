#!/usr/bin/env python3
"""
Convert all tags and categories to kebab-case format.

This script:
1. Scans all blog posts for tags/categories with spaces or capitals
2. Converts them to kebab-case (lowercase with hyphens)
3. Updates the frontmatter in place
4. Generates a report of changes made

Usage:
    python3 scripts/convert-taxonomy-to-kebab-case.py --dry-run  # Preview changes
    python3 scripts/convert-taxonomy-to-kebab-case.py             # Apply changes
"""

import re
import glob
import argparse
from pathlib import Path
from collections import defaultdict

def to_kebab_case(text):
    """Convert text to kebab-case: lowercase with hyphens"""
    # Replace spaces and underscores with hyphens
    text = re.sub(r'[\s_]+', '-', text)
    # Convert to lowercase
    text = text.lower()
    # Remove any characters that aren't alphanumeric or hyphens
    text = re.sub(r'[^a-z0-9-]', '', text)
    # Remove multiple consecutive hyphens
    text = re.sub(r'-+', '-', text)
    # Remove leading/trailing hyphens
    text = text.strip('-')
    return text

def needs_conversion(term):
    """Check if a term needs to be converted to kebab-case"""
    if not term:
        return False
    kebab = to_kebab_case(term)
    return term != kebab

def extract_taxonomy(content):
    """Extract tags and categories from frontmatter"""
    tags_match = re.search(r'^tags:\s*\[(.*?)\]', content, re.MULTILINE | re.DOTALL)
    cats_match = re.search(r'^categories:\s*\[(.*?)\]', content, re.MULTILINE | re.DOTALL)

    tags = []
    categories = []

    if tags_match:
        tag_str = tags_match.group(1)
        tags = [t.strip().strip('"').strip("'") for t in re.split(r',\s*', tag_str) if t.strip()]

    if cats_match:
        cat_str = cats_match.group(1)
        categories = [c.strip().strip('"').strip("'") for c in re.split(r',\s*', cat_str) if c.strip()]

    return tags, categories

def convert_taxonomy_line(line, term_type):
    """Convert a tags: or categories: line to kebab-case"""
    # Extract the array content
    match = re.match(rf'^({term_type}):\s*\[(.*?)\]\s*$', line)
    if not match:
        return line

    prefix = match.group(1)
    content = match.group(2)

    # Parse terms (handling quotes)
    terms = [t.strip().strip('"').strip("'") for t in re.split(r',\s*', content) if t.strip()]

    # Convert to kebab-case
    converted_terms = [to_kebab_case(t) for t in terms]

    # Rebuild line (no quotes needed for kebab-case)
    if converted_terms:
        return f"{prefix}: [{', '.join(converted_terms)}]\n"
    else:
        return f"{prefix}: []\n"

def process_file(filepath, dry_run=False):
    """Process a single markdown file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return None, f"Error reading: {e}"

    # Track changes
    changes = {'tags': {}, 'categories': {}}
    original_content = content

    # Extract current taxonomy
    tags, categories = extract_taxonomy(content)

    # Check if any terms need conversion
    tags_to_convert = {t: to_kebab_case(t) for t in tags if needs_conversion(t)}
    cats_to_convert = {c: to_kebab_case(c) for c in categories if needs_conversion(c)}

    if not tags_to_convert and not cats_to_convert:
        return None, "No changes needed"

    # Convert taxonomy lines
    lines = content.split('\n')
    new_lines = []

    for line in lines:
        if line.strip().startswith('tags:'):
            new_line = convert_taxonomy_line(line, 'tags')
            new_lines.append(new_line)
            if new_line != line:
                changes['tags'] = tags_to_convert
        elif line.strip().startswith('categories:'):
            new_line = convert_taxonomy_line(line, 'categories')
            new_lines.append(new_line)
            if new_line != line:
                changes['categories'] = cats_to_convert
        else:
            new_lines.append(line)

    new_content = '\n'.join(new_lines)

    # Write if not dry run
    if not dry_run and new_content != original_content:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
        except Exception as e:
            return None, f"Error writing: {e}"

    return changes, "Success"

def main():
    parser = argparse.ArgumentParser(description='Convert taxonomy to kebab-case')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without applying')
    args = parser.parse_args()

    print("=" * 70)
    print("TAXONOMY KEBAB-CASE CONVERSION")
    print("=" * 70)

    if args.dry_run:
        print("\n🔍 DRY RUN MODE - No files will be modified\n")
    else:
        print("\n✏️  LIVE MODE - Files will be modified\n")

    # Process all blog posts
    files = glob.glob('content/blog/*.md')
    files.sort()

    total_files = 0
    modified_files = 0
    all_tag_changes = defaultdict(set)
    all_cat_changes = defaultdict(set)

    print(f"Processing {len(files)} files...\n")

    for filepath in files:
        total_files += 1
        changes, status = process_file(filepath, dry_run=args.dry_run)

        if changes:
            modified_files += 1
            filename = Path(filepath).name

            print(f"📝 {filename}")

            if changes['tags']:
                print("   Tags:")
                for old, new in changes['tags'].items():
                    print(f"      '{old}' → '{new}'")
                    all_tag_changes[old].add(new)

            if changes['categories']:
                print("   Categories:")
                for old, new in changes['categories'].items():
                    print(f"      '{old}' → '{new}'")
                    all_cat_changes[old].add(new)

            print()

    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total files processed: {total_files}")
    print(f"Files modified: {modified_files}")
    print(f"Files unchanged: {total_files - modified_files}")

    if all_tag_changes:
        print(f"\nTag conversions ({len(all_tag_changes)} unique):")
        for old, new_set in sorted(all_tag_changes.items()):
            new = next(iter(new_set))
            print(f"  '{old}' → '{new}'")

    if all_cat_changes:
        print(f"\nCategory conversions ({len(all_cat_changes)} unique):")
        for old, new_set in sorted(all_cat_changes.items()):
            new = next(iter(new_set))
            print(f"  '{old}' → '{new}'")

    if args.dry_run:
        print("\n" + "=" * 70)
        print("This was a DRY RUN. Run without --dry-run to apply changes.")
        print("=" * 70)
    else:
        print("\n" + "=" * 70)
        print("✅ Conversion complete! Please review changes with 'git diff'")
        print("=" * 70)

if __name__ == '__main__':
    main()
