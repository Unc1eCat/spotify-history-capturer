from dataclasses import dataclass
from io import StringIO
from typing import Iterable
import urllib.request
import urllib.parse
import base64
import json
import random
import sys
import string
from datetime import timedelta
from uu import encode

CLIENT_ID = ...
CLIENT_SECRET = ...

URL_SPOTIFY_ACCOUNT = 'accounts.spotify.com'


# TODO: Make correct state implementation (e.g. storing it in a session)
STATE_STRING_CHARS = string.ascii_letters + string.digits

@dataclass()
class _TokenExchangeResponse:
    access_token: str
    token_type: str
    scope: list['str']
    expires_in: timedelta
    refresh_token: str

    @classmethod 
    def fromDict(cls, d: dict['str']):
        d['expires_in'] = timedelta(seconds=d['expires_in'])
        d['scope'] = d['scope'].split(' ')
        return _TokenExchangeResponse(**d)


def generate_state_string(length: int):
    return ''.join(random.choices(STATE_STRING_CHARS, k=length))


def create_authorization_url(redirect_uri: str, scope: Iterable['str'] | str):
    if isinstance(scope, Iterable):
        scope = ' '.join(scope)
    qs = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': redirect_uri,
        'state': generate_state_string(16),
        'scope': scope
    }
    return f'https://{URL_SPOTIFY_ACCOUNT}/authorize?{urllib.parse.urlencode(qs)}'


def exchange_code_for_token(code: str, redirect_uri: str):
    data = {'code': code.encode('ascii'),
            'grant_type': b'authorization_code',
            'redirect_uri': redirect_uri.encode('ascii')}
    req = urllib.request.Request(url=f'https://{URL_SPOTIFY_ACCOUNT}/api/token', data=urllib.parse.urlencode(data).encode('ascii'), method='POST')
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')
    req.add_header('Authorization', 'Basic ' + base64.b64encode((CLIENT_ID + ':' + CLIENT_SECRET).encode('ascii')).decode('ascii'))
    with urllib.request.urlopen(req) as res:
        return _TokenExchangeResponse.fromDict(json.loads(res.read().decode('ascii')))

        