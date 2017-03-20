import numpy as np

from .base import Representation
from acousticsim.exceptions import AcousticSimError
from acousticsim.analysis.specgram import file_to_powerspec

class Spectrogram(Representation):
    def __init__(self, file_path, min_freq, max_freq, win_len, time_step, data=None, attributes=None):
        Representation.__init__(self,file_path, data=data, attributes=attributes)

        self.min_freq = min_freq
        self.max_freq = max_freq
        self.win_len = win_len
        self.time_step = time_step
        if self.time_step is None:
            steps = 100
            self.time_step = self.duration / steps
        self.pspec = {}
        self.freqs = []

    def powerspec(self):
        times = sorted(self.pspec.keys())
        ex = next(iter(self.pspec.values()))
        try:
            frame_len = len(ex)
        except ValueError:
            frame_len = 1

        output = np.zeros((len(times),frame_len))
        for i, t in enumerate(times):
            output[i, :] = self.pspec[t]
        return output

    def process(self, algorithm='as', reset=False):

        if algorithm not in ['as']:
            raise AcousticSimError('Spectrogram algorithm must be one of: as')
        if reset:
            self.data = {}
        if self.data:
            raise AcousticSimError('Data already exists for this representation, use reset=True to generate new data.')

        self.pspec = file_to_powerspec(self.file_path, self.win_len, self.time_step)
        for k in self.pspec.keys():
            nfft = (len(self.pspec[k])-1) * 2
            self.data[k] = 10 * np.log10(self.pspec[k] + np.spacing(1))

        self.freqs = (self.sr / nfft) * np.arange((nfft/2) + 1)

