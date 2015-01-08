
import os
from collections import defaultdict

import numpy as np

from numpy import mean, std, array, min, max, inf,sqrt, exp, pi
import pylab as P

from acousticsim.representations.mfcc import Mfcc

#Features:
#Amplitude (relative?), Spectral slope?

SEGMENT_SET = {'C':{'b','d','g','p','t','k','dx','q','jh','ch','s','sh',
                    'z','zh','f','th','v','dh','hh','hv','ax-h'},
                'V':{'m','n','ng','em','en','eng','nx','l','r','w','y','el',
                    'iy','ih','eh','ey','ae','aa','aw','ay','ah','ao','oy','ow','uh',
                    'uw','ux','er','ax','ix','axr'},
                'SIL':{'pau','epi','h#','bcl','dcl','gcl','pcl','tcl','kcl'}}

TIMIT_DIR = r'C:\Users\michael\Documents\Data\TIMIT_fixed'

TIMIT_DRS = ['DR1','DR2','DR3','DR4','DR5','DR6','DR7','DR8']

def align_dialog_info(words, phones, wavs):
    dialogs = {}
    for p in words:
        name = os.path.splitext(os.path.split(p)[1])[0]
        dialogs[name] = {'words':p}
    for p2 in phones:
        name = os.path.splitext(os.path.split(p2)[1])[0]
        dialogs[name]['phones'] = p2
    for p3 in wavs:
        name = os.path.splitext(os.path.split(p3)[1])[0]
        dialogs[name]['wav'] = p3
    return dialogs

def read_phones(path, dialect = 'timit', sr = None):
    output = list()
    with open(path,'r') as f:
        for line in f:
            if dialect == 'timit':
                l = line.strip().split(' ')
                start = float(l[0])
                end = float(l[1])
                phone = l[2]
            else:
                raise(NotImplementedError)
            if sr is not None:
                start /= sr
                end /= sr
            output.append([phone, start, end])
    return output

class SpeechClassifier(object):

    _num_coeffs = 2

    _use_priors = True

    def __init__(self):
        self._guass_values = {'C': [None]*self._num_coeffs*2,
                    'V': [None]*self._num_coeffs*2,
                    'SIL': [None]*self._num_coeffs*2}
        self._ranges = [[inf, -inf] for i in range(self._num_coeffs)]
        self._priors = {'C': None,
                    'V': None,
                    'SIL': None}

    def train(self,path=None,segment_set = None):
        #assume training on TIMIT
        if path is None:
            path = TIMIT_DIR
        if segment_set is None:
            segment_set = SEGMENT_SET

        words = []
        phones = []
        wavs = []
        train_dir = os.path.join(path, 'TRAIN')
        for root, subdirs, files in os.walk(train_dir):
            for f in files:
                if f.lower().endswith('.wrd'):
                    words.append(os.path.join(root,f))
                elif f.lower().endswith('.phn'):
                    phones.append(os.path.join(root,f))
                elif f.lower().endswith('.wav'):
                    wavs.append(os.path.join(root,f))
        dialogs = align_dialog_info(words, phones,wavs)
        values = [defaultdict(list) for i in range(self._num_coeffs)]
        for (i,(d,info)) in enumerate(dialogs.items()):
            print(i,len(dialogs))
            mfcc = Mfcc(info['wav'], (80,7800), self._num_coeffs, 0.025,
                        0.01, num_filters = 26, use_power = True)
            phones = read_phones(info['phones'],sr=mfcc.sampling_rate)
            for p in phones:
                for k,v in segment_set.items():
                    if p[0] in v:
                        phone_class = k
                        break
                else:
                    continue
                coeffs = mfcc[p[1],p[2]]
                for i in range(self._num_coeffs):
                    t = [x[i] for x in coeffs]
                    try:
                        mini = min(t)
                        if mini < self._ranges[i][0]:
                            self._ranges[i][0] = mini
                    except:
                        continue
                    maxi = max(t)
                    if maxi > self._ranges[i][1]:
                        self._ranges[i][1] = maxi
                    values[i][phone_class].extend(t)
            #break
        #Find out the max of each value
        total = 0
        for k in self._guass_values.keys():
            for i in range(self._num_coeffs):
                ind = i * 2
                self._guass_values[k][ind] = mean(values[i][k])
                self._guass_values[k][ind+1] = std(values[i][k])
            self._priors[k] = len(values[0][k])
            total += self._priors[k]
        for k,v in self._priors.items():
            self._priors[k] = v/total

    def predict(self,feature_values):
        if len(feature_values) != self._num_coeffs:
            return None
        best_value = 0
        best_cat = None
        for k in self._guass_values.keys():
            if self._priors[k] is None:
                return None
            if self._use_priors:
                val = self._priors[k]
            else:
                val = 0.33
            for i in range(self._num_coeffs):
                ind = i * 2
                mean = self._guass_values[k][ind]
                var = self._guass_values[k][ind+1]**2
                prob = exp(-1*(feature_values[i]-mean)**2/(2*var))/(sqrt(pi*var))
                val *= prob
            if val > best_value:
                best_value = val
                best_cat = k
        return best_cat

    def test(self,path=None,segment_set = None, debug = False):
        #assume testing on TIMIT
        if path is None:
            path = TIMIT_DIR
        if segment_set is None:
            segment_set = SEGMENT_SET
        if debug:
            with open('debug.txt','w') as f:
                pass
        words = []
        phones = []
        wavs = []
        test_dir = os.path.join(path, 'TEST')
        for root, subdirs, files in os.walk(test_dir):
            for f in files:
                if f.lower().endswith('.wrd'):
                    words.append(os.path.join(root,f))
                elif f.lower().endswith('.phn'):
                    phones.append(os.path.join(root,f))
                elif f.lower().endswith('.wav'):
                    wavs.append(os.path.join(root,f))
        dialogs = align_dialog_info(words, phones,wavs)
        hits = 0
        total = 0
        vhits = 0
        vtotal = 0
        for (i,(d,info)) in enumerate(dialogs.items()):
            print(i,len(dialogs))
            mfcc = Mfcc(info['wav'], (80,7800), self._num_coeffs, 0.025,
                        0.01, num_filters = 26, use_power = True)
            phones = read_phones(info['phones'],sr=mfcc.sampling_rate)
            if debug:
                with open('debug.txt','a') as f:
                    f.write('{}\n{}\n\n'.format(info['wav'],' '.join([x[0] for x in phones])))
            for p in phones:
                for k,v in segment_set.items():
                    if p[0] in v:
                        phone_class = k
                        break
                else:
                    continue
                if debug:
                    with open('debug.txt','a') as f:
                        f.write('{}\n\n'.format(p))
                coeffs = mfcc[p[1],p[2]]
                for frame in coeffs:
                    predicted = self.predict(frame)
                    if predicted == phone_class:
                        hits += 1
                        if phone_class == 'V':
                            vhits += 1
                    total += 1
                    if phone_class == 'V':
                        vtotal += 1
                    if debug:
                        with open('debug.txt','a') as f:
                            f.write('{}\t{}\t{}\n'.format(phone_class,predicted,' '.join(map(str,frame))))
        print('Accuracy:',hits/total)
        print('Vowel ccuracy:',vhits/vtotal)


if __name__ == '__main__':
    sc = SpeechClassifier()
    sc.train()
    sc.test(debug=False)
    print(sc._guass_values)
    print(sc._priors)
