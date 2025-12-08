# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

This is Joshua P. Steele's personal website built with Hugo static site generator using the PaperMod theme. The site is deployed via GitHub Pages with automated builds and contains 400+ blog posts covering theology, technology, and personal topics.

## Development Commands

### Core Hugo Commands
```bash
# Start development server with drafts and future posts
npm run dev
# Or directly: hugo server --buildDrafts --buildFuture

# Build for production (optimized)
npm run build
# Or directly: hugo --gc --minify --cleanDestinationDir

# Quick build without optimization
npm run build:fast

# Build with performance metrics
npm run build:stats

# Clean build artifacts
npm run clean
```

### Content Management
```bash
# Create new blog post
hugo new content/blog/post-title.md

# Create new page
hugo new content/pages/page-title.md
```

### Deployment
```bash
# Deploy using convenience script
./deploy.sh "Optional commit message"
# Or: npm run deploy

# Manual deployment steps:
git add .
git commit -m "Update content"
git push origin main  # Triggers GitHub Actions
```

### Testing and Development
```bash
# Test local build
hugo && cd public && python3 -m http.server 8080

# Check for broken links (if linkchecker installed)
hugo && linkchecker public/

# Validate Hugo configuration
hugo config
```

## Architecture and Structure

### Content Organization
- **Primary content**: `content/blog/` contains 400+ markdown blog posts
- **Static pages**: `content/pages/` for about, contact, CV, etc.
- **Special pages**: `content/archives.md`, `content/search.md`, `content/files.md`
- **Front matter**: Posts use Hugo's YAML front matter with title, date, tags, categories

### Theme and Customization
- **Base theme**: PaperMod (via Hugo modules or submodules)
- **Custom layouts**: Override theme defaults in `layouts/` directory
- **Custom shortcodes**: Located in `layouts/shortcodes/`:
  - `audio.html` - Embed audio files
  - `figure.html` - Enhanced image handling with WebP conversion
  - `gallery.html` - Image galleries
  - `files-list.html` - Auto-generate file listings from `static/files/`
  - `callout.html` - Styled callout boxes

### Configuration Highlights
- **Profile mode enabled**: Homepage shows author bio with navigation buttons
- **Search**: Powered by Fuse.js with configurable search parameters
- **Performance optimizations**: Asset minification, caching, WebP image conversion
- **Social features**: Multiple social icons, sharing buttons, RSS/JSON feeds
- **Content features**: Table of contents, reading time, breadcrumbs, edit links to GitHub

### Build Process
1. **GitHub Actions workflow** (`.github/workflows/hugo.yml`):
   - Triggers on push to main branch
   - Uses Hugo 0.147.3 with extended features
   - Node.js 20 for npm dependencies
   - Builds with `--gc --minify` flags
   - Deploys to GitHub Pages

2. **Asset processing**:
   - Images converted to WebP format with JPG fallback
   - CSS/JS minification enabled
   - Hugo's built-in asset pipeline for optimization

### Key Features Implementation
- **Multi-format feeds**: RSS XML and JSON Feed formats
- **Edit integration**: Direct links to GitHub for content editing
- **Image optimization**: Automatic WebP conversion with fallbacks
- **Performance monitoring**: Hugo build statistics and metrics
- **Content taxonomy**: Tags and categories with dedicated listing pages

## Development Workflow

### Adding New Content
1. Blog posts go in `content/blog/` with descriptive filenames
2. Use Hugo archetypes for consistent front matter
3. Preview with `npm run dev` before publishing
4. Deploy with `./deploy.sh "Description of changes"`

### Customizing Layouts
- Override theme templates by placing files in `layouts/` with same structure
- Custom shortcodes go in `layouts/shortcodes/`
- Partials for reusable components in `layouts/partials/`

### Managing Static Assets
- Images and files in `static/` directory
- Use `figure` shortcode for optimized image display
- Files in `static/files/` auto-listed via `files-list` shortcode

## Important Files and Directories

- `hugo.yaml` - Main site configuration with theme settings, menu, social icons
- `package.json` - NPM scripts for development workflow
- `deploy.sh` - Deployment automation script
- `CLAUDE.md` - Existing AI assistant guidance (reference for consistency)
- `layouts/shortcodes/` - Custom content components
- `.github/workflows/hugo.yml` - CI/CD pipeline configuration

## Special Considerations

### Performance
- Site uses aggressive caching and minification
- Images automatically optimized to WebP with fallbacks
- Hugo's fast render mode available for development

### Content Standards
- Blog posts should include front matter with proper tags/categories
- Use existing shortcodes for consistent formatting
- Images should be web-optimized before adding to static/

### Deployment Notes
- Automatic deployment via GitHub Actions on main branch push
- Manual deployment possible via `deploy.sh` script
- Built site goes to `public/` directory (git ignored)
- GitHub Pages serves from repository root after build
