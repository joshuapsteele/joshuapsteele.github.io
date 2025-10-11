#!/usr/bin/env python3
"""
Analyze website statistics to develop audience growth strategy.
"""

import pandas as pd
import numpy as np
from collections import Counter
from datetime import datetime
import re

# Read the CSV
print("Loading website statistics...")
df = pd.read_csv('stats-Personal Hugo Website-2025-10-11T09_08_55.csv')

print(f"✅ Loaded {len(df):,} page views")
print(f"📊 Columns: {', '.join(df.columns)}\n")

# Convert timestamp
df['created_at'] = pd.to_datetime(df['created_at'], utc=True)
df['date'] = df['created_at'].dt.date
df['month'] = df['created_at'].dt.to_period('M')

# Calculate date range
print("="*80)
print("📅 DATA OVERVIEW")
print("="*80)
print(f"Date Range: {df['created_at'].min()} to {df['created_at'].max()}")
print(f"Total Page Views: {len(df):,}")
print(f"Unique Visitors: {df['unique_id'].nunique():,}")
print(f"Unique Pages: {df['path'].nunique():,}")
print(f"Countries: {df['country'].nunique()}")
print(f"Mobile Traffic: {(df['is_mobile'].sum() / len(df) * 100):.1f}%")
print("\n")

# Top performing pages
print("="*80)
print("🏆 TOP 20 PAGES BY VIEWS")
print("="*80)
top_pages = df['path'].value_counts().head(20)
for i, (path, views) in enumerate(top_pages.items(), 1):
    pct = (views / len(df) * 100)
    print(f"{i:2d}. {path[:65]:<65} {views:>6,} ({pct:>5.1f}%)")
print("\n")

# Categorize content
def categorize_url(path):
    """Categorize URLs into content types."""
    if pd.isna(path) or path == '/':
        return 'Homepage'

    path_lower = str(path).lower()

    # Specific topic categories
    if any(word in path_lower for word in ['barth', 'bonhoeffer', 'romans', 'theology', 'bible', 'church', 'christian', 'sermon', 'pastor']):
        return 'Theology/Church'
    elif any(word in path_lower for word in ['code', 'coding', 'software', 'programming', 'developer', 'engineer', 'bootcamp', 'python', 'testing']):
        return 'Software/Tech'
    elif any(word in path_lower for word in ['ordination', 'women', 'anglican', 'priest', 'acna', 'egalitarian', 'mutualist']):
        return 'Women\'s Ordination'
    elif any(word in path_lower for word in ['productivity', 'gtd', 'tools', 'organize', 'habit', 'better']):
        return 'Productivity'
    elif any(word in path_lower for word in ['cedarville', 'personal', 'family', 'kids', 'father', 'marriage']):
        return 'Personal'
    elif any(word in path_lower for word in ['politics', 'fascism', 'nationalism', 'tyranny', 'resist', 'election']):
        return 'Politics/Ethics'
    elif any(page in path_lower for page in ['/about', '/cv', '/contact', '/now', '/portfolio', '/my-story']):
        return 'About/Bio'
    elif any(page in path_lower for page in ['/sermons', '/essays', '/dissertation']):
        return 'Academic/Ministry'
    else:
        return 'Other'

df['category'] = df['path'].apply(categorize_url)

# Category performance
print("="*80)
print("📈 CONTENT PERFORMANCE BY CATEGORY")
print("="*80)
cat_stats = df.groupby('category').agg({
    'path': 'count',
    'unique_id': 'nunique'
}).rename(columns={'path': 'Total Views', 'unique_id': 'Unique Visitors'})
cat_stats['Pages'] = df.groupby('category')['path'].nunique()
cat_stats = cat_stats.sort_values('Total Views', ascending=False)
cat_stats['% of Traffic'] = (cat_stats['Total Views'] / len(df) * 100).round(1)
print(cat_stats)
print("\n")

# Traffic sources
print("="*80)
print("🔗 TOP 15 REFERRERS")
print("="*80)
# Clean referrers
df['referrer_clean'] = df['referrer'].fillna('Direct/None')
df['referrer_clean'] = df['referrer_clean'].replace('', 'Direct/None')

top_refs = df['referrer_clean'].value_counts().head(15)
for i, (ref, count) in enumerate(top_refs.items(), 1):
    pct = (count / len(df) * 100)
    ref_display = ref if len(ref) < 55 else ref[:52] + '...'
    print(f"{i:2d}. {ref_display:<55} {count:>6,} ({pct:>5.1f}%)")
print("\n")

# Identify search vs social vs direct
def categorize_referrer(ref):
    """Categorize referrer type."""
    if pd.isna(ref) or ref == '' or ref == 'Direct/None':
        return 'Direct/None'
    ref_lower = str(ref).lower()

    if 'google' in ref_lower or 'bing' in ref_lower or 'duckduckgo' in ref_lower or 'search' in ref_lower:
        return 'Search Engines'
    elif any(social in ref_lower for social in ['facebook', 'twitter', 'linkedin', 'instagram', 'reddit', 'youtube']):
        return 'Social Media'
    elif 'ai' in ref_lower or 'chatgpt' in ref_lower or 'claude' in ref_lower or 'blackbox' in ref_lower:
        return 'AI Tools'
    else:
        return 'Other Websites'

df['referrer_type'] = df['referrer_clean'].apply(categorize_referrer)

print("="*80)
print("🌐 TRAFFIC SOURCE BREAKDOWN")
print("="*80)
source_stats = df['referrer_type'].value_counts()
for source, count in source_stats.items():
    pct = (count / len(df) * 100)
    print(f"{source:<20} {count:>8,} ({pct:>5.1f}%)")
print("\n")

# Monthly traffic trends
print("="*80)
print("📊 MONTHLY TRAFFIC TRENDS")
print("="*80)
monthly_stats = df.groupby('month').agg({
    'path': 'count',
    'unique_id': 'nunique'
}).rename(columns={'path': 'Total Views', 'unique_id': 'Unique Visitors'})

print("\nLast 12 months:")
for period, row in monthly_stats.tail(12).iterrows():
    print(f"{period}: {row['Total Views']:>6,} views | {row['Unique Visitors']:>5,} visitors")
print("\n")

# Geographic distribution
print("="*80)
print("🌎 TOP 10 COUNTRIES")
print("="*80)
country_stats = df['country'].value_counts().head(10)
for i, (country, count) in enumerate(country_stats.items(), 1):
    pct = (count / len(df) * 100)
    print(f"{i:2d}. {country:<3} {count:>8,} ({pct:>5.1f}%)")
print("\n")

# Device breakdown
print("="*80)
print("📱 DEVICE & BROWSER BREAKDOWN")
print("="*80)
print(f"Mobile: {df['is_mobile'].sum():,} ({df['is_mobile'].sum()/len(df)*100:.1f}%)")
print(f"Desktop: {(~df['is_mobile']).sum():,} ({(~df['is_mobile']).sum()/len(df)*100:.1f}%)")
print("\nTop Browsers:")
browser_stats = df['browser_name'].value_counts().head(5)
for browser, count in browser_stats.items():
    pct = (count / len(df) * 100)
    print(f"  {browser:<25} {count:>6,} ({pct:>5.1f}%)")
print("\n")

# Identify top performers by category
print("="*80)
print("⭐ TOP 3 POSTS PER CATEGORY")
print("="*80)
for category in ['Theology/Church', 'Software/Tech', 'Women\'s Ordination', 'Productivity', 'Politics/Ethics']:
    cat_df = df[df['category'] == category]
    if len(cat_df) > 0:
        print(f"\n{category}:")
        top_cat_pages = cat_df['path'].value_counts().head(3)
        for i, (path, views) in enumerate(top_cat_pages.items(), 1):
            print(f"  {i}. {path} ({views:,} views)")

print("\n" + "="*80)
print("✅ Analysis complete!")
print("="*80)
