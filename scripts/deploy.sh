#!/usr/bin/env bash
# Publish only explicitly staged, verified changes from main.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
if [[ "$(git branch --show-current)" != main ]]; then
  echo 'Deploy must run on main. Use a reviewed pull request for other branches.' >&2
  exit 1
fi
if ! git diff --quiet; then
  echo 'Unstaged tracked changes found. Stage the intended changes before deploying.' >&2
  exit 1
fi
if [[ -n "$(git ls-files --others --exclude-standard)" ]]; then
  echo 'Untracked files found. Stage intended files or ignore local files before deploying.' >&2
  exit 1
fi
if git diff --cached --quiet; then
  echo 'No staged changes to deploy.' >&2
  exit 1
fi
npm run verify
git diff --cached --check
# Verification must not change tracked source files.
git diff --exit-code
msg="${*:-Update site content}"
git commit -m "$msg"
git push origin HEAD:main
echo 'Push succeeded. GitHub Actions will validate and deploy the commit.'
