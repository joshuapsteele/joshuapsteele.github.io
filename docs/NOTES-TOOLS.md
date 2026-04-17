---
title: "Notes Tools"
date: 2026-04-17
---

# Notes Tools

This repo has two scripts for maintaining the Hugo `/notes/` section:

- `scripts/migrate-microblog-archive.py` imports an exported Micro.blog Markdown archive into `content/notes/`.
- `scripts/manage-notes.py` lists or removes notes by date/time, tag, draft status, or syndication flag.

## Important Defaults

The active syndication feed is:

```text
https://joshuapsteele.com/notes/feed.json
```

Notes with this frontmatter are omitted from that feed but still render on the site:

```yaml
syndicate: false
```

The Micro.blog archive import writes `syndicate: false` by default so historical imports do not get treated as fresh cross-post material.

`manage-notes.py delete` is also conservative by default. It previews matches unless you pass `--yes`, and `--yes` moves files to `attic/deleted-notes/` instead of permanently deleting them.

## Bulk Import Micro.blog Archive

Use this only after exporting the archive from Micro.blog:

1. Micro.blog → Account → Export → Markdown archive.
2. Unzip the archive somewhere local, for example `~/Downloads/microblog-archive/`.
3. Run a dry run first.

Install dependencies:

```bash
cd ~/git/joshuapsteele.github.io
pip install --break-system-packages pyyaml requests
```

Preview the import:

```bash
python3 scripts/migrate-microblog-archive.py \
  --archive ~/Downloads/microblog-archive/ \
  --hugo-repo ~/git/joshuapsteele.github.io \
  --dry-run
```

Run the import:

```bash
python3 scripts/migrate-microblog-archive.py \
  --archive ~/Downloads/microblog-archive/ \
  --hugo-repo ~/git/joshuapsteele.github.io \
  --download-images
```

What the import does:

- Creates notes in `content/notes/YYYY-MM-DD-HHMM.md`.
- Preserves original post dates.
- Adds `syndicate: false` by default.
- Preserves the original Micro.blog URL as an alias when the archive includes it.
- Rewrites your Micro.blog-hosted image URLs to `/notes/images/...`.
- With `--download-images`, saves those images into `static/notes/images/`.

Only use this option if you intentionally want imported posts in `/notes/feed.json`:

```bash
--syndicate
```

Usually, do **not** use `--syndicate` for archive imports.

After importing:

```bash
hugo server
```

Review `/notes/`, spot-check imported posts, especially posts with images, then:

```bash
git status
git add content/notes static/notes
git commit -m "Import Micro.blog archive into /notes/"
git push
```

If something looks wrong before committing, delete the new imported files or use Git to discard only the import changes.

## Manage Notes

List all notes:

```bash
python3 scripts/manage-notes.py list
```

List notes before a date:

```bash
python3 scripts/manage-notes.py list --before 2026-05-01
```

List a time window:

```bash
python3 scripts/manage-notes.py list \
  --from 2026-04-17T10:00:00-04:00 \
  --to 2026-04-17T11:00:00-04:00
```

List notes by tag:

```bash
python3 scripts/manage-notes.py list --tag indieweb
```

List non-syndicating notes:

```bash
python3 scripts/manage-notes.py list --syndicate false
```

List as JSON:

```bash
python3 scripts/manage-notes.py list --tag test --json
```

## Remove Notes

Preview a removal. This does not change files:

```bash
python3 scripts/manage-notes.py delete --tag test --before 2026-05-01
```

Actually remove matching notes from Hugo by moving them to `attic/deleted-notes/`:

```bash
python3 scripts/manage-notes.py delete --tag test --before 2026-05-01 --yes
```

Move a specific time range:

```bash
python3 scripts/manage-notes.py delete \
  --from 2026-04-17T10:00:00-04:00 \
  --to 2026-04-17T11:00:00-04:00 \
  --yes
```

Permanently delete matching files:

```bash
python3 scripts/manage-notes.py delete --tag test --before 2026-05-01 --permanent --yes
```

Permanent deletion removes files from the worktree, but Git history will still contain them unless you later rewrite history. Use the default move-to-attic behavior for normal cleanup.

After any real removal:

```bash
hugo server
git status
git add content/notes attic/deleted-notes
git commit -m "Prune notes"
git push
```

For permanent deletes:

```bash
git add -A content/notes
git commit -m "Prune notes"
git push
```

## What Deletion Does Not Do

Deleting a note from Hugo removes the canonical page and future feed item from `joshuapsteele.com`.

It does **not** guarantee deletion of downstream copies already syndicated to Micro.blog, Mastodon, or Threads. For sensitive removals, delete from Hugo first, then manually verify and remove downstream copies.

## Help

Both scripts have command-line help:

```bash
python3 scripts/migrate-microblog-archive.py --help
python3 scripts/manage-notes.py --help
python3 scripts/manage-notes.py list --help
python3 scripts/manage-notes.py delete --help
```
