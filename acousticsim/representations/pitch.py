
from acousticsim.representations.base import Representation

from .gammatone import to_gammatone

class Pitch(Representation):
    def __init__(self, filepath, time_step, freq_lims, attributes=None):
        Representation.__init__(self,filepath, freq_lims, attributes)
        self._time_step = time_step


    def is_voiced(self, time):
        if self[time] is None:
            return False
        return True

def to_pitch_zcd(gt):
    import matplotlib.pyplot as plt
    print(gt.shape)
    nsamps = gt.shape[0]
    nbands = get.shape[1]
    for i in range(1,nsamps-1):
        pass
    plt.plot(gt)
    plt.show()
