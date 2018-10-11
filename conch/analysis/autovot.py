from .functions import BaseAnalysisFunction
import wave
import subprocess
import textgrid 
import os
import tempfile
from shutil import copyfile

class MeasureVOTPretrained(object):
    def __init__(self, autovot_binaries_path=None, classifier_to_use=None, min_vot_length=15, max_vot_length=250, window_max=30, window_min=30):
        if autovot_binaries_path is None:
            self.autovot_binaries_path = '/home/michael/Honours-Thesis/autovot/autovot/bin/auto_vot_decode.py'
        else:
            self.autovot_binaries_path = autovot_binaries_path
        if classifier_to_use is None:
            self.classifier_to_use = '/home/michael/Honours-Thesis/autovot/experiments/models/bb_jasa.classifier'
        else:
            self.classifier_to_use = classifier_to_use
        self.min_vot_length = min_vot_length
        self.max_vot_length = max_vot_length
        self.window_max = window_max
        self.window_min = window_min

    def __call__(self, segment):
        file_path = segment["file_path"]
        begin = segment["begin"]
        end = segment["end"]
        vot_marks = sorted(segment["vot_marks"], key=lambda x: x[0])
        grid = textgrid.TextGrid(maxTime=end)
        vot_tier = textgrid.IntervalTier(name='vot', maxTime=end)
        for vot_begin, vot_end, *extra_data in vot_marks:
            vot_tier.add(vot_begin, vot_end, 'vot')
        grid.append(vot_tier)
        with tempfile.TemporaryDirectory() as tmpdirname:
            grid_path = "{}/file.TextGrid".format(tmpdirname)
            csv_path = "{}/file.csv".format(tmpdirname)
            wav_filenames = "{}/wavs.txt".format(tmpdirname)
            textgrid_filenames = "{}/textgrids.txt".format(tmpdirname)

            with open(wav_filenames, 'w') as f:
                f.write("{}\n".format(file_path))

            with open(textgrid_filenames, 'w') as f:
                f.write("{}\n".format(grid_path))

            grid.write(grid_path)
            #TODO: default window size to 30 also let it be changed. 
            #Args: are window_min and window_max
            subprocess.run([self.autovot_binaries_path, wav_filenames, textgrid_filenames, self.classifier_to_use, '--vot_tier', 'vot', '--vot_mark', 'vot', '--csv_file', csv_path, "--min_vot_length", str(self.min_vot_length), "--max_vot_length", str(self.max_vot_length), "--window_max", str(self.window_max), "--window_min", str(self.window_min)])

            return_list = []
            copyfile(csv_path, "/tmp/vot.csv")
            with open(csv_path, "r") as f: 
                f.readline()
                for l, (b, e, *extra_data) in zip(f, vot_marks):
                    _, time, vot, confidence = l.split(',')
                    return_list.append((float(time), float(vot), *extra_data))
            return return_list

class AutoVOTAnalysisFunction(BaseAnalysisFunction):
    def __init__(self, autovot_binaries_path=None, classifier_to_use=None, min_vot_length=15, max_vot_length=250, window_max=30, window_min=30, arguments=None):
        super(AutoVOTAnalysisFunction, self).__init__()
        self._function = MeasureVOTPretrained(autovot_binaries_path=autovot_binaries_path, classifier_to_use=classifier_to_use, min_vot_length=min_vot_length, max_vot_length=max_vot_length, window_max=window_max, window_min=window_min)
        self.requires_file = True
        self.uses_segments = True
        self.requires_segment_as_arg = True
