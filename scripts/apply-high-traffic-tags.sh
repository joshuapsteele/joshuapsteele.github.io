#!/bin/bash

# Apply well-curated tags to high-traffic posts

echo "Applying tags to high-traffic posts..."
echo

# 1. "You Can't Follow Jesus and Hate Immigrants" (#1 post - 4,499 views)
# Current: immigration
# Add: bible, refugees, christian ethics
echo "1. Immigration post - adding tags..."
python3 << 'PYTHON1'
import frontmatter

post = frontmatter.load('content/blog/you-cant-follow-jesus-and-hate-immigrants.md')
current_tags = post.get('tags', [])
if isinstance(current_tags, str):
    current_tags = [current_tags]

new_tags = ['immigration', 'bible', 'refugees', 'christian ethics', 'matthew 25']
post['tags'] = sorted(set(new_tags))

with open('content/blog/you-cant-follow-jesus-and-hate-immigrants.md', 'wb') as f:
    frontmatter.dump(post, f)

print(f"   Updated: {post['tags']}")
PYTHON1

# 2. "Romans 13" (#3 post - 2,880 views)
# Current: None
# Add: romans 13, bible, politics, government, political theology
echo "2. Romans 13 post - adding tags..."
python3 << 'PYTHON2'
import frontmatter

post = frontmatter.load('content/blog/romans-13.md')
new_tags = ['romans 13', 'bible', 'politics', 'government', 'political theology']
post['tags'] = new_tags

with open('content/blog/romans-13.md', 'wb') as f:
    frontmatter.dump(post, f)

print(f"   Updated: {post['tags']}")
PYTHON2

# 3. "Bonhoeffer Timeline"
# Current: bonhoeffer
# Add: theology, biography, research
echo "3. Bonhoeffer Timeline - adding tags..."
python3 << 'PYTHON3'
import frontmatter

post = frontmatter.load('content/blog/bonhoeffer-timeline-a-brief-chronology-of-dietrich-bonhoeffers-life.md')
new_tags = ['bonhoeffer', 'theology', 'biography', 'research', 'history']
post['tags'] = new_tags

with open('content/blog/bonhoeffer-timeline-a-brief-chronology-of-dietrich-bonhoeffers-life.md', 'wb') as f:
    frontmatter.dump(post, f)

print(f"   Updated: {post['tags']}")
PYTHON3

# 4. "14 Characteristics of Fascism"
# Current: fascism, authoritarianism  
# Add: politics, ethics, umberto eco
echo "4. Fascism post - adding tags..."
python3 << 'PYTHON4'
import frontmatter

post = frontmatter.load('content/blog/14-characteristics-of-fascism.md')
new_tags = ['fascism', 'authoritarianism', 'politics', 'ethics', 'umberto eco']
post['tags'] = new_tags

with open('content/blog/14-characteristics-of-fascism.md', 'wb') as f:
    frontmatter.dump(post, f)

print(f"   Updated: {post['tags']}")
PYTHON4

echo
echo "✅ All high-traffic posts updated with relevant tags!"

