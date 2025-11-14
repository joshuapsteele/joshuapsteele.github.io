# Joshua P. Steele's Personal Website

[![Hugo](https://img.shields.io/badge/Hugo-0.147.3-blue.svg)](https://gohugo.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Deploy Hugo site to Pages](https://github.com/joshuapsteele/joshuapsteele.github.io/actions/workflows/hugo.yml/badge.svg)](https://github.com/joshuapsteele/joshuapsteele.github.io/actions/workflows/hugo.yml)

This is the source code for my personal website and blog, built with Hugo and deployed via GitHub Pages.

**Live Site**: [joshuapsteele.com](https://joshuapsteele.com)

## Tech Stack

- **Static Site Generator**: [Hugo](https://gohugo.io/) 0.147.3 (Extended)
- **Theme**: [PaperMod](https://github.com/adityatelange/hugo-PaperMod)
- **Deployment**: GitHub Pages with GitHub Actions
- **Search**: Fuse.js
- **Node**: 18+ (local) / 20 (CI)

## Features

- 📝 Blog with 300+ posts organized by categories and tags
- 🔍 Full-text search functionality
- 📱 Responsive design with dark mode support
- 📊 RSS and JSON feeds
- 🏷️ Taxonomy management system
- 💬 Comment system integration (Disqus)
- 📈 Analytics integration (Google Analytics, Tinylytics)
- ⚡ Optimized build with minification and caching

## Quick Start

### Prerequisites

- [Hugo Extended](https://gohugo.io/installation/) 0.147.3+
- [Node.js](https://nodejs.org/) 18+
- Git

### Installation

```bash
# Clone the repository with submodules
git clone --recurse-submodules https://github.com/joshuapsteele/joshuapsteele.github.io.git
cd joshuapsteele.github.io

# If you forgot --recurse-submodules, initialize them:
git submodule update --init --recursive

# Install dependencies (if any)
npm install
```

### Development

```bash
# Start local development server with drafts
npm run dev
# Site will be available at http://localhost:1313

# Build for production
npm run build

# Build without minification (faster)
npm run build:fast

# Build with template performance metrics
npm run build:stats

# Clean generated files
npm run clean
```

## Project Structure

```
.
├── content/
│   ├── blog/          # Blog posts (309 markdown files)
│   ├── pages/         # Static pages (about, contact, cv, etc.)
│   └── search.md      # Search page
├── layouts/           # Custom Hugo layouts and overrides
│   ├── shortcodes/    # Custom shortcodes (audio, callout, figure, etc.)
│   ├── partials/      # Partial templates
│   └── _default/      # Default layouts
├── static/            # Static assets (images, PDFs, favicons)
├── assets/            # Processed assets (CSS extensions)
├── themes/            # PaperMod theme (git submodule)
├── public/            # Generated site (git-ignored)
├── hugo.yaml          # Main site configuration
└── .github/
    └── workflows/
        └── hugo.yml   # GitHub Actions deployment workflow
```

## Content Management

### Creating a New Blog Post

```bash
# Create a new post file in content/blog/
# Use kebab-case naming: my-new-post.md
```

Example front matter:
```yaml
---
title: "My New Post"
date: 2025-11-14
tags: ["hugo", "blogging"]
categories: ["Tech"]
description: "A brief description of the post"
draft: false
---

Your content here...
```

### Customizing the Theme

- **CSS**: Edit `assets/css/extended/custom.css` (do not edit theme files directly)
- **Layouts**: Create overrides in `layouts/` mirroring theme paths
- **Shortcodes**: Add custom shortcodes in `layouts/shortcodes/`

## Deployment

The site automatically deploys to GitHub Pages when changes are pushed to the `main` branch via GitHub Actions.

### Manual Deployment

```bash
# Using the deploy script (commits all changes and pushes to main)
npm run deploy
# or with a custom commit message:
./deploy.sh "Your commit message"
```

**Important**: Always test locally with `npm run dev` and `npm run build` before deploying!

## Maintenance Tools

### Audit Scripts (Python)
- `audit-frontmatter.py` - Check front matter consistency
- `check-internal-links.py` - Verify internal links
- `check-external-links.py` - Check external links
- `apply-taxonomy.py` - Apply taxonomy consolidation

### Utility Scripts (Shell)
- `deploy.sh` - Automated deployment to main branch
- `review_changes.sh` - Review staged changes
- `apply-high-traffic-tags.sh` - Tag management

## Configuration

Main configuration is in `hugo.yaml`. Key settings include:

- **Profile Mode**: Custom homepage with profile buttons
- **Navigation**: Top menu and footer customization
- **Social**: BlueSky, Mastodon, GitHub, LinkedIn, RSS
- **Search**: Fuse.js configuration
- **Feeds**: RSS and JSON output formats
- **Build**: Image optimization, caching, minification

## Documentation

- **[CLAUDE.md](CLAUDE.md)** - Comprehensive guide for AI assistants working with this codebase
- **[AGENTS.md](AGENTS.md)** - Repository guidelines and conventions
- **Audit Reports** - Various `AUDIT-*.md` files with site analysis

## Contributing

This is a personal website, but if you notice any issues or have suggestions:

1. Open an issue describing the problem or suggestion
2. If you'd like to contribute a fix, fork the repo and submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details

## Contact

- **Website**: [joshuapsteele.com](https://joshuapsteele.com)
- **Blog**: [joshuapsteele.com/blog](https://joshuapsteele.com/blog)
- **Contact**: [joshuapsteele.com/contact](https://joshuapsteele.com/contact)

## Acknowledgments

- Built with [Hugo](https://gohugo.io/)
- Theme: [PaperMod](https://github.com/adityatelange/hugo-PaperMod) by Aditya Telange
- Hosted on [GitHub Pages](https://pages.github.com/)
