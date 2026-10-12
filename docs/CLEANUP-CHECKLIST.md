# Maintenance checklist

**Updated:** 2026-10-12

Current baseline: [October audit](AUDIT-2026-10-12.md). Procedures: [maintenance guide](MAINTENANCE.md). Historical reports: [archive](archive/). Git records earlier completed work; this tracker is not a parallel changelog.

## Open work

### Medium priority

- [ ] Write or verify alt text for legacy content images. The October production scan found 50 occurrences without `alt`, including old WordPress figures, slide thumbnails, remote images, and an Amazon tracking pixel. Review images in context: do not use guessed filename descriptions or blanket empty alt text for meaningful images. This is an accessibility content pass, not a build failure.

### Optional / low priority

- [ ] Individually review the 21 legacy-media orphan candidates (about 10.3 MiB); check public/inbound URL needs before deleting anything. No media deletion or history rewrite is part of this cleanup.
- [ ] Consider splitting extended CSS by feature when next editing those features. Keep the current cascade and `custom.css` entry point for now; removing its duplicate load already addresses the runtime issue.
- [ ] Revisit Obsidian workspace/plugin tracking only if repository churn outweighs the benefit to the writing workflow. Existing editor files are deliberately preserved.
- [ ] Separate generated audit/suggestion data from canonical configuration after checking consumers. Current `scripts/data/` files remain available to existing scripts.

## Completed in the October cleanup

- [x] Fixed all 9 broken rendered link occurrences, kept drafts unpublished, and added an alias for the older credo URL. Production link/asset validation now runs in `npm run build`; the older source checker can no longer accept source existence over missing production output.
- [x] Moved conversations/reply context into fingerprinted JavaScript. Counter and display share fetches and deduplication; reply context reads the original URL from its data attribute. Counters render only on single posts, avoiding repeated IDs on lists.
- [x] Removed duplicate CSS/social metadata and the site-wide 2.2 MB social-image preload. Kept cover/default image behavior and meaningful Open Graph image alt text.
- [x] Added read-only PR verification, pinned Hugo 0.167.0 centrally, and adopted per-format image quality. Local production build has no warnings.
- [x] Hardened deployment: staged changes on main only, verification before commit/push, fail-fast behavior, exact gate revision, freshness check inside serialized deployment, and Webmentions after successful deployment using that artifact. Workflow syntax passes actionlint; hosted deployment itself has not been exercised or triggered in this session.
- [x] Removed unmatched footer markup and corrected guest-author attribution in HTML and JSON Feed. Normalized draft taxonomy while retaining/documenting the existing published `diy` category.
- [x] Archived four superseded reports and the completed tagging handoff byte-for-byte. Added a documentation index and maintenance guide; report generators now use dated Markdown filenames, accept `--report`, and reject overwriting existing reports.
- [x] Retired the unsafe bulk image-deletion script, stopped tracking `.hugo_build.lock` while preserving its local copy, documented optional Python requirements and actual vendored-theme/CI setup.
- [x] Verification: 5 Python + 2 JavaScript regression tests pass; production build and 110-page/530-link disclosure check pass; rendered links/assets/metadata/JSON/XML check passes; source checker reports 474 working internal links; metadata audit has complete blog field coverage. Browser checks confirmed homepage styling and Romans search results. Shell syntax, workflow lint, and report overwrite protection pass. Production output fell from 143,778,326 to 133,656,441 bytes (about 10.1 MB), primarily by removing repeated inline scripts/markup.

## Routine checks

- New posts: use stable URLs, useful descriptions, canonical categories, and relevant kebab-case tags.
- After source changes: `npm run verify`, followed by local visual review for template/style changes.
- After metadata changes: `python3 scripts/audit-frontmatter.py`.
- Periodically: review external links and media using dated report outputs; blocked network checks do not establish dead links.
- Before publication: review staged changes and verify the production build. See [maintenance guide](MAINTENANCE.md).
