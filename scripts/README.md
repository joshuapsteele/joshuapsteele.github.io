# Welcome to Joshua P. Steele's Source Code

This repository contains the source code for my personal website, [joshuapsteele.com](https://joshuapsteele.com). It is built using [Hugo](https://gohugo.io/), a popular static site generator.

## Taxonomy Cleanup Guide

Prereqs

- In repo root, on a fresh branch.
- Ensure Python 3 is available.
- Your preferences are preserved: the tools won’t touch url, aliases, guid, or id.

1) Inventory Current Terms

- Command: scripts/taxonomy_tools.py inventory
- Purpose: Get a count of all unique tags and categories to see what needs consolidation.

2) Generate a Mapping Skeleton

- Command: scripts/taxonomy_tools.py export-map taxonomy_map.generated.yaml
- Purpose: Write all current terms to a YAML you can edit.
- Tip: Copy it to a working file you’ll maintain: cp taxonomy_map.generated.yaml taxonomy_map.yaml

3) Curate Your Mapping

- Edit taxonomy_map.yaml:
    - Under tags: and categories:, set each existing term (left) to a canonical term (right).
    - Map to an empty string to drop a term.
    - Terms are normalized to lowercase and deduped automatically.
- Examples:
    - tags:
    - `'Bonhoeffer': 'bonhoeffer'`
    - `'Reading Notes': 'reading notes'`
    - `'to-remove': ''`
- categories:
    - `'Church and Theology': 'church and theology'`
    - `'Uncategorized': 'misc'`

4) Dry‑Run the Changes

- Command: scripts/taxonomy_tools.py apply-map taxonomy_map.yaml
- Purpose: See exactly which files would change without writing.

5) Apply the Changes

- Command: scripts/taxonomy_tools.py apply-map taxonomy_map.yaml --write
- Effect: Updates all posts’ front matter with your canonical terms, removing duplicates and empty lists.

6) Validate Locally

- Build: npm run build:fast
- Spot‑check:
    - Taxonomy pages render correctly.
    - Posts show expected tags/categories in lowercase.
    - Old content and URLs unaffected (we didn’t change url or aliases).

7) Optional: Preserve Old Taxonomy URLs

- If you want old taxonomy slugs to redirect (e.g., /tags/Old-Tag/ → /tags/new-tag/), we can generate stub _index.md files with aliases for those old terms. Say the word and I’ll add a helper to emit those.

8) Re‑Inventory to Confirm

- Command: scripts/taxonomy_tools.py inventory
- Purpose: Verify that only your canonical terms remain.

9) Commit + PR

- Commit with a concise summary (e.g., “Consolidate tags/categories per taxonomy_map.yaml”).
- If you changed high‑visibility terms, include a brief note in the PR.

Notes

- Lists are written in block form for consistency.
- Lowercasing is automatic after mapping.
- Dropping a term: map it to '' (empty string).
- The process is reversible via Git if you want to tweak mappings and reapply.