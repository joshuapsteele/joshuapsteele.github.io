# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is Joshua P. Steele's personal website built with Hugo static site generator using the PaperMod theme. The site is deployed via GitHub Pages with automated builds using GitHub Actions.

## Site Architecture

- **Static Site Generator**: Hugo 0.147.3 extended (Node 20 in CI, Node 18+ locally)
- **Theme**: PaperMod (in `themes/` directory, override via `layouts/` and `assets/`)
- **Content Structure**:
  - `content/blog/` - Blog posts (314 markdown files with YAML front matter)
  - `content/pages/` - Static pages (42 files including about, contact, cv, now, uses, follow, etc.)
  - `content/search.md` - Search functionality page
- **Newsletter**: "Steele Notes" email newsletter via [Buttondown](https://buttondown.com/joshuapsteele)
  - Subscription forms on homepage (`layouts/partials/index_profile.html`) and `/follow` page
  - Powered by Buttondown API embed
- **Layouts**: Custom Hugo layouts in `layouts/` directory
  - Custom shortcodes: `audio`, `callout`, `figure`, `files-list`, and `gallery`
  - Partials for comments, analytics (`google_analytics`, `tinylytics_kudos`), and site components
  - IndieWeb partials: `webmentions.html`, `webmention_display.html`, `reply_context.html`
  - Custom blockquote rendering (`layouts/_default/_markup/render-blockquote.html`)
  - Custom 404 page (`layouts/404.html`)
  - Profile and home info customizations with h-card microformats
  - List template override with h-feed markup
  - Single post template with h-entry markup
- **Static Assets**: Images and files in `static/` directory (served as-is, includes favicons, PDFs, logos)
- **Processed Assets**: `assets/css/extended/custom.css` for theme CSS extensions
- **Configuration**: `hugo.yaml` (main site configuration)
- **Build Output**: `public/` directory (generated, git-ignored, never edit directly)
- **Templates**: Obsidian blog post templates in `templates/` directory (for use with Obsidian editor)

## Development Commands

### Local Development
```bash
# Start Hugo development server with drafts and future posts
npm run dev
# or: hugo server --buildDrafts --buildFuture

# Build site for production (minified, cleaned)
npm run build
# or: hugo --gc --minify --cleanDestinationDir

# Quick build without minification (for sanity checks)
npm run build:fast
# or: hugo --gc

# Build with template performance metrics
npm run build:stats
# or: hugo --gc --minify --templateMetrics --templateMetricsHints

# Clean generated files
npm run clean
# or: rm -rf public resources

# Deploy to GitHub (commits and pushes to main, triggering CI)
npm run deploy
# or: ./deploy.sh "Optional commit message"
```

### Deployment
The site uses GitHub Actions for automated deployment (`.github/workflows/hugo.yml`):
- Workflow triggered on push to `main` branch or manual dispatch
- Build job: Checks out code with submodules, sets up Hugo 0.147.3 extended + Node 20, caches dependencies, builds site with `hugo --gc --minify`
- Deploy job: Deploys to GitHub Pages using built artifact

The `deploy.sh` script simplifies local deployment workflow:
1. Adds all changes to git (`git add .`)
2. Commits with timestamp or custom message
3. Pushes to `main` branch (triggers GitHub Actions build and deployment)

**Important**: Never push directly to `main` without testing locally first with `npm run dev` and `npm run build`

## Content Management

### Blog Posts
- All blog posts are in `content/blog/` as individual markdown files
- Posts use YAML front matter with fields: title, date, tags, categories, draft
- File naming convention: `my-post.md` (kebab-case, no date prefixes)
- Use `scripts/rename_blog_files.sh` script to rename dated posts if needed

### Pages
- Static pages in `content/pages/`
- Include about, contact, CV, resources, etc.

### Coding Style & Conventions
- **Markdown**: YAML front matter (not TOML/JSON)
- **Filenames**: kebab-case (e.g., `my-post.md`)
- **Templates**: 2-space indentation, semantic HTML
- **CSS**: Extend via `assets/css/extended/custom.css` (do not edit theme directly)
- **Overrides**: Place template overrides in `layouts/` mirroring theme paths

## Hugo Configuration Highlights

### Profile Mode & Navigation
- Profile mode enabled on homepage with custom image, title, and subtitle
- 27 custom profile buttons linking to key pages (About, Blog, Contact, CV, Now, Uses, etc.)
- Top navigation menu: About, Blog, Contact, Resources, Social, Search
- Footer text: "Navigate my [blog](/blog) by [categories](/categories) and [tags](/tags)"

### Social & Sharing
- Social icons: BlueSky, Mastodon, GitHub, LinkedIn, microblog, RSS
- Default social sharing image: `/images/headshot.jpg`
- Share buttons enabled on posts
- Disqus comments configured but disabled by default

### Search & Feeds
- Search functionality with Fuse.js (configurable in `hugo.yaml` under `fuseOpts`)
- RSS and JSON feeds enabled (custom output formats: `/feed.xml`, `/feed.json`)
- Full content in RSS feeds enabled

### Newsletter
- **"Steele Notes"** email newsletter via Buttondown
- Subscription form embedded on homepage and `/follow` page
- Subscribe URL: https://buttondown.com/joshuapsteele
- Form uses Buttondown's embed API (`https://buttondown.com/api/emails/embed-subscribe/joshuapsteele`)

### Content Features
- Table of contents enabled by default on posts
- Reading time display enabled
- Code copy buttons enabled
- Breadcrumbs enabled
- Post navigation links (previous/next)
- Edit links point to GitHub repository source

### Build & Performance
- Image optimization: CatmullRom resampling, quality 75
- Build stats and write stats enabled
- Resource caching configured (1h for JSON/CSV, 24h for images/assets/modules)
- Custom minification settings for production builds (tdewolff)
- Syntax highlighting with Monokai style, code fences enabled
- Goldmark renderer with unsafe HTML enabled
- Git info enabled for last modified dates

## IndieWeb Features

This site is fully IndieWeb-enabled with comprehensive support for decentralized social web features.

### Microformats2
- **h-card**: Homepage profile marked up with identity information (`layouts/partials/index_profile.html`)
  - Classes: `h-card`, `p-name`, `u-url`, `u-photo`, `p-note`
- **h-entry**: Blog posts marked up for machine readability (`layouts/_default/single.html`)
  - Classes: `h-entry`, `p-name`, `e-content`, `dt-published`, `p-author`, `p-category`, `u-url`
- **h-feed**: Blog list pages marked up as feeds (`layouts/_default/list.html`)
  - Wraps collections of h-entry posts for feed readers

### Identity & Authentication
- **rel="me"**: Verified identity links in footer and social icons
  - Links to Micro.blog, Bluesky, Mastodon (bidirectional verification)
- **IndieAuth**: Domain-based authentication endpoints (`layouts/partials/extend_head.html`)
  - Authorization endpoint: `https://indieauth.com/auth`
  - Token endpoint: `https://tokens.indieauth.com/token`
- **WebFinger**: Fediverse discovery support (`static/.well-known/webfinger`)
  - Enables Mastodon account lookup via domain

### Webmentions
- **Receiving**: Webmention.io integration (`layouts/partials/webmentions.html`)
  - Webmention endpoint: `https://webmention.io/joshuapsteele.com/webmention`
  - Pingback endpoint: `https://webmention.io/joshuapsteele.com/xmlrpc`
- **Display**: JavaScript-based webmention display (`layouts/partials/webmention_display.html`)
  - Fetches from webmention.io API on page load
  - Groups by type: likes (facepile), reposts (facepile), replies (full cards), mentions (list)
  - Styled with extensive CSS (`assets/css/extended/custom.css` lines 383-538)
- **Bridgy**: Backfeed social media interactions as webmentions
  - Integration with Bluesky and Mastodon via brid.gy

### Reply Context
- **Reply Posts**: Support for replying to other posts with context (`layouts/partials/reply_context.html`)
  - Activated by `in_reply_to` parameter in front matter
  - Displays original post with author, title, excerpt
  - JavaScript-based fetching with graceful fallback for CORS issues
  - Marked up with `u-in-reply-to` microformat class
  - Styled with CSS (`assets/css/extended/custom.css` lines 540-611)

### Creating Reply Posts
Add this to your post's front matter to create a reply:
```yaml
---
title: "My Reply"
date: 2025-12-09
in_reply_to: "https://example.com/original-post"
---
```

### POSSE Workflow
- Posts published on joshuapsteele.com first
- Syndicated to Micro.blog, which cross-posts to Bluesky and Mastodon
- Social interactions backfed as webmentions via Bridgy

### IndieWeb Testing
Validate implementations with:
- https://indiewebify.me/ - General IndieWeb validation
- https://indiewebify.me/validate-h-entry/ - h-entry validator
- https://indiewebify.me/validate-h-card/ - h-card validator
- https://indiewebify.me/validate-h-feed/ - h-feed validator
- https://webmention.rocks/ - Webmention testing tools

## Taxonomy Management

The site uses a taxonomy consolidation system to maintain consistent categories and tags:

### Taxonomy Files
- `scripts/data/taxonomy_map.yaml` - Master configuration defining category/tag consolidation rules
- `scripts/data/taxonomy_map.suggested.yaml` - AI-generated suggestions (review before using)
- `scripts/data/taxonomy_map.generated.yaml` - Generated mapping results from processing

### Taxonomy Scripts
- `scripts/apply-taxonomy.py` - Apply taxonomy consolidation based on `taxonomy_map.yaml`
- `scripts/suggest-tags.py` - Generate tag suggestions for posts
- `scripts/categorize-uncategorized.py` - Suggest categories for uncategorized posts

## Maintenance Scripts

### Shell Scripts
- `scripts/deploy.sh` - Commits all changes with timestamp (or custom message) and pushes to main
- `scripts/cleanup_images.sh` - Removes legacy/external images (DANGEROUS: review before running)
- `scripts/rename_blog_files.sh` - Renames dated blog posts to remove date prefixes (review before running)
- `scripts/apply-high-traffic-tags.sh` - Apply tags to high-traffic posts
- `scripts/review_changes.sh` - Review staged changes before committing

### Python Audit & Analysis Scripts
- `scripts/audit-frontmatter.py` - Analyze front matter for missing fields and inconsistencies (outputs to `scripts/data/`)
- `scripts/check-internal-links.py` - Check for broken internal links (outputs to `scripts/data/`)
- `scripts/check-external-links.py` - Check for broken external links (outputs to `scripts/data/`)
- `scripts/analyze_website_stats.py` - Analyze traffic statistics
- `scripts/cleanup_frontmatter.py` - Clean up and standardize front matter fields
- `scripts/fix_malformed_yaml.py` - Fix malformed YAML front matter
- `scripts/generate_descriptions.py` - Generate descriptions for posts missing them
- `scripts/update_descriptions.py` - Update existing descriptions
- `scripts/categorize_page_changes.py` - Categorize and analyze page changes
- `scripts/show_posts_batch.py` - Display posts in batches for review

### Documentation Files
- `CLAUDE.md` - This file - AI assistant guidance
- `docs/AGENTS.md` - Repository guidelines and conventions
- `docs/AUDIT-*.md` - Various audit reports (structure, frontmatter, internal links, external links, taxonomy, action plan)
- `docs/AUDIT-MASTER-REPORT.md` - Consolidated audit findings
- `docs/CLEANUP-CHECKLIST.md` - Checklist for site maintenance
- `docs/AUDIENCE_GROWTH_STRATEGY.md` - Strategy document
- `docs/WARP.md` - Additional documentation

## Common Workflows

### Adding a New Blog Post

**Option 1: Using Obsidian Templates (Recommended)**
1. Open Obsidian vault (set to repo root or use symlink to `content/blog/`)
2. Create new note in `content/blog/`
3. Insert template (Cmd+P → "Insert template" → choose template):
   - `blog-post-full.md` - Complete article with metadata
   - `blog-post-quick.md` - Simple post
   - `blog-post-reply.md` - Reply to another post
   - `blog-post-draft.md` - Work in progress
   - `blog-post-with-image.md` - Post with cover image
4. Fill in content and metadata
5. Save file with kebab-case name (e.g., `my-new-post.md`)
6. Commit and push (via Obsidian Git plugin, Working Copy, or command line)

See `templates/README.md` for detailed template documentation.

**Option 2: Using Drafts App (Mobile)**
1. Write post in Drafts app (first line = title, rest = body)
2. Run one of the Drafts actions:
   - "Quick Blog Post" - Fast publishing
   - "Full Blog Post" - Prompts for metadata
3. Post is automatically committed to GitHub
4. GitHub Actions builds site in 2-3 minutes

See `DRAFTS-ACTIONS.md` for Drafts setup and usage.

**Note**: For micro-blog style posts without titles, use [Micro.blog](https://micro.blog/) instead - it integrates better with social media.

**Option 3: Manual Creation**
1. Create new markdown file in `content/blog/` with kebab-case name (e.g., `my-new-post.md`)
2. Add YAML front matter with required fields: `title`, `date`, `tags`, `categories`
3. Optional fields: `description`, `draft: true`, `featured_image`
4. Test locally with `npm run dev`
5. Deploy with `npm run deploy "Add new post: Post Title"`

### Editing an Existing Post
1. Find the post in `content/blog/` or `content/pages/`
2. Edit the markdown file directly
3. Update front matter if needed (date, tags, categories)
4. Test locally with `npm run dev`
5. Deploy with `npm run deploy "Update post: Post Title"`

### Modifying Site Layout or Theme
1. Never edit files in `themes/` directly
2. Create override in `layouts/` mirroring the theme path
3. For CSS: edit `assets/css/extended/custom.css`
4. For shortcodes: create/edit in `layouts/shortcodes/`
5. Test thoroughly with `npm run dev`
6. Build and check for errors with `npm run build`

### Running Audits
1. Front matter audit: `python3 scripts/audit-frontmatter.py`
2. Internal links: `python3 scripts/check-internal-links.py`
3. External links: `python3 scripts/check-external-links.py` (may take time)
4. Review generated JSON files in `scripts/data/` for issues
5. Fix issues incrementally and re-run audits

### Applying Taxonomy Changes
1. Review/edit `scripts/data/taxonomy_map.yaml` for consolidation rules
2. Run `python3 scripts/apply-taxonomy.py` to apply changes
3. Review changes in git diff before committing
4. Test with `npm run build` to ensure no errors
5. Deploy changes carefully

## Best Practices for AI Assistants

### Do's
- Always read existing files before editing
- Test changes locally with `npm run dev` before suggesting deployment
- Preserve YAML front matter format (not TOML or JSON)
- Use kebab-case for file names
- Check for broken links after bulk edits
- Run `npm run build` to verify no errors before deploying
- Use git to review changes before committing

### Don'ts
- Never edit files in `themes/` directory directly
- Never edit `public/` directory (it's generated)
- Don't commit without testing locally first
- Don't change file naming conventions without asking
- Don't remove or modify front matter fields without understanding their purpose
- Don't run destructive scripts (`scripts/cleanup_images.sh`, `scripts/rename_blog_files.sh`) without explicit confirmation
- Don't push directly to `main` in production without testing

### Safety Checks
- Before modifying multiple files: run relevant audit scripts first
- Before deploying: check `git status` and `git diff`
- Before taxonomy changes: backup `scripts/data/taxonomy_map.yaml`
- Before link changes: run `scripts/check-internal-links.py` afterwards
- Before front matter changes: run `scripts/audit-frontmatter.py` afterwards

## Troubleshooting

### Build Failures
- **Error: "Hugo not found"**: Ensure Hugo extended is installed and in PATH
- **Error: "template error"**: Check layout files for syntax errors in Go templates
- **YAML parsing errors**: Run `python3 scripts/fix_malformed_yaml.py` to fix front matter
- **Image processing errors**: Check image paths and formats in content files

### Local Development Issues
- **Port 1313 already in use**: Kill existing Hugo server or use `hugo server -p 1314`
- **Changes not reflecting**: Hard refresh browser (Ctrl+F5) or clear cache
- **Theme not loading**: Ensure theme submodule is initialized: `git submodule update --init`

### Content Issues
- **Broken internal links**: Run `python3 scripts/check-internal-links.py` and fix reported issues
- **Missing descriptions**: Run `python3 scripts/generate_descriptions.py` to auto-generate
- **Inconsistent taxonomy**: Review and apply `scripts/data/taxonomy_map.yaml` with `scripts/apply-taxonomy.py`
- **Malformed front matter**: Run `python3 scripts/fix_malformed_yaml.py`

### Deployment Issues
- **GitHub Actions build failing**: Check workflow logs at `.github/workflows/hugo.yml`
- **404 on deployed site**: Verify baseURL in `hugo.yaml` matches domain
- **CSS not loading**: Check `assets/css/extended/custom.css` syntax
- **Feed not updating**: Clear browser cache and verify `outputs` in `hugo.yaml`

## Verification Before Deployment
- Run `npm run dev` and review pages, menus, feeds, social images locally (http://localhost:1313)
- Run `npm run build` and scan console output for warnings and errors
- Review `git status` and `git diff` to verify all changes are intentional
- No unit tests; manual verification required
- Check that navigation, search, and RSS feeds work correctly

## Additional Resources
- Hugo Documentation: https://gohugo.io/documentation/
- PaperMod Theme: https://github.com/adityatelange/hugo-PaperMod
- GitHub Pages: https://docs.github.com/en/pages
- Fuse.js Search: https://fusejs.io/
- Buttondown (Newsletter): https://buttondown.com/
- Repository: https://github.com/joshuapsteele/joshuapsteele.github.io