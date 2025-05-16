from .functions import BaseAnalysisFunction
import subprocess
from praatio import textgrid
import os
import tempfile


def is_autovot_friendly_file(sound_file):
    rate = subprocess.run(["soxi", "-r", sound_file], encoding="UTF-8", stdout=subprocess.PIPE).stdout
    if int(rate) != 16000:
        return False

    channels = subprocess.run(["soxi", "-c", sound_file], encoding="UTF-8", stdout=subprocess.PIPE).stdout
    if int(channels) != 1:
        return False
    
    precision = subprocess.run(["soxi", "-p", sound_file], encoding="UTF-8", stdout=subprocess.PIPE).stdout
    if int(precision) != 16:
        return False
    
    return True

def resample_for_autovot(soundfile, tmpdir):
    output_file = os.path.join(tmpdir, "sound_file.wav")
    subprocess.call(["sox", soundfile, "-c", "1", "-r", "16000", "-b", "16", output_file])
    return output_file
    

class MeasureVOTPretrained(object):
    def __init__(self, classifier_to_use=None, min_vot_length=15, max_vot_length=250, window_max=30, window_min=30, debug=False):
        if classifier_to_use is None:
            raise ValueError("There must be a classifier to run AutoVOT")
        else:
            self.classifier_to_use = classifier_to_use
        self.min_vot_length = min_vot_length
        self.max_vot_length = max_vot_length
        self.debug = debug
        self.window_max = window_max
        self.window_min = window_min

    def __call__(self, segment):
        file_path = os.path.expanduser(segment["file_path"])
        begin = segment["begin"]
        end = segment["end"]
        vot_marks = sorted(segment["vot_marks"], key=lambda x: x[0])
        grid = textgrid.Textgrid()
        grid.minTimestamp = 0
        grid.maxTimestamp = end
        vots = []
        for vot_begin, vot_end, *extra_data in vot_marks:
            vots.append((vot_begin, vot_end, 'vot'))
        vot_tier = textgrid.IntervalTier('vot', vots, minT=0, maxT=end)
        grid.addTier(vot_tier)
        with tempfile.TemporaryDirectory() as tmpdirname:
            grid_path = "{}/file.TextGrid".format(tmpdirname)
            csv_path = "{}/file.csv".format(tmpdirname)
            wav_filenames = "{}/wavs.txt".format(tmpdirname)
            textgrid_filenames = "{}/textgrids.txt".format(tmpdirname)

            if not is_autovot_friendly_file(file_path):
                file_path = resample_for_autovot(file_path, tmpdirname)

            with open(wav_filenames, 'w') as f:
                f.write("{}\n".format(file_path))

            with open(textgrid_filenames, 'w') as f:
                f.write("{}\n".format(grid_path))

            grid.save(grid_path, includeBlankSpaces=True, format='long_textgrid')
            
            if self.debug:
                grid.save('/tmp/textgrid_from_conch.csv', includeBlankSpaces=True, format='long_textgrid')
                with open('/tmp/alt_wordlist.txt', 'w') as f:
                    f.write("{}\n".format('/tmp/textgrid_from_conch.csv'))
                subprocess.run(["auto_vot_decode.py", wav_filenames, '/tmp/alt_wordlist.txt', self.classifier_to_use, '--vot_tier', 'vot', '--vot_mark', 'vot', "--min_vot_length", str(self.min_vot_length), "--max_vot_length", str(self.max_vot_length), "--window_max", str(self.window_max), "--window_min", str(self.window_min)])
            subprocess.run(["auto_vot_decode.py", wav_filenames, textgrid_filenames, self.classifier_to_use, '--vot_tier', 'vot', '--vot_mark', 'vot', '--csv_file', csv_path, "--min_vot_length", str(self.min_vot_length), "--max_vot_length", str(self.max_vot_length), "--window_max", str(self.window_max), "--window_min", str(self.window_min)])

            return_list = []
            with open(csv_path, "r") as f: 
                f.readline()
                for l, (b, e, *extra_data) in zip(f, vot_marks):
                    _, time, vot, confidence = l.split(',')
                    if "neg 0\n" ==  confidence:
                        confidence = 0
                    return_list.append((float(time), float(vot), float(confidence), *extra_data))
            return return_list

class AutoVOTAnalysisFunction(BaseAnalysisFunction):
    def __init__(self, classifier_to_use=None, min_vot_length=15, max_vot_length=250, window_max=30, window_min=30, debug=False, arguments=None):
        super(AutoVOTAnalysisFunction, self).__init__()
        self._function = MeasureVOTPretrained(classifier_to_use=classifier_to_use, min_vot_length=min_vot_length, max_vot_length=max_vot_length, window_max=window_max, window_min=window_min, debug=debug)
        self.requires_file = True
        self.uses_segments = True
        self.requires_segment_as_arg = True
