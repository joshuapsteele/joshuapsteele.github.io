import importlib.util
import json
from pathlib import Path
import tempfile
import threading
import unittest
from datetime import datetime, timedelta, timezone
from http.client import HTTPConnection
from urllib.error import HTTPError, URLError
from unittest.mock import MagicMock, Mock

SPEC = importlib.util.spec_from_file_location('recycler', Path(__file__).resolve().parents[1] / 'tools/evergreen-recycler/app.py')
app = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(app)
NOW = datetime(2026, 10, 12, 14, 0, tzinfo=timezone.utc)  # Monday, 10am Eastern
URL = 'https://joshuapsteele.com/my-custom-url/'
DEST = 'https://joshuapsteele.micro.blog/'


class RecyclerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.store = app.Store(Path(self.tmp.name) / 'state.sqlite3')
        self.store.import_articles([{'url': URL, 'title': 'A useful article', 'date_published': '2020-01-01T00:00:00Z'}])
        self.store.edit_article({'id': 1, 'enabled': True, 'variants': ['First angle', 'Second angle']})
        self.settings = dict(app.DEFAULTS, paused=False, destination=DEST)
        self.save_settings()
        self.client = Mock()
        self.client.config.return_value = {'destination': [{'uid': DEST}]}
        self.client.publish.return_value = ('accepted', 'https://social.joshuapsteele.com/teaser/', 'Accepted')

    def save_settings(self):
        with self.store.connect() as db:
            db.execute('UPDATE settings SET value=? WHERE id=1', (json.dumps(self.settings),))

    def tick(self, **kwargs):
        return app.tick(self.store, self.client, kwargs.get('moment', NOW), kwargs.get('live', True))

    def test_import_preserves_approval_and_variants_and_handles_custom_urls(self):
        self.store.import_articles([{'url': URL, 'title': 'Revised title', 'date_published': '2020-01-01T00:00:00Z'}])
        article = self.store.snapshot()['articles'][0]
        self.assertEqual(article['title'], 'Revised title')
        self.assertEqual(article['variants'], ['First angle', 'Second angle'])
        self.assertEqual(article['enabled'], 1)
        self.assertEqual(article['url'], URL)

    def test_import_excludes_drafts_future_and_notes(self):
        count = self.store.import_articles([
            {'permalink': 'https://joshuapsteele.com/note/', 'section': 'notes'},
            {'permalink': 'https://joshuapsteele.com/draft/', 'draft': 'true'},
            {'url': 'https://joshuapsteele.com/future/', 'title': 'Future', 'date_published': '2099-01-01T00:00:00Z'}])
        self.assertEqual(count, 0)

    def test_full_import_disables_missing_articles_but_partial_import_does_not(self):
        self.store.import_articles([])
        self.assertEqual(self.store.snapshot()['articles'][0]['present'], 1)
        self.store.import_articles([{'url': 'https://joshuapsteele.com/other/', 'title': 'Other', 'date': '2020-01-01'}], authoritative=True)
        self.assertEqual(next(a for a in self.store.snapshot()['articles'] if a['id'] == 1)['present'], 0)
        self.assertEqual(self.tick()['status'], 'empty')
        with self.assertRaises(ValueError):
            self.store.import_articles([], authoritative=True)

    def test_paused_and_dry_run_never_post_or_consume_slot(self):
        self.assertEqual(self.tick(live=False)['status'], 'dry-run')
        self.assertEqual(self.store.snapshot()['history'], [])
        self.settings['paused'] = True
        self.save_settings()
        self.assertEqual(self.tick()['status'], 'paused')
        self.client.publish.assert_not_called()

    def test_only_due_slots_and_no_catchup(self):
        for moment in [NOW - timedelta(minutes=1), NOW + timedelta(hours=1), NOW + timedelta(days=1)]:
            self.assertEqual(self.tick(moment=moment)['status'], 'outside-slot')
        self.client.publish.assert_not_called()

    def test_success_survives_restart_and_never_duplicates_slot(self):
        self.assertEqual(self.tick()['status'], 'accepted')
        restarted = app.Store(self.store.path)
        self.assertEqual(app.tick(restarted, self.client, NOW, True)['status'], 'already-claimed')
        self.assertEqual(self.client.publish.call_count, 1)
        self.assertEqual(restarted.snapshot()['articles'][0]['shares'], 1)

    def test_concurrent_workers_claim_only_once(self):
        results = []
        workers = [threading.Thread(target=lambda: results.append(self.tick()['status'])) for _ in range(2)]
        for worker in workers:
            worker.start()
        for worker in workers:
            worker.join()
        self.assertEqual(results.count('accepted'), 1)
        self.assertEqual(self.client.publish.call_count, 1)

    def test_cooldown_rotation_and_expiry(self):
        self.tick()
        self.assertEqual(self.tick(moment=NOW + timedelta(days=2))['status'], 'empty')
        # Exactly 91 days later is another Monday and exceeds the 90-day cooldown.
        self.tick(moment=NOW + timedelta(days=91, hours=1))
        self.assertTrue(self.client.publish.call_args.args[1].startswith('Second angle'))
        self.store.edit_article({'id': 1, 'enabled': True, 'variants': ['First angle'], 'expires': '2026-01-01'})
        self.assertEqual(self.tick(moment=NOW + timedelta(days=182))['status'], 'empty')

    def test_fairness_article_cooldown_applies_across_variants(self):
        self.store.import_articles([{'url': 'https://joshuapsteele.com/second/', 'title': 'Second', 'date': '2021-01-01'}])
        self.store.edit_article({'id': 2, 'enabled': True, 'variants': ['Another article']})
        self.tick()
        self.tick(moment=NOW + timedelta(days=2))
        self.assertIn('/second/', self.client.publish.call_args.args[1])

    def test_uncertain_outcome_blocks_all_slots_until_resolved(self):
        self.client.publish.return_value = ('uncertain', '', 'Timeout')
        self.assertEqual(self.tick()['status'], 'uncertain')
        self.assertEqual(self.tick(moment=NOW + timedelta(days=2))['status'], 'blocked')
        self.store.resolve({'id': 1, 'outcome': 'accepted'}, NOW + timedelta(minutes=5))
        self.assertEqual(self.store.snapshot()['articles'][0]['shares'], 1)
        self.assertEqual(self.tick(moment=NOW + timedelta(days=2))['status'], 'empty')
        with self.assertRaises(ValueError):
            self.store.resolve({'id': 1, 'outcome': 'accepted'})

    def test_crash_claim_cannot_be_reconciled_while_request_is_in_flight(self):
        with self.store.connect() as db:
            db.execute("INSERT INTO attempts(slot,article_id,created,status,content) VALUES (?,1,?,'sending','copy')", (NOW.date().isoformat(), NOW.isoformat()))
        self.assertEqual(self.tick()['status'], 'blocked')
        with self.assertRaises(ValueError):
            self.store.resolve({'id': 1, 'outcome': 'not-delivered'}, NOW)
        self.store.resolve({'id': 1, 'outcome': 'not-delivered'}, NOW + timedelta(minutes=6))
        self.assertEqual(self.tick()['status'], 'already-claimed')

    def test_rejected_request_does_not_retry_same_slot_or_start_cooldown(self):
        self.client.publish.return_value = ('rejected', '', 'HTTP 401')
        self.assertEqual(self.tick()['status'], 'rejected')
        self.assertEqual(self.tick()['status'], 'already-claimed')
        self.assertEqual(self.store.snapshot()['articles'][0]['shares'], 0)
        self.assertEqual(self.tick(moment=NOW + timedelta(days=2))['status'], 'rejected')

    def test_configuration_failure_does_not_claim_or_publish(self):
        self.client.config.return_value = {'destination': []}
        with self.assertRaises(ValueError):
            self.tick()
        self.assertEqual(self.store.snapshot()['history'], [])
        self.client.publish.assert_not_called()

    def test_validation_protects_content_and_settings(self):
        for url in ['http://joshuapsteele.com/post/', 'https://evil.com/post/', 'https://joshuapsteele.com@evil.com/post/']:
            with self.assertRaises(ValueError):
                app.canonical_url(url)
        for variants in [[], ['x' * 280], ['one\ntwo']]:
            with self.assertRaises(ValueError):
                app.validate_variants(variants, URL)
        with self.assertRaises(ValueError):
            app.validate_settings(dict(self.settings, weekdays=[7]))
        with self.assertRaises(ValueError):
            app.validate_settings(dict(self.settings, cooldown_days=0))

    def test_dst_fall_back_slot_is_only_claimed_once_per_local_date(self):
        settings = dict(self.settings, weekdays=[6], time='01:30')
        first = datetime(2026, 11, 1, 5, 30, tzinfo=timezone.utc)
        second = datetime(2026, 11, 1, 6, 30, tzinfo=timezone.utc)
        self.assertEqual(app.due_slot(settings, first), '2026-11-01')
        self.assertEqual(app.due_slot(settings, second), '2026-11-01')

    def test_nonexistent_spring_forward_slot_is_skipped(self):
        settings = dict(self.settings, weekdays=[6], time='02:30')
        moment = datetime(2026, 3, 8, 7, 30, tzinfo=timezone.utc)
        self.assertIsNone(app.due_slot(settings, moment))

    def test_recent_article_is_excluded(self):
        with self.store.connect() as db:
            db.execute('UPDATE articles SET published=? WHERE id=1', ((NOW - timedelta(days=1)).isoformat(),))
        self.assertEqual(self.tick()['status'], 'empty')


class MicroblogTests(unittest.TestCase):
    def test_request_is_untitled_html_with_explicit_destination_and_escaped_copy(self):
        client = app.Microblog('secret-token')
        client.opener = MagicMock()
        response = client.opener.open.return_value.__enter__.return_value
        response.status = 201
        response.headers = {'Location': 'https://social.joshuapsteele.com/post/'}
        status, url, _ = client.publish(DEST, '<script> & thoughts\n\n' + URL)
        self.assertEqual(status, 'accepted')
        request = client.opener.open.call_args.args[0]
        payload = json.loads(request.data)
        self.assertEqual(payload['mp-destination'], DEST)
        self.assertNotIn('name', payload['properties'])
        self.assertIn('&lt;script&gt; &amp;', payload['properties']['content'][0]['html'])
        self.assertIn(URL, payload['properties']['content'][0]['html'])

    def test_timeout_and_server_errors_are_uncertain(self):
        client = app.Microblog('secret-token')
        for error in [TimeoutError(), URLError('timeout'), HTTPError(app.MICROPUB, 500, 'error', {}, None)]:
            client.opener = Mock()
            client.opener.open.side_effect = error
            self.assertEqual(client.publish(DEST, 'Teaser\n\n' + URL)[0], 'uncertain')
        client.opener.open.side_effect = HTTPError(app.MICROPUB, 401, 'unauthorized', {}, None)
        self.assertEqual(client.publish(DEST, 'Teaser\n\n' + URL)[0], 'rejected')


class DashboardTests(unittest.TestCase):
    def test_api_authentication_and_no_credential_disclosure(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = app.Store(Path(tmp) / 'db.sqlite3')
            token = 'dashboard-key-with-enough-length'
            server = app.ThreadingHTTPServer(('127.0.0.1', 0), app.handler_for(store, token))
            worker = threading.Thread(target=server.serve_forever, daemon=True)
            worker.start()
            try:
                connection = HTTPConnection('127.0.0.1', server.server_port)
                connection.request('GET', '/api/state')
                self.assertEqual(connection.getresponse().status, 401)
                connection.close()
                connection = HTTPConnection('127.0.0.1', server.server_port)
                connection.request('GET', '/api/state', headers={'Authorization': 'Bearer ' + token})
                response = connection.getresponse()
                body = response.read().decode()
                self.assertEqual(response.status, 200)
                self.assertNotIn(token, body)
                self.assertEqual(response.getheader('Cache-Control'), 'no-store')
                connection.close()
            finally:
                server.shutdown()
                server.server_close()
                worker.join()


class StartupTests(unittest.TestCase):
    def test_missing_key_reports_the_specific_setup_instruction(self):
        import os
        import subprocess
        import sys
        with tempfile.TemporaryDirectory() as tmp:
            env = dict(os.environ)
            env.pop('RECYCLER_ADMIN_TOKEN', None)
            result = subprocess.run([sys.executable, str(Path(app.__file__)),
                                     '--env-file', str(Path(tmp) / 'missing.env'),
                                     '--db', str(Path(tmp) / 'db.sqlite3'), 'serve'],
                                    env=env, capture_output=True, text=True, timeout=5)
            self.assertEqual(result.returncode, 1)
            self.assertIn('Set RECYCLER_ADMIN_TOKEN', result.stderr)
            self.assertNotIn('Configuration or connection error', result.stderr)

    def test_env_file_loads_quoted_values_without_overriding_exports(self):
        import os
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / '.env'
            path.write_text('RECYCLER_ADMIN_TOKEN="fixture-dashboard-access-key"\n'
                            'MICROBLOG_TOKEN=fixture-microblog-token\n'
                            'RECYCLER_LIVE=0 # stay in preview\n'
                            'RECYCLER_DB="a path with spaces.sqlite3"\n')
            with patch.dict(os.environ, {'MICROBLOG_TOKEN': 'explicit-export'}, clear=True):
                app.load_env(path)
                self.assertEqual(os.environ['RECYCLER_ADMIN_TOKEN'], 'fixture-dashboard-access-key')
                self.assertEqual(os.environ['MICROBLOG_TOKEN'], 'explicit-export')
                self.assertEqual(os.environ['RECYCLER_LIVE'], '0')
                self.assertEqual(os.environ['RECYCLER_DB'], 'a path with spaces.sqlite3')

    def test_malformed_env_reports_line_number_without_disclosing_secrets(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / '.env'
            path.write_text('MICROBLOG_TOKEN="secret-not-closed\n')
            with self.assertRaises(ValueError) as error:
                app.load_env(path)
            self.assertIn('line 1', str(error.exception))
            self.assertNotIn('secret-not-closed', str(error.exception))


class BackupTests(unittest.TestCase):
    def test_backup_preserves_state_and_history_and_prunes_only_its_own_snapshots(self):
        spec = importlib.util.spec_from_file_location('recycler_backup', Path(app.__file__).with_name('backup.py'))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            store = app.Store(root / 'recycler.sqlite3')
            store.import_articles([{'url': URL, 'title': 'An article', 'date': '2020-01-01'}])
            with store.connect() as db:
                db.execute("INSERT INTO attempts(slot,article_id,created,status,content) VALUES ('2026-10-13',1,?,'accepted','copy')", (NOW.isoformat(),))
            folder = root / 'backups'
            folder.mkdir()
            unrelated = folder / 'keep-this-file.sqlite3'
            unrelated.write_text('preserve')
            for _ in range(3):
                snapshot = module.backup(store.path, folder, keep=2)
            with app.sqlite3.connect(snapshot) as db:
                self.assertEqual(db.execute('SELECT url FROM articles').fetchone()[0], URL)
                self.assertEqual(db.execute('SELECT status FROM attempts').fetchone()[0], 'accepted')
            self.assertEqual(len(list(folder.glob('recycler-*.sqlite3'))), 2)
            self.assertEqual(unrelated.read_text(), 'preserve')
            self.assertEqual(snapshot.stat().st_mode & 0o777, 0o600)
