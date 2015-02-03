
import os
import subprocess
import re

from acousticsim.representations.formants import Formants
from acousticsim.representations.pitch import Pitch
from acousticsim.representations.intensity import Intensity
from acousticsim.representations.base import Representation

def to_pitch_praat(praatpath, filename, time_step = 0.01, freq_lims = (75, 600), attributes = None):
    script = 'pitch.praat'
    listing = run_script(praatpath, script, filename, time_step, freq_lims[0], freq_lims[1])
    output = Pitch(filename, time_step, freq_lims, attributes = attributes)
    r = read_praat_out(listing)
    for k,v in r.items():
        r[k] = v['Pitch']
    output.rep = r
    return output

def to_formants_praat(praatpath, filename, time_step = 0.01,
                    win_len = 0.025, num_formants = 5, max_freq = 5000, attributes = None):
    script = 'formants.praat'
    listing = run_script(praatpath, script, filename, time_step,
                    win_len, num_formants, max_freq)
    output = Formants(filename, max_freq, num_formants, win_len,
                    time_step, attributes = attributes)
    r = read_praat_out(listing)
    for k,v in r.items():
        new_v = list()
        for i in range(1,num_formants+1):
            try:
                new_v.append((v['F%d'%i],v['B%d'%i]))
            except KeyError:
                new_v.append((None,None))
        r[k] = new_v
    output.rep = r
    return output

def to_intensity_praat(praatpath, filename, time_step = 0.01, attributes = None):
    script = 'intensity.praat'
    listing = run_script(praatpath, script, filename, time_step)
    output = Intensity(filename, time_step, attributes = attributes)
    r = read_praat_out(listing)
    for k,v in r.items():
        print(k,v['Intensity'])
        r[k] = v['Intensity']
    output.rep = r
    return output

def to_mfcc_praat(praatpath, filename, num_coeffs = 12, win_len = 0.025, time_step = 0.01, max_freq = 7800):
    script = 'mfcc.praat'
    listing = run_script(praatpath, script, filename, num_coeffs, win_len, time_step, max_freq)
    output = Representation(filename, (0,max_freq), attributes = attributes)


def run_script(praatpath,name,*args):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    com = [praatpath]
    if praatpath.endswith('con.exe'):
        com += ['-a']
    com +=[os.path.join(script_dir,name)] + list(map(str,args))
    p = subprocess.Popen(com,stdout=subprocess.PIPE,stderr=subprocess.PIPE,stdin=subprocess.PIPE)
    stdout, stderr = p.communicate()
    if stderr:
        print('stderr: %s' % str(stderr))
    return str(stdout.decode())

def read_praat_out(text):
    if not text:
        return None
    lines = text.splitlines()
    head = None
    while head is None:
        l = lines.pop(0)
        if l.startswith('time'):
            head = re.sub('[(]\w+[)]','',l)
            head = head.split("\t")[1:]
    output = {}
    for l in lines:
        if '\t' in l:
            line = l.split("\t")
            time = line.pop(0)
            values = {}
            for j in range(len(line)):
                v = line[j]
                if v != '--undefined--':
                    try:
                        v = float(v)
                    except ValueError:
                        print(text)
                        print(head)
                else:
                    v = 0
                values[head[j]] = v
            if values:
                output[float(time)] = values
    return output
