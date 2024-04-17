from argparse import ArgumentParser
from collections import namedtuple
from datetime import datetime
from glob import glob
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import sys
from threading import Event
import urllib.parse
import webbrowser
from spotify_history_capturer.analysis.score_analysis import ScoreAnalysis, ScoreAnalysisParameters, square
from spotify_history_capturer.spotify import auth, calls, conf

from spotify_history_capturer.spotify.downloaded_data import EndsongItem


class _AuthHTTPRedirectHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        qs = urllib.parse.parse_qs(urllib.parse.urlsplit(self.path).query)
        if not ('code' in qs and 'state' in qs):
            self.send_response(400, 'Must include "code" and "state" query parameters in the request.')
        self.send_response(100)
        self.end_headers()
        self.server.response_qs = qs
        self.server.shutdown()


def _auth(ns):
    conf.CLIENT_ID = '454156f6b44b4644b7dc79b04232c811'
    conf.CLIENT_SECRET = ...  # If you put a valid client ID and its secret then it will work. Having `conf` in the design allows for configuring at any time
    # from any place.

    s = HTTPServer(('', 3000), _AuthHTTPRedirectHandler)
    redirect_url = f'http://localhost:{s.server_port}'
    state_value = auth.generate_state_value(32)
    auth_url = auth.create_authorization_url(redirect_uri=redirect_url, scope=calls.create_playlist.needed_spotify_scope, state_value=state_value)
    webbrowser.open(auth_url)
    s.serve_forever()
    if s.response_qs['state'] != state_value:
        raise RuntimeError('Redirect state value does not match the original.')
    return auth.exchange_code_for_token(s.response_qs['code'], redirect_url).access_token


def _process(ns):
    source = []
    files = set()
    for i in ns.files:
        files.update(glob(i))
    for i in files:
        with open(i, 'r', encoding='utf-8') as f:
            source.extend(json.load(f))
    endsongs = EndsongItem.from_json_many(source)

    start = datetime.fromisoformat(ns.start)
    end = datetime.fromisoformat(ns.end)

    a = ScoreAnalysis(ScoreAnalysisParameters(square), start, end, ns.length, endsongs)
    a.run()

    calls.create_playlist(f'Era {start.day} %s {start.year} — {end.day} %s {end.year}' % (start.strftime('%b'), end.strftime('%b')), ns.token, track_uris=a.result)


def run():
    parser = ArgumentParser('shc')
    sps = parser.add_subparsers(required=True)

    ap = sps.add_parser('auth')
    ap.set_defaults(func=_auth)

    pp = sps.add_parser('process')
    pp.add_argument('-t', '--token', required=True)
    pp.add_argument('-s', '--start', required=True)
    pp.add_argument('-e', '--end', required=True)
    pp.add_argument('-l', '--length', type=int, default=15)
    pp.add_argument('files', nargs='+')
    pp.set_defaults(func=_process)

    ns = parser.parse_args(sys.argv[1:])
    ns.func(ns)
