#!/usr/bin/env python3
"""
Suggest relevant tags for posts based on content analysis
"""

import os
import frontmatter
import re
from collections import Counter
import json
import sys

# Tag vocabulary based on existing successful tags
TAG_PATTERNS = {
    # Theological themes
    'barth': ['barth', 'karl barth'],
    'bonhoeffer': ['bonhoeffer', 'dietrich bonhoeffer'],
    'theology': ['theology', 'theological', 'doctrine', 'dogma'],
    'bible': ['bible', 'biblical', 'scripture'],
    'church': ['church', 'ecclesiology'],
    'prayer': ['prayer', 'liturgy', 'worship'],
    
    # Political/Ethics themes  
    'immigration': ['immigration', 'immigrant', 'refugee'],
    'romans 13': ['romans 13', 'submission to authorities'],
    'fascism': ['fascism', 'fascist', 'ur-fascism'],
    'authoritarianism': ['authoritarianism', 'authoritarian', 'tyranny', 'tyrant'],
    'politics': ['politics', 'political'],
    'ethics': ['ethics', 'ethical', 'moral', 'morality'],
    'racism': ['racism', 'racist', 'anti-racism'],
    'justice': ['justice', 'injustice', 'social justice'],
    'christian nationalism': ['christian nationalism', 'christian nationalist'],
    
    # Ministry themes
    'anglican': ['anglican', 'anglicanism', 'acna'],
    "women's ordination": ["women's ordination", 'women priests', 'female ordination'],
    'ministry': ['ministry', 'pastoral', 'priest', 'clergy'],
    'preaching': ['preaching', 'sermon', 'homily'],
    
    # Academic/Research
    'research': ['research', 'dissertation', 'phd'],
    'writing': ['writing', 'author'],
    
    # Productivity/Tech
    'productivity': ['productivity', 'efficiency', 'gtd'],
    'coding': ['coding', 'programming', 'software'],
    'career': ['career', 'job', 'vocation'],
    
    # Personal
    'family': ['family', 'children', 'kids', 'parenting'],
    'books': ['book', 'reading', 'books'],
}

def extract_key_phrases(content):
    """Extract important phrases from content"""
    # Remove markdown/HTML
    content = re.sub(r'<[^>]+>', '', content)
    content = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', content)
    
    # Get word frequency
    words = re.findall(r'\b[a-z]{3,}\b', content.lower())
    return Counter(words)

def suggest_tags(filepath, max_tags=5):
    """Suggest tags for a post based on content analysis"""
    try:
        post = frontmatter.load(filepath)
        
        # Combine title, description, and content for analysis
        title = post.get('title', '').lower()
        description = post.get('description', '').lower()
        content = post.content[:2000].lower()  # First 2000 chars
        
        full_text = f"{title} {description} {content}"
        
        # Score potential tags
        tag_scores = Counter()
        
        for tag, patterns in TAG_PATTERNS.items():
            score = 0
            for pattern in patterns:
                # Count occurrences in full text
                count = full_text.count(pattern.lower())
                if count > 0:
                    # Weight by pattern specificity (longer = more specific)
                    weight = len(pattern.split()) * 2
                    score += count * weight
            
            if score > 0:
                tag_scores[tag] = score
        
        # Get top scoring tags
        suggested = [tag for tag, score in tag_scores.most_common(max_tags)]
        
        return suggested, tag_scores
    
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return [], {}

def main():
    # Load posts needing tags
    with open('high-traffic-posts-needing-tags.json', 'r') as f:
        posts = json.load(f)
    
    print("=" * 70)
    print("TAG SUGGESTIONS FOR HIGH-TRAFFIC POSTS")
    print("=" * 70)
    print()
    
    suggestions = []
    
    for post_info in posts:
        filepath = post_info['file']
        title = post_info['title']
        current_tags = post_info['tags'] if post_info['tags'] else []
        
        print(f"📄 {title}")
        print(f"   File: {os.path.basename(filepath)}")
        print(f"   Current tags: {current_tags if current_tags else 'None'}")
        
        # Get suggestions
        suggested, scores = suggest_tags(filepath, max_tags=7)
        
        # Filter out tags already present
        if isinstance(current_tags, list):
            new_suggestions = [t for t in suggested if t not in current_tags]
        else:
            new_suggestions = suggested
        
        print(f"   Suggested tags: {new_suggestions[:5]}")
        print()
        
        suggestions.append({
            'file': filepath,
            'title': title,
            'current_tags': current_tags,
            'suggested_tags': new_suggestions[:5],
            'all_scores': dict(scores.most_common(10))
        })
    
    # Save suggestions
    with open('tag-suggestions.json', 'w') as f:
        json.dump(suggestions, f, indent=2)
    
    print("=" * 70)
    print(f"✅ Generated tag suggestions for {len(suggestions)} posts")
    print("   Saved to: tag-suggestions.json")
    print("=" * 70)
    print()
    print("Review suggestions and run with --apply to add tags")

if __name__ == "__main__":
    main()
