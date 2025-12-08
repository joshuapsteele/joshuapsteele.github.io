# Scripts

This directory contains maintenance, audit, and deployment scripts for the joshuapsteele.com Hugo website.

## Structure

- **Root scripts** (`.py` and `.sh` files) - Executable maintenance and utility scripts
- **`data/`** - Generated data files, audit results, and configuration files

## Main Scripts

### Deployment
- `deploy.sh` - Deploy site to GitHub (commits with timestamp and pushes)
- `fetch_popular_posts.py` - Fetch popular posts from Tinylytics API (used in CI/CD)

### Content Maintenance
- `cleanup_frontmatter.py` - Clean up and standardize YAML front matter
- `fix_malformed_yaml.py` - Fix malformed YAML in post front matter
- `generate_descriptions.py` - Auto-generate descriptions for posts
- `update_descriptions.py` - Update existing post descriptions
- `categorize-uncategorized.py` - Suggest categories for uncategorized posts

### Auditing & Analysis
- `audit-frontmatter.py` - Analyze front matter for issues (outputs to `data/`)
- `check-internal-links.py` - Check for broken internal links (outputs to `data/`)
- `check-external-links.py` - Check for broken external links (outputs to `data/`)
- `analyze_website_stats.py` - Analyze website traffic statistics

### Taxonomy Management
- `apply-taxonomy.py` - Apply taxonomy consolidation rules from `data/taxonomy_map.yaml`
- `suggest-tags.py` - Generate tag suggestions for posts
- `apply-high-traffic-tags.sh` - Apply tags to high-traffic posts

### Utilities
- `cleanup_images.sh` - Remove legacy/external images (**DANGEROUS**)
- `rename_blog_files.sh` - Rename dated blog posts to remove date prefixes
- `review_changes.sh` - Review staged git changes before committing
- `show_posts_batch.py` - Display posts in batches for review
- `categorize_page_changes.py` - Categorize and analyze page changes

## Usage

All scripts should be run from the repository root directory:

\`\`\`bash
# Example: Run front matter audit
python3 scripts/audit-frontmatter.py

# Example: Deploy site
./scripts/deploy.sh "Commit message"

# Example: Fetch popular posts (requires TINYLYTICS_API_KEY)
export TINYLYTICS_API_KEY='your_key_here'
python3 scripts/fetch_popular_posts.py
\`\`\`

## Data Directory

The `data/` subdirectory contains:
- **Audit results** - JSON files from audit scripts
- **Taxonomy configuration** - `taxonomy_map.yaml` and related files
- **Generated data** - CSV stats and other output files

See the main repository [CLAUDE.md](../CLAUDE.md) for detailed documentation.
