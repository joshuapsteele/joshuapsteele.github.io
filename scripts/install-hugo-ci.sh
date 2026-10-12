#!/usr/bin/env bash
# Linux GitHub-hosted runners; same pinned version as local setup.
set -euo pipefail
version="$(cat .hugo-version)"
curl --fail --location --retry 3 "https://github.com/gohugoio/hugo/releases/download/v${version}/hugo_extended_${version}_linux-amd64.tar.gz" -o "$RUNNER_TEMP/hugo.tar.gz"
mkdir -p "$RUNNER_TEMP/hugo"
tar -xzf "$RUNNER_TEMP/hugo.tar.gz" -C "$RUNNER_TEMP/hugo" hugo
echo "$RUNNER_TEMP/hugo" >> "$GITHUB_PATH"
"$RUNNER_TEMP/hugo/hugo" version
