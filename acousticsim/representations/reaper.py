import subprocess
import os
import shutil
from scipy.io import wavfile
from tempfile import TemporaryDirectory, NamedTemporaryFile

from acousticsim.representations.pitch import Pitch

def file_to_pitch_reaper(filepath, reaper = None, time_step = None,
                                freq_lims = None, attributes = None):
    if reaper is None:
        reaper = 'reaper'

    directory = os.path.dirname(filepath)
    base = os.path.basename(filepath)
    name = os.path.splitext(base)[0]
    output_path = os.path.join(directory, name + '.f0')
    com = [reaper, '-i', filepath, '-f', output_path, '-a']
    if time_step is not None:
        com.extend(['-e', str(time_step)])
    if freq_lims is not None:
        com.extend(['-m', str(freq_lims[0]), '-x', str(freq_lims[1])])
    with open(os.devnull, 'w') as devnull:
        subprocess.call(com, stdout=devnull, stderr=devnull)
    output = Pitch(filepath, time_step, freq_lims, attributes = attributes)
    output.rep = parse_output(output_path)
    os.remove(output_path)
    return output

def signal_to_pitch_reaper(signal, sr, reaper = None, time_step = None,
                                freq_lims = None, attributes = None,
                                begin = None, padding = None):
    if reaper is None:
        reaper = 'reaper'
    with TemporaryDirectory(prefix = 'acousticsim') as tempdir:
        t_wav = NamedTemporaryFile(dir = tempdir, delete = False, suffix = '.wav')
        signal *= 32768
        wavfile.write(t_wav, sr, signal.astype('int16'))
        t_wav.close()
        output = file_to_pitch_reaper(t_wav.name, reaper, time_step, freq_lims,
                                        attributes)
    duration = signal.shape[0] / sr
    if begin is not None:
        if padding is not None:
            begin -= padding
        real_output = {}
        for k,v in output.items():
            if padding is not None and (k < padding or k > duration - padding):
                continue
            real_output[k+begin] = v
        return real_output
    return output

def parse_output(output_file):
    output = {}
    with open(output_file, 'r') as f:
        body = False
        for line in f:
            line = line.strip()
            if line == 'EST_Header_End':
                body = True
                continue
            if not body:
                continue
            time, voiced, pitch = line.split(' ')
            output[float(time)] = float(pitch)
    return output
