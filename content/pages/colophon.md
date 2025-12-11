---
title: Colophon
description: How this website is built, hosted, and designed to be independent and user-controlled
url: /colophon
draft: false
showtoc: true
---

This page describes the technical details, design philosophy, and tools behind this website.

## Infrastructure

- **Domain registrar**: [Porkbun](https://porkbun.com/)
- **Hosting**: [GitHub Pages](https://pages.github.com/)
- **Repository**: [github.com/joshuapsteele/joshuapsteele.github.io](https://github.com/joshuapsteele/joshuapsteele.github.io)
- **Deployment**: Automated via [GitHub Actions](https://github.com/joshuapsteele/joshuapsteele.github.io/actions)

## Tech Stack

- **Static Site Generator**: [Hugo](https://gohugo.io/) 0.147.3 Extended
- **Theme**: [PaperMod](https://github.com/adityatelange/hugo-PaperMod) by Aditya Telange
- **Node.js**: 18+ (local development) / 20 (CI)
- **Search**: [Fuse.js](https://fusejs.io/) for client-side full-text search
- **Feeds**: RSS and JSON Feed formats

## Design Philosophy

This site embraces several web philosophies:

### IndieWeb

I'm part of the [IndieWeb](https://indieweb.org/), a community effort to keep the web independent and user-controlled. This site implements:

- **Identity & Discovery**
  - [h-card](https://microformats.org/wiki/h-card) microformats for machine-readable identity
  - [rel="me"](https://indieweb.org/rel-me) links for identity verification across platforms
  - [WebFinger](https://webfinger.net/) for Fediverse discovery
  - [IndieAuth](https://indieauth.com/) for signing in with my domain

- **Social Interactions**
  - [Webmentions](https://webmention.io/) for receiving interactions from across the web
  - [Bridgy](https://brid.gy/) for backfeeding social media interactions
  - Reply context display when responding to others' posts
  - Integration with Bluesky, Mastodon, and Micro.blog

- **Content Ownership**
  - [POSSE](https://indieweb.org/POSSE) workflow (Publish Own Site, Syndicate Everywhere)
  - All content published here first, then syndicated
  - [Microformats2](https://microformats.org/) markup (h-entry, h-feed) for machine readability

### Digital Garden

This site incorporates [digital garden](https://maggieappleton.com/garden-history) principles:

- **Topography over timelines**: Posts are connected by topic through "Connected Notes" rather than just chronology
- **Continuous growth**: Content evolves over time (visible through Git history)
- **Learning in public**: Sharing thoughts at various stages of development
- **Dense interconnections**: Related posts linked through tags, categories, and content relationships

## Features

- 📝 **300+ blog posts** organized by categories and tags
- 🔍 **Full-text search** with fuzzy matching
- 📱 **Responsive design** with dark mode support
- 💬 **Multiple interaction methods**: Webmentions, email, social media
- 🌿 **Connected notes** showing related posts by topic
- 📊 **RSS and JSON feeds** for syndication
- 🌐 **Micro.blog integration** showing recent posts on homepage

## Content & Licensing

This repository uses a dual-license structure:

- **Code & Configuration**: [MIT License](https://github.com/joshuapsteele/joshuapsteele.github.io/blob/main/LICENSE-CODE) - feel free to use the site's technical implementation
- **Written Content**: [CC BY-NC-SA 4.0](https://github.com/joshuapsteele/joshuapsteele.github.io/blob/main/LICENSE-CONTENT) - you can share and adapt with attribution, but not for commercial purposes

## Analytics & Privacy

- **Analytics**: [Google Analytics](https://analytics.google.com/) and [Tinylytics](https://tinylytics.app/)
- **No tracking cookies**: Analytics are privacy-respecting and aggregate
- **No ads**: This site is completely ad-free
- **No paywalls**: All content is freely accessible

## Development

The site is built with modern web standards and optimized for performance:

- **Image optimization**: CatmullRom resampling, quality 75
- **Minification**: HTML, CSS, and JavaScript compressed for production
- **Caching**: Resource caching configured for optimal performance
- **Build time**: Typically under 5 seconds for full site generation
- **Version control**: Full Git history preserved for content evolution

## Source Code

The complete source code for this site is available on GitHub:
- [View the code](https://github.com/joshuapsteele/joshuapsteele.github.io)
- [See the documentation](https://github.com/joshuapsteele/joshuapsteele.github.io/blob/main/README.md)
- [Explore the architecture](https://github.com/joshuapsteele/joshuapsteele.github.io/blob/main/CLAUDE.md)

## Credits & Acknowledgments

- **Static site generator**: [Hugo](https://gohugo.io/) by Steve Francia and contributors
- **Theme**: [PaperMod](https://github.com/adityatelange/hugo-PaperMod) by Aditya Telange
- **Hosting**: [GitHub Pages](https://pages.github.com/)
- **Domain**: [Porkbun](https://porkbun.com/)
- **Webmentions**: [Webmention.io](https://webmention.io/) by Aaron Parecki
- **Social bridging**: [Brid.gy](https://brid.gy/) by Ryan Barrett
- **IndieWeb community**: For inspiration and standards

## Site Evolution

This site is continuously evolving. Recent additions include:

- Enhanced webmention display with interaction counters
- Connected notes for digital garden navigation
- Reply context for threaded conversations
- Micro.blog feed integration on homepage
- Comprehensive microformats2 markup

The full history of changes is available in the [Git commit log](https://github.com/joshuapsteele/joshuapsteele.github.io/commits/main).

{{< callout "note" >}}
This `/colophon` page is just one of [my many "slash pages."](/slashes)
{{< /callout >}}