import os

from ..praat import PraatAnalysisFunction


class PraatIntensiyFunction(PraatAnalysisFunction):
    def __init__(self, praat_path=None, time_step=0.01):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        script = os.path.join(script_dir, 'intensity.praat')
        arguments = [time_step]
        super(PraatIntensiyFunction, self).__init__(script, praat_path=praat_path, arguments=arguments)
