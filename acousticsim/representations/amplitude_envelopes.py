import numpy as np

from acousticsim.representations.base import Representation
from ..analysis.amplitude_envelopes import file_to_amplitude_envelopes

from acousticsim.exceptions import AcousticSimError


class Envelopes(Representation):
    """Generate amplitude envelopes from a full path to a .wav, following
    Lewandowski (2012).

    Parameters
    ----------
    file_path : str
        Full path to .wav file to process.
    num_bands : int
        Number of frequency bands to use.
    min_freq : int
        Minimum frequency in Hertz
    max_freq : int
        Maximum frequency in Hertz

    """

    def __init__(self, file_path, num_bands, min_freq, max_freq, data=None, attributes=None):
        Representation.__init__(self, file_path, data, attributes)

        self.num_bands = num_bands
        self.min_freq = min_freq
        self.max_freq = max_freq

    def window(self, win_len, time_step):
        if self.is_windowed:
            return
        nperseg = int(win_len * self.sr)
        if nperseg % 2 != 0:
            nperseg -= 1
        nperstep = int(time_step * self.sr)
        halfperseg = int(nperseg/2)

        print(nperseg, halfperseg)
        num_samps, num_bands = self.shape

        indices = np.arange(halfperseg, num_samps - halfperseg + 1, nperstep)
        num_frames = len(indices)
        print(indices)
        new_rep = {}
        for i in range(num_frames):
            print(indices[i])
            time_key = indices[i]/self.sr
            rep_line = list()
            print(indices[i] - halfperseg, indices[i] + halfperseg)
            array = self[indices[i] - halfperseg, indices[i] + halfperseg]
            print(array.shape)
            for b in range(num_bands):
                rep_line.append(sum(array[:, b]))
            new_rep[time_key] = rep_line
        self.data = new_rep
        self.is_windowed = True

    def process(self, reset=False):
        if reset:
            self.data = {}
        if self.data:
            raise AcousticSimError('Data already exists for this representation, use reset=True to generate new data.')
        self.data = file_to_amplitude_envelopes(self.file_path, self.num_bands, self.min_freq, self.max_freq)
