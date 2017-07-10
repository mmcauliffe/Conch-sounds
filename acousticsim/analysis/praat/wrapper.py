
import os
from subprocess import Popen, PIPE
import re


from acousticsim.exceptions import AcousticSimPraatError


def run_script(praat_path, script_path, *args):
    com = [praat_path]
    if praat_path.endswith('con.exe'):
        com += ['-a']
    com += ['--run']
    com +=[script_path] + list(map(str,args))
    err = ''
    text = ''
    with Popen(com, stdout=PIPE, stderr=PIPE, stdin=PIPE) as p:
        try:
            text = str(p.stdout.read().decode('latin'))
            err = str(p.stderr.read().decode('latin'))
        except UnicodeDecodeError:
            print(p.stdout.read())
            print(p.stderr.read())
    if (err and not err.strip().startswith('Warning')) or not text:
        print(args)
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
