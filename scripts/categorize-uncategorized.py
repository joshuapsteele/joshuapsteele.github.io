#!/usr/bin/env python3
"""
Automatically categorize uncategorized posts based on content analysis
"""

import os
import frontmatter
import re
from collections import defaultdict
import sys

# Define keyword patterns for each category
CATEGORY_KEYWORDS = {
    'theology': [
        'god', 'jesus', 'christ', 'holy spirit', 'trinity', 'gospel', 'salvation',
        'barth', 'bonhoeffer', 'theology', 'theological', 'church dogmatics',
        'scripture', 'bible', 'biblical', 'sermon', 'homily', 'liturgy',
        'doctrine', 'dogma', 'ecclesiology', 'christology', 'pneumatology',
        'prayer', 'worship', 'faith', 'grace', 'redemption', 'covenant'
    ],
    'ethics': [
        'politics', 'political', 'immigration', 'immigrant', 'refugee',
        'romans 13', 'justice', 'injustice', 'racism', 'racist', 'fascism',
        'authoritarianism', 'democracy', 'tyranny', 'ethics', 'ethical',
        'christian nationalism', 'social justice', 'human rights', 'dignity',
        'trump', 'election', 'vote', 'voting', 'government', 'policy'
    ],
    'ministry': [
        'ministry', 'minister', 'pastor', 'pastoral', 'priest', 'clergy',
        'ordination', 'ordained', 'acna', 'anglican', 'anglicanism', 'church',
        "women's ordination", 'egalitarian', 'complementarian', 'mutualist',
        'diocese', 'bishop', 'deacon', 'preaching', 'congregation'
    ],
    'personal': [
        'family', 'wife', 'husband', 'kids', 'children', 'son', 'daughter',
        'father', 'mother', 'parent', 'parenting', 'marriage', 'married',
        'birthday', 'anniversary', 'personal', 'life update', 'reflection',
        'cedarville', 'seminary', 'student', 'graduation', 'moving'
    ],
    'productivity': [
        'productivity', 'gtd', 'getting things done', 'time management',
        'software', 'coding', 'programming', 'developer', 'engineer',
        'bootcamp', 'python', 'javascript', 'react', 'code', 'app',
        'tool', 'workflow', 'efficiency', 'organization', 'system',
        'evernote', 'notion', 'obsidian', 'markdown', 'podcast', 'book review'
    ],
    'dissertation': [
        'dissertation', 'phd', 'doctoral', 'research', 'colloquium',
        'barth conference', 'thesis', 'römerbrief', 'church dogmatics volume'
    ]
}

def analyze_content(title, description, content, tags):
    """Analyze post content and suggest category"""
    
    # Combine all text for analysis (lowercase for matching)
    full_text = f"{title} {description} {content}".lower()
    
    # Handle tags safely
    if tags:
        if isinstance(tags, list):
            tag_text = " ".join(str(t) for t in tags)
        else:
            tag_text = str(tags)
        full_text += " " + tag_text.lower()
    
    # Score each category based on keyword matches
    scores = defaultdict(int)
    
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            # Count occurrences of each keyword
            count = full_text.count(keyword.lower())
            if count > 0:
                # Weight by keyword importance (longer phrases = more weight)
                weight = len(keyword.split())
                scores[category] += count * weight
    
    # Special rules for better accuracy
    
    # If it mentions dissertation/phd prominently, likely dissertation
    if any(word in full_text for word in ['dissertation', 'phd', 'doctoral']):
        scores['dissertation'] += 10
    
    # If it's about Barth/Bonhoeffer and research, likely dissertation
    if ('barth' in full_text or 'bonhoeffer' in full_text) and 'research' in full_text:
        scores['dissertation'] += 5
    
    # Immigration + Christian = ethics (not just theology)
    if 'immigration' in full_text or 'immigrant' in full_text:
        scores['ethics'] += 10
    
    # Romans 13 posts are ethics (political theology)
    if 'romans 13' in full_text:
        scores['ethics'] += 10
    
    # Software/coding clearly productivity
    if any(word in full_text for word in ['software', 'coding', 'programming', 'developer']):
        scores['productivity'] += 5
    
    # Family/kids = personal
    if any(word in full_text for word in ['family', 'wife', 'kids', 'children', 'marriage']):
        scores['personal'] += 5
    
    # Get top scoring categories
    if scores:
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_scores[0][0], dict(scores)  # Return best match and scores dict

    return None, {}

def categorize_uncategorized_posts(content_dir, dry_run=True):
    """Find and categorize posts without categories"""
    
    uncategorized = []
    changes = []
    
    # Find uncategorized posts
    for root, dirs, files in os.walk(content_dir):
        for filename in files:
            if not filename.endswith('.md'):
                continue
            
            filepath = os.path.join(root, filename)
            rel_path = filepath.replace(content_dir + '/', '')
            
            # Skip special pages
            if any(x in filepath for x in ['search.md', 'files.md', 'archives.md']):
                continue
            
            try:
                post = frontmatter.load(filepath)
                
                # Check if post has no category or empty category
                needs_category = False
                if 'categories' not in post:
                    needs_category = True
                elif post['categories'] is None:
                    needs_category = True
                elif isinstance(post['categories'], list) and len(post['categories']) == 0:
                    needs_category = True
                
                if needs_category:
                    # Analyze content to suggest category
                    title = post.get('title', '')
                    description = post.get('description', '')
                    content = post.content[:1000]  # First 1000 chars
                    tags = post.get('tags', [])
                    
                    suggested_cat, scores = analyze_content(title, description, content, tags)
                    
                    if suggested_cat:
                        changes.append({
                            'file': rel_path,
                            'title': title,
                            'suggested': suggested_cat,
                            'confidence': scores[suggested_cat] if scores else 0,
                            'all_scores': dict(scores)
                        })
                        
                        if not dry_run:
                            post['categories'] = suggested_cat
                            with open(filepath, 'wb') as f:
                                frontmatter.dump(post, f)
                    else:
                        uncategorized.append({
                            'file': rel_path,
                            'title': title
                        })
            
            except Exception as e:
                print(f"Error processing {rel_path}: {e}")
    
    return changes, uncategorized

def main():
    dry_run = '--apply' not in sys.argv
    
    if dry_run:
        print("=" * 70)
        print("DRY RUN MODE - Analyzing uncategorized posts")
        print("Run with --apply flag to make actual changes")
        print("=" * 70)
    else:
        print("=" * 70)
        print("CATEGORIZING UNCATEGORIZED POSTS")
        print("=" * 70)
    
    print("\n🔍 Analyzing posts without categories...")
    changes, still_uncategorized = categorize_uncategorized_posts('content/', dry_run)
    
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    
    print(f"\n📊 Statistics:")
    print(f"  Posts analyzed: {len(changes) + len(still_uncategorized)}")
    print(f"  Categories suggested: {len(changes)}")
    print(f"  Still need manual review: {len(still_uncategorized)}")
    
    if changes:
        print(f"\n📝 Suggested categorizations:")
        
        # Group by category
        by_category = defaultdict(list)
        for change in changes:
            by_category[change['suggested']].append(change)
        
        for category in sorted(by_category.keys()):
            items = by_category[category]
            print(f"\n  {category.upper()} ({len(items)} posts):")
            for item in items[:5]:  # Show first 5 of each category
                conf = item['confidence']
                print(f"    [{conf:2d}] {item['file']}")
                title_display = item['title'][:60] + "..." if len(item['title']) > 60 else item['title']
                print(f"         \"{title_display}\"")
            
            if len(items) > 5:
                print(f"    ... and {len(items) - 5} more")
    
    if still_uncategorized:
        print(f"\n⚠️  Posts needing manual categorization ({len(still_uncategorized)}):")
        for item in still_uncategorized[:10]:
            print(f"    - {item['file']}")
            print(f"      \"{item['title']}\"")
        
        if len(still_uncategorized) > 10:
            print(f"    ... and {len(still_uncategorized) - 10} more")
    
    if dry_run:
        print("\n" + "=" * 70)
        print("To apply these changes, run:")
        print("  python3 categorize-uncategorized.py --apply")
        print("=" * 70)
    else:
        print("\n" + "=" * 70)
        print("✅ CATEGORIZATION COMPLETE")
        print("=" * 70)
        print("\nNext steps:")
        print("  1. Review changes: git diff")
        print("  2. Test locally: npm run dev")
        print("  3. Manually categorize remaining posts if needed")

if __name__ == "__main__":
    main()
