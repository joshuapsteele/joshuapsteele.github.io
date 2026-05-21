# Site Audit — Master Report

**Date:** 2026-05-21
**Site:** joshuapsteele.com (Hugo / PaperMod)
**Auditor:** Claude Code

---

## What Matters Most (start here)

These are the four areas where attention will produce the most improvement, in order:

1. **Tags on older blog posts.** 134 of 324 blog posts (41%) have no tags at all. Tags are the primary discovery mechanism for related content. Running `scripts/suggest-tags.py` on the untagged posts and reviewing the suggestions is the lowest-effort, highest-return action available.

2. **Tag drift and casing inconsistencies.** Tags have grown to 163 distinct values (up from 114 in October 2025). Two casing variants exist: `bonhoeffer` vs `Bonhoeffer`, and `romans 13` vs `Romans 13`. One oddly-cased tag: `ICE`. Consolidate these with `scripts/apply-taxonomy.py`.

3. **One broken internal link.** `content/blog/my-soccer-kit.md` links to `/recommended-tools-and-resources/` but the page now lives at `/resources/`. Fix this manually.

4. **Hugo deprecation warning from the PaperMod theme.** `.Language.LanguageDirection` and a residual `.Language.LanguageCode` reference in the theme's own templates will eventually break when Hugo removes those APIs. The fix requires opening an issue or PR against PaperMod, or overriding `themes/PaperMod/layouts/_default/baseof.html` locally. Not urgent today, but will become urgent when Hugo removes the deprecated API.

---

## Current State (measured 2026-05-21)

### Content

| Section | Count | Date range |
|---------|-------|------------|
| Blog posts (published) | 322 | 2009-05-10 to 2026-05-17 |
| Blog posts (draft) | 2 | — |
| Notes | 16 | 2026-04-17 to 2026-05-19 |
| Pages | 43 | — |
| **Total pages (Hugo output)** | **730** | — |

The notes section (`content/notes/`) was added in April 2026 as the POSSE canonical feed, syndicated to Mastodon and Threads via Micro.blog.

### Frontmatter Coverage (blog posts, 324 total)

| Field | Missing | % Missing | Status |
|-------|---------|-----------|--------|
| title | 0 | 0% | Good |
| date | 0 | 0% | Good |
| categories | 5 | 1.5% | Good |
| description | 13 | 4.0% | Acceptable |
| url | 7 | 2.2% | Acceptable |
| tags | 134 | 41.4% | Needs work |

### Taxonomy

**Categories (8 distinct):**

| Category | Posts |
|----------|-------|
| theology | 130 |
| personal | 85 |
| ethics | 65 |
| productivity | 59 |
| dissertation | 38 |
| ministry | 13 |
| poem | 1 |
| politics | 1 |
| Uncategorized | 5 |

Note: post counts exceed 324 because some posts carry multiple categories.

The prior audit (October 2025) found 24 categories with 53 uncategorized posts. The consolidation to 8 categories was completed and worked well — only 5 posts remain uncategorized.

**Tags (163 distinct):**

Tags have drifted up from 114 (October 2025) to 163. Top tags: barth (33), research (26), bonhoeffer (25), bible (19), politics (15), list (13), reading (13). Tag casing issues: `bonhoeffer`/`Bonhoeffer`, `romans 13`/`Romans 13`, `ICE`.

### Build

Build succeeds cleanly: 730 pages, 1260ms (tested 2026-05-21 with Hugo 0.161.1 locally, CI uses 0.160.1).

Two deprecation warnings remain from the PaperMod theme (not fixable without theme changes):
- `.Language.LanguageDirection` in `themes/PaperMod/layouts/_default/baseof.html`
- `.Language.LanguageCode` in `themes/PaperMod/layouts/partials/templates/opengraph.html`

Fixed in this audit:
- `languageCode` → `locale` in `hugo.yaml` (was deprecated since Hugo 0.158.0)
- `site.Language.LanguageCode` → `site.Language.Locale` in `layouts/partials/templates/opengraph.html` (project override)

### Internal Links

One confirmed broken internal link:
- `content/blog/my-soccer-kit.md` links to `/recommended-tools-and-resources/` but the resources page URL is now `/resources/`

Most other "suspect" internal links are valid — they use custom `url:` frontmatter overrides that a naive path-checker misses. The existing `scripts/check-internal-links.py` is more reliable than ad-hoc path matching for this.

### External Links

437 distinct external hosts are referenced. A full pass was not done in this audit (the existing `docs/AUDIT-06-external-links.md` is the inventory of known-broken links from the prior audit). Notable:
- Links to `twitter.com/joshuapsteele` exist in several posts — the account appears inactive.
- Several links point to expired church/theology sites (acnatoo.org, various Anglican sites) that may have moved.

### Scripts

All scripts in `scripts/` appear structurally intact (no empty files, no obviously broken imports). The `scripts/README.md` is current as of the April 2026 POSSE setup. Scripts added since October 2025 that are now documented: `check_conversation_sources.py`, `cleanup_posts.py`, `convert-taxonomy-to-kebab-case.py`, `fetch_popular_posts.py`, `fetch_syndication_links.py`, `manage-notes.py`, `migrate-microblog-archive.py`, `taxonomy_tools.py`, `amazon/`.

### Dead Code

All 8 shortcodes have at least one use in content:
- `callout`: 65 uses (most used)
- `audio`: 12 uses
- `figure`: 14 uses
- `gallery`, `files-list`, `amazon-purchases-table`, `linklog-pinned`, `popular-posts`: 1 use each

The `layouts/_default/redirect.html` is used by `content/blog/if-women-can-be-saved-then-women-can-be-priests.md` (redirects to inchristus.com). Not dead.

The Disqus shortname in `hugo.yaml` is commented out — harmless but also harmless to leave.

The `static/wp-content/` directory contains legacy WordPress media. A full incoming-link check against content would be needed to identify orphaned files. The existing `scripts/cleanup_images.sh` is flagged as dangerous — run only after a full link audit.

---

## Improvement Priorities

### High (do next)

1. **Tag the untagged posts.** Run `scripts/suggest-tags.py` on the 134 untagged posts, review suggestions, and apply with `scripts/apply-taxonomy.py`. Focus on high-traffic posts first.

2. **Fix the broken internal link.** Change `/recommended-tools-and-resources/` to `/resources/` in `content/blog/my-soccer-kit.md`.

3. **Consolidate tag casing.** Add rules to `scripts/data/taxonomy_map.yaml` for: `Bonhoeffer` → `bonhoeffer`, `Romans 13` → `romans-13` (or similar), `ICE` → `ice`. Run `scripts/apply-taxonomy.py`.

### Medium (worth doing)

4. **Add missing descriptions.** 13 posts have no description. Run `scripts/generate_descriptions.py` on those posts.

5. **Add missing URL slugs.** 7 posts have no explicit `url:` field. Not a breaking issue (Hugo derives the URL from the filename), but explicit URLs prevent accidental slug changes.

6. **Prune low-value tags.** With 163 distinct tags, many are used only once or twice on old theology posts (sermons, anglicanism-specific terms). Periodic consolidation keeps the tag cloud usable.

7. **Add Bluesky to socialIcons in hugo.yaml.** The account is active, the POSSE workflow syndicates to it, and the GitHub profile already lists it. One-line addition.

### Low (when convenient)

8. **Track the PaperMod deprecation warnings.** Subscribe to PaperMod releases or file the issue upstream. The deprecated APIs will be removed eventually.

9. **Audit static/wp-content/.** Identify and remove orphaned legacy WordPress media files using `scripts/cleanup_images.sh` (run with care, after verifying no content references the files).

10. **Review the 2 draft posts.** Decide whether they should be published, revised, or deleted.

---

## Docs Status (as of 2026-05-21)

| File | Status |
|------|--------|
| AGENTS.md | Current |
| AUDIT-MASTER-REPORT.md | Refreshed (this file) |
| AUDIT-06-external-links.md | From March 2025 — use as baseline; re-run `check-external-links.py` for a full refresh |
| CLEANUP-CHECKLIST.md | Updated |
| NOTES-TOOLS.md | Current (April 2026) |
| POSSE-SETUP.md | Current (April 2026) |
| theology-blog.md | Current |
| archive/AUDIT-01-structure.md | Archived — from October 2025, pre-POSSE |
| archive/AUDIT-02-frontmatter.md | Archived — from October 2025 |
| archive/AUDIT-03-internal-links.md | Archived — from October 2025 |
| archive/AUDIT-04-action-plan.md | Archived — superseded by this report |
| archive/AUDIT-05-taxonomy.md | Archived — taxonomy consolidation was completed |
| archive/AUDIENCE_GROWTH_STRATEGY.md | Archived — strategy document, not a reference artifact |
