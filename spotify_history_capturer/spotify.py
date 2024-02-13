from io import StringIO
from typing import Iterable
import urllib.request
import urllib.parse
import random
import sys
import string

CLIENT_ID = ...
CLIENT_SECRET = ...

URL_SPOTIFY_ACCOUNT = 'accounts.spotify.com'

def generate_state_string(length: int):
    s = StringIO()
    for i in range(length):
        s.write(chr(random.randint(1, 127)))
    return s.getvalue()

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
    
