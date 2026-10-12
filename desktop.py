#!/usr/bin/env python3
"""Desktop launcher for Product Manager on Windows and Linux."""

from __future__ import annotations

import os
import secrets
import sys
import threading
import webbrowser
from pathlib import Path
from http.server import ThreadingHTTPServer

APP_ROOT = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent))
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from api.app import AppHandler, user_count  # noqa: E402


def main() -> int:
    host = os.environ.get('PRODUCT_MANAGER_HOST', '127.0.0.1')
    port = int(os.environ.get('PRODUCT_MANAGER_PORT', '0'))
    server = ThreadingHTTPServer((host, port), AppHandler)
    browser_host = '127.0.0.1' if host in ('0.0.0.0', '::') else host
    first_setup = user_count() == 0
    if first_setup and not os.environ.get('PRODUCT_MANAGER_SETUP_TOKEN'):
        os.environ['PRODUCT_MANAGER_SETUP_TOKEN'] = secrets.token_urlsafe(32)
    if first_setup:
        setup_token = os.environ['PRODUCT_MANAGER_SETUP_TOKEN']
        url = f'http://{browser_host}:{server.server_port}/login#setup_token={setup_token}'
    else:
        url = f'http://{browser_host}:{server.server_port}/dashboard'
    threading.Timer(0.8, webbrowser.open, args=(url,)).start()
    display_url = f'http://{browser_host}:{server.server_port}/login' if first_setup else url
    print(f'Product Manager em execução em {display_url}. Pressione Ctrl+C para encerrar.')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.shutdown()
        server.server_close()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
