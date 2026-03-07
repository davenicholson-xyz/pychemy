import argparse
import json
import os
import sys
import shutil
import webbrowser
import subprocess
import threading
import tomllib
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

try:
    from PyQt6.QtWidgets import QApplication as _QApp
except ImportError:
    try:
        from PyQt5.QtWidgets import QApplication as _QApp
    except ImportError:
        _QApp = None
if _QApp is not None:
    _qt_app = _QApp.instance() or _QApp(sys.argv)
    _qt_app.setApplicationName('pyvista')

import webview

CONFIG_PATH = Path.home() / '.config' / 'pyvista' / 'config.toml'

DEFAULTS = {
    'api_key': '',
    'username': '',
    'query': '',
    'categories': '111',
    'purity': '100',
    'thumb-size': 'm',
    'min-resolution': '',
    'close-on-select': False,
}


def load_config():
    if not CONFIG_PATH.exists():
        return DEFAULTS.copy()
    try:
        with open(CONFIG_PATH, 'rb') as f:
            data = tomllib.load(f)
        return {**DEFAULTS, **data}
    except Exception as e:
        return DEFAULTS.copy()


class WallhavenAPI:
    def __init__(self, config):
        self.config = config

    def get_config(self):
        return self.config

    def open_browser(self, url):
        webbrowser.open(url)

    def close(self):
        webview.windows[0].destroy()

    def run_script(self, url):
        script = self.config.get('script', '')
        if not script:
            return
        threading.Thread(target=self._download_and_run, args=(script, url), daemon=True).start()

    def _download_and_run(self, script, url):
        parsed = urllib.parse.urlparse(url)
        filename = Path(parsed.path).name or 'wallpaper.jpg'
        cache_dir = Path.home() / '.cache' / 'pyvista'
        cache_dir.mkdir(parents=True, exist_ok=True)
        dest = cache_dir / filename
        try:
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'Pyvista/1.0')
            with urllib.request.urlopen(req, timeout=30) as resp:
                with open(dest, 'wb') as f:
                    shutil.copyfileobj(resp, f)
            subprocess.run([script, str(dest)])
            if self.config.get('output'):
                print(str(dest), flush=True)
            if self.config.get('close-on-select'):
                webview.windows[0].destroy()
        except Exception:
            pass

    def _fetch(self, url, api_key):
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Pyvista/1.0 (Wallhaven Gallery Desktop App)')
        if api_key:
            req.add_header('X-API-Key', api_key)
        with urllib.request.urlopen(req, timeout=15) as response:
            return json.loads(response.read().decode('utf-8'))

    def fetch_image(self, url, api_key):
        import base64
        try:
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'Pyvista/1.0')
            if api_key:
                req.add_header('X-API-Key', api_key)
            with urllib.request.urlopen(req, timeout=30) as resp:
                mime = resp.headers.get('Content-Type', 'image/jpeg').split(';')[0]
                data = base64.b64encode(resp.read()).decode('ascii')
            return {'success': True, 'data_url': f'data:{mime};base64,{data}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def fetch_wallpaper(self, wallpaper_id, api_key):
        try:
            data = self._fetch(f'https://wallhaven.cc/api/v1/w/{wallpaper_id}', api_key)
            return {'success': True, 'data': data.get('data', {})}
        except urllib.error.HTTPError as e:
            return {'success': False, 'error': f'HTTP {e.code}: {e.reason}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

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

    def fetch_wallpapers(self, page, api_key, query, categories, purity, sorting='date_added', seed='', atleast=''):
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
        if atleast:
            params['atleast'] = atleast

        url = 'https://wallhaven.cc/api/v1/search?' + urllib.parse.urlencode(params)

        try:
            return {'success': True, 'data': self._fetch(url, api_key)}
        except urllib.error.HTTPError as e:
            return {'success': False, 'error': f'HTTP {e.code}: {e.reason}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}


def parse_args():
    p = argparse.ArgumentParser(description='Pyvista — Wallhaven gallery browser')
    p.add_argument('--api-key',        metavar='KEY',  help='Wallhaven API key')
    p.add_argument('--username',       metavar='USER', help='Wallhaven username')
    p.add_argument('--query',          metavar='Q',    help='Default search query')
    p.add_argument('--categories',     metavar='MASK', help='Category bitmask (e.g. 111)')
    p.add_argument('--purity',         metavar='MASK', help='Purity bitmask (e.g. 100)')
    p.add_argument('--thumb-size',     dest='thumb-size',     metavar='SIZE', choices=['xs', 'sm', 'm', 'l', 'xl'], help='Thumbnail size')
    p.add_argument('--min-resolution', dest='min-resolution', metavar='RES',  help='Minimum resolution (e.g. 1920x1080)')
    p.add_argument('--script',         metavar='PATH', help='Script to run on selected wallpaper')
    p.add_argument('--close-on-select', dest='close-on-select', action='store_true', default=None, help='Close after selecting wallpaper')
    sort_group = p.add_mutually_exclusive_group()
    sort_group.add_argument('--hot',    dest='sorting', action='store_const', const='hot',        help='Start on Hot sorting')
    sort_group.add_argument('--latest', dest='sorting', action='store_const', const='date_added', help='Start on Latest sorting')
    sort_group.add_argument('--top',    dest='sorting', action='store_const', const='toplist',    help='Start on Toplist sorting')
    sort_group.add_argument('--random', dest='sorting', action='store_const', const='random',     help='Start on Random sorting')
    p.add_argument('--search',     dest='query',      metavar='QUERY', help='Start with this search query')
    p.add_argument('--collection', dest='collection', metavar='NAME',  help='Start with this collection open')
    p.add_argument('--output', action='store_true', default=None, help='Print wallpaper filepath to stdout after setting')
    return {k: v for k, v in vars(p.parse_args()).items() if v is not None}


if __name__ == '__main__':
    # Redirect fd 2 (stderr) to /dev/null to suppress Qt/WebEngine noise.
    # On an unhandled crash, restore it so the traceback is visible.
    _real_stderr_fd = os.dup(2)
    _devnull = os.open(os.devnull, os.O_WRONLY)
    os.dup2(_devnull, 2)
    os.close(_devnull)
    _real_stderr = os.fdopen(_real_stderr_fd, 'w')

    def _excepthook(exc_type, exc_value, exc_tb):
        import traceback
        os.dup2(_real_stderr.fileno(), 2)
        sys.stderr = _real_stderr
        traceback.print_exception(exc_type, exc_value, exc_tb)

    sys.excepthook = _excepthook

    sys.argv[0] = 'pyvista'
    config = {**load_config(), **parse_args()}
    api = WallhavenAPI(config)
    ui_html = str(Path(__file__).parent / 'ui.html')
    window = webview.create_window(
        'Wallhaven Gallery',
        ui_html,
        js_api=api,
        width=1400,
        height=900,
        min_size=(800, 600),
    )
    webview.start()
    os._exit(0)
