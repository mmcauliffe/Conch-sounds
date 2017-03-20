
from .base import Representation

from acousticsim.exceptions import AcousticSimError
from acousticsim.analysis.mfcc import file_to_mfcc, file_to_mfcc_praat


class Mfcc(Representation):
    """
    Mel frequency cepstrum coefficient representation of a sound.

    Parameters
    ----------
    file_path : str
        Filepath of wav file to process

    min_freq : int
        Minimum frequency in Hertz

    max_freq : int
        Maximum frequency in Hertz

    num_coeffs : int
        Number of cepstrum coefficients

    win_len : float
        Window length in seconds

    time_step : float
        Time step between successive frames

    num_filters : int, defaults to 26
        Number of triangular filters in the filterbank

    use_power : bool, defaults to True
        Flag for keeping first cepstrum coefficient, which corresponds
        to the power in the frame

    deltas : bool, defaults to False
        Flag to calculate the delta coefficients
    """
    _is_windowed = True

    def __init__(self, file_path,  win_len, time_step,  min_freq=80, max_freq=7800,
                 num_filters=26, num_coeffs=13, use_power=True, deltas=False, data=None, attributes=None):
        Representation.__init__(self, file_path, data, attributes)
        self.min_freq = min_freq
        self.max_freq = max_freq
        self.num_coeffs = num_coeffs
        self.ranges = [None] * self.num_coeffs
        self.win_len = win_len
        self.time_step = time_step
        self.num_filters = num_filters
        self.use_power = use_power
        self.deltas = deltas

    def process(self, algorithm='rastamat', executable_path=None, reset=False):
        if algorithm not in ['rastamat', 'praat']:
            raise AcousticSimError('Formant algorithm must be one of: lpc, praat')
        if reset:
            self.data = {}
        if self.data:
            raise AcousticSimError('Data already exists for this representation, use reset=True to generate new data.')
        if algorithm == 'rastamat':
            data = file_to_mfcc(self.file_path,  self.win_len, self.time_step,  self.min_freq, self.max_freq,
                                self.num_filters, self.num_coeffs, self.use_power, self.deltas)
        else:
            data = file_to_mfcc_praat(self.file_path, executable_path, self.win_len, self.time_step,
                                      self.min_freq, self.max_freq,
                                      self.num_filters, self.num_coeffs, self.use_power, self.deltas)
        self.data = data

    def norm_amp(self, new_ranges):
        """
        Normalize the ranges of coefficients to a set of ranges.

        Parameters
        ----------
        new_ranges : list of tuple
            New ranges for each coefficient to normalize to

        """
        for i, r in enumerate(new_ranges):
            new_min, new_max = r
            if self.ranges[i] is None:
                old = [x[i] for x in self.data.values()]
                self.ranges[i] = [min(old), max(old)]
            for k, v in self.data.items():
                normed = (v[i] - self.data[i][0]) / (self.data[i][1] - self.data[i][0])
                self.data[k][i] = (normed * (new_max - new_min)) + new_min
