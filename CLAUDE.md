# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is Joshua P. Steele's personal website built with Hugo static site generator using the PaperMod theme. The site is deployed via GitHub Pages with automated builds using GitHub Actions.

## Site Architecture

- **Static Site Generator**: Hugo 0.147.3 extended (Node 20 in CI, Node 18+ locally)
- **Theme**: PaperMod (in `themes/` directory, override via `layouts/` and `assets/`)
- **Content Structure**:
  - `content/blog/` - Blog posts (309 markdown files with YAML front matter)
  - `content/pages/` - Static pages (40 files including about, contact, cv, now, uses, etc.)
  - `content/search.md` - Search functionality page
- **Layouts**: Custom Hugo layouts in `layouts/` directory
  - Custom shortcodes: `audio`, `callout`, `figure`, `files-list`, and `gallery`
  - Partials for comments, analytics (`google_analytics`, `tinylytics_kudos`), and site components
  - Custom blockquote rendering (`layouts/_default/_markup/render-blockquote.html`)
  - Custom 404 page (`layouts/404.html`)
  - Profile and home info customizations
- **Static Assets**: Images and files in `static/` directory (served as-is, includes favicons, PDFs, logos)
- **Processed Assets**: `assets/css/extended/custom.css` for theme CSS extensions
- **Configuration**: `hugo.yaml` (main site configuration)
- **Build Output**: `public/` directory (generated, git-ignored, never edit directly)

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
- Use `rename_blog_files.sh` script to rename dated posts if needed

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

## Taxonomy Management

The site uses a taxonomy consolidation system to maintain consistent categories and tags:

### Taxonomy Files
- `taxonomy_map.yaml` - Master configuration defining category/tag consolidation rules
- `taxonomy_map.suggested.yaml` - AI-generated suggestions (review before using)
- `taxonomy_map.generated.yaml` - Generated mapping results from processing

### Taxonomy Scripts
- `apply-taxonomy.py` - Apply taxonomy consolidation based on `taxonomy_map.yaml`
- `suggest-tags.py` - Generate tag suggestions for posts
- `categorize-uncategorized.py` - Suggest categories for uncategorized posts

## Maintenance Scripts

### Shell Scripts
- `deploy.sh` - Commits all changes with timestamp (or custom message) and pushes to main
- `cleanup_images.sh` - Removes legacy/external images (DANGEROUS: review before running)
- `rename_blog_files.sh` - Renames dated blog posts to remove date prefixes (review before running)
- `apply-high-traffic-tags.sh` - Apply tags to high-traffic posts
- `review_changes.sh` - Review staged changes before committing

### Python Audit & Analysis Scripts
- `audit-frontmatter.py` - Analyze front matter for missing fields and inconsistencies (outputs `audit-frontmatter.json`)
- `check-internal-links.py` - Check for broken internal links (outputs `audit-internal-links.json`)
- `check-external-links.py` - Check for broken external links (outputs `audit-external-links.json`)
- `analyze_website_stats.py` - Analyze traffic statistics
- `cleanup_frontmatter.py` - Clean up and standardize front matter fields
- `fix_malformed_yaml.py` - Fix malformed YAML front matter
- `generate_descriptions.py` - Generate descriptions for posts missing them
- `update_descriptions.py` - Update existing descriptions
- `categorize_page_changes.py` - Categorize and analyze page changes
- `show_posts_batch.py` - Display posts in batches for review

### Documentation Files
- `CLAUDE.md` - This file - AI assistant guidance
- `AGENTS.md` - Repository guidelines and conventions
- `AUDIT-*.md` - Various audit reports (structure, frontmatter, internal links, external links, taxonomy, action plan)
- `AUDIT-MASTER-REPORT.md` - Consolidated audit findings
- `CLEANUP-CHECKLIST.md` - Checklist for site maintenance
- `AUDIENCE_GROWTH_STRATEGY.md` - Strategy document
- `WARP.md` - Additional documentation

## Common Workflows

### Adding a New Blog Post
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
1. Front matter audit: `python3 audit-frontmatter.py`
2. Internal links: `python3 check-internal-links.py`
3. External links: `python3 check-external-links.py` (may take time)
4. Review generated JSON files for issues
5. Fix issues incrementally and re-run audits

### Applying Taxonomy Changes
1. Review/edit `taxonomy_map.yaml` for consolidation rules
2. Run `python3 apply-taxonomy.py` to apply changes
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
- Don't run destructive scripts (`cleanup_images.sh`, `rename_blog_files.sh`) without explicit confirmation
- Don't push directly to `main` in production without testing

### Safety Checks
- Before modifying multiple files: run relevant audit scripts first
- Before deploying: check `git status` and `git diff`
- Before taxonomy changes: backup `taxonomy_map.yaml`
- Before link changes: run `check-internal-links.py` afterwards
- Before front matter changes: run `audit-frontmatter.py` afterwards

## Troubleshooting

### Build Failures
- **Error: "Hugo not found"**: Ensure Hugo extended is installed and in PATH
- **Error: "template error"**: Check layout files for syntax errors in Go templates
- **YAML parsing errors**: Run `python3 fix_malformed_yaml.py` to fix front matter
- **Image processing errors**: Check image paths and formats in content files

### Local Development Issues
- **Port 1313 already in use**: Kill existing Hugo server or use `hugo server -p 1314`
- **Changes not reflecting**: Hard refresh browser (Ctrl+F5) or clear cache
- **Theme not loading**: Ensure theme submodule is initialized: `git submodule update --init`

### Content Issues
- **Broken internal links**: Run `python3 check-internal-links.py` and fix reported issues
- **Missing descriptions**: Run `python3 generate_descriptions.py` to auto-generate
- **Inconsistent taxonomy**: Review and apply `taxonomy_map.yaml` with `apply-taxonomy.py`
- **Malformed front matter**: Run `python3 fix_malformed_yaml.py`

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
- Repository: https://github.com/joshuapsteele/joshuapsteele.github.io