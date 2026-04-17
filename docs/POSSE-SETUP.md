---
title: "POSSE Pivot — Setup Runbook"
date: 2026-04-17
---

# POSSE Pivot: Hugo as canonical, Micro.Blog as syndicator

This runbook walks through the one-time migration from *Micro.Blog is the shortform home, Hugo embeds it* (PESOS) to *Hugo is the shortform home, Micro.Blog subscribes to a feed* (POSSE).

Total time if you don't hit surprises: 60–90 minutes, most of it waiting for Hugo builds and the first Micro.Blog poll cycle.

## What lives where after this change

joshuapsteele.com is the canonical home for everything you write: long posts at `/blog/`, short posts at `/notes/` (new), and saved links at `links.joshuapsteele.com` via LinkLog. The new `/notes/` section publishes a full-content JSON Feed at `/notes/feed.json` that Micro.Blog polls every few minutes.

Micro.Blog stops being an authoring surface. It becomes a syndicator: it reads `/notes/feed.json`, cross-posts each new note to Mastodon (@joshuapsteele@mastodon.social) and Threads (@joshuapsteele), and supplies reply collection via its own feed + webmention.io (already wired up on your site).

The `Post to Micro.blog` Drafts action stays installed as a manual fast path. Use it only when you want a near-instant Mastodon/Threads post and are OK with it living only on Micro.Blog, not on joshuapsteele.com.

## Prerequisites

You already have: the Hugo repo at `~/git/joshuapsteele.github.io`, the new `drafts-actions/` files in that repo, and webmention.io set up for joshuapsteele.com.

You still need to do manually: install the Drafts actions from `drafts-actions/README.md`, then enter the Drafts Credentials when each action prompts for them on first run.

You'll also need: Python 3.8+ on your Mac Mini (comes preinstalled), `pip install --break-system-packages pyyaml requests` for the migration script, and your Micro.Blog account access.

## Step 1 — Verify and publish the new Hugo section

The notes section files should already exist in this repo:

- `archetypes/notes.md`
- `content/notes/_index.md`
- `layouts/notes/list.html`
- `layouts/notes/list.jsonfeed.json`
- `layouts/notes/single.html`
- `hugo.yaml` edits for the Notes menu/profile links and `JSONFeed` section output

Run `hugo server` locally and visit http://localhost:1313/notes/. You should see a mostly-empty stream (one `_index.md` greeting, nothing else yet). `http://localhost:1313/notes/feed.json` should render valid JSON Feed with no items.

Commit and push the structure before running any Drafts action that writes notes. The Drafts actions push directly to GitHub `main`, so the live site needs to know how to render `/notes/` first.

```bash
git add archetypes/notes.md content/notes layouts/notes hugo.yaml drafts-actions docs/POSSE-SETUP.md scripts/migrate-microblog-archive.py
git commit -m "Add /notes/ section for shortform POSSE"
git push
```

Wait for the GitHub Action to finish before moving on. `https://joshuapsteele.com/notes/feed.json` should now resolve to an empty JSON Feed.

## Step 2 — Install the Drafts action group

Follow `drafts-actions/README.md` to create the actions manually in Drafts.

Install the destination actions first, then the router last:

1. `Publish: Blog` from `drafts-actions/02-publish-blog.js`
2. `Publish: Link` from `drafts-actions/03-publish-link.js`
3. `Publish: Newsletter` from `drafts-actions/04-publish-newsletter.js`
4. `Publish: Note` from `drafts-actions/05-publish-note.js`
5. `Publish` from `drafts-actions/01-publish-router.js`

That order lets the router find the destination actions when you test it.

## Step 3 — Add a test note and verify the feed

Open Drafts, type something short like "Testing the new POSSE pipeline.", run `Publish: Note`. The action writes `content/notes/2026-04-17-1920.md` (or whatever the timestamp is), commits to main, and your GitHub Action rebuilds.

Within a minute or two, `https://joshuapsteele.com/notes/` should show the note and `/notes/feed.json` should include it. If the note is missing from the feed, check that `hugo.yaml`'s `outputs.section` still includes `JSONFeed` and that `layouts/notes/list.jsonfeed.json` made it into the repo.

## Step 4 — Export your Micro.Blog archive

In Micro.Blog: Account → Export → "Markdown archive". You'll get a `.zip` with one `.md` per post.

Unzip it somewhere you'll remember, e.g. `~/Downloads/microblog-archive/`.

## Step 5 — Run the migration script in dry-run first

```bash
cd ~/git/joshuapsteele.github.io
pip install --break-system-packages pyyaml requests
python3 scripts/migrate-microblog-archive.py \
    --archive ~/Downloads/microblog-archive/ \
    --hugo-repo ~/git/joshuapsteele.github.io \
    --dry-run
```

You should see one `DRY` line per Micro.Blog post, mapped to a `content/notes/YYYY-MM-DD-HHMM.md` filename. Spot-check the conversion by running the same command on one file and reading the output (re-run without `--dry-run` but against a scratch directory if you want to be careful).

## Step 6 — Run the migration for real

```bash
python3 scripts/migrate-microblog-archive.py \
    --archive ~/Downloads/microblog-archive/ \
    --hugo-repo ~/git/joshuapsteele.github.io \
    --download-images
```

`--download-images` fetches every Micro.Blog-hosted image into `static/notes/images/` and rewrites the URLs. Depending on how many posts have images, this could take a few minutes.

When it finishes, `git status` in the Hugo repo will show a lot of new files. Build locally (`hugo server`), browse `/notes/`, spot-check ten or twenty imported posts at random, pay attention to any with images or code blocks.

Commit and push when satisfied:

```bash
git add content/notes static/notes
git commit -m "Import Micro.Blog archive into /notes/"
git push
```

The GitHub Action rebuild will take longer than usual because it's generating a page per note. Wait for it to finish; the `/notes/feed.json` will now include all of your imported history (capped to the most recent N, configurable via `services.rss.limit` in `hugo.yaml`).

## Step 7 — Subscribe Micro.Blog to the new feed

In Micro.Blog: Account → Edit Feeds (or "Feeds" in some versions of the UI). Add a new feed:

    URL: https://joshuapsteele.com/notes/feed.json

Micro.Blog will do an initial poll right away and then re-poll every 5–20 minutes. Your imported archive will appear in the Micro.Blog timeline.

Critically: at this point Micro.Blog is reading posts it *already knows about* (because they originated there) and will happily duplicate them in the timeline if you don't disable the old side.

Do one of the following, depending on how you answered the "old posts" question:

**If you want Micro.Blog to keep syndicating, but only new Hugo-authored posts**: go to Account → Feeds and either delete the internal Micro.Blog blog feed (if present), or turn off "Also post to Mastodon/Threads" for that blog. The external feed you just added will be the one Micro.Blog cross-posts from.

**If you want to decommission social.joshuapsteele.com entirely**: go to the blog at social.joshuapsteele.com → Settings → Delete blog. Wait to do this until the external feed has successfully posted something to Mastodon at least once, so you know the syndication works.

## Step 8 — Re-point the router

If you installed the Drafts actions in Step 2, your `Publish` router is already using the updated `01-publish-router.js`: the `note` / `micro` signals dispatch to `Publish: Note` (writes to Hugo) instead of `Post to Micro.blog` (Micropub direct).

If you previously had an older `Publish` action installed, open Drafts, open the `Publish` action, and paste the updated `01-publish-router.js` into its Script step. Save.

Now `Publish` on a short draft writes to Hugo by default. The built-in `Post to Micro.blog` action is still there and still works — use it directly (from the action bar) for the manual fast path.

## Step 9 — Update the homepage Micro.Blog widget

`layouts/partials/microblog_posts.html` is currently a client-side widget that fetches `https://social.joshuapsteele.com/feed.json`. After the migration, this is showing the downstream version of content you already authored locally.

Two cleanup options:

- **Delete the widget call.** Find where it's included (likely `home_info.html` or a profileMode partial) and remove the line. Simplest.
- **Replace it with a server-rendered recent-notes widget.** Inside `layouts/partials/microblog_posts.html`, replace the whole file with something like:

```html
{{- /* Recent notes from the local Hugo /notes/ section */ -}}
<div class="microblog-section">
  <h2>Recent Notes</h2>
  <div class="microblog-list">
    {{- range first 5 (where site.RegularPages "Section" "notes") }}
    <article class="microblog-post h-entry">
      {{- if .Title }}
      <h3 class="microblog-title p-name"><a href="{{ .Permalink }}" class="u-url">{{ .Title }}</a></h3>
      {{- end }}
      <div class="microblog-content e-content">{{ .Summary }}</div>
      <div class="microblog-meta">
        <a href="{{ .Permalink }}" class="u-url">
          <time class="dt-published" datetime="{{ .Date.Format "2006-01-02T15:04:05Z07:00" }}">
            {{ .Date.Format "Jan 2, 2006" }}
          </time>
        </a>
      </div>
    </article>
    {{- end }}
  </div>
</div>
```

No JavaScript, no external fetch, no race with page load. Rename the partial to `recent_notes.html` if you want the filename to match the new meaning; just update the one `partial` call that includes it.

## Step 10 — Webmentions for shortform

webmention.io is already wired up via `layouts/partials/webmentions.html`, and `layouts/notes/single.html` calls `partial "webmention_display.html" .`, so reply collection works out of the box once the notes are live.

For Mastodon replies to reach your notes, set up **Brid.gy Fed**:

1. Go to https://fed.brid.gy and sign in with the Mastodon account (@joshuapsteele@mastodon.social).
2. Authorize it. Brid.gy will now relay Mastodon replies to joshuapsteele.com → webmention.io.
3. Verify by replying to your test note from Step 3 from your Mastodon account. Within 5 minutes the reply should show up in the webmention display on the note page.

For IndieWeb-style replies via Micro.Blog (someone using Micro.Blog's reply UI), the existing `webmention_display.html` already handles that — Micro.Blog sends webmentions for replies.

## Step 11 — Delete or park the old actions

Once you're confident the new workflow is stable (give it a week of regular use), clean up Drafts:

- `Quick Post to Hugo` — delete (superseded by `Publish: Blog`)
- `Full Post to Hugo` — delete (superseded by `Publish: Blog`)
- `Send to Buttondown` — delete (superseded by `Publish: Newsletter`, **and rotate the leaked API token in that script if you haven't already**)
- `LinkLog` — delete (superseded by `Publish: Link`)
- `Post to Micro.blog` — **keep** as manual fast path
- `Post/Update to Micro.blog` — delete (you said you don't use it)

## Rollback

If something goes wrong and you want to revert:

- The Hugo changes: `git revert` the commits that added `content/notes/`, `layouts/notes/`, the archetype, and the `hugo.yaml` edits.
- The router change: paste the pre-change version of `01-publish-router.js` back into the `Publish` Drafts action.
- The Micro.Blog feed subscription: Account → Feeds → remove the joshuapsteele.com feed.

No data is lost. Your Micro.Blog archive remains whole even after Step 4 (you exported a copy, not moved the originals).

## What's left on the table (future work)

A few IndieWeb-ish niceties that are cheap to add later but not critical:

- **Reply-context**: add frontmatter like `reply_to: "https://example.com/post"` on notes that are replies, and render a quoted preview via `layouts/partials/reply_context.html` (already present in the repo — designed for this).
- **Location/geo** on notes via frontmatter.
- **Note types** — Micro.Blog has `photo` / `reply` / `bookmark` / `like` as semantic categories. If you want parity, add a `post_type` frontmatter field and render it on the note page.
- **Cross-post status indicator**: fetch Micro.Blog's own feed periodically in CI and annotate each note with its downstream Mastodon URL.
