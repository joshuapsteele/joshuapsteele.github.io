# Maintenance Checklist
## joshuapsteele.com Hugo Site

**Updated:** 2026-05-21
**See:** `AUDIT-MASTER-REPORT.md` for full findings.

> **Living tracker — keep it current.** This is the open-items list for the audit-and-cleanup project. When you complete an item, check it off and move it to "Completed" in the same commit as the change. See the "Audit & Cleanup Project" section of `CLAUDE.md`/`AGENTS.md` for the full logging protocol.

---

## Open Items (prioritized)

### High priority

_No open high-priority items._

### Medium priority

_No open medium-priority items._

### Low priority / when convenient

- [ ] **Review orphaned legacy media candidates before deletion.** `docs/AUDIT-static-wp-content.md` identifies 32 orphan candidates. Do not run `scripts/cleanup_images.sh` as-is; it would remove files still referenced by site content.

---

## Completed (since last audit)

- [x] **Audited `static/wp-content/` legacy media (2026-05-21).** Added a non-destructive audit script and generated `docs/AUDIT-static-wp-content.md` plus `scripts/data/audit-static-wp-content.json`. Current pass found 151 files / 391.7 MiB: 119 referenced by site sources, 32 orphan candidates. No media was deleted, and `scripts/cleanup_images.sh` was not run because it would remove the entire directory despite live references.
- [x] **Re-ran external link check (2026-05-21).** Updated `docs/AUDIT-06-external-links.md` and `scripts/data/audit-external-links.json`. Current pass found 2003 external links across 283 files: 1689 working, 314 broken/error, 0 timeouts.
- [x] **Resolved PaperMod deprecation warnings locally (2026-05-21).** Added project overrides for `layouts/_default/baseof.html` and `layouts/_default/rss.xml`, replacing deprecated `.Language.LanguageDirection` and `.Language.LanguageCode` usage without editing `themes/`. `npm run build` now passes without deprecation warnings.
- [x] **Completed first-pass tag pruning (2026-05-21).** Consolidated obvious duplicate and non-kebab tags (`political theology`, `matthew 25`, `public health`, `prophetic witness`, `Christianity`, `churches`, `pareto`). `python3 scripts/audit-frontmatter.py` now reports 166 distinct tags, below the 175 maintenance target.
- [x] **Completed blog front matter coverage cleanup (2026-05-21).** Added/fixed missing or empty descriptions, added explicit `url:` fields, and categorized the remaining uncategorized blog posts. `python3 scripts/audit-frontmatter.py` now reports 0 posts missing categories, tags, descriptions, URLs, or dates.
- [x] **Removed stale draft smoke-test post (2026-05-21).** `content/blog/drafts-action-smoke-test.md` was deleted by the user; the front matter audit now reports 0 draft blog posts.
- [x] **Fixed one confirmed broken internal link (2026-05-21).** In `content/blog/my-soccer-kit.md`, changed `/recommended-tools-and-resources/` → `/resources/`. Verified the targeted link is absent from `python3 scripts/check-internal-links.py` output; `npm run build` passes.
- [x] **Consolidated tag casing variants (2026-05-21).** Added taxonomy cleanup rules for `Bonhoeffer` → `bonhoeffer`, `Romans 13` → `romans-13`, `ICE` → `ice`, plus existing lowercase-space `romans 13` → `romans-13`; applied with `python3 scripts/apply-taxonomy.py --apply`. A follow-up dry run reports 0 remaining taxonomy changes.
- [x] **Tagged all untagged blog posts (2026-05-21).** 132 posts tagged across ministry, dissertation, productivity, theology, personal, ethics + the AMA post; 0 untagged remaining. Added new tags: `podcasts`, `personality`, `lent`, `creation`, `trinity`, `cedarville`, `travel`, `gtd`, `pacifism`, `jordan-peterson`. See `docs/TAGGING-PROGRESS.md`.
- [x] Bluesky socialIcons item dropped: the account was deleted by the user, so the "add Bluesky" recommendation is void (do not re-add).
- [x] Category consolidation: 24 categories → 8 (October 2025 → current)
- [x] Uncategorized posts reduced: 53 → 5
- [x] `/notes/` section added (April 2026), POSSE workflow configured
- [x] POSSE setup documented in `docs/POSSE-SETUP.md`
- [x] `languageCode` → `locale` in `hugo.yaml` (deprecated since Hugo 0.158.0)
- [x] `site.Language.LanguageCode` → `site.Language.Locale` in `layouts/partials/templates/opengraph.html`
- [x] Stale audit docs (AUDIT-01 through AUDIT-05, October 2025) moved to `docs/archive/`

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
- Review tag list for drift (target: stay below 175 distinct tags)

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
