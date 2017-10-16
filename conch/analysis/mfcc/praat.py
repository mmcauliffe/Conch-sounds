import os

from ..helper import freq_to_mel

from ..praat import PraatAnalysisFunction


class PraatMfccFunction(PraatAnalysisFunction):
    def __init__(self, praat_path=None, window_length=0.025, time_step=0.01, max_frequency=7800,
                 num_coefficients=13):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        script = os.path.join(script_dir, 'mfcc.praat')
        arguments = [num_coefficients, window_length, time_step, freq_to_mel(max_frequency)]
        super(PraatMfccFunction, self).__init__(script, praat_path=praat_path, arguments=arguments)
