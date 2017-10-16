import os

from ..praat import PraatAnalysisFunction
from ..functions import BaseAnalysisFunction


class PraatFormantTrackFunction(BaseAnalysisFunction):
    def __init__(self, praat_path=None, num_formants=5, max_frequency=5000,
                 time_step=0.01, window_length=0.025):
        super(PraatFormantTrackFunction, self).__init__()
        self.requires_file = True
        script_dir = os.path.dirname(os.path.abspath(__file__))
        script = os.path.join(script_dir, 'formants.praat')
        arguments = [time_step, window_length, num_formants, max_frequency]
        self._function = PraatAnalysisFunction(script, praat_path=praat_path, arguments=arguments)
