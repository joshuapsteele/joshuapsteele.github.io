#!/usr/bin/env python3
"""
Apply taxonomy consolidation based on taxonomy_map.yaml
Consolidates 24 categories into 6 core categories
"""

import os
import yaml
import frontmatter
from collections import defaultdict, Counter
import sys

def load_taxonomy_map(filename='taxonomy_map.yaml'):
    """Load the taxonomy mapping configuration"""
    with open(filename, 'r') as f:
        config = yaml.safe_load(f)
    return config['category_mapping'], config.get('tag_cleanup', {})

def process_categories(categories, mapping):
    """Apply category mapping to a list of categories"""
    if not categories:
        return None
    
    if isinstance(categories, str):
        categories = [categories]
    
    # Apply mapping
    new_categories = set()
    for cat in categories:
        mapped = mapping.get(cat)
        if mapped:
            new_categories.add(mapped)
        elif cat not in mapping:  # Category not in map, keep as-is
            new_categories.add(cat)
    
    # Remove None values
    new_categories.discard(None)
    
    # Return as list, or single string if only one category
    result = sorted(list(new_categories))
    return result[0] if len(result) == 1 else result

def process_tags(tags, tag_cleanup):
    """Apply tag cleanup/consolidation"""
    if not tags:
        return None
    
    if isinstance(tags, str):
        tags = [tags]
    
    new_tags = []
    for tag in tags:
        # Apply cleanup mapping
        new_tag = tag_cleanup.get(tag, tag)
        if new_tag and new_tag not in new_tags:
            new_tags.append(new_tag)
    
    return new_tags if new_tags else None

def apply_taxonomy(content_dir, category_mapping, tag_cleanup, dry_run=True):
    """Apply taxonomy changes to all posts"""
    changes = []
    stats = {
        'total_files': 0,
        'files_changed': 0,
        'categories_updated': 0,
        'tags_updated': 0,
        'errors': []
    }
    
    for root, dirs, files in os.walk(content_dir):
        for filename in files:
            if not filename.endswith('.md'):
                continue
                
            filepath = os.path.join(root, filename)
            rel_path = filepath.replace(content_dir + '/', '')
            stats['total_files'] += 1
            
            try:
                post = frontmatter.load(filepath)
                file_changed = False
                change_details = {'file': rel_path, 'changes': []}
                
                # Process categories
                if 'categories' in post:
                    old_cats = post['categories']
                    new_cats = process_categories(old_cats, category_mapping)
                    
                    if new_cats != old_cats:
                        change_details['changes'].append({
                            'field': 'categories',
                            'old': old_cats,
                            'new': new_cats
                        })
                        
                        if not dry_run:
                            post['categories'] = new_cats
                        
                        file_changed = True
                        stats['categories_updated'] += 1
                
                # Process tags
                if 'tags' in post and tag_cleanup:
                    old_tags = post['tags']
                    new_tags = process_tags(old_tags, tag_cleanup)
                    
                    if new_tags != old_tags:
                        change_details['changes'].append({
                            'field': 'tags',
                            'old': old_tags,
                            'new': new_tags
                        })
                        
                        if not dry_run:
                            post['tags'] = new_tags
                        
                        file_changed = True
                        stats['tags_updated'] += 1
                
                # Save changes
                if file_changed:
                    changes.append(change_details)
                    stats['files_changed'] += 1
                    
                    if not dry_run:
                        with open(filepath, 'wb') as f:
                            frontmatter.dump(post, f)
                
            except Exception as e:
                stats['errors'].append(f"{rel_path}: {str(e)}")
    
    return changes, stats

def main():
    dry_run = '--apply' not in sys.argv
    
    if dry_run:
        print("=" * 70)
        print("DRY RUN MODE - No files will be modified")
        print("Run with --apply flag to make actual changes")
        print("=" * 70)
    else:
        print("=" * 70)
        print("APPLYING TAXONOMY CHANGES")
        print("=" * 70)
    
    # Load taxonomy map
    print("\n📋 Loading taxonomy map...")
    category_mapping, tag_cleanup = load_taxonomy_map()
    
    print(f"\nCategory mappings loaded:")
    unique_targets = set(v for v in category_mapping.values() if v)
    print(f"  Consolidating {len(category_mapping)} categories → {len(unique_targets)} core categories")
    print(f"  Core categories: {', '.join(sorted(unique_targets))}")
    
    if tag_cleanup:
        print(f"\nTag cleanup rules: {len(tag_cleanup)}")
    
    # Apply changes
    print(f"\n🔄 Processing content files...")
    changes, stats = apply_taxonomy('content/', category_mapping, tag_cleanup, dry_run)
    
    # Report results
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    
    print(f"\n📊 Statistics:")
    print(f"  Total files processed: {stats['total_files']}")
    print(f"  Files with changes: {stats['files_changed']}")
    print(f"  Categories updated: {stats['categories_updated']}")
    print(f"  Tags updated: {stats['tags_updated']}")
    
    if stats['errors']:
        print(f"\n⚠️  Errors: {len(stats['errors'])}")
        for error in stats['errors'][:5]:
            print(f"  - {error}")
    
    # Show sample changes
    if changes:
        print(f"\n📝 Sample changes (first 10):")
        for change in changes[:10]:
            print(f"\n  {change['file']}:")
            for c in change['changes']:
                print(f"    {c['field']}: {c['old']} → {c['new']}")
        
        if len(changes) > 10:
            print(f"\n  ... and {len(changes) - 10} more files")
    
    if dry_run:
        print("\n" + "=" * 70)
        print("To apply these changes, run: python3 apply-taxonomy.py --apply")
        print("=" * 70)
    else:
        print("\n" + "=" * 70)
        print("✅ CHANGES APPLIED SUCCESSFULLY")
        print("=" * 70)
        print("\nNext steps:")
        print("  1. Review changes: git diff")
        print("  2. Test locally: npm run dev")
        print("  3. If good: git commit and deploy")

if __name__ == "__main__":
    main()
