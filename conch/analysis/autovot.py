from .functions import BaseAnalysisFunction
import wave
import subprocess
import textgrid 
import os
import tempfile

class MeasureVOTPretrained(object):
    def __init__(self, autovot_binaries_path=None):
        if autovot_binaries_path is None:
            self.autovot_binaries_path = 'auto_vot_train.py'

    def __call__(self, *args, **kwargs):
        file_path, begin, end = args[:3]
        grid = textgrid.TextGrid(maxTime=end)
        vot_tier = textgrid.IntervalTier(name="vot", maxTime=end)
        vot_tier.add(begin, end, "vot")
        grid.append(vot_tier)


class AutoVOTAnalysisFunction(BaseAnalysisFunction):
    def __init__(self, autovot_binaries_path=None, arguments=None):
        super(AutoVOTAnalysisFunction, self).__init__()
        self._function = MeasureVOTPretrained()
        self.requires_file = True
        self.uses_segments = True
