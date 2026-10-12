# Tagging Progress — Untagged Blog Posts

_Started: 2026-05-21_

> **Living tracker — keep it current.** This file is resumable state for the tagging effort. Update the "Progress" section in the same commit as each batch of tag changes, so any agent (Claude Code or Codex) can pick up where the last one stopped. See the "Audit & Cleanup Project" section of `CLAUDE.md`/`AGENTS.md` for the full logging protocol.

Handoff file for the effort to add tags to untagged blog posts. Either Claude Code or Codex can resume from here.

---

## Goal

Add tags to blog posts that have no tags. The May 2026 audit found a sizeable untagged backlog; use `python3 scripts/audit-frontmatter.py` for live counts instead of copying them here.

## Rules (decided — do not re-litigate)

- **Reuse the existing tag vocabulary first.** Do not invent new tags unless an existing one genuinely doesn't fit; if you add a new tag, record it in the "New tags added" list below.
- **kebab-case** for all tags (e.g., `book-of-common-prayer`, not `Book of Common Prayer`).
- **3–5 tags per post.** Tags are for grouping across posts, not for describing a single post. Fewer is fine when only one or two fit.
- **YAML block-list format**, inserted in the frontmatter before the `url:` line:
  ```yaml
  tags:
    - tag-one
    - tag-two
  url: /the-slug/
  ```
  (Match the file's existing list indentation — some files use no indent under `categories:`; mirror that.)
- Some untagged posts have an empty `tags:` or `tags: null` line — replace it in place rather than adding a second `tags:` key.
- After each batch: run `npm run build` and confirm it succeeds with no `ERROR` lines. New tags create new taxonomy pages, so the page count can rise slightly.

## New tags added (intentionally created — keep using these, don't duplicate)

- `podcasts` — for podcast recommendation posts
- `personality` — for personality-framework posts (Four Tendencies, etc.)
- `lent` — for Lenten posts (wilderness-temptations series, etc.)
- `creation` — for creation-theology posts (Creation and Doxology series, etc.)
- `trinity` — for Trinity / trinitarian posts (Holy Trinity, Rublev icon, etc.)
- `cedarville` — for posts about Cedarville University (the Pahl firing, "Let There Be Light," etc.)
- `travel` — for trip/travel posts (Grand Canyon, Peru, etc.)
- `gtd` — for Getting Things Done / productivity-system posts
- `pacifism` — for posts on Christian pacifism / peace vs. violence
- `jordan-peterson` — for posts about Jordan Peterson

Note: the theology batch used `political-theology` (kebab) as the target form; the existing `political theology` (2 uses) should fold into it during the casing cleanup.

## Completed taxonomy cleanups

These casing/format duplicates were consolidated via `scripts/data/taxonomy_map.yaml` + `python3 scripts/apply-taxonomy.py`:

- `Bonhoeffer` → `bonhoeffer`
- `Romans 13` and `romans 13` → `romans-13`
- `matthew 25` → `matthew-25`
- `political theology` → `political-theology`
- `prophetic witness` → `prophetic-witness`
- `public health` → `public-health`
- `Christianity`, `ICE` → lowercase

---

## Progress

**COMPLETE (2026-05-21):** the untagged backlog was cleared. Use `python3 scripts/audit-frontmatter.py` for current coverage.

- [x] ministry — pilot
- [x] dissertation — pilot
- [x] productivity
- [x] theology; "Political Thoughts" was deleted by the user rather than tagged
- [x] personal; "Heads up! Guest post on the way" was deleted by the user rather than tagged
- [x] ethics
- [x] uncategorized AMA — "Ask Me Anything This November"; assigned category `personal` + tags `questions`, `writing`

**Remaining:** none known; rerun the front matter audit before resuming this effort.

## How to resume

1. Read this file and the current tag vocabulary:
   ```bash
   # List untagged posts grouped by category
   python3 - <<'PY'
   import os, re, glob
   from collections import defaultdict
   SITE = "."
   def fm(c):
       e=c.find('\n---',3); return c[3:e] if c.startswith('---') and e!=-1 else None
   def plf(f,k):
       if not f: return []
       m=re.search(rf'^{k}:\s*\[([^\]]*)\]',f,re.M)
       if m: return [x.strip().strip('\"\'') for x in m.group(1).split(',') if x.strip()]
       m2=re.search(rf'^{k}:\s*\n((?:[ \t]*-[^\n]*\n?)+)',f,re.M)
       if m2: return [t.strip().strip('\"\'') for t in re.findall(r'-\s+(.+)',m2.group(1)) if t.strip()]
       m3=re.search(rf'^{k}:\s*([^\n\[{{]+)',f,re.M)
       if m3:
           v=m3.group(1).strip().strip('\"\'')
           return [v] if v and v.lower() not in ('null','~','') else []
       return []
   by=defaultdict(list)
   for p in glob.glob('content/blog/*.md'):
       f=fm(open(p,errors='replace').read())
       if not plf(f,'tags'):
           cats=plf(f,'categories'); by[cats[0] if cats else 'UNCATEGORIZED'].append(os.path.basename(p))
   for c in sorted(by,key=lambda x:-len(by[c])): print(c,len(by[c]))
   PY
   ```
2. Pick the next remaining category. Read each post's title, description, and opening paragraphs.
3. Propose tags from the existing vocabulary; apply in the YAML format above.
4. `npm run build` to verify.
5. Update the "Progress" section here and commit.
