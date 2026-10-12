import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('rendered', Path(__file__).resolve().parents[1] / 'scripts/check-rendered-site.py')
rendered = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rendered)

class RenderedSiteTests(unittest.TestCase):
    def test_source_file_does_not_make_a_url_public(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'public'
            root.mkdir()
            (Path(tmp) / 'draft.md').write_text('draft: true')
            (root / 'index.html').write_text('<a href="/draft/">Draft</a><a href="/old-slug/">Old</a>')
            self.assertEqual(len(rendered.check(root)), 2)

    def test_rendered_alias_relative_asset_and_feed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'index.html').write_text('<a href="/alias/">Alias</a>')
            (root / 'alias').mkdir()
            (root / 'alias/index.html').write_text('<img src="../photo.png" alt=""><a href="/?q=test#top">Home</a>')
            (root / 'photo.png').write_bytes(b'fixture')
            (root / 'feed.json').write_text('{"items": []}')
            self.assertEqual(rendered.check(root), [])
            (root / 'feed.json').write_text('{"items":')
            self.assertTrue(rendered.check(root))

    def test_duplicate_social_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'index.html').write_text('<meta property="og:title" content="A"><meta property="og:title" content="B">')
            self.assertIn('duplicate og:title', rendered.check(root)[0])
