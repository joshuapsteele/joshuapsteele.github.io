# Maintenance Checklist
## joshuapsteele.com Hugo Site

**Updated:** 2026-05-22
**See:** `AUDIT-MASTER-REPORT.md` for full findings.

> **Living tracker — keep it current.** This is the open-items list for the audit-and-cleanup project. When you complete an item, check it off and move it to "Completed" in the same commit as the change. See the "Audit & Cleanup Project" section of `CLAUDE.md`/`AGENTS.md` for the full logging protocol.

---

## Open Items (prioritized)

### High priority

_No open high-priority items._

### Medium priority

_No open medium-priority items._

### Low priority / when convenient

_No open low-priority items._

---

## Completed (since last audit)

- [x] **Site-wide Amazon affiliate link cleanup (2026-05-22).** Canonicalized every Amazon product link across `content/` (34 files, 74 links) to `https://www.amazon.com/dp/<ASIN>?tag=joshuapsteele-20` — stripping tracking junk (`dib`/`crid`/`qid`/`linkId`/etc.) and slug paths, upgrading `http`→`https`, adding the affiliate tag to previously untagged links, and replacing four third-party tags (`anglicanpasto-20`, `bettwowor0e-20`, `faithinirelan-20`) with the owner's tag per his instruction. Amazon **search** (`/s?k=`) and **wishlist** (`/hz/wishlist/`) links were intentionally left alone (no product ASIN). Done with a reusable regex over `/dp/`, `/gp/product/`, and `/gp/aw/d/` forms; `npm run build` passes.
- [x] **Cleaned `/resources` Amazon links and added `/catechism` description (2026-05-22).** Added a missing front-matter `description` to `/catechism` (Episcopal/Anglican catechism). On `/resources`, canonicalized 9 tracking-laden Amazon URLs to `https://www.amazon.com/dp/<ASIN>?tag=joshuapsteele-20`, preserving the affiliate tag while dropping `dib`/`crid`/`qid`/`linkId`/etc. `npm run build` passes.
- [x] **Refreshed site-meta and tools pages (2026-05-22).** `/colophon`: removed Google Analytics (the `google_analytics.html` partial is empty and no GA is configured — only Tinylytics is active), made the cookieless/privacy claim accurate, and dropped stale version pins (`Hugo 0.147.3`, exact Node versions). `/slashes`: added the two existing-but-unlisted pages `/resist` and `/subscriptions`. `/resources` (alias `/uses` — same page): added an affiliate-link disclosure callout and updated the current computer to a 2024 Mac Mini (M4), keeping the 2016 MacBook Pro as "Previous." `/posse` reviewed and left as-is (current). `npm run build` passes with no warnings.
- [x] **Drafted first public-facing page refresh (2026-05-22).** Updated the homepage profile buttons plus `/about`, `/now`, `/contact`, `/follow`, and selected `/cv` links/status text to make the front door clearer and less stale. Verified with `npm run build` and local Hugo server checks. Not pushed; waiting for approval before publishing.
- [x] **Refreshed living repository documentation (2026-05-22).** Removed quick-stale counts/version pins from `README.md`, `CLAUDE.md`, `docs/AGENTS.md`, `scripts/README.md`, and active cleanup/tagging docs; kept dated audit reports as point-in-time snapshots. Retired one-off scripts that could overwrite completed taxonomy/description work.
- [x] **Parked legacy media cleanup (2026-05-22).** Reviewed the `static/wp-content/` audit outcome and decided to leave legacy media in place for now. Unused files add repo weight, but they do not affect page runtime unless referenced by rendered pages. Do not run `scripts/cleanup_images.sh` as-is; use `scripts/audit-static-wp-content.py` for future review.
- [x] **Completed popular-post description curation (2026-05-22).** Reviewed the full ranked blog-post traffic list from the available Tinylytics CSV export, rewrote weak/fallback descriptions, and left already-useful descriptions intact. `python3 scripts/audit-frontmatter.py` and `npm run build` passed after the curation work.
- [x] **Refreshed and hardened popular-post analytics data (2026-05-21).** Updated `scripts/fetch_popular_posts.py` to support Tinylytics CSV exports, filter to actual Hugo blog posts, generate data for `/popular/`, and refuse to overwrite `data/popular.json` with an empty result. Refreshed `data/popular.json` from the available Tinylytics export; `npm run build` renders `/popular/` with current posts.
- [x] **Audited `static/wp-content/` legacy media (2026-05-21).** Added a non-destructive audit script and generated `docs/AUDIT-static-wp-content.md` plus `scripts/data/audit-static-wp-content.json`. No media was deleted, and `scripts/cleanup_images.sh` was not run because it would remove the entire directory despite live references.
- [x] **Re-ran external link check (2026-05-21).** Updated `docs/AUDIT-06-external-links.md` and `scripts/data/audit-external-links.json`; use those generated files for current details instead of copying counts here.
- [x] **Resolved PaperMod deprecation warnings locally (2026-05-21).** Added project overrides for `layouts/_default/baseof.html` and `layouts/_default/rss.xml`, replacing deprecated `.Language.LanguageDirection` and `.Language.LanguageCode` usage without editing `themes/`. `npm run build` now passes without deprecation warnings.
- [x] **Completed first-pass tag pruning (2026-05-21).** Consolidated obvious duplicate and non-kebab tags (`political theology`, `matthew 25`, `public health`, `prophetic witness`, `Christianity`, `churches`, `pareto`). Use `python3 scripts/audit-frontmatter.py` for the current tag count.
- [x] **Completed blog front matter coverage cleanup (2026-05-21).** Added/fixed missing or empty descriptions, added explicit `url:` fields, and categorized previously uncategorized blog posts. Use `python3 scripts/audit-frontmatter.py` for current coverage.
- [x] **Removed stale draft smoke-test post (2026-05-21).** `content/blog/drafts-action-smoke-test.md` was deleted by the user.
- [x] **Fixed one confirmed broken internal link (2026-05-21).** In `content/blog/my-soccer-kit.md`, changed `/recommended-tools-and-resources/` → `/resources/`. Verified the targeted link is absent from `python3 scripts/check-internal-links.py` output; `npm run build` passes.
- [x] **Consolidated tag casing variants (2026-05-21).** Added taxonomy cleanup rules for `Bonhoeffer` → `bonhoeffer`, `Romans 13` → `romans-13`, `ICE` → `ice`, plus existing lowercase-space `romans 13` → `romans-13`; applied with `python3 scripts/apply-taxonomy.py --apply`.
- [x] **Tagged all untagged blog posts (2026-05-21).** Added tags across the older untagged backlog and documented the new vocabulary in `docs/TAGGING-PROGRESS.md`.
- [x] Bluesky socialIcons item dropped: the account was deleted by the user, so the "add Bluesky" recommendation is void (do not re-add).
- [x] Category consolidation completed (October 2025 audit cycle)
- [x] `/notes/` section added (April 2026), POSSE workflow configured
- [x] POSSE setup documented in `docs/POSSE-SETUP.md`
- [x] `languageCode` → `locale` in `hugo.yaml` (deprecated since Hugo 0.158.0)
- [x] `site.Language.LanguageCode` → `site.Language.Locale` in `layouts/partials/templates/opengraph.html`
- [x] Stale October 2025 audit docs moved to `docs/archive/`

---

## Ongoing Maintenance

**Each new post:**
- Assign a category (one of: theology, ethics, personal, productivity, dissertation, ministry, poem, politics)
- Add 3-5 tags in kebab-case
- Add a description (1-2 sentences)

**Monthly:**
- Run `python3 scripts/audit-frontmatter.py` and review output in `scripts/data/`
- Spot-check for new broken links

**Quarterly:**
- Run `python3 scripts/check-internal-links.py` and fix confirmed broken links
- Review tag list for drift and consolidate obvious duplicates

---

## Quick Commands

```bash
# Audit frontmatter coverage
python3 scripts/audit-frontmatter.py

# Check internal links
python3 scripts/check-internal-links.py

# Suggest tags for untagged posts
python3 scripts/suggest-tags.py

# Apply taxonomy consolidation
python3 scripts/apply-taxonomy.py

# Build and verify
npm run build

# Local dev server
npm run dev

# Deploy (commits all changes and pushes to main)
npm run deploy "Describe changes here"
```
