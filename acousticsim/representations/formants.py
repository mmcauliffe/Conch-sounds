
import numpy as np

from .base import Representation

from acousticsim.exceptions import AcousticSimError
from acousticsim.analysis.formants import file_to_formants, file_to_formants_praat


class Formants(Representation):
    def __init__(self, file_path, num_formants, max_freq, win_len,
                 time_step, data=None, attributes=None):
        Representation.__init__(self, file_path, data=data, attributes=attributes)

        self.num_formants = num_formants
        self.max_freq = max_freq
        self.win_len = win_len
        self.time_step = time_step

    def __getitem__(self, key):
        item = Representation.__getitem__(self, key)
        return np.array([x[0] for x in item], dtype='float32')

    def to_array(self, value='formant'):
        times = sorted(self.data.keys())
        ex = next(iter(self.data.values()))
        try:
            frame_len = len(ex)
        except ValueError:
            frame_len = 1

        output = np.zeros((len(times),frame_len))
        for i, t in enumerate(times):
            if value == 'formant':
                output[i, :] = [x[0] for x in self.data[t]]
            elif value == 'bandwidth':
                output[i, :] = [x[1] for x in self.data[t]]
        return output

    def process(self, algorithm='lpc', executable_path=None, reset=False):
        if algorithm not in ['lpc', 'praat']:
            raise AcousticSimError('Formant algorithm must be one of: lpc, praat')
        if reset:
            self.data = {}
        if self.data:
            raise AcousticSimError('Data already exists for this representation, use reset=True to generate new data.')
        if algorithm == 'lpc':
            data = file_to_formants(self.file_path, self.num_formants, self.max_freq, self.win_len, self.time_step)
        else:
            data = file_to_formants_praat(self.file_path, executable_path, self.num_formants, self.max_freq,
                                          self.win_len, self.time_step)
        self.data = data
