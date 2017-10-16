import os

from ..praat import PraatAnalysisFunction


class PraatIntensityTrackFunction(PraatAnalysisFunction):
    def __init__(self, praat_path=None, time_step=0.01):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        script = os.path.join(script_dir, 'intensity.praat')
        arguments = [time_step]
        super(PraatIntensityTrackFunction, self).__init__(script, praat_path, arguments)
