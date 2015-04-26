
import os
from subprocess import Popen, PIPE
import re

from acousticsim.representations.formants import Formants
from acousticsim.representations.pitch import Pitch
from acousticsim.representations.intensity import Intensity
from acousticsim.representations.base import Representation
from acousticsim.representations.mfcc import Mfcc, freq_to_mel

from acousticsim.exceptions import AcousticSimPraatError

def to_pitch_praat(praatpath, filename, time_step = 0.01, freq_lims = (75, 600), attributes = None):
    script = 'pitch.praat'
    listing = run_script(praatpath, script, filename, time_step, freq_lims[0], freq_lims[1])
    output = Pitch(filename, time_step, freq_lims, attributes = attributes)
    r = read_praat_out(listing)
    for k,v in r.items():
        r[k] = [v['Pitch']]
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
        r[k] = [v['Intensity']]
    output.rep = r
    return output

def to_mfcc_praat(praatpath, filename, num_coeffs = 12,
                win_len = 0.025, time_step = 0.01, max_freq = 7800, use_power = False, attributes = None):
    script = 'mfcc.praat'
    listing = run_script(praatpath, script, filename, num_coeffs, win_len, time_step, freq_to_mel(max_freq))
    output = Mfcc(filename, (0,max_freq), num_coeffs, win_len, time_step,
                attributes = attributes, process = False)
    r = read_praat_out(listing)
    for k,v in r.items():
        r[k] = [v[k2] for k2 in sorted(v.keys())]
    output.rep = r

    return output

def run_script(praatpath,name,*args):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    com = [praatpath]
    if praatpath.endswith('con.exe'):
        com += ['-a']
    com +=[os.path.join(script_dir,name)] + list(map(str,args))
    with Popen(com,stdout=PIPE,stderr=PIPE,stdin=PIPE) as p:
        try:
            text = str(p.stdout.read().decode('latin'))
            err = str(p.stderr.read().decode('latin'))
        except UnicodeDecodeError:
            print(p.stdout.read())
            print(p.stderr.read())
    if err:
        raise(AcousticSimPraatError(err))
    return text

def read_praat_out(text):
    if not text:
        return None
    lines = text.splitlines()
    head = None
    while head is None:
        try:
            l = lines.pop(0)
        except IndexError:
            print(text)
            raise
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
