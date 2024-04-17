from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import operator
from typing import Iterable, Mapping, Sequence


class ReasonsTrackSwitched(Enum):
    TRACK_DONE = 'trackdone'
    LOGOUT = 'logout'
    CLICK_ROW = 'clickrow'
    END_PLAY = 'endplay'
    PLAY_BUTTON = 'playbtn'
    FORWARD_BUTTON = 'fwdbtn'
    BACK_BUTTON = 'backbtn'
    REMOTE = 'remote'
    APP_LOAD = 'appload'
    TRACK_ERROR = 'trackerror'
    UNEXPECTED_EXIT_ON_PAUSE = 'unexpected-exit-while-paused'
    UNEXPECTED_EXIT = 'unexpected-exit'
    UNKNOWN = 'unknown'


@dataclass(frozen=True)
class EndsongItem:
    ended_at: datetime
    duration_played: timedelta
    track_name: str
    album_name: str
    artist_name: str
    track_spotify_uri: str
    reason_start: str
    reason_end: str
    shuffle: bool
    connection_country: str
    incognito: bool

    @classmethod
    def from_json_one(cls, json_obj: Mapping):
        try:
            return EndsongItem(
                ended_at=datetime.fromisoformat(json_obj['ts'].rstrip('Z')),
                duration_played=timedelta(milliseconds=json_obj['ms_played']),
                album_name=json_obj['master_metadata_album_album_name'],
                artist_name=json_obj['master_metadata_album_artist_name'],
                track_name=json_obj['master_metadata_track_name'],
                connection_country=json_obj['conn_country'],
                incognito=json_obj['incognito_mode'],
                reason_start=ReasonsTrackSwitched(json_obj['reason_start']),
                reason_end=ReasonsTrackSwitched(json_obj['reason_end']),
                shuffle=json_obj['shuffle'],
                track_spotify_uri=json_obj['spotify_track_uri']
            )
        except KeyError as e:
            if e.args[0] in ('reason_start', 'reason_end'):
                raise NotImplementedError('While parsing EndSongItem from JSON, an unknown track switch reason occurred in the JSON data: %s' % e.args[1])
            else:
                raise e

    @classmethod
    def from_json_many(cls, json_list: Iterable[Mapping]):
        return [EndsongItem.from_json_one(i) for i in json_list]


def merge_endsongs(*endsong_collection: Iterable[EndsongItem]):
    ret = set()
    for i in endsong_collection:
        ret.update(i)
    return ret
