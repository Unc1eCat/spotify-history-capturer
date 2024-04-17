from collections import namedtuple
from datetime import datetime
from typing import Collection, Sequence

from spotify_history_capturer.spotify.downloaded_data import EndsongItem


TimePeriod = namedtuple('TimePeriod', 'start end')


class Analysis:
    ''' Base class for classes that encapsulate a process of turning a collection of endsong entries into a playlist. See `spotify_history_capturer.spotify.downloaded_data` 
     for classes used for input. '''

    def __init__(self, parameters, period_start: datetime, period_end: datetime, result_length: int, streaming_history: Collection[EndsongItem]):
        self._parameters = parameters
        self._streaming_history = streaming_history
        self._time_period = TimePeriod(period_start, period_end)
        self._result_length = result_length

    ### PUBLIC FACING ###
    @property
    def parameters(self):
        return self._parameters

    @property
    def time_period(self):
        return self._time_period

    @property
    def streaming_history(self):
        return list(self._streaming_history)
    
    @property
    def result_length(self):
        return self._result_length

    @property
    def result(self):
        try:
            return self._result
        except AttributeError as e:
            raise ValueError('You must call "run" method of an Analysis object before trying to get its result.')

    def run(self):
        assert not hasattr(self, '_result'), 'Running an analysis object more than once is not allowed'
        self._result = self.calculation()

    ### TO OVERRIDE ###
    def calculation(self) -> Sequence[str]:
        raise NotImplementedError

