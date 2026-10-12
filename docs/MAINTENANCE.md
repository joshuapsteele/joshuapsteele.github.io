# Maintenance guide

## Verification and deployment

Use Hugo Extended at the version in `.hugo-version`. CI reads the same file through `scripts/install-hugo-ci.sh`. Node 22 runs verification in CI; no npm dependencies are needed for the build or tests. Sequoia has its own package dependency for ATProto publishing.

Run `npm run dev` for visual review, then `npm run verify` for regression tests and a clean production build. The production build validates affiliate disclosures, rendered internal links/assets, social metadata, and JSON/XML. Development includes drafts/future posts, so it cannot establish which links work in production. Fragment targets and external URLs are separate checks.

PR validation is read-only and does not fetch analytics, deploy, or send Webmentions. Production builds still refresh analytics; scheduled builds reuse the exact syndication revision produced by their gate. A deployment checks its revision against main after entering the deployment concurrency group. Webmentions run after deployment using the deployed artifact. No notifications are sent by local verification.

Prefer reviewed commits/PRs. `npm run deploy -- "Message"` accepts only intentionally staged changes on main, rejects unstaged/untracked files, runs verification, and stops on errors. It no longer stages the whole working tree. Always review `git diff --cached` first.

## Content and taxonomy

Published blog posts should have a title, date, description, explicit stable URL, category, and useful tags. Preserve old public URLs with aliases when changing slugs.

Canonical categories: theology, ethics, personal, productivity, dissertation, ministry, poem, politics, and diy. The existing diy category is retained for hands-on projects/gift content rather than changing a published taxonomy URL.

Use lowercase kebab-case tags, reusing vocabulary first. Usually 3–5 tags are enough; fewer is fine when only one or two fit. Do not merge meaningful low-frequency tags solely to lower the count. Use YAML block lists for new posts, matching surrounding indentation. The completed May tagging handoff is archived; track new work in the cleanup checklist.

Run `python3 scripts/audit-frontmatter.py` after metadata edits. It checks presence/coverage, not comprehensive YAML validity. Hugo provides the actual content parsing check.

## Theme and assets

PaperMod is vendored as tracked files, not a submodule. Keep custom templates in `layouts/` and CSS in `assets/css/extended/`; do not edit the theme for site customizations. A future vendor refresh should identify the desired upstream revision, review the vendor diff and matching overrides, then run verification and visual checks. No upstream revision is inferred from the current directory.

PaperMod bundles all extended CSS. Do not load those files again in `extend_head.html`. Shared conversation/reply scripts live in `assets/js/` and are fingerprinted by Hugo. Keep social metadata in the dedicated metadata partials.

Image quality is configured per format, following [Hugo's imaging configuration](https://gohugo.io/configuration/imaging/). Images copied from `static/` are not processed by those settings. Keep existing public media URLs unless a reviewed migration preserves them.

## Reports and housekeeping

Dated reports are immutable. Link the newest audit from `docs/README.md`, CLAUDE.md, and the cleanup checklist. Archive superseded reports unchanged; Git is the history of record. Generated audit JSON and suggestions in `scripts/data/` are not canonical taxonomy configuration. Do not delete them without checking script consumers.

External/Amazon/media auditors accept explicit report paths and default to dated report filenames. They refuse to overwrite an existing Markdown report; choose a new output name for a repeat run. External checks can be slow and bot-blocked, so they are not CI gates.

The legacy bulk image-deletion script has been retired. Use the read-only media auditor, then review candidates individually. Source references cannot prove the absence of external inbound links.

Editor configuration is intentionally retained in this pass: shared Obsidian settings/plugin availability may be part of the writing workflow. Revisit vendored plugins/workspace state separately if their churn becomes a problem. Keep `.hugo_build.lock` ignored and untracked.
