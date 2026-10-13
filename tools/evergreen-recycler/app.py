#!/usr/bin/env python3
"""A private, standard-library-only evergreen queue. Python 3.9+."""
import argparse
from contextlib import contextmanager
import csv
import hmac
import html
import io
import json
import logging
import os
from pathlib import Path
import shlex
import sqlite3
import threading
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
UTC = timezone.utc
MICROPUB = 'https://micro.blog/micropub'
FEED = 'https://joshuapsteele.com/blog/feed.json'
DEFAULTS = {'paused': True, 'timezone': 'America/New_York', 'weekdays': [0, 2, 4],
            'time': '10:00', 'cooldown_days': 90, 'minimum_age_days': 30,
            'grace_minutes': 60, 'destination': ''}
LOG = logging.getLogger('recycler')


def load_env(path):
    """Load local configuration without executing shell code; exports win."""
    path = Path(path)
    if not path.exists():
        return
    allowed = {'RECYCLER_ADMIN_TOKEN', 'MICROBLOG_TOKEN', 'RECYCLER_LIVE', 'RECYCLER_DB'}
    values = {}
    for number, line in enumerate(path.read_text().splitlines(), 1):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if line.startswith('export '):
            line = line[7:].strip()
        key, separator, raw = line.partition('=')
        key = key.strip()
        if key not in allowed:
            continue
        try:
            parts = shlex.split(raw, comments=True)
        except ValueError:
            raise ValueError('Invalid .env syntax on line %d; check quoting.' % number) from None
        if not separator or len(parts) > 1:
            raise ValueError('Invalid .env syntax on line %d; quote values containing spaces.' % number)
        values[key] = parts[0] if parts else ''
    for key, value in values.items():
        os.environ.setdefault(key, value)


def now_utc():
    return datetime.now(UTC)


def parse_date(value):
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    return parsed.replace(tzinfo=UTC) if parsed.tzinfo is None else parsed.astimezone(UTC)


def canonical_url(value):
    p = urlparse(value)
    if (p.scheme != 'https' or p.netloc not in ('joshuapsteele.com', 'www.joshuapsteele.com')
            or p.query or p.fragment or not p.path or p.path == '/' or any(c.isspace() for c in value)):
        raise ValueError('Use an HTTPS article URL on joshuapsteele.com without a query or fragment.')
    return value.replace('https://www.', 'https://', 1)


def validate_variants(variants, url):
    if not isinstance(variants, list) or not 1 <= len(variants) <= 20:
        raise ValueError('Provide 1–20 teaser variants, one per line.')
    clean = []
    for text in variants:
        if not isinstance(text, str) or not text.strip() or '\n' in text or '\r' in text:
            raise ValueError('Each teaser must be one nonempty line.')
        text = text.strip()
        if len(text + '\n\n' + url) > 280:
            raise ValueError('Each teaser plus the article URL must fit within 280 characters.')
        clean.append(text)
    return clean


def validate_settings(value):
    if set(value) != set(DEFAULTS):
        raise ValueError('Invalid settings fields.')
    ZoneInfo(value['timezone'])
    if type(value['paused']) is not bool:
        raise ValueError('Paused must be a boolean.')
    if (not isinstance(value['weekdays'], list) or not value['weekdays']
            or any(type(day) is not int or not 0 <= day <= 6 for day in value['weekdays'])):
        raise ValueError('Select weekdays from Monday (0) through Sunday (6).')
    datetime.strptime(value['time'], '%H:%M')
    if len(value['time']) != 5:
        raise ValueError('Use HH:MM for the posting time.')
    for key, lower, upper in [('cooldown_days', 1, 3650), ('minimum_age_days', 0, 3650),
                              ('grace_minutes', 1, 180)]:
        if type(value[key]) is not int or not lower <= value[key] <= upper:
            raise ValueError('%s must be between %d and %d.' % (key, lower, upper))
    destination = urlparse(value['destination'])
    if value['destination'] and (destination.scheme != 'https' or not destination.netloc
                                  or destination.username or destination.query or destination.fragment):
        raise ValueError('Copy the HTTPS destination UID from Test connection.')
    return value


class Store:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.executescript('''
              CREATE TABLE IF NOT EXISTS settings (id INTEGER PRIMARY KEY CHECK(id=1), value TEXT NOT NULL);
              CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY, url TEXT UNIQUE NOT NULL, title TEXT NOT NULL,
                published TEXT NOT NULL, variants TEXT NOT NULL DEFAULT '[]',
                enabled INTEGER NOT NULL DEFAULT 0, expires TEXT NOT NULL DEFAULT '',
                last_shared TEXT, shares INTEGER NOT NULL DEFAULT 0, present INTEGER NOT NULL DEFAULT 1);
              CREATE TABLE IF NOT EXISTS attempts (
                id INTEGER PRIMARY KEY, slot TEXT UNIQUE NOT NULL, article_id INTEGER NOT NULL,
                created TEXT NOT NULL, status TEXT NOT NULL, content TEXT NOT NULL,
                post_url TEXT NOT NULL DEFAULT '', message TEXT NOT NULL DEFAULT '',
                FOREIGN KEY(article_id) REFERENCES articles(id));
            ''')
            db.execute('INSERT OR IGNORE INTO settings VALUES (1, ?)', (json.dumps(DEFAULTS),))

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        db.execute('PRAGMA foreign_keys=ON')
        try:
            with db:
                yield db
        finally:
            db.close()

    def settings(self, db):
        return json.loads(db.execute('SELECT value FROM settings WHERE id=1').fetchone()[0])

    def import_articles(self, items, authoritative=False):
        rows = []
        seen = set()
        for item in items:
            if item.get('section', 'blog') != 'blog' or str(item.get('draft', 'false')).lower() == 'true':
                continue
            url = canonical_url(item.get('url') or item.get('permalink') or '')
            title = item.get('title', '').strip()
            date = parse_date(item.get('date_published') or item.get('publishDate') or item['date'])
            if not title or date > now_utc() or url in seen:
                continue
            seen.add(url)
            rows.append((url, title, date.isoformat()))
        if authoritative and not rows:
            raise ValueError('Empty archive; existing articles were preserved.')
        with self.connect() as db:
            if authoritative:
                db.execute('UPDATE articles SET present=0')
            db.executemany('''INSERT INTO articles(url,title,published) VALUES (?,?,?)
              ON CONFLICT(url) DO UPDATE SET title=excluded.title,published=excluded.published,present=1''', rows)
        return len(rows)

    def edit_article(self, value):
        with self.connect() as db:
            row = db.execute('SELECT * FROM articles WHERE id=?', (value['id'],)).fetchone()
            if row is None:
                raise ValueError('Article not found.')
            if type(value['enabled']) is not bool:
                raise ValueError('Enabled must be a boolean.')
            variants = value['variants']
            # Draft rows may have no copy; enabled rows must have validated copy.
            if variants or value['enabled']:
                variants = validate_variants(variants, row['url'])
            if not isinstance(variants, list):
                raise ValueError('Variants must be a list.')
            expires = value.get('expires', '')
            if expires:
                datetime.strptime(expires, '%Y-%m-%d')
            db.execute('UPDATE articles SET enabled=?, variants=?, expires=? WHERE id=?',
                       (value['enabled'], json.dumps(variants), expires, row['id']))

    def eligible(self, db, settings, moment):
        local_date = moment.astimezone(ZoneInfo(settings['timezone'])).date().isoformat()
        candidates = db.execute('''SELECT * FROM articles WHERE enabled=1 AND present=1
          ORDER BY COALESCE(last_shared,''), shares, published, id''').fetchall()
        for row in candidates:
            if parse_date(row['published']) > moment - timedelta(days=settings['minimum_age_days']):
                continue
            if row['last_shared'] and parse_date(row['last_shared']) > moment - timedelta(days=settings['cooldown_days']):
                continue
            if row['expires'] and row['expires'] < local_date:
                continue
            variants = validate_variants(json.loads(row['variants']), row['url'])
            return dict(row), variants[row['shares'] % len(variants)] + '\n\n' + row['url']
        return None, None

    def snapshot(self):
        with self.connect() as db:
            settings = self.settings(db)
            article, content = self.eligible(db, settings, now_utc())
            return {'settings': settings,
                    'articles': [dict(row, variants=json.loads(row['variants'])) for row in
                                 db.execute('SELECT * FROM articles ORDER BY published DESC')],
                    'history': [dict(row) for row in db.execute('SELECT * FROM attempts ORDER BY id DESC LIMIT 100')],
                    'next': {'article': article, 'content': content},
                    'live': os.environ.get('RECYCLER_LIVE') == '1',
                    'connected': bool(os.environ.get('MICROBLOG_TOKEN'))}

    def resolve(self, value, moment=None):
        moment = moment or now_utc()
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            row = db.execute("SELECT * FROM attempts WHERE id=? AND status IN ('sending','uncertain')", (value['id'],)).fetchone()
            if not row:
                raise ValueError('No uncertain attempt to resolve.')
            if row['status'] == 'sending' and moment - parse_date(row['created']) < timedelta(minutes=5):
                raise ValueError('This request may still be in flight. Wait five minutes before reconciling it.')
            if value['outcome'] not in ('accepted', 'not-delivered'):
                raise ValueError('Choose accepted or not-delivered after checking Micro.blog.')
            post_url = value.get('post_url', '')
            if post_url and (urlparse(post_url).scheme != 'https' or not urlparse(post_url).netloc):
                raise ValueError('Post URL must be HTTPS.')
            if value['outcome'] == 'accepted':
                db.execute('UPDATE articles SET last_shared=?, shares=shares+1 WHERE id=?',
                           (moment.isoformat(), row['article_id']))
            db.execute('UPDATE attempts SET status=?,post_url=?,message=? WHERE id=?',
                       (value['outcome'], post_url, 'Manually reconciled after checking Micro.blog.', row['id']))


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class Microblog:
    def __init__(self, token):
        if not token or any(c.isspace() for c in token):
            raise ValueError('Set MICROBLOG_TOKEN to a Micro.blog app token.')
        self.token = token
        self.opener = build_opener(NoRedirect)

    def config(self, destination=''):
        query = {'q': 'config'}
        if destination:
            query['mp-destination'] = destination
        request = Request(MICROPUB + '?' + urlencode(query), headers={'Authorization': 'Bearer ' + self.token})
        try:
            with self.opener.open(request, timeout=30) as response:
                return json.load(response)
        except (HTTPError, URLError, TimeoutError, OSError, ValueError):
            # Never log response bodies, request headers, or token-bearing errors.
            raise ValueError('Micro.blog configuration check failed; check the app token and network.') from None

    def publish(self, destination, content):
        text, url = content.rsplit('\n\n', 1)
        rendered = '<p>%s</p><p><a href="%s">%s</a></p>' % (html.escape(text), html.escape(url, quote=True), html.escape(url))
        body = {'type': ['h-entry'], 'mp-destination': destination,
                'properties': {'content': [{'html': rendered}]}}
        request = Request(MICROPUB, data=json.dumps(body).encode(),
                          headers={'Authorization': 'Bearer ' + self.token, 'Content-Type': 'application/json'})
        try:
            with self.opener.open(request, timeout=30) as response:
                if response.status not in (200, 201, 202):
                    return 'uncertain', '', 'Unexpected success response; check Micro.blog before resolving.'
                return 'accepted', response.headers.get('Location', ''), 'Accepted by Micro.blog; downstream cross-posting is unverified.'
        except HTTPError as exc:
            if exc.code in (400, 401, 403, 404, 405, 413, 415, 422, 429):
                return 'rejected', '', 'Micro.blog rejected the request (HTTP %d).' % exc.code
            return 'uncertain', '', 'HTTP %d; check Micro.blog before resolving.' % exc.code
        except (URLError, TimeoutError, OSError):
            return 'uncertain', '', 'Network failure; check Micro.blog before resolving.'


def due_slot(settings, moment):
    local = moment.astimezone(ZoneInfo(settings['timezone']))
    if local.weekday() not in settings['weekdays']:
        return None
    hour, minute = map(int, settings['time'].split(':'))
    scheduled = local.replace(hour=hour, minute=minute, second=0, microsecond=0)
    roundtrip = scheduled.astimezone(UTC).astimezone(ZoneInfo(settings['timezone']))
    if (roundtrip.hour, roundtrip.minute) != (hour, minute):
        return None  # A spring-forward slot that never occurs is skipped.
    # UTC comparison handles DST offsets; date key prevents a repeated-hour duplicate.
    elapsed = (moment - scheduled.astimezone(UTC)).total_seconds()
    if 0 <= elapsed < settings['grace_minutes'] * 60:
        return local.date().isoformat()
    return None


def tick(store, client=None, moment=None, live=None):
    moment = moment or now_utc()
    live = os.environ.get('RECYCLER_LIVE') == '1' if live is None else live
    # An immediate transaction serializes claims across processes and workers.
    with store.connect() as db:
        db.execute('BEGIN IMMEDIATE')
        settings = store.settings(db)
        slot = due_slot(settings, moment)
        if settings['paused'] or not slot:
            return {'status': 'paused' if settings['paused'] else 'outside-slot'}
        if db.execute("SELECT 1 FROM attempts WHERE status IN ('sending','uncertain')").fetchone():
            return {'status': 'blocked', 'message': 'Reconcile the uncertain attempt in history.'}
        if db.execute('SELECT 1 FROM attempts WHERE slot=?', (slot,)).fetchone():
            return {'status': 'already-claimed'}
        article, content = store.eligible(db, settings, moment)
        if not article:
            return {'status': 'empty'}
        if not live:
            return {'status': 'dry-run', 'content': content}
        if not settings['destination']:
            raise ValueError('Choose a Micro.blog destination before enabling live publishing.')
        client = client or Microblog(os.environ.get('MICROBLOG_TOKEN', ''))
        config = client.config(settings['destination'])
        if settings['destination'] not in [d['uid'] for d in config.get('destination', [])]:
            raise ValueError('Destination UID was not returned by Micro.blog; copy it from Test connection.')
        attempt_id = db.execute('''INSERT INTO attempts(slot,article_id,created,status,content)
          VALUES (?,?,?,'sending',?)''', (slot, article['id'], moment.isoformat(), content)).lastrowid
    # Persist the claim before the network call. A crash leaves a blocking sending record.
    try:
        status, post_url, message = client.publish(settings['destination'], content)
    except Exception:
        status, post_url, message = 'uncertain', '', 'Unexpected publishing failure; check Micro.blog before resolving.'
    with store.connect() as db:
        db.execute('BEGIN IMMEDIATE')
        db.execute('UPDATE attempts SET status=?,post_url=?,message=? WHERE id=?', (status, post_url, message, attempt_id))
        if status == 'accepted':
            db.execute('UPDATE articles SET last_shared=?,shares=shares+1 WHERE id=?', (moment.isoformat(), article['id']))
    LOG.info('Attempt %d: %s', attempt_id, status)
    return {'status': status, 'id': attempt_id}


def fetch_feed():
    with build_opener(NoRedirect).open(Request(FEED, headers={'Accept': 'application/feed+json'}), timeout=30) as response:
        return json.load(response).get('items', [])


def handler_for(store, admin_token):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            pass  # Avoid logging authorization and private queue details.

        def send(self, status, body, mime='application/json'):
            payload = body.encode() if isinstance(body, str) else json.dumps(body).encode()
            self.send_response(status)
            self.send_header('Content-Type', mime + '; charset=utf-8')
            self.send_header('Content-Length', str(len(payload)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Referrer-Policy', 'no-referrer')
            self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
            self.end_headers()
            self.wfile.write(payload)

        def authorized(self):
            supplied = self.headers.get('Authorization', '')
            if not hmac.compare_digest(supplied.encode(), ('Bearer ' + admin_token).encode()):
                self.send(401, {'error': 'Enter your dashboard access key.'})
                return False
            return True

        def do_GET(self):
            if self.path in ('/', '/app.js', '/style.css'):
                filename = {'/': 'index.html', '/app.js': 'app.js', '/style.css': 'style.css'}[self.path]
                mime = {'/': 'text/html', '/app.js': 'text/javascript', '/style.css': 'text/css'}[self.path]
                self.send(200, (HERE / filename).read_text(), mime)
            elif self.path == '/api/state' and self.authorized():
                self.send(200, store.snapshot())
            elif self.path != '/api/state':
                self.send(404, {'error': 'Not found.'})

        def do_POST(self):
            if not self.authorized():
                return
            if not self.headers.get('Content-Type', '').startswith('application/json'):
                self.send(415, {'error': 'Use application/json.'})
                return
            try:
                size = int(self.headers.get('Content-Length', '0'))
                if not 0 < size <= 65536:
                    raise ValueError('Invalid request size.')
                value = json.loads(self.rfile.read(size))
                if self.path == '/api/article':
                    store.edit_article(value)
                    result = {'ok': True}
                elif self.path == '/api/settings':
                    validate_settings(value)
                    with store.connect() as db:
                        db.execute('UPDATE settings SET value=? WHERE id=1', (json.dumps(value),))
                    result = {'ok': True}
                elif self.path == '/api/import':
                    result = {'count': store.import_articles(fetch_feed())}
                elif self.path == '/api/connection':
                    config = Microblog(os.environ.get('MICROBLOG_TOKEN', '')).config()
                    result = {'destinations': config.get('destination', [])}
                elif self.path == '/api/resolve':
                    store.resolve(value)
                    result = {'ok': True}
                else:
                    self.send(404, {'error': 'Not found.'})
                    return
                self.send(200, result)
            except ValueError as exc:
                self.send(400, {'error': str(exc) if not isinstance(exc, json.JSONDecodeError) else 'Invalid JSON.'})
            except (KeyError, TypeError, URLError, OSError):
                self.send(400, {'error': 'Invalid request or connection failed. Check your fields and server configuration.'})
    return Handler


def serve(store, host, port):
    token = os.environ.get('RECYCLER_ADMIN_TOKEN', '')
    if len(token) < 24 or any(c.isspace() for c in token):
        raise ValueError('Set RECYCLER_ADMIN_TOKEN to an access key of at least 24 characters.')
    stop = threading.Event()
    def worker():
        while not stop.is_set():
            try:
                result = tick(store)
                if result['status'] not in ('paused', 'outside-slot', 'already-claimed'):
                    LOG.info('Worker: %s', result['status'])
            except Exception:
                LOG.error('Worker failed; check configuration, connectivity, and queue state.')
            stop.wait(60)
    server = ThreadingHTTPServer((host, port), handler_for(store, token))
    server.daemon_threads = True
    threading.Thread(target=worker, daemon=True).start()
    LOG.info('Dashboard: http://%s:%d (live=%s)', host, port, os.environ.get('RECYCLER_LIVE') == '1')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        stop.set()
        server.server_close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--env-file', type=Path, default=HERE / '.env',
                        help='Local configuration file (default: .env beside app.py). Shell exports take precedence.')
    parser.add_argument('--db', help='Override the database path from RECYCLER_DB.')
    commands = parser.add_subparsers(dest='command', required=True)
    web = commands.add_parser('serve')
    web.add_argument('--host', default='127.0.0.1')
    web.add_argument('--port', default=8787, type=int)
    imp = commands.add_parser('import', help='Import recent JSON Feed or full Hugo CSV catalog.')
    imp.add_argument('--catalog', type=Path)
    commands.add_parser('tick', help='Run one scheduling check; dry run unless RECYCLER_LIVE=1.')
    commands.add_parser('preview', help='Preview the next eligible article without posting.')
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
    try:
        load_env(args.env_file)
        store = Store(args.db or os.environ.get('RECYCLER_DB', str(HERE / 'state' / 'recycler.sqlite3')))
        if args.command == 'serve':
            serve(store, args.host, args.port)
        elif args.command == 'import':
            if args.catalog:
                items = list(csv.DictReader(io.StringIO(args.catalog.read_text())))
            else:
                items = fetch_feed()
            print(json.dumps({'imported': store.import_articles(items, authoritative=bool(args.catalog))}))
        elif args.command == 'tick':
            print(json.dumps(tick(store), indent=2))
        elif args.command == 'preview':
            print(json.dumps(store.snapshot()['next'], indent=2))
    except ValueError as exc:
        parser.exit(1, 'Configuration error: %s\n' % exc)
    except OSError as exc:
        if exc.errno in (48, 98):
            parser.exit(1, 'Port %d is already in use. Stop the other recycler or use serve --port 8788.\n' % args.port)
        parser.exit(1, 'Could not read configuration, access the database, or connect. Check file permissions and network access.\n')


if __name__ == '__main__':
    main()
