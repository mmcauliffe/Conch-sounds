from acousticsim.representations.base import Representation

class Pitch(Representation):
    def __init__(self, filepath, time_step, freq_lims,
                window_shape = 'gaussian', attributes=None):
        Representation.__init__(self,filepath, freq_lims, attributes)
        self._time_step = time_step

    def is_voiced(self, time):
        if self[time] is None:
            return False
        return True