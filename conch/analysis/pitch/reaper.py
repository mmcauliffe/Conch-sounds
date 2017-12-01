import subprocess
import os
from functools import partial

from ..helper import fix_time_points, ASTemporaryWavFile
from ..functions import BaseAnalysisFunction


def call_reaper(file_path, time_step=0.01, min_pitch=75, max_pitch=600, reaper_path=None):
    directory = os.path.dirname(file_path)
    base = os.path.basename(file_path)
    name = os.path.splitext(base)[0]
    output_path = os.path.join(directory, name + '.f0')
    com = [reaper_path, '-i', file_path, '-f', output_path, '-a']
    if time_step is not None:
        com.extend(['-e', str(time_step)])
    if min_pitch is not None:
        com.extend(['-m', str(min_pitch)])
    if max_pitch is not None:
        com.extend(['-x', str(max_pitch)])
    proc = subprocess.Popen(com, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    output = parse_output(output_path)
    os.remove(output_path)
    return output


def call_reaper_with_pulses(file_path, time_step=0.01, min_pitch=75, max_pitch=600, reaper_path=None):
    directory = os.path.dirname(file_path)
    base = os.path.basename(file_path)
    name = os.path.splitext(base)[0]
    output_path = os.path.join(directory, name + '.f0')
    pm_output_path = os.path.join(directory, name + '.pm')
    com = [reaper_path, '-i', file_path, '-f', output_path, '-p', pm_output_path, '-a']
    if time_step is not None:
        com.extend(['-e', str(time_step)])
    if min_pitch is not None:
        com.extend(['-m', str(min_pitch)])
    if max_pitch is not None:
        com.extend(['-x', str(max_pitch)])
    with open(os.devnull, 'w') as devnull:
        subprocess.call(com, stdout=devnull, stderr=devnull)
    output = parse_output(output_path)
    pulse_output = parse_pulse_output(pm_output_path)
    os.remove(output_path)
    os.remove(pm_output_path)
    return output, pulse_output


class ReaperPitchTrackFunction(BaseAnalysisFunction):
    def __init__(self, reaper_path=None, time_step=0.01, min_pitch=75, max_pitch=600, with_pulses=False):
        super(ReaperPitchTrackFunction, self).__init__()
        self.requires_file = True
        if not reaper_path:
            reaper_path = 'reaper'
        self.reaper_path = reaper_path
        self.arguments = [time_step, min_pitch, max_pitch]
        self.with_pulses = with_pulses
        self.uses_segments = False
        if self.with_pulses:
            self._function = partial(call_reaper_with_pulses, reaper_path=reaper_path)
        else:
            self._function = partial(call_reaper, reaper_path=reaper_path)


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
            output[float(time)] = {'F0': float(pitch)}
    return output


def parse_pulse_output(output_file):
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
            if voiced == '1':
                output[float(time)] = 1
    return output
