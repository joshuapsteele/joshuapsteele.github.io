# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is Joshua P. Steele's personal website built with Hugo static site generator using the PaperMod theme. The site is deployed via GitHub Pages with automated builds.

## Site Architecture

- **Static Site Generator**: Hugo (extended version required, Node 18+ environment)
- **Theme**: PaperMod (in `themes/` directory, override via `layouts/` and `assets/`)
- **Content Structure**:
  - `content/blog/` - Blog posts (400+ markdown files with YAML front matter)
  - `content/pages/` - Static pages (about, contact, cv, etc.)
  - `content/search.md` - Search functionality
- **Layouts**: Custom Hugo layouts in `layouts/` directory
  - Custom shortcodes: audio, callout, figure, files-list, and gallery
  - Partials for comments, analytics (google_analytics, tinylytics_kudos), and site components
  - Custom blockquote rendering (`layouts/_default/_markup/render-blockquote.html`)
- **Static Assets**: Images and files in `static/` directory (served as-is)
- **Processed Assets**: `assets/css/extended/custom.css` for theme extensions
- **Configuration**: `hugo.yaml` (main site configuration)
- **Build Output**: `public/` directory (generated, do not edit)

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
The site uses GitHub Actions for automated deployment. The `deploy.sh` script handles:
1. Adding changes to git
2. Committing with timestamp or custom message
3. Pushing to main branch (triggers GitHub Actions build)

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
- Profile mode enabled with 20+ custom buttons and social icons
- Search functionality with Fuse.js (configurable in `hugo.yaml` under `fuseOpts`)
- RSS and JSON feeds enabled (custom output formats: `/feed.xml`, `/feed.json`)
- Edit links point to GitHub repository
- Image optimization: WebP/JPG conversion, quality 75, CatmullRom resampling
- Build stats and caching enabled for performance
- Custom minification settings for production builds

## Taxonomy Management
- `taxonomy_map.yaml` - Define consolidation rules for tags and categories
- `taxonomy_map.suggested.yaml` - AI-generated suggestions (review before using)
- `taxonomy_map.generated.yaml` - Generated mapping results

## Maintenance Scripts
- `deploy.sh` - Commits all changes with timestamp and pushes to main
- `cleanup_images.sh` - Removes legacy/external images (review before running)
- `rename_blog_files.sh` - Renames dated blog posts (review before running)

## Verification Before Deployment
- Run `npm run dev` and review pages, menus, feeds, social images locally (http://localhost:1313)
- Run `npm run build` and scan console output for warnings before deploying
- No unit tests; manual verification required