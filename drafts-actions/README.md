---
title: "Publish Action Group — Setup"
date: 2026-04-17
---

# Publish Action Group

Six Drafts actions that replace your current Hugo / LinkLog / Buttondown scripts, add a new shortform `Publish: Note` action for the POSSE pivot, and wrap everything behind a single unified `Publish` router. Micro.Blog stops being an authoring surface; shortform notes are authored at joshuapsteele.com first (via `Publish: Note`) and Micro.Blog syndicates them outward by subscribing to `/notes/feed.json`.

## Files in this folder

| File | Becomes this Drafts action | Purpose |
|---|---|---|
| `00-shared-helpers.js` | (not an action) | Reference copy of the helpers inlined in 02–05. Update here when you change something, then propagate. |
| `01-publish-router.js` | `Publish` | The unified router. Inspects the draft and dispatches. |
| `02-publish-blog.js` | `Publish: Blog` | Hugo long-form post → `content/blog/` on joshuapsteele.com via GitHub API. |
| `03-publish-link.js` | `Publish: Link` | Link post → links.joshuapsteele.com. |
| `04-publish-newsletter.js` | `Publish: Newsletter` | Buttondown issue, always created as a draft. |
| `05-publish-note.js` | `Publish: Note` | Hugo shortform → `content/notes/` on joshuapsteele.com. Micro.Blog polls the feed and crossposts to Mastodon + Threads. |

Not created here, retained as a manual fast path:
- `Post to Micro.blog` (Drafts built-in). After the POSSE pivot this action bypasses Hugo and posts directly to Micro.Blog, so its content only lives at social.joshuapsteele.com. Use it sparingly, only when you need something on Mastodon/Threads in the next minute and are OK with it not being on joshuapsteele.com.

## Credentials (auto-created on first run)

Drafts creates Credential entries automatically the first time an action requests one. You do NOT create them manually in Settings → Credentials. The first time you run each action below, Drafts will show an authorization dialog asking for the token; after you enter it, Drafts saves it as a named Credential and never prompts again.

What each action asks for:

- `Publish: Blog` — Credential named **GitHub Blog Token**, field `token`. Paste a GitHub Personal Access Token with `repo` scope, scoped to `joshuapsteele/joshuapsteele.github.io`. Fine-grained PATs work; classic PATs work too. Create at https://github.com/settings/personal-access-tokens.
- `Publish: Link` — Credential named **LinkLog**, field `token`. Paste the same value as your server's `LINKLOG_API_TOKEN` env var on the DigitalOcean VPS.
- `Publish: Newsletter` — Credential named **Buttondown**, field `token`. Paste your Buttondown API key from the Buttondown dashboard → Settings → Programming.
- `Publish: Note` — reuses the **GitHub Blog Token** Credential. No new credential to set up if `Publish: Blog` is already working.

Your existing Drafts Credential for `Micro.blog` (field `apptoken`) is already set up and used by the built-in `Post to Micro.blog` action; nothing changes there.

If you later want to rotate a token: Settings → Credentials → tap the Credential → "Forget". The next run of the action will prompt again.

## Install the actions

Before installing these, make sure the Hugo `/notes/` section has been committed, pushed, and deployed. `Publish: Note` writes straight to GitHub `main`, so the live site should already know how to render notes before Drafts starts creating them.

Create the destination actions first, then create the router last:

1. `Publish: Blog` from `02-publish-blog.js`
2. `Publish: Link` from `03-publish-link.js`
3. `Publish: Newsletter` from `04-publish-newsletter.js`
4. `Publish: Note` from `05-publish-note.js`
5. `Publish` from `01-publish-router.js`

For each action:

1. In Drafts, open the action list (⚡), tap `+`, choose "Action".
2. Name it exactly as listed in the table above. (The router dispatches by name.)
3. Add a single "Script" step.
4. Paste the full contents of the `.js` file into the script editor.
5. Save.

Recommended settings per action:

- `Publish`: show in action bar, optionally assign a keyboard shortcut (I use ⌃⌘P).
- `Publish: Blog`, `Publish: Link`, `Publish: Note`, `Publish: Newsletter`: include in action bar for the rare case you want to force a destination without touching frontmatter or tags.

## Routing signals

The router picks a destination using three signals, in this order of priority:

1. **Frontmatter**: `destination: post | link | note | micro | newsletter` as a line in a leading YAML block. (`micro` is kept as an alias for `note` so you don't have to retag existing drafts — both land at `/notes/`.)
2. **Drafts tag**: apply `post`, `link`, `note`, `micro`, or `newsletter` to the draft.
3. **Shape heuristic**:
   - First line matches `^https?://` → `link`
   - First line is a markdown `# Heading` and body is longer than ~400 chars → `post`
   - Shorter than ~300 chars, no H1 → `note`
   - Anything else prompts.

Signals 1 and 2 dispatch silently. Signal 3 always shows a confirmation prompt with the guess pre-selected.

Before the POSSE pivot, `micro` routed to the Drafts built-in `Post to Micro.blog` action. After the pivot, it routes to `Publish: Note` which writes to the Hugo repo — Micro.Blog then picks the note up from `/notes/feed.json` on its next poll and fans out to Mastodon/Threads. If you specifically want to bypass Hugo for something time-sensitive, invoke `Post to Micro.blog` directly from the action list.

## Suggested tags

Add these to your tag list (they are referenced by the router and by other Drafts workflow conventions). Drafts creates tags implicitly the first time you apply them, so this is just a list to be aware of.

| Tag | Meaning |
|---|---|
| `post` | Route to joshuapsteele.com `/blog/` (long-form). |
| `link` | Route to LinkLog. |
| `note` | Route to joshuapsteele.com `/notes/` (shortform; Micro.Blog syndicates). |
| `micro` | Alias for `note`. Kept so old drafts still route correctly. |
| `newsletter` | Route to Buttondown (also what your Obsidian Micro.Blog plugin syncs). |
| `published` | Applied automatically on successful publish. Safe to filter by. |
| `drafting` | Apply by hand for multi-session work. |

Your existing `8020tools`, `revdev`, `work`, `wordpress`, and the auto-managed `domain:*` / `post:*` tags are untouched.

## Suggested workspaces

You currently have no workspaces configured. These four cover most of the workflow:

| Workspace | Tag filter | Purpose |
|---|---|---|
| Inbox | *(none)* or negate `published`, `drafting`, `archived` | Quick capture. |
| Drafting | has `drafting` | Multi-session pieces in progress. |
| Ready to Publish | has `post`, `link`, `note`, or `newsletter`, NOT `published` | Triage queue — the things the router would actually dispatch. |
| Published | has `published` | Archive of shipped content. Read-only in practice. |

Create them via Drafts → Workspaces → New.

## Templates (optional, via the Templates action step)

Three starter templates save you from typing boilerplate. Drafts doesn't have first-class templates built in, but the "New Draft with Template" action step does the job.

**Link post template**

```
<cursor>

<!-- Commentary here. Use inline #tags. -->
```

**Blog post template** (matches the minimal frontmatter your recent posts use)

```
---
destination: post
title: "<cursor>"
tags: []
categories: []
---


```

**Note template** (shortform, typically untitled)

```
<cursor>
```

That's it. No frontmatter required; the `Publish: Note` action supplies everything from the current date. Add `#hashtags` inline if you want taxonomy.

**Newsletter template**

```
---
destination: newsletter
subject: "<cursor>"
---


```

Save each as a Drafts action: "New Draft with Template" step, paste the template text into the "Template" field. Name them "Template: Link", "Template: Blog", "Template: Note", "Template: Newsletter".

## The old actions

You can delete or just stop using these once the new ones are working:

- `Quick Post to Hugo` — superseded by `Publish: Blog`.
- `Full Post to Hugo` — superseded by `Publish: Blog`.
- `LinkLog` — superseded by `Publish: Link`. New format is: URL on line 1, blank line, then commentary with inline `#tags`. The old format (tags on line 2) still works for continuity.
- `Send to Buttondown` — superseded by `Publish: Newsletter`. **Rotate the Buttondown API token that was hardcoded in the old script before deleting it.**
- `Post/Update to Micro.blog` — delete (unused).

`Post to Micro.blog` stays installed as a manual fast path. The router no longer calls it; invoke it directly from the action list when you need instant Mastodon/Threads without going through Hugo.

## First-run checklist

1. Hugo `/notes/` section committed, pushed, deployed, and visible at `https://joshuapsteele.com/notes/feed.json`.
2. Actions 01–05 installed with exact names as above. Credentials are auto-created on first run of each action.
3. Test each action end to end with a throwaway draft:
   - Blog: write a 3-sentence post with a title, run `Publish: Blog`, choose the draft option when prompted, confirm it commits to the repo and the GitHub Action runs.
   - Link: paste a URL on line 1, blank line, a sentence of commentary with `#test` somewhere, run `Publish: Link`, confirm it appears at links.joshuapsteele.com.
   - Note: type a short sentence, run `Publish: Note`, confirm `content/notes/{timestamp}.md` appears in the repo and the page renders at `/notes/{timestamp}/` after the rebuild.
   - Newsletter: write a subject line and a body, run `Publish: Newsletter`, confirm it shows as a draft in Buttondown (NOT sent).
4. Run the router against a tagged draft to verify dispatch (try `note`, `post`, `link`, `newsletter`).
5. Check that the draft is tagged `published` and archived after each success.
6. Subscribe Micro.Blog to `/notes/feed.json` (see POSSE-SETUP step 7). Verify that a newly published note shows up on your Mastodon timeline within 20 minutes.

## Known limitations

- The helpers are duplicated across action files because Drafts' script environment doesn't support real imports. The canonical copy is in `00-shared-helpers.js`; if you edit one, propagate.
- The Hugo action pushes directly to `main` (per your preference). If you ever want a PR-based flow, swap the branch in the PUT request and add a follow-up `POST /repos/.../pulls` call.
- Buttondown's API base path (`/v1/emails`) is stable as of 2026-04. If they change the shape, the error handler will show the status + body so you can update the field names without guessing.
- The router's "confident" path for tag-based dispatch does not prompt. If you habitually tag drafts speculatively, you may want to change the router to always prompt — flip `confident = true` to `confident = false` on the tag branch.
