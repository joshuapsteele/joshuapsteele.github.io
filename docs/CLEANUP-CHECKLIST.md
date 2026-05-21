# Maintenance Checklist
## joshuapsteele.com Hugo Site

**Updated:** 2026-05-21
**See:** `AUDIT-MASTER-REPORT.md` for full findings.

> **Living tracker — keep it current.** This is the open-items list for the audit-and-cleanup project. When you complete an item, check it off and move it to "Completed" in the same commit as the change. See the "Audit & Cleanup Project" section of `CLAUDE.md`/`AGENTS.md` for the full logging protocol.

---

## Open Items (prioritized)

### High priority

- [ ] **Fix one confirmed broken internal link.** In `content/blog/my-soccer-kit.md`, change `/recommended-tools-and-resources/` → `/resources/`.

- [ ] **Consolidate tag casing variants.** In `scripts/data/taxonomy_map.yaml`, add rules: `Bonhoeffer` → `bonhoeffer`, `Romans 13` → `romans-13`, `ICE` → `ice`. Apply with `python3 scripts/apply-taxonomy.py`.

### Medium priority

- [ ] **Add descriptions to 13 posts missing them.** Run `python3 scripts/generate_descriptions.py` and review.

- [ ] **Add explicit URL slugs to 7 posts missing `url:` field.** Not urgent (Hugo derives the slug from filename), but explicit URLs prevent accidental breakage.

- [ ] **Prune or consolidate the long tail of tags.** 163 distinct tags with many used only once. Run `scripts/audit-frontmatter.py` to get a fresh list and triage.

- [ ] **Categorize the remaining uncategorized posts (4).** Small number — find them with `python3 scripts/audit-frontmatter.py` and assign manually.

### Low priority / when convenient

- [ ] **Track PaperMod deprecation warnings.** `.Language.LanguageDirection` and `.Language.LanguageCode` are deprecated since Hugo 0.158.0 and used in the PaperMod theme. Watch PaperMod releases; file an upstream issue if needed.

- [ ] **Audit static/wp-content/ for orphaned legacy media.** Use `scripts/cleanup_images.sh` (dangerous — run only after verifying no content references the files).

- [ ] **Review or publish the 2 draft blog posts.**

- [ ] **Re-run external link check.** `docs/AUDIT-06-external-links.md` is the prior inventory (March 2025). Run `python3 scripts/check-external-links.py` for a fresh pass when time allows.

---

## Completed (since last audit)

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
