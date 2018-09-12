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

    def __call__(self, segment):
        file_path = segment["file_path"]
        begin = segment["begin"]
        end = segment["end"]
        vot_marks = segment["vot_marks"]
        grid = textgrid.TextGrid(maxTime=end)
        vot_tier = textgrid.IntervalTier(name="vot", maxTime=end)
        for (vot_begin, vot_end) in vot_marks:
            vot_tier.add(vot_begin, vot_end, "vot")
        grid.append(vot_tier)


class AutoVOTAnalysisFunction(BaseAnalysisFunction):
    def __init__(self, autovot_binaries_path=None, arguments=None):
        super(AutoVOTAnalysisFunction, self).__init__()
        self._function = MeasureVOTPretrained()
        self.requires_file = True
        self.uses_segments = True
        self.requires_segment_as_arg = True
