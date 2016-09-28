
import os
import sys
from subprocess import Popen, PIPE
import shutil
import re
from scipy.io import wavfile
from tempfile import TemporaryDirectory, NamedTemporaryFile

from acousticsim.representations.formants import Formants
from acousticsim.representations.pitch import Pitch
from acousticsim.representations.intensity import Intensity
from acousticsim.representations.base import Representation
from acousticsim.representations.mfcc import Mfcc, freq_to_mel

from acousticsim.exceptions import AcousticSimPraatError

def file_to_pitch_praat(filepath, praatpath = None, time_step = 0.01, freq_lims = (75, 600), attributes = None, **kwargs):
    script = 'pitch.praat'
    if praatpath is None:
        praatpath = 'praat'
        if sys.platform == 'win32':
            praatpath.append('con.exe')
    listing = run_script(praatpath, script, filepath, time_step, freq_lims[0], freq_lims[1])
    output = Pitch(filepath, time_step, freq_lims, attributes = attributes)
    r = read_praat_out(listing)
    for k,v in r.items():
        r[k] = [v['Pitch']]
    output.rep = r
    return output

def signal_to_pitch_praat(signal, sr, praatpath = None,
            time_step = 0.01, freq_lims = (75, 600),
            attributes = None,
            begin = None, padding = None):
    with TemporaryDirectory(prefix = 'acousticsim') as tempdir:
        t_wav = NamedTemporaryFile(dir = tempdir, delete = False, suffix = '.wav')
        signal *= 32768
        wavfile.write(t_wav, sr, signal.astype('int16'))
        t_wav.close()
        output = file_to_pitch_praat(t_wav.name, praatpath, time_step, freq_lims,
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

def file_to_formants_praat(filepath, praatpath = None, time_step = 0.01,
                    win_len = 0.025, num_formants = 5, max_freq = 5000, attributes = None, **kwargs):
    script = 'formants.praat'
    listing = run_script(praatpath, script, filepath, time_step,
                    win_len, num_formants, max_freq)
    output = Formants(filepath, max_freq, num_formants, win_len,
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

def file_to_intensity_praat(filepath, praatpath = None, time_step = 0.01, attributes = None, **kwargs):
    script = 'intensity.praat'
    listing = run_script(praatpath, script, filepath, time_step)
    output = Intensity(filepath, time_step, attributes = attributes)
    r = read_praat_out(listing)
    for k,v in r.items():
        r[k] = [v['Intensity']]
    output.rep = r
    return output

def file_to_mfcc_praat(filepath, praatpath = None, num_coeffs = 12,
                win_len = 0.025, time_step = 0.01, max_freq = 7800,
                use_power = False, attributes = None,  **kwargs):
    script = 'mfcc.praat'
    listing = run_script(praatpath, script, filepath, num_coeffs, win_len, time_step, freq_to_mel(max_freq))
    output = Mfcc(filepath, (0,max_freq), num_coeffs, win_len, time_step,
                attributes = attributes, process = False)
    r = read_praat_out(listing)
    for k,v in r.items():
        r[k] = [v[k2] for k2 in sorted(v.keys())]
    output.rep = r

    return output

def run_script(praatpath, name, *args):
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
    if err and not err.strip().startswith('Warning'):
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
