# Evergreen recycler operations

The production worker is on the existing DigitalOcean droplet, accessed through the `linklog-server` SSH alias (`159.203.190.26`, user `joshuapsteele`). It runs directly on Python 3.12 as a systemd **user** service. Docker is not installed or required.

## Current installation

- Application: `/home/joshuapsteele/evergreen-recycler/`
- Credentials and runtime flag: `/home/joshuapsteele/evergreen-recycler/.env` (mode 600)
- SQLite database: `/home/joshuapsteele/evergreen-recycler/state/recycler.sqlite3`
- Backups: `/home/joshuapsteele/evergreen-recycler/state/backups/`
- Units: `/home/joshuapsteele/.config/systemd/user/evergreen-recycler*`
- Worker listens on `127.0.0.1:8787` on the droplet.
- Production dashboard: <https://recycler.joshuapsteele.com>
- `loginctl enable-linger joshuapsteele` is enabled, so the user service survives logout and starts at boot.

The local library, approvals, teaser copy, schedule, destination, and first accepted post were migrated together. The local worker was stopped and local `.env` changed to `RECYCLER_LIVE=0`. Its database remains paused. Keep production scheduling on the droplet; two independent live databases can post duplicate teasers.

The first live teaser was accepted at <https://social.joshuapsteele.com/2026/10/13/wide-feet-play-soccer-try.html>. Josh confirmed delivery to [Threads](https://www.threads.com/@joshuapsteele/post/Deb5RymlqXl) and [Bluesky](https://bsky.app/profile/joshuapsteele.com/post/3mxr4jr6mbv26). Migration preserved that day's slot claim and the article cooldown.

## HTTPS configuration

The configured Porkbun DNS record for `joshuapsteele.com` is:

| Type | Host | Value |
| --- | --- | --- |
| A | recycler | 159.203.190.26 |

No AAAA record is needed unless the droplet's IPv6 address is deliberately configured. An incorrect AAAA record can send visitors or certificate verification to another server.

For a fresh installation, run this on the Mac after creating the DNS record:

```sh
ssh -t linklog-server 'sudo python3 ~/evergreen-recycler/enable-https.py'
```

The prepared installer adds only the recycler reverse proxy, validates the complete Caddy configuration before replacing it, saves the previous configuration at `/etc/caddy/Caddyfile.before-recycler-<timestamp>`, and reloads Caddy. A failed reload restores the previous configuration. It preserves the existing LinkLog proxy. Running it requires the droplet account's sudo password; do not send the password in chat.

Caddy obtains and renews the certificate. On October 13, 2026, DNS resolution, certificate verification, the HTTPS dashboard, authenticated API access, and rejection of unauthenticated API requests were verified. The existing LinkLog HTTPS site also returned 200 after the Caddy change. Open <https://recycler.joshuapsteele.com> and log in using the **server's** `RECYCLER_ADMIN_TOKEN`.

For access through an SSH tunnel instead:

```sh
ssh -N -L 8787:127.0.0.1:8787 linklog-server
```

Leave that terminal open and visit <http://127.0.0.1:8787>. Ctrl+C closes only the tunnel; the worker continues on the server. If port 8787 is occupied locally, use `-L 8788:127.0.0.1:8787` and open port 8788 instead.

## Manage the service

From the Mac:

```sh
# Authenticated health check (prints no credentials or teaser copy)
ssh linklog-server 'python3 ~/evergreen-recycler/healthcheck.py'

# Status
ssh linklog-server 'systemctl --user status evergreen-recycler --no-pager'

# Restart after editing .env or updating code
ssh linklog-server 'systemctl --user restart evergreen-recycler'

# Stop/start the worker
ssh linklog-server 'systemctl --user stop evergreen-recycler'
ssh linklog-server 'systemctl --user start evergreen-recycler'

# Recent logs
ssh linklog-server 'journalctl --user -u evergreen-recycler --no-pager -n 50'

# Edit server configuration interactively
ssh -t linklog-server 'nano ~/evergreen-recycler/.env'
```

Dashboard changes to approval, pause, and schedule are immediate. Environment/credential changes need a restart. The dashboard badge reports the process's active publishing mode. **Accepted** in history means Micro.blog accepted the request; downstream delivery should be checked in Micro.blog and the social services.

## Deploy code updates

From the repository root:

```sh
python3 -m unittest discover -s tests -p 'test_evergreen_recycler.py'
node --check tools/evergreen-recycler/app.js
sh tools/evergreen-recycler/update-droplet.sh
```

The updater first backs up the remote database, copies only explicitly listed app files and service units, restarts the user service, and verifies authenticated access. It never copies your local `.env` or database over production. To update credentials or import new articles, make those changes on the server or through the hosted dashboard.

This updates the existing installation; it does not bootstrap a new server. Pushing this repository to GitHub deploys the Hugo site through GitHub Actions. The recycler is updated separately with the command above; GitHub Actions does not restart or deploy the droplet service.

## Import the full archive

The dashboard's **Import recent articles** uses the public JSON Feed. For all published blog articles, generate Hugo's complete CSV catalog on the Mac and import it on the droplet:

```sh
hugo list published > /tmp/evergreen-catalog.csv
scp /tmp/evergreen-catalog.csv linklog-server:evergreen-recycler/state/catalog.csv
ssh linklog-server 'python3 ~/evergreen-recycler/app.py import --catalog ~/evergreen-recycler/state/catalog.csv'
```

Imports preserve existing teaser copy, approvals, and history. A full catalog marks missing URLs unavailable for recycling; an incremental feed import cannot detect removals outside that feed. New article URLs start unapproved.

## Backups and restore

A systemd user timer runs a verified SQLite backup daily and retains the newest 14 snapshots. It uses the droplet's system time zone (currently UTC), shortly after midnight with up to 20 minutes of randomized delay. Article posting uses the separate time zone configured in the dashboard. SQLite's backup API allows backups while the worker runs. The initial deployment's backup was verified. These snapshots are on the same droplet; periodically download one to protect against losing the droplet itself.

```sh
# Create a backup now
ssh linklog-server 'systemctl --user start evergreen-recycler-backup.service'

# Check the timer
ssh linklog-server 'systemctl --user list-timers evergreen-recycler-backup.timer --no-pager'

# List snapshots (timestamps use UTC)
ssh linklog-server 'ls -lt ~/evergreen-recycler/state/backups/'
```

Download the chosen snapshot with `scp linklog-server:evergreen-recycler/state/backups/<filename> /your/local/backup/folder/`. Keep credentials separately in your password manager.

To restore: stop the worker, create a backup of its current database, and copy the chosen snapshot into `state/recycler.sqlite3`, preserving owner `joshuapsteele` and mode 600. Set `RECYCLER_LIVE=0` in the server's `.env` before starting the worker and running the health check. Review restored history, resolve uncertain attempts, and check Micro.blog for posts made since the snapshot. An older snapshot loses later slot claims and cooldown updates; keep already-shared articles unapproved until they are ready to recycle again. After reviewing, restore `RECYCLER_LIVE=1`, restart the service, and resume the queue when ready.
