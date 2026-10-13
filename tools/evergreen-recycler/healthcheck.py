#!/usr/bin/env python3
"""Check authenticated access without printing credentials or teaser copy."""
import json
import os
from pathlib import Path
import time
from urllib.error import URLError
from urllib.request import Request, urlopen

from app import load_env


def check():
    load_env(Path(__file__).resolve().parent / '.env')
    token = os.environ.get('RECYCLER_ADMIN_TOKEN', '')
    if not token:
        raise SystemExit('Dashboard key is missing from server configuration.')
    request = Request('http://127.0.0.1:8787/api/state', headers={'Authorization': 'Bearer ' + token})
    for attempt in range(10):
        try:
            with urlopen(request, timeout=5) as response:
                state = json.load(response)
            return {'healthy': True, 'live': state['live'], 'paused': state['settings']['paused'],
                    'articles': len(state['articles']),
                    'approved': sum(bool(row['enabled']) for row in state['articles']),
                    'attempts_shown': len(state['history'])}
        except (URLError, OSError):
            if attempt == 9:
                raise SystemExit('Authenticated dashboard check failed. Inspect the service journal.') from None
            time.sleep(0.3)


if __name__ == '__main__':
    print(json.dumps(check()))
