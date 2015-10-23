import subprocess
import os

from acousticsim.representations.pitch import Pitch

def to_pitch_reaper(filepath, reaper = None, time_step = None, freq_lims = None, attributes = None):
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
    devnull = open(os.devnull, 'w')
    subprocess.call(com, stdout=devnull, stderr=devnull)
    output = Pitch(filepath, time_step, freq_lims, attributes = attributes)
    output.rep = parse_output(output_path)
    os.remove(output_path)
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
