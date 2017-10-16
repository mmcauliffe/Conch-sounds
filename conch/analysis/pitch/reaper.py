import subprocess
import os

from ..helper import fix_time_points, ASTemporaryWavFile


def call_reaper(file_path, reaper_path, time_step=0.01, min_pitch=75, max_pitch=600):
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
    print(com)
    with open(os.devnull, 'w') as devnull:
        subprocess.call(com, stdout=devnull, stderr=devnull)
    output = parse_output(output_path)
    os.remove(output_path)
    return output


def call_reaper_with_pulses(file_path, reaper_path, time_step=0.01, min_pitch=75, max_pitch=600):
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


class ReaperPitchTrackFunction(object):
    def __init__(self, reaper_path=None, time_step=0.01, min_pitch=75, max_pitch=600, with_pulses=False):
        if not reaper_path:
            reaper_path = 'reaper'
        self.reaper_path = reaper_path
        self.arguments = [time_step, min_pitch, max_pitch]
        self.with_pulses = with_pulses
        self.uses_segments = False
        if self.with_pulses:
            self._function = call_reaper_with_pulses
        else:
            self._function = call_reaper

    def __call__(self, *args, **kwargs):
        first_arg = args[0]
        args = args[1:]
        if isinstance(first_arg, (tuple, list)):
            signal, sr = first_arg[:2]
            begin = kwargs.get('begin', None)
            padding = kwargs.get('padding', None)
            with ASTemporaryWavFile(signal, sr) as wav_path:
                output = self._function(wav_path, self.reaper_path, *args)
            if begin is not None:
                duration = signal.shape[0] / sr
                output = fix_time_points(output, begin, padding, duration)
            return output

        return self._function(first_arg, self.reaper_path, *args)


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
