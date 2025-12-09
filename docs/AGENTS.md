# Repository Guidelines

This site is built with Hugo (PaperMod theme) and deployed via GitHub Pages. Use the commands and structure below to contribute safely and consistently.

## Project Structure & Module Organization
- `content/` – Markdown content. `content/blog/` for posts, `content/pages/` for static pages.
- `layouts/` – Hugo template overrides (Go templates).
- `assets/` – Custom CSS/images processed by Hugo (`assets/css/extended/custom.css`).
- `static/` – Static files served as-is (favicons, images).
- `themes/` – Theme (PaperMod). Do not edit directly; prefer overrides.
- `public/` – Build output (generated). Do not edit.
- `hugo.yaml` – Site config. Edit with care and commit.

## Build, Test, and Development Commands
- `npm run dev` – Start local server with drafts/future posts: http://localhost:1313.
- `npm run build` – Production build with minify and clean output.
- `npm run build:fast` – Quick build for sanity checks.
- `npm run build:stats` – Build with template metrics (performance insights).
- `npm run deploy` – Runs `deploy.sh` to commit and push `main` (CI publishes).
- Prereqs: Node 18+, Hugo (extended) installed and on PATH.

## Coding Style & Naming Conventions
- Markdown: use YAML front matter. Example:
  ---
  title: "Post Title"
  date: 2025-01-01
  tags: [tag1, tag2]
  categories: [cat]
  draft: true
  ---
- Filenames: `content/blog/my-post.md` (kebab-case). Avoid date prefixes—see `rename_blog_files.sh` if needed.
- Templates: 2-space indentation; semantic HTML. Place overrides under `layouts/` mirroring theme paths.
- CSS: extend via `assets/css/extended/custom.css`.

## Testing Guidelines
- No unit tests; verify locally: `npm run dev`, review pages, menus, feeds, and social images.
- Before PR: run `npm run build` and scan console output for warnings.

## Commit & Pull Request Guidelines
- Commits: concise, imperative summaries (e.g., "Update site content", "Fix menu link").
- Branch from `main`. PRs should include:
  - What changed and why; affected pages.
  - Screenshots for visual changes (desktop/mobile, light/dark).
  - Links to related issues/notes.
- Optional: `./deploy.sh "Your message"` to commit/push when merging directly.

## IndieWeb Features
This site is IndieWeb-enabled. Key implementations:
- **Microformats2**: h-card (homepage), h-entry (posts), h-feed (lists)
- **Webmentions**: Receiving via webmention.io; display via JavaScript
- **Reply Context**: Posts with `in_reply_to` front matter show original post context
- **Identity**: rel="me" links, IndieAuth endpoints, WebFinger for Fediverse
- **POSSE**: Publish here first, syndicate to Micro.blog → Bluesky/Mastodon

When creating reply posts, add to front matter:
```yaml
in_reply_to: "https://example.com/original-post"
```

See CLAUDE.md "IndieWeb Features" section for full technical details.

## Notes & Maintenance
- Housekeeping scripts: `cleanup_images.sh` (removes legacy/external images) and `rename_blog_files.sh` (renames dated posts). Both assume local paths—review before running.
- Avoid editing `public/`. Prefer config, content, and overrides.
