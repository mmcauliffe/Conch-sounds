import subprocess
import os

from ..helper import fix_time_points, ASTemporaryWavFile


def file_to_pitch_reaper(file_path, reaper_path=None, time_step=0.01,
                         min_pitch=75, max_pitch=600):
    if reaper_path is None:
        reaper_path = 'reaper'

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
    with open(os.devnull, 'w') as devnull:
        subprocess.call(com, stdout=devnull, stderr=devnull)
    output = parse_output(output_path)
    os.remove(output_path)
    return output


def signal_to_pitch_reaper(signal, sr, reaper_path=None, time_step=0.01,
                           min_pitch=75, max_pitch=600,
                           begin=None, padding=None):
    with ASTemporaryWavFile(signal, sr) as wav_path:
        output = file_to_pitch_reaper(wav_path, reaper_path, time_step, min_pitch, max_pitch)
    duration = signal.shape[0] / sr
    return fix_time_points(output, begin, padding, duration)


def file_to_pitch_and_pulse_reaper(file_path, reaper_path=None, time_step=0.01,
                                   min_pitch=75, max_pitch=600):
    if reaper_path is None:
        reaper_path = 'reaper'

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


def signal_to_pitch_and_pulse_reaper(signal, sr, reaper_path=None, time_step=0.01,
                                     min_pitch=75, max_pitch=600,
                                     begin=None, padding=None):
    with ASTemporaryWavFile(signal, sr) as wav_path:
        output, pulse_output = file_to_pitch_and_pulse_reaper(wav_path, reaper_path, time_step, min_pitch, max_pitch)
    duration = signal.shape[0] / sr
    return fix_time_points(output, begin, padding, duration), sorted(
        fix_time_points(pulse_output, begin, padding, duration).keys())


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
