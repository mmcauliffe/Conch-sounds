
from pyraat import PraatAnalysisFunction as PyraatFunction
from .functions import BaseAnalysisFunction


class PraatAnalysisFunction(BaseAnalysisFunction):
    def __init__(self, praat_script_path, praat_path=None, arguments=None):
        super(PraatAnalysisFunction, self).__init__()
        self._function = PyraatFunction(praat_script_path,praat_path, arguments)
        self.requires_file = True
        self.uses_segments = self._function.uses_long
