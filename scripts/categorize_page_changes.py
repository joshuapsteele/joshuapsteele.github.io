#!/usr/bin/env python3
"""
Categorize page description changes for review.
"""

import subprocess
import re
from pathlib import Path

def get_descriptions(filepath):
    """Get old and new descriptions for a file."""
    # Get old description from git
    try:
        old_content = subprocess.check_output(
            ['git', 'show', f'HEAD:{filepath}'],
            stderr=subprocess.DEVNULL
        ).decode('utf-8')
        old_match = re.search(r'^description:\s*(.*)$', old_content, re.MULTILINE)
        old_desc = old_match.group(1).strip() if old_match else ""
    except:
        old_desc = ""

    # Get new description from current file
    try:
        with open(filepath, 'r') as f:
            new_content = f.read()
        new_match = re.search(r'^description:\s*(.*)$', new_content, re.MULTILINE)
        new_desc = new_match.group(1).strip() if new_match else ""
    except:
        new_desc = ""

    return old_desc, new_desc

def categorize():
    """Categorize changes into groups."""
    pages_dir = Path('content/pages')

    generic = []
    broken_template = []
    slash_page = []
    acceptable = []

    for page in sorted(pages_dir.glob('*.md')):
        # Check if modified
        status = subprocess.check_output(['git', 'status', '--short', str(page)]).decode('utf-8')
        if not status.strip().startswith('M'):
            continue

        old_desc, new_desc = get_descriptions(str(page))

        # Categorize
        if new_desc == "A blog post by Joshua P. Steele.":
            generic.append((page.name, old_desc, new_desc))
        elif '{{ }}' in new_desc or '{{' in new_desc:
            broken_template.append((page.name, old_desc, new_desc))
        elif 'slash pages' in new_desc.lower():
            slash_page.append((page.name, old_desc, new_desc))
        elif new_desc and len(new_desc) > 20:
            acceptable.append((page.name, old_desc, new_desc))
        else:
            generic.append((page.name, old_desc, new_desc))

    return generic, broken_template, slash_page, acceptable

def main():
    generic, broken, slash, acceptable = categorize()

    print("="*80)
    print("AUTO-GENERATED PAGE DESCRIPTION REVIEW")
    print("="*80)
    print()

    print(f"📊 SUMMARY:")
    print(f"   ❌ Generic fallback: {len(generic)} pages")
    print(f"   🔧 Broken template syntax: {len(broken)} pages")
    print(f"   ⚠️  'Slash pages' generic: {len(slash)} pages")
    print(f"   ✅ Acceptable: {len(acceptable)} pages")
    print(f"   📝 Total: {len(generic) + len(broken) + len(slash) + len(acceptable)} pages")
    print()

    if generic:
        print("❌ GENERIC FALLBACK (needs manual descriptions):")
        for name, old, new in generic:
            print(f"   • {name}")
        print()

    if broken:
        print("🔧 BROKEN TEMPLATE SYNTAX (needs fixing):")
        for name, old, new in broken[:5]:
            print(f"   • {name}")
            print(f"     NEW: {new[:100]}...")
        if len(broken) > 5:
            print(f"   ... and {len(broken) - 5} more")
        print()

    if slash:
        print("⚠️  'SLASH PAGES' GENERIC (consider improving):")
        for name, old, new in slash[:5]:
            print(f"   • {name}")
            print(f"     NEW: {new[:100]}...")
        if len(slash) > 5:
            print(f"   ... and {len(slash) - 5} more")
        print()

    if acceptable:
        print("✅ ACCEPTABLE (might be okay as-is):")
        for name, old, new in acceptable:
            print(f"   • {name}: {new[:80]}...")
        print()

    print("="*80)
    print("RECOMMENDATION:")
    print("="*80)
    print("These auto-generated descriptions need review. Options:")
    print("1. Discard all changes: git checkout content/pages/*.md content/files.md")
    print("2. Fix manually before committing")
    print("3. Commit as-is and improve later")
    print()

if __name__ == '__main__':
    main()
