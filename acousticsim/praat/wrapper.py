
import os
import subprocess
import re

from acousticsim.representations.formants import Formants
from acousticsim.representations.pitch import Pitch

def to_pitch_praat(praatpath, filename, time_step, min_pitch, max_pitch):
    script = 'pitch.praat'
    listing = run_script(praatpath, script, filename, time_step, min_pitch, max_pitch)
    output = Pitch(filename, time_step, (min_pitch,max_pitch))
    r = read_praat_out(listing)
    for k,v in r.items():
        r[k] = v['Pitch']
    output.set_rep(r)
    return output

def to_formants_praat(praatpath, filename, time_step,
                    window_length, num_formants, ceiling):
    script = 'formants.praat'
    listing = run_script(praatpath, script, filename, time_step,
                    window_length, num_formants, ceiling)
    output = Formants(filename, ceiling, num_formants, window_length,
                    time_step)
    output.set_rep(read_praat_out(listing))
    return output

def to_intensity_praat(praatpath,*args):
    pass



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
    head = re.sub('[(]\w+[)]','',lines.pop(0))
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
                    v = float(v)
                else:
                    v = None
                values[head[j]] = v
            if values:
                output[float(time)] = values
    return output
