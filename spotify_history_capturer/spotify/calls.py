from dataclasses import dataclass
from io import StringIO
from typing import Callable, Iterable, Set
import urllib.request
import urllib.parse
import urllib.error
import base64
import json
import random
import sys
import string
from datetime import timedelta
from uu import encode
from spotify_history_capturer.spotify import conf

from spotify_history_capturer.spotify.needs_scopes import needs_scope


def set_common_headers(request: urllib.request.Request, access_token: str):
    request.add_header('Authorization', 'Bearer ' + access_token)
    request.add_header('Content-Type', 'application/json')

@needs_scope('playlist-modify-private')
def create_playlist(name: str, user_id: str, track_ids: Iterable[str], access_token: str):
    ''' Creates a playlist filled with given tracks and and having the given name for the given user (base62) '''
    data = {
        'name': name,
        'public': False,
        'collaborative': False,
        'description': ''
    }
    req = urllib.request.Request(f'https://{URL_SPOTIFY_API}/users/{user_id}/playlists', json.dumps(data).encode('utf-8'))
    set_common_headers(req, access_token)
    with urllib.request.urlopen(req) as res:
        return json.loads(res.read())

