import os

from ..praat import PraatAnalysisFunction
from ..functions import BaseAnalysisFunction


class PraatIntensityTrackFunction(BaseAnalysisFunction):
    def __init__(self, praat_path=None, time_step=0.01):
        super(PraatIntensityTrackFunction, self).__init__()
        self.requires_file = True
        script_dir = os.path.dirname(os.path.abspath(__file__))
        script = os.path.join(script_dir, 'intensity.praat')
        arguments = [time_step]
        self._function = PraatAnalysisFunction(script, praat_path=praat_path, arguments=arguments)
