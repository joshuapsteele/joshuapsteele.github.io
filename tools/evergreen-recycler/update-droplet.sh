#!/bin/sh
# Deploy code updates without copying credentials or replacing the live database.
set -eu
recycler_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
recycler_host=${1:-linklog-server}
ssh "$recycler_host" 'python3 ~/evergreen-recycler/backup.py'
# An explicit list excludes .env, private state, caches, and development artifacts.
scp "$recycler_dir/app.py" "$recycler_dir/app.js" "$recycler_dir/index.html" \
  "$recycler_dir/style.css" "$recycler_dir/backup.py" "$recycler_dir/README.md" \
  "$recycler_dir/healthcheck.py" "$recycler_dir/OPERATIONS.md" "$recycler_dir/enable-https.py" \
  "$recycler_host:evergreen-recycler/"
scp "$recycler_dir/evergreen-recycler.service" \
  "$recycler_dir/evergreen-recycler-backup.service" \
  "$recycler_dir/evergreen-recycler-backup.timer" \
  "$recycler_host:.config/systemd/user/"
ssh "$recycler_host" 'systemctl --user daemon-reload && systemctl --user restart evergreen-recycler && systemctl --user enable --now evergreen-recycler-backup.timer && python3 evergreen-recycler/healthcheck.py'
