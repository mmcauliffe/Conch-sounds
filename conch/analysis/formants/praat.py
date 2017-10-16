import os

from ..praat import PraatAnalysisFunction


class PraatFormantTrackFunction(PraatAnalysisFunction):
    def __init__(self, praat_path=None, num_formants=5, max_frequency=5000,
                 time_step=0.01, window_length=0.025):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        script = os.path.join(script_dir, 'formants.praat')
        arguments = [time_step, window_length, num_formants, max_frequency]
        super(PraatFormantTrackFunction, self).__init__(script, praat_path, arguments)
