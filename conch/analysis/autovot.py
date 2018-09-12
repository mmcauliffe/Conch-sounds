from .functions import BaseAnalysisFunction
import wave
import subprocess
import textgrid 
import os
import tempfile

class MeasureVOTPretrained(object):
    def __init__(self, vot_markings, autovot_binaries_path=None):
        '''Creates function to analyse VOT
           vot_markings is a dictionary of lists, where the keys
           are paths to sound files, which have a corresponding
           value of a list of tuples marking the beginning and 
           end of each VOT mark
        '''
        self.vot_markings = vot_markings
        if autovot_binaries_path is None:
            self.autovot_binaries_path = 'auto_vot_train.py'

    def __call__(self, *args, **kwargs):
        with wave.open(path,'r') as f: 
            frames = f.getnframes()
            rate = f.getframerate()
            length = frames / float(rate)
        grid = textgrid.TextGrid(maxTime=length)
        vot_tier = textgrid.IntervalTier(name="vot", maxTime=length)
        vot_tier.add(begin, end, "vot")
        grid.append(vot_tier)


class AutoVOTAnalysisFunction(BaseAnalysisFunction):
    def __init__(self, vot_markings, autovot_binaries_path=None, arguments=None):
        super(AutoVOTAnalysisFunction, self).__init__()
        self._function = MeasureVOTPretrained(vot_markings)
        self.requires_file = True
        self.uses_segments = False
