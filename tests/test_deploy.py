import os
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/deploy.sh'

class DeployTests(unittest.TestCase):
    def run_wrapper(self, branch='main', verify_status=0):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            log = root / 'calls'
            (root / 'git').write_text('''#!/bin/sh
printf '%s\\n' "$*" >> "$CALL_LOG"
case "$*" in
  'rev-parse --show-toplevel') echo "$FAKE_ROOT";;
  'branch --show-current') echo "$FAKE_BRANCH";;
  'diff --cached --quiet') exit 1;;
esac
''')
            (root / 'npm').write_text('#!/bin/sh\nexit "$VERIFY_STATUS"\n')
            for name in ['git', 'npm']:
                (root / name).chmod(0o755)
            env = dict(os.environ, PATH=str(root)+':'+os.environ['PATH'], CALL_LOG=str(log), FAKE_ROOT=tmp,
                       FAKE_BRANCH=branch, VERIFY_STATUS=str(verify_status))
            result = subprocess.run(['bash', str(SCRIPT), 'Test'], env=env, capture_output=True)
            return result.returncode, log.read_text()

    def test_wrong_branch_never_commits_or_pushes(self):
        code, calls = self.run_wrapper(branch='feature')
        self.assertNotEqual(code, 0)
        self.assertNotIn('commit ', calls)
        self.assertNotIn('push ', calls)

    def test_failed_verification_never_commits_or_pushes(self):
        code, calls = self.run_wrapper(verify_status=1)
        self.assertNotEqual(code, 0)
        self.assertNotIn('commit ', calls)
        self.assertNotIn('push ', calls)
