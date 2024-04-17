from collections import namedtuple
from typing import Iterable
import urllib.request
import urllib.parse
import urllib.error
import json
from datetime import date, datetime, timedelta, timezone
from spotify_history_capturer.spotify import conf

from spotify_history_capturer.spotify.needs_scopes import needs_scope


recentlyPlayedItem = namedtuple('RecentlyPlayedItem', 'track_id played_at')


def set_common_headers(request: urllib.request.Request, access_token: str):
    request.add_header('Authorization', 'Bearer ' + access_token)
    request.add_header('Content-Type', 'application/json')


@needs_scope('playlist-modify-public', 'playlist-modify-private')
def create_playlist(name: str, access_token: str, track_uris: Iterable[str] = [], user_id: str | None = None):
    ''' Creates a playlist filled with given tracks and and having the given name for the given user.
    :return: Spotify ID of the created playlist. '''
    user_id = user_id or get_current_user(access_token)['id']
    data = {
        'name': name,
        'public': False,
        'collaborative': False,
        'description': ''
    }
    req = urllib.request.Request(f'https://{conf.URL_SPOTIFY_API}/users/{user_id}/playlists', json.dumps(data)
                                 .encode('utf-8'), method='POST')
    set_common_headers(req, access_token)
    with urllib.request.urlopen(req) as res:
        playlist_id = json.loads(res.read())['id']

    if len(track_uris) > 0:
        data = {
            'uris': track_uris
        }
        req = urllib.request.Request(f'https://{conf.URL_SPOTIFY_API}/playlists/{playlist_id}/tracks', json.dumps(data).encode('ascii'), method='POST')
        set_common_headers(req, access_token)
        urllib.request.urlopen(req)

    return playlist_id


@needs_scope('user-read-recently-played')
def fetch_recent_plays(access_token: str, limit: int = 50):
    qs = urllib.parse.urlencode({'limit': limit})
    req = urllib.request.Request(f'https://{conf.URL_SPOTIFY_API}/me/player/recently-played?{qs}')
    set_common_headers(req, access_token=access_token)
    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read())
        return [recentlyPlayedItem(i['track']['id'], datetime.fromisoformat(i['played_at'].rstrip('Z')).replace(tzinfo=timezone(timedelta(), 'UTC'))) for
                i in data['items']]

@needs_scope('user-read-private', 'user-read-email')
def get_current_user(access_token: str):
    req = urllib.request.Request('https://' + conf.URL_SPOTIFY_API + '/me')
    set_common_headers(req, access_token=access_token)
    with urllib.request.urlopen(req) as res:
        return json.loads(res.read())
