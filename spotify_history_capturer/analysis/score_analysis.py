from dataclasses import dataclass
from datetime import datetime
from functools import partial, reduce
from heapq import nlargest
from itertools import accumulate
import operator
from typing import Callable, Collection, Sequence
from spotify_history_capturer.spotify.downloaded_data import EndsongItem
from .base import Analysis, TimePeriod

StreamScoreFunction = Callable[[TimePeriod, EndsongItem], float]

@dataclass(frozen=True)
class ScoreAnalysisParameters:
    stream_score_function: StreamScoreFunction


class ScoreAnalysis(Analysis):
    ''' Each stream (endsong item) is passed through a function of the stream and the time period, the function returns a number, score, representing 
     how the stream affects the likeliness of its track's inclusion into the resulting playlist. For each track the average of its streams' scores is 
     calculated, the track score. Tracks with top score are included into the playlist. '''
    
    def __init__(self, parameters: ScoreAnalysisParameters, period_start: datetime, period_end: datetime, result_length: int, streaming_history: Collection[EndsongItem]):
        super().__init__(parameters, period_start, period_end, result_length, streaming_history) 

    
    def calculation(self):
        func = partial(self.parameters.stream_score_function, self.time_period)
        track_score_count = {}
        for i in self.streaming_history:
            v = track_score_count.setdefault(i.track_spotify_uri, [0, 0])
            v[0] += func(i)
            v[1] += 1
        for k, v in track_score_count.items():
            track_score_count[k] = v[0] / v[1]
        return list(map(operator.itemgetter(0), nlargest(self.result_length, track_score_count.items(), operator.itemgetter(1))))


def square(tp: TimePeriod, endsong: EndsongItem):
    return 2 if tp.start < endsong.ended_at < tp.end else -1
