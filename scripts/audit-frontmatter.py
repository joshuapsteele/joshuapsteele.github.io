#!/usr/bin/env python3
"""
Analyze front matter across all markdown files.
Identifies missing fields, inconsistencies, and taxonomy issues.
"""

import os
import frontmatter
from collections import Counter, defaultdict
import json
import re

def analyze_frontmatter(content_dir):
    """Analyze front matter across all markdown files"""
    results = {
        'total_posts': 0,
        'missing_fields': defaultdict(list),
        'field_usage': Counter(),
        'posts_by_category': defaultdict(list),
        'posts_by_tag': defaultdict(list),
        'posts_without_categories': [],
        'posts_without_tags': [],
        'posts_without_description': [],
        'date_issues': [],
        'all_categories': set(),
        'all_tags': set(),
        'author_variants': set(),
        'draft_posts': [],
        'posts_with_aliases': [],
        'field_type_issues': [],
    }

    for root, dirs, files in os.walk(content_dir):
        for filename in files:
            if filename.endswith('.md'):
                filepath = os.path.join(root, filename)
                results['total_posts'] += 1

                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        post = frontmatter.load(f)

                    # Track which fields are used
                    for key in post.keys():
                        results['field_usage'][key] += 1

                    # Track authors
                    if 'author' in post:
                        results['author_variants'].add(str(post['author']))

                    # Check for drafts
                    if post.get('draft', False):
                        results['draft_posts'].append(filepath)

                    # Check for aliases
                    if 'aliases' in post:
                        results['posts_with_aliases'].append(filepath)

                    # Check categories
                    if 'categories' not in post or not post['categories']:
                        results['posts_without_categories'].append(filepath)
                    else:
                        # Handle both string and list categories
                        cats = post['categories']
                        if isinstance(cats, str):
                            cats = [cats]
                        elif not isinstance(cats, list):
                            cats = []

                        for cat in cats:
                            cat_str = str(cat).strip()
                            if cat_str:
                                results['all_categories'].add(cat_str)
                                results['posts_by_category'][cat_str].append(filepath)

                    # Check tags
                    if 'tags' not in post or not post['tags']:
                        results['posts_without_tags'].append(filepath)
                    else:
                        # Handle both string and list tags
                        tags = post['tags']
                        if isinstance(tags, str):
                            tags = [tags]
                        elif not isinstance(tags, list):
                            tags = []

                        for tag in tags:
                            tag_str = str(tag).strip()
                            if tag_str:
                                results['all_tags'].add(tag_str)
                                results['posts_by_tag'][tag_str].append(filepath)

                    # Check description
                    if 'description' not in post or not post['description']:
                        results['posts_without_description'].append(filepath)

                    # Check date
                    if 'date' not in post:
                        results['date_issues'].append(f"{filepath}: Missing date")
                    elif not post['date']:
                        results['date_issues'].append(f"{filepath}: Empty date")

                    # Track missing recommended fields
                    recommended = ['title', 'date', 'author', 'categories', 'tags', 'description']
                    for field in recommended:
                        if field not in post:
                            results['missing_fields'][field].append(filepath)

                except Exception as e:
                    results['date_issues'].append(f"{filepath}: Error parsing - {str(e)}")

    return results

def main():
    print("Analyzing front matter in content directory...")
    print("This may take a minute...\n")

    results = analyze_frontmatter('content/')

    # Convert sets to sorted lists for JSON serialization
    results['all_categories'] = sorted(list(results['all_categories']))
    results['all_tags'] = sorted(list(results['all_tags']))
    results['author_variants'] = sorted(list(results['author_variants']))

    # Save raw results
    with open('audit-frontmatter.json', 'w') as f:
        # Convert defaultdicts to dicts
        results_dict = {
            k: dict(v) if isinstance(v, defaultdict) else v
            for k, v in results.items()
        }
        json.dump(results_dict, f, indent=2, default=str)

    # Print summary
    print("=" * 80)
    print("FRONT MATTER AUDIT SUMMARY")
    print("=" * 80)
    print(f"\n📊 Total Posts Analyzed: {results['total_posts']}")

    print(f"\n❌ Missing Critical Fields:")
    print(f"   - Without categories: {len(results['posts_without_categories'])} posts")
    print(f"   - Without tags: {len(results['posts_without_tags'])} posts")
    print(f"   - Without description: {len(results['posts_without_description'])} posts")
    print(f"   - Date issues: {len(results['date_issues'])} posts")

    print(f"\n📁 Taxonomy Overview:")
    print(f"   - Total unique categories: {len(results['all_categories'])}")
    print(f"   - Total unique tags: {len(results['all_tags'])}")

    print(f"\n📝 Field Usage (Top 15):")
    for field, count in results['field_usage'].most_common(15):
        pct = (count / results['total_posts'] * 100)
        print(f"   - {field:<20} {count:>4} ({pct:>5.1f}%)")

    print(f"\n✍️  Author Variants: {', '.join(results['author_variants'])}")

    print(f"\n📄 Draft Posts: {len(results['draft_posts'])}")
    print(f"🔗 Posts with Aliases: {len(results['posts_with_aliases'])}")

    print(f"\n✅ Analysis complete!")
    print(f"   - Raw data: audit-frontmatter.json")
    print(f"   - Human report: Will be generated next...")
    print("=" * 80)

if __name__ == "__main__":
    main()
