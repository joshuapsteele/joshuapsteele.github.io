# Joshua P. Steele's Personal Website

[![Hugo](https://img.shields.io/badge/Hugo-0.147.3-blue.svg)](https://gohugo.io/)
[![Code License: MIT](https://img.shields.io/badge/Code%20License-MIT-yellow.svg)](LICENSE-CODE)
[![Content License: CC BY-NC-SA 4.0](https://img.shields.io/badge/Content%20License-CC%20BY--NC--SA%204.0-lightgrey.svg)](LICENSE-CONTENT)
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
- 🌐 **IndieWeb Integration**:
  - Microformats2 markup (h-card, h-entry, h-feed)
  - Webmention support for receiving interactions
  - Reply context display for reply posts
  - IndieAuth for domain-based authentication
  - WebFinger for Fediverse discovery
  - rel="me" identity verification
  - POSSE workflow (Publish Own Site, Syndicate Everywhere)

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

## IndieWeb Features

This site is part of the [IndieWeb](https://indieweb.org/), a community effort to keep the web independent and user-controlled.

### Identity & Discovery

- **h-card**: Machine-readable identity information on the homepage
- **rel="me"**: Verified links to other profiles (Micro.blog, Bluesky, Mastodon)
- **WebFinger**: Fediverse discovery at `/.well-known/webfinger`
- **IndieAuth**: Sign in with your domain at `https://joshuapsteele.com`

### Content Markup

- **h-entry**: Blog posts marked up with microformats2 for machine readability
- **h-feed**: Blog list pages formatted as feeds for IndieWeb readers
- **Semantic classes**: `p-name`, `e-content`, `dt-published`, `p-author`, `p-category`

### Social Interactions

- **Webmentions**: Receive likes, replies, and mentions from across the web
  - Powered by [webmention.io](https://webmention.io/)
  - JavaScript-based display of webmentions on each post
  - Grouped by type: likes, reposts, replies, mentions
- **Bridgy**: Backfeed social media interactions as webmentions
  - [brid.gy](https://brid.gy/) integration for Bluesky and Mastodon

### Reply Posts

Create reply posts by adding `in_reply_to` to your front matter:

```yaml
---
title: "My Reply"
date: 2025-12-09
in_reply_to: "https://example.com/original-post"
---
```

The site will automatically:
- Display a reply context card showing the original post
- Mark up the post with `u-in-reply-to` for proper webmention threading
- Attempt to fetch and show the original author, title, and excerpt

### IndieWeb Webring

This site is part of the [IndieWeb Webring](https://xn--sr8hvo.ws/) - a collection of IndieWeb sites linked together. Find the webring navigation in the footer.

### POSSE Workflow

Posts are published on this site first, then syndicated to:
- [Micro.blog](https://social.joshuapsteele.com/)
- [Bluesky](https://bsky.app/profile/joshuapsteele.bsky.social)
- [Mastodon](https://mastodon.social/@joshuapsteele)

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

This repository uses a dual-license structure:

### Code and Configuration (MIT License)

The code, scripts, layouts, configuration files, and other technical implementations in this repository are licensed under the **MIT License** - see [LICENSE-CODE](LICENSE-CODE) file for details.

This includes but is not limited to:
- Hugo configuration (`hugo.yaml`)
- Layout templates and partials (`layouts/`)
- Custom shortcodes
- Build scripts and automation tools
- CSS and JavaScript files
- GitHub Actions workflows

### Content (CC BY-NC-SA 4.0)

All original written content, including blog posts, articles, and pages in the `content/` directory, is licensed under the **Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License** - see [LICENSE-CONTENT](LICENSE-CONTENT) file for details.

This means:
- ✅ You can share and adapt the content with attribution
- ❌ You cannot use it for commercial purposes
- 🔄 Derivative works must use the same license
- 📝 You must provide proper attribution and indicate changes

**In summary**: Feel free to learn from and use the site's code and configuration, but please don't republish my writing without permission.

## Contact

- **Website**: [joshuapsteele.com](https://joshuapsteele.com)
- **Blog**: [joshuapsteele.com/blog](https://joshuapsteele.com/blog)
- **Contact**: [joshuapsteele.com/contact](https://joshuapsteele.com/contact)

## Acknowledgments

- Built with [Hugo](https://gohugo.io/)
- Theme: [PaperMod](https://github.com/adityatelange/hugo-PaperMod) by Aditya Telange
- Hosted on [GitHub Pages](https://pages.github.com/)
