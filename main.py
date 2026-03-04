import json
import os
import subprocess
import tempfile
import threading
import tomllib
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import webview

CONFIG_PATH = Path.home() / '.config' / 'pychemy' / 'config.toml'

DEFAULTS = {
    'api_key': '',
    'username': '',
    'query': '',
    'categories': '111',
    'purity': '100',
}


def load_config():
    if not CONFIG_PATH.exists():
        return DEFAULTS.copy()
    try:
        with open(CONFIG_PATH, 'rb') as f:
            data = tomllib.load(f)
        return {**DEFAULTS, **data}
    except Exception as e:
        print(f'Warning: could not read config ({CONFIG_PATH}): {e}')
        return DEFAULTS.copy()


class WallhavenAPI:
    def __init__(self, config):
        self.config = config

    def get_config(self):
        return self.config

    def close(self):
        os._exit(0)

    def run_script(self, url):
        script = self.config.get('script', '')
        if not script:
            return
        threading.Thread(target=self._download_and_run, args=(script, url), daemon=True).start()

    def _download_and_run(self, script, url):
        ext = Path(urllib.parse.urlparse(url).path).suffix or '.jpg'
        try:
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'Pychemy/1.0')
            with urllib.request.urlopen(req, timeout=30) as resp:
                with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as f:
                    f.write(resp.read())
                    tmp_path = f.name
            subprocess.Popen([script, tmp_path])
        except Exception as e:
            print(f'run_script error: {e}')

    def _fetch(self, url, api_key):
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Pychemy/1.0 (Wallhaven Gallery Desktop App)')
        if api_key:
            req.add_header('X-API-Key', api_key)
        with urllib.request.urlopen(req, timeout=15) as response:
            return json.loads(response.read().decode('utf-8'))

    def get_collections(self, username, api_key):
        try:
            data = self._fetch(f'https://wallhaven.cc/api/v1/collections/{username}', api_key)
            return {'success': True, 'data': data.get('data', [])}
        except urllib.error.HTTPError as e:
            return {'success': False, 'error': f'HTTP {e.code}: {e.reason}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def fetch_collection(self, username, collection_id, page, api_key, purity):
        params = {'page': str(page), 'purity': purity}
        url = (f'https://wallhaven.cc/api/v1/collections/{username}/{collection_id}?'
               + urllib.parse.urlencode(params))
        try:
            data = self._fetch(url, api_key)
            return {'success': True, 'data': data}
        except urllib.error.HTTPError as e:
            return {'success': False, 'error': f'HTTP {e.code}: {e.reason}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def fetch_wallpapers(self, page, api_key, query, categories, purity, sorting='date_added', seed=''):
        params = {
            'sorting': sorting,
            'order': 'desc',
            'page': str(page),
            'categories': categories,
            'purity': purity,
        }
        if query:
            params['q'] = query
        if seed:
            params['seed'] = seed

        url = 'https://wallhaven.cc/api/v1/search?' + urllib.parse.urlencode(params)

        try:
            return {'success': True, 'data': self._fetch(url, api_key)}
        except urllib.error.HTTPError as e:
            return {'success': False, 'error': f'HTTP {e.code}: {e.reason}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}


if __name__ == '__main__':
    config = load_config()
    api = WallhavenAPI(config)
    window = webview.create_window(
        'Wallhaven Gallery',
        'ui.html',
        js_api=api,
        width=1400,
        height=900,
        min_size=(800, 600),
    )
    webview.start()
