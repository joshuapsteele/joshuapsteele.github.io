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

- [x] **Removed remaining legacy WordPress/Jetpack front-matter cruft (2026-05-23).** Deleted 10 dead fields across 9 posts: `format: aside` (×4), `excerpt` (×2), and one each of `tagazine-media` (corrupted value), `advanced_seo_description`, `jetpack_seo_html_title`, and `activitypub_status`. The two `excerpt`s and the `advanced_seo_description` were confirmed redundant with each post's `description` before deletion. None were read by any template. Used a multi-line-aware regex so wrapped values (e.g. the Holy Innocents `excerpt`) were fully removed without leaving orphaned YAML lines. Kept the functional `redirect_to` in the women's-ordination post. `npm run build` clean.
- [x] **Ran Amazon link check; fixed the one dead link (2026-05-23).** `scripts/check-amazon-links.py` checked 458 unique Amazon URLs: **363 working, 150 blocked (CAPTCHA/503 bot defense — left as-is), 1 dead.** The anti-block tactics (browser headers, cookie jar, jittered sequential requests) kept ~79% from being blocked. The one dead link — `https://amzn.to/2Mu7tpI`, a defunct short link to a "Color of Compromise" Prime video in `top-3-books-movies-and-podcasts-about-race-for-white-christians-like-me.md` — had no Wayback snapshot, so it was unlinked with an "(old, broken link)" marker. Report in `docs/AUDIT-amazon-links.md`. The 150 blocked are not actionable (Amazon blocks bots regardless); re-run later or spot-check manually if desired.
- [x] **Fixed dead external links via Wayback + unlink strategy (2026-05-23).** Triaged the 136 dead-link occurrences (108 unique) from the external audit and fixed them: rewrote **88** to Internet Archive snapshots (`lookup-wayback.py` found usable 2xx captures for 69/108 URLs), and **unlinked 43** that had no snapshot, keeping the visible text and appending "(old, broken link)" / "(old, broken image)". Added `scripts/lookup-wayback.py` and `scripts/fix-dead-links.py` to do this. Caught a class of false positives — Wikipedia URLs with parentheses (e.g. `/300_(film)`) were being truncated by the link extractor at the inner `)`; excluded those 5 from fixing and hardened the markdown URL regex in `check-external-links.py`/`check-amazon-links.py` to allow one level of balanced parens. 55 files changed; `npm run build` clean; 0 broken internal links; verified no no-snapshot URL was left as a live link. The 121 "blocked/manual" links were left as-is (bot defense, not breakage). Scripts documented in `CLAUDE.md`/`scripts/README.md`. **Still pending:** Amazon link results (run in progress).
- [x] **External-link tooling overhaul + self-link conversion (2026-05-23).** Prep for the external-link triage. (1) Hardened `scripts/check-external-links.py`: realistic browser headers (the old bot UA got 403'd), per-domain throttling (1 req/host at a time + min interval) to avoid rate-limit false positives, retries with backoff, HEAD→GET fallback, and dead-vs-blocked/manual classification; it now also skips Amazon and self links (handled separately). (2) Added `scripts/check-amazon-links.py` — checks the ~514 Amazon links (amazon.com/amzn.to/a.co) with anti-block best effort (browser headers, persistent cookie jar, sequential jittered delays, redirect-following, CAPTCHA/soft-404 detection). (3) Added `scripts/convert-internal-links.py` and ran it: converted **171 absolute joshuapsteele.com self-links → root-relative** across 90 post bodies (0 failed to resolve; front matter `guid`/`redirect_to` left untouched). `npm run build` clean; internal-link checker still 0 broken. Script docs updated in `CLAUDE.md` and `scripts/README.md`. **Next:** run the two network checkers and triage the dead links.
- [x] **Legacy front-matter cleanup (2026-05-22).** Removed dead WordPress Jetpack `publicize_*` fields (`publicize_facebook_url`, `publicize_twitter_url`, `publicize_twitter_user` — 32 fields across 17 posts; mostly `null`, a few held truncated migration text fragments already covered by each post's `description`). No Hugo template reads these. Also normalized `showtoc`→`showToc` across 40 files for consistency with the PaperMod param name and `hugo.yaml` config — purely cosmetic, since Hugo's `.Param` lookup is case-insensitive (verified the theme reads `(.Param "ShowToc")`, so behavior was already correct). Care taken: the first removal pass left orphaned YAML continuation lines where a `publicize_*` value wrapped across lines (broke the build); redone with a regex that consumes multi-line values. `npm run build` passes; frontmatter audit still 100% on critical fields; 0 broken internal links.
- [x] **Eliminated false positives in `scripts/check-internal-links.py` (2026-05-22).** The checker now validates links against the built site in `public/` (authoritative) instead of reconstructing Hugo's output from front matter. Walking `public/` captures alias redirect pages, generated feeds (`/blog/feed.xml`, `/notes/feed.json`), and the `static/` assets Hugo copies in (`/wp-content/*.pdf`, images) — all previously misreported. Also fixed `extract_links` to strip the markdown `"title"` text from link targets. Falls back to the old content-derived set with a warning if `public/` is absent. Result: broken-link count dropped from 62 (all false positives) to 0, with the valid-URL set growing ~1460→2017; verified it still rejects bogus and removed URLs.
- [x] **Fixed all genuinely broken internal links (2026-05-22).** Repaired the legacy-WordPress link rot surfaced by `scripts/check-internal-links.py` (was 106 flagged across 47 files). Using a ground-truth URL set built from `public/`: redirected 38 dated `/YYYY/MM/DD/slug` permalinks to their current `/slug/`, mapped old taxonomy URLs (`/category/productivity-and-time-management`→`/categories/productivity/`, `/category/personal`→`/categories/personal/`, `/category/sermons`→`/tags/sermons/`, `/tag/cedarville`→`/tags/cedarville/`), fixed `/portfolio/*` and date-mangled slugs, and resolved retitled posts (e.g. Amy Chase "Scripture, Handle With Care"→`/inductive-bible-study-7-steps-amy-chase-ashley/`). For ~9 references to deleted content, applied per-link decisions: redirected some to the closest live post (Romans write-ups→`/romans-distilled-paraphrased/`, "4 questions"→note-taking post, `/start-here`→`/about/`, `/ordination`→ordination-video post), unlinked others (Volf-on-gender, Eisenhower matrix, a leaked `craftdocs://` private link), and removed one broken image embed. Result: 0 genuinely broken internal links; the ~62 still reported are checker false positives (see Low priority item). `npm run build` passes with no warnings.
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
- [x] **Restored Bluesky identity links (2026-07-05).** The account is active again as [`@joshuapsteele.com`](https://bsky.app/profile/joshuapsteele.com); added it to `socialIcons`, public identity/follow pages, repository docs, and syndication-link recognition. Verified with `npm run build` and generated-page checks.
- [x] **Preserved `.well-known` files in Pages deployments (2026-07-05).** Removed the broad dotfile exclusion that discarded Hugo's generated `.well-known` directory and added a CI assertion that the deployment artifact contains `webfinger`.
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
