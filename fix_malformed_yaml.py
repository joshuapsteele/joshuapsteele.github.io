#!/usr/bin/env python3
"""
Fix malformed YAML front matter where empty fields appear as `fieldname:---`
"""

import re
from pathlib import Path

def fix_file(filepath: Path) -> bool:
    """Fix malformed YAML in a single file. Returns True if changed."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Pattern to match lines like "fieldname:---" at the end of front matter
        # This captures cases where an empty field is immediately followed by the closing delimiter
        pattern = r'^([a-zA-Z_]+):\-\-\-$'

        original_content = content
        content = re.sub(pattern, r'---', content, flags=re.MULTILINE)

        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True

        return False

    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False

def main():
    content_dir = Path('content')
    md_files = list(content_dir.rglob('*.md'))

    fixed_count = 0
    for filepath in md_files:
        if fix_file(filepath):
            fixed_count += 1
            print(f"Fixed: {filepath.name}")

    print(f"\nFixed {fixed_count} files")

if __name__ == '__main__':
    main()
