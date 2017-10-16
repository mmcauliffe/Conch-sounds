import os

from ..praat import PraatAnalysisFunction


class PraatFormantTrackFunction(PraatAnalysisFunction):
    def __init__(self, praat_path=None, num_formants=5, max_freq=5000,
                 time_step=0.01, win_len=0.025):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        script = os.path.join(script_dir, 'formants.praat')
        arguments = [num_formants, max_freq, time_step, win_len]
        super(PraatFormantTrackFunction, self).__init__(script, praat_path=praat_path, arguments=arguments)
