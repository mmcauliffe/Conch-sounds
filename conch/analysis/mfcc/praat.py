import os

from ..helper import freq_to_mel

from ..praat import PraatAnalysisFunction


class PraatMfccFunction(PraatAnalysisFunction):
    def __init__(self, praat_path=None, win_len=0.025, time_step=0.01, min_freq=80, max_freq=7800,
                 num_filters=26, num_coeffs=13, use_power=True, deltas=False):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        script = os.path.join(script_dir, 'mfcc.praat')
        arguments = [num_coeffs, win_len, time_step, freq_to_mel(max_freq)]
        super(PraatMfccFunction, self).__init__(script, praat_path=praat_path, arguments=arguments)
