#!/usr/bin/env python3
"""
Generate SEO descriptions for blog posts missing them.
Uses Claude API to create concise, relevant descriptions.
"""

import os
import re
import yaml
from pathlib import Path
from typing import Dict, Any, Tuple
import json

def extract_frontmatter_and_body(content: str) -> Tuple[Dict[str, Any], str, str]:
    """
    Extract YAML front matter and body content from markdown.
    Returns: (frontmatter_dict, yaml_string, body_content)
    """
    pattern = r'^---\s*\n(.*?\n)---\s*\n(.*)$'
    match = re.match(pattern, content, re.DOTALL)

    if not match:
        return {}, "", content

    yaml_str = match.group(1)
    body = match.group(2)

    try:
        frontmatter = yaml.safe_load(yaml_str)
        if frontmatter is None:
            frontmatter = {}
    except yaml.YAMLError as e:
        print(f"YAML parsing error: {e}")
        frontmatter = {}

    return frontmatter, yaml_str, body


def needs_description(frontmatter: Dict[str, Any]) -> bool:
    """Check if post needs a description."""
    if 'description' not in frontmatter:
        return True

    desc = frontmatter.get('description', '')
    return desc == '' or desc is None


def extract_text_content(body: str, max_chars: int = 1000) -> str:
    """Extract plain text from markdown body for analysis."""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', body)

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


def generate_description_prompt(title: str, content_preview: str, categories: list = None, tags: list = None) -> str:
    """Create a prompt for generating the description."""
    prompt = f"""Based on this blog post, write a concise SEO-friendly description (1-2 sentences, max 160 characters):

Title: {title}

Categories: {', '.join(categories) if categories else 'None'}
Tags: {', '.join(tags) if tags else 'None'}

Content preview:
{content_preview}

Write ONLY the description, nothing else. Make it engaging and informative."""

    return prompt


def format_yaml_with_description(yaml_str: str, description: str) -> str:
    """Insert description into YAML string."""
    # Parse the existing YAML
    data = yaml.safe_load(yaml_str)
    if data is None:
        data = {}

    # Update description
    data['description'] = description

    # Re-order fields
    field_order = ['title', 'date', 'author', 'categories', 'tags', 'description', 'url', 'draft']
    ordered = {}

    for field in field_order:
        if field in data:
            ordered[field] = data[field]

    # Add any remaining fields
    for key, value in data.items():
        if key not in ordered:
            ordered[key] = value

    # Convert to YAML
    yaml_str = yaml.dump(ordered, default_flow_style=False, allow_unicode=True, sort_keys=False, width=1000)

    return yaml_str


def find_posts_needing_descriptions(content_dir: Path) -> list:
    """Find all posts with empty descriptions."""
    posts = []

    for md_file in content_dir.rglob('*.md'):
        if md_file.name in ['_index.md', 'archives.md', 'search.md']:
            continue

        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()

            frontmatter, _, _ = extract_frontmatter_and_body(content)

            if needs_description(frontmatter):
                posts.append(md_file)

        except Exception as e:
            print(f"Error reading {md_file}: {e}")

    return posts


def generate_simple_description(title: str, content_preview: str, categories: list = None) -> str:
    """
    Generate a simple description without AI.
    Takes first 1-2 sentences from content.
    """
    # Clean up the preview
    preview = content_preview.strip()

    # Try to get first 2 sentences
    sentences = re.split(r'[.!?]+\s+', preview)

    # Take first 1-2 sentences
    desc_parts = []
    char_count = 0

    for sentence in sentences[:3]:
        sentence = sentence.strip()
        if not sentence:
            continue

        # Clean up common artifacts
        sentence = re.sub(r'^\*+\s*', '', sentence)  # Remove leading asterisks
        sentence = re.sub(r'^Editor\'s Note:.*?$', '', sentence, flags=re.IGNORECASE)

        if len(sentence) < 20:  # Skip very short sentences
            continue

        if char_count + len(sentence) < 155:  # Leave room for period
            desc_parts.append(sentence)
            char_count += len(sentence) + 2
        else:
            break

    description = '. '.join(desc_parts)
    if description and not description.endswith('.'):
        description += '.'

    # Truncate if too long
    if len(description) > 160:
        description = description[:157] + '...'

    # Fallback to title + category if extraction failed
    if not description or len(description) < 30:
        cat_text = f" on {categories[0]}" if categories else ""
        description = f"A blog post{cat_text} by Joshua P. Steele."

    return description


def main():
    content_dir = Path('content')

    print("Finding posts needing descriptions...")
    posts = find_posts_needing_descriptions(content_dir)

    print(f"Found {len(posts)} posts needing descriptions\n")

    if len(posts) == 0:
        print("All posts have descriptions!")
        return

    # Generate descriptions
    updated_count = 0

    for i, post_path in enumerate(posts, 1):
        try:
            print(f"[{i}/{len(posts)}] Processing: {post_path.name}")

            # Read file
            with open(post_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse
            frontmatter, yaml_str, body = extract_frontmatter_and_body(content)

            # Extract info
            title = frontmatter.get('title', 'Untitled')
            categories = frontmatter.get('categories', [])
            tags = frontmatter.get('tags', [])

            # Get content preview
            text_preview = extract_text_content(body, max_chars=800)

            # Generate description
            description = generate_simple_description(title, text_preview, categories)

            print(f"  Generated: {description[:80]}...")

            # Update YAML
            new_yaml = format_yaml_with_description(yaml_str, description)

            # Write back
            new_content = f"---\n{new_yaml}---\n{body}"

            with open(post_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            updated_count += 1

        except Exception as e:
            print(f"  ERROR: {e}")

    print(f"\n✅ Updated {updated_count}/{len(posts)} posts")


if __name__ == '__main__':
    main()
