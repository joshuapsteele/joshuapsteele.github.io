#!/usr/bin/env python3
"""Create a consistent SQLite snapshot. Keep the newest 14 backups."""
from datetime import datetime, timezone
from pathlib import Path
import os
import sqlite3


def backup(database, directory, keep=14):
    database = Path(database)
    directory = Path(directory)
    if not database.is_file():
        raise FileNotFoundError('Recycler database not found; nothing was backed up.')
    directory.mkdir(parents=True, exist_ok=True)
    name = 'recycler-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '.sqlite3'
    destination = directory / name
    # The SQLite backup API is safe while the worker is using the source.
    source = sqlite3.connect(database.as_uri() + '?mode=ro', uri=True)
    target = sqlite3.connect(destination)
    try:
        source.backup(target)
        if target.execute('PRAGMA quick_check').fetchone()[0] != 'ok':
            raise RuntimeError('Snapshot verification failed; existing backups were preserved.')
    finally:
        target.close()
        source.close()
    destination.chmod(0o600)
    for older in sorted(directory.glob('recycler-*.sqlite3'), reverse=True)[keep:]:
        older.unlink()
    return destination


if __name__ == '__main__':
    os.umask(0o077)
    root = Path(__file__).resolve().parent
    print('Verified backup: ' + str(backup(root / 'state/recycler.sqlite3', root / 'state/backups')))
