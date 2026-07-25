# Scripts

This directory contains maintenance, audit, and deployment scripts for the joshuapsteele.com Hugo website.

## Structure

- **Root scripts** (`.py` and `.sh` files) - Executable maintenance and utility scripts
- **`data/`** - Generated data files, audit results, and configuration files

## Main Scripts

### Deployment
- `deploy.sh` - Deploy site to GitHub (commits with timestamp and pushes)
- `fetch_popular_posts.py` - Fetch popular posts from Tinylytics API (used in CI/CD)
- `fetch_syndication_links.py` - Fetch Micro.blog syndication URLs (including Mastodon, Threads, and Bluesky) for Hugo response links
- `send_webmentions.py` - Discover and send outgoing Webmentions for recently built reply posts
- `check_conversation_sources.py` - Check Webmention.io and Micro.blog conversation data for a post URL

### Content Maintenance
- `cleanup_frontmatter.py` - Clean up and standardize YAML front matter
- `fix_malformed_yaml.py` - Fix malformed YAML in post front matter
- `generate_descriptions.py` - Auto-generate descriptions for posts
- `manage-notes.py` - List or move Hugo notes by date/time, tag, draft status, or syndication flag
- `migrate-microblog-archive.py` - Import an exported Micro.blog archive into `content/notes/`

### Auditing & Analysis
- `audit-frontmatter.py` - Analyze front matter for issues (outputs to `data/`)
- `audit-static-wp-content.py` - Non-destructively audit legacy WordPress media references
- `check-internal-links.py` - Check for broken internal links; validates against the built `public/` site (run `npm run build` first). Outputs to `data/`
- `check-external-links.py` - Check non-Amazon, non-self external links. Sends browser headers, throttles per-domain, retries, and classifies results as dead vs. blocked/manual. Skips Amazon and joshuapsteele.com (handled below). Outputs to `data/`
- `check-amazon-links.py` - Check Amazon links (amazon.com/amzn.to/a.co) with anti-block best effort (browser headers, cookie jar, sequential jittered delays, redirect-following). Flags `--delay`/`--jitter`/`--limit`. Outputs `docs/AUDIT-amazon-links.md` + `data/`
- `check-amazon-disclosures.py` - Verify every Amazon-affiliate-link page in the built `public/` site contains the required Associate statement and every tagged or shortened Amazon affiliate link has an adjacent `(paid link)` disclosure. Runs automatically in `npm run build` and CI
- `convert-internal-links.py` - Rewrite absolute self-links (joshuapsteele.com) in post bodies to root-relative internal links, validating against `public/` and flagging any that don't resolve. Dry-run by default; `--apply` to write
- `lookup-wayback.py` - For the dead URLs in `data/audit-external-links.json`, query the Internet Archive for the closest usable (2xx) snapshot; writes `data/wayback-map.json`
- `fix-dead-links.py` - Apply dead-link fixes from the audit + Wayback map: rewrite to the snapshot where one exists, else unlink and mark "(old, broken link)" / "(old, broken image)". Body-only; dry-run by default, `--apply` to write
- `analyze_website_stats.py` - Analyze website traffic statistics
- `categorize_page_changes.py` - Categorize and analyze page changes

### Taxonomy Management
- `apply-taxonomy.py` - Apply taxonomy consolidation rules from `data/taxonomy_map.yaml`
- `suggest-tags.py` - Generate tag suggestions for posts
- `categorize-uncategorized.py` - Suggest categories for uncategorized posts
- `convert-taxonomy-to-kebab-case.py` - Convert taxonomy terms to kebab-case
- `taxonomy_tools.py` - Shared taxonomy utilities

### Utilities
- `cleanup_images.sh` - Legacy broad image cleanup (**DANGEROUS**; run a fresh media audit first)
- `rename_blog_files.sh` - Rename dated blog posts to remove date prefixes
- `review_changes.sh` - Review staged git changes before committing
- `show_posts_batch.py` - Display posts in batches for review

### Amazon Data Helpers
- `amazon/` - Scripts for building public/private Amazon purchase data views

## Usage

All scripts should be run from the repository root directory:

```bash
# Example: Run front matter audit
python3 scripts/audit-frontmatter.py

# Example: Deploy site
./scripts/deploy.sh "Commit message"

# Example: Fetch popular posts (requires TINYLYTICS_API_KEY)
export TINYLYTICS_API_KEY='your_key_here'
python3 scripts/fetch_popular_posts.py

# Example: Fetch Micro.blog cross-post URLs for response links
python3 scripts/fetch_syndication_links.py

# Example: Check whether Join the Conversation has anything to load
python3 scripts/check_conversation_sources.py https://joshuapsteele.com/notes/2026-04-17-1204/

# Example: Preview outgoing Webmentions after a local build
hugo --gc --destination /tmp/jps-public
python3 scripts/send_webmentions.py --public-dir /tmp/jps-public --feed /tmp/jps-public/notes/feed.json --dry-run
```

## Data Directory

The `data/` subdirectory contains:
- **Audit results** - JSON files from audit scripts
- **Taxonomy configuration** - `taxonomy_map.yaml` and related files
- **Generated data** - CSV stats and other output files

## Retired One-Off Scripts

One-off bulk scripts should not stay here after the migration or cleanup pass they supported is complete. Recently retired examples:

- `apply-high-traffic-tags.sh` - Hardcoded an already-completed high-traffic tagging pass and old tag forms.
- `update_descriptions.py` - Hardcoded a prior description rewrite batch and could overwrite later curation.

See the main repository [CLAUDE.md](../CLAUDE.md) for detailed documentation.
