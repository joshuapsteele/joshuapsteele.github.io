#!/usr/bin/env python3
"""Run once with sudo on the droplet to add the recycler HTTPS proxy."""
from datetime import datetime, timezone
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

DOMAIN = 'recycler.joshuapsteele.com'
CONFIG = Path('/etc/caddy/Caddyfile')


def main():
    if os.geteuid() != 0:
        raise SystemExit('Run with sudo on the droplet; this changes Caddy configuration.')
    original = CONFIG.read_text()
    if DOMAIN in original:
        raise SystemExit('Recycler domain already appears in Caddy configuration. Existing configuration preserved.')
    stat = CONFIG.stat()
    new = original.rstrip() + '\n\n' + DOMAIN + ' {\n  reverse_proxy 127.0.0.1:8787\n}\n'
    with tempfile.NamedTemporaryFile(mode='w', dir=CONFIG.parent, prefix='.Caddyfile.recycler.', delete=False) as handle:
        handle.write(new)
        staged = Path(handle.name)
    try:
        staged.chmod(stat.st_mode & 0o777)
        os.chown(staged, stat.st_uid, stat.st_gid)
        subprocess.run(['/usr/bin/caddy', 'validate', '--config', str(staged), '--adapter', 'caddyfile'], check=True)
        if CONFIG.read_text() != original:
            raise SystemExit('Caddy configuration changed during validation; existing configuration preserved.')
        stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
        backup = CONFIG.with_name('Caddyfile.before-recycler-' + stamp)
        if backup.exists():
            raise SystemExit('Backup path already exists; existing configuration preserved.')
        shutil.copy2(CONFIG, backup)
        os.replace(staged, CONFIG)
        try:
            subprocess.run(['/usr/bin/systemctl', 'reload', 'caddy'], check=True)
        except subprocess.CalledProcessError:
            shutil.copy2(backup, CONFIG)
            subprocess.run(['/usr/bin/systemctl', 'reload', 'caddy'], check=True)
            raise SystemExit('Reload failed; the previous Caddy configuration was restored.') from None
        print('Enabled HTTPS proxy for https://' + DOMAIN)
        print('Previous Caddy configuration: ' + str(backup))
    finally:
        if staged.exists():
            staged.unlink()


if __name__ == '__main__':
    main()
