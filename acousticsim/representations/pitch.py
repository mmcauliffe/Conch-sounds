
from numpy import (log10,zeros,abs,arange, hanning, pad, spacing, ceil,
                    log, correlate, max,argmax, argpartition, mean, log2,
                    maximum,empty, inf)
from numpy.fft import fft
from scipy.signal import gaussian, argrelmax

#import matplotlib.pyplot as plt

from acousticsim.representations.base import Representation
from .helper import preproc

from .gammatone import to_gammatone

class Pitch(Representation):
    #Praat parameters
    _sil_thresh = 0.03
    _voice_thresh = 0.45
    _octave_cost = 0.01
    _octave_jump_cost = 0.35
    _voice_change_cost = 0.14
    _num_candidates = 15
    _periods_per_window = 3

    def __init__(self, filepath, time_step, freq_lims,
                window_shape = 'gaussian', attributes=None):
        Representation.__init__(self,filepath, freq_lims, attributes)
        self._win_len = self._periods_per_window/self._freq_lims[0]
        self._window_shape = window_shape
        if self._window_shape == 'gaussian':
            self._win_len *= 2
        self._time_step = time_step

    def process(self):
        self._sr, proc = preproc(self._filepath,alpha=None)
        maxproc = max(proc)
        #print(maxproc)
        nperseg = int(self._win_len*self._sr)
        nperstep = int(self._time_step*self._sr)
        if self._window_shape == 'gaussian':
            window = gaussian(nperseg+2,0.5*(nperseg-1)/2)[1:nperseg+2]
        else:
            window = hanning(nperseg+2)[1:nperseg+1]

        maxpos = int(1/self._freq_lims[0]*self._sr)
        minpos = int(1/self._freq_lims[1]*self._sr)
        #print(minpos,maxpos)
        indices = arange(int(nperseg/2), proc.shape[0] - int(nperseg/2), nperstep)
        num_frames = len(indices)
        self._rep = dict()
        win_ac = correlate(window,window,'full')
        win_ac = win_ac[int(win_ac.size/2):]/ max(win_ac)
        #plt.plot(win_ac)
        #plt.show()
        candidate_matrix = list()
        for i in range(num_frames):
            X = proc[indices[i]-int(nperseg/2):indices[i]+int(nperseg/2)+1]
            try:
                X = X * window
            except ValueError:
                print(i,num_frames)
                print(indices[i], len(proc))
                raise(ValueError)
            X -= mean(X)
            #print(max(X)/maxproc)
            unvoicedR = self._voice_thresh + maximum(0,
                        2 - (max(X)/maxproc)/
                        (self._sil_thresh/(1+self._voice_thresh)))
            candidates = [(0,unvoicedR)]
            ac = correlate(X,X,'full')
            #print(ac)
            sig_ac = ac[int(ac.size/2):] / max(ac)

            orig_ac = sig_ac/win_ac
            cands = minpos + argrelmax(orig_ac[minpos:maxpos])[0]
            values = orig_ac[cands]
            inds = values.argsort()
            cands = cands[inds][:self._num_candidates]
            for pos in cands:
                f0 = 1/(pos/self._sr)
                R = orig_ac[pos] - self._octave_cost * log(self._freq_lims[0] * pos)
                candidates.append((f0,R))
            #print(candidates)
            #plt.plot(orig_ac)
            #plt.show()
            candidate_matrix.append(candidates)
        def transition_cost(f1, f2):
            if f1 == 0 and f2 == 0:
                return 0
            elif f1 == 0 or f2 == 0:
                return self._voice_change_cost
            else:
                return self._octave_jump_cost * log(f1/f2)

        V = [{}]
        path = {}

        # Initialize base cases (t == 0)
        for y in range(self._num_candidates):
            try:
                V[0][y] = candidate_matrix[0][y][1]
                path[y] = [y]
            except IndexError:
                pass

        # Run Viterbi for t > 0
        for t in range(1, num_frames):
            V.append({})
            newpath = {}
            for y in range(self._num_candidates):
                best = inf
                state = -1
                try:
                    freq, r = candidate_matrix[t][y]
                except IndexError:
                    continue
                for y0 in range(self._num_candidates):
                    try:
                        cost = V[t-1][y0]
                        cost += transition_cost(candidate_matrix[t-1][y0][0],
                                                freq)
                        cost -= r
                    except (IndexError,KeyError):
                        continue

                    if cost < best:
                        best = cost
                        state = y0
                V[t][y] = best
                newpath[y] = path[state] + [y]

            # Don't need to remember the old paths
            path = newpath
        n = 0           # if only one element is observed max is sought in the initialization values
        if num_frames != 1:
            n = t
        best = inf
        state = -1
        for y in range(self._num_candidates):
            try:
                c = V[n][y]
            except KeyError:
                continue
            if c < best:
                best =c
                state = y

        for i,p in enumerate(path[state]):
            #print(candidate_matrix[i][p])
            self._rep[indices[i]/self._sr] = [candidate_matrix[i][p][0]]
        #print_dptable(V)
        #raise(ValueError)

    def is_voiced(self, time):
        if self[time] is None:
            return False
        return True

class Harmonicity(Pitch):
    #Praat parameters
    _sil_thresh = 0.1
    _voice_thresh = 0
    _octave_cost = 0
    _octave_jump_cost = 0
    _voice_change_cost = 0
    _num_candidates = 1
    _periods_per_window = 4.5

    def __init__(self, filepath, time_step, min_pitch,
                window_shape = 'gaussian', attributes=None):
        freq_lims = (min_pitch,None)
        Pitch.__init__(self, filepath, time_step, freq_lims,
                window_shape, attributes)

    def process(self):
        self._sr, proc = preproc(self._filepath,alpha=None)
        maxproc = max(proc)
        #print(maxproc)
        nperseg = int(self._win_len*self._sr)
        nperstep = int(self._time_step*self._sr)
        if self._window_shape == 'gaussian':
            window = gaussian(nperseg+2,0.5*(nperseg-1)/2)[1:nperseg+2]
        else:
            window = hanning(nperseg+2)[1:nperseg+1]

        maxpos = int(1/self._freq_lims[0]*self._sr)
        indices = arange(int(nperseg/2), proc.shape[0] - int(nperseg/2), nperstep)
        num_frames = len(indices)
        self._rep = dict()
        win_ac = correlate(window,window,'full')
        win_ac = win_ac[int(win_ac.size/2):]/ max(win_ac)
        for i in range(num_frames):
            X = proc[indices[i]-int(nperseg/2):indices[i]+int(nperseg/2)+1]
            X = X * window
            X -= mean(X)
            ac = correlate(X,X,'full')
            sig_ac = ac[int(ac.size/2):] / max(ac)

            orig_ac = sig_ac/win_ac

            cands = argrelmax(orig_ac[:maxpos])[0]
            rs = orig_ac[cands]
            if len(rs) > 0:
                r = max(rs)
            else:
                r = -1
            if r > 1:
                r = 1/r

            elif r < 0:
                r = 0.0001
                #print(argrelmax(orig_ac[:maxpos])[0])
                #print(rs)
                #plt.plot(orig_ac)
                #plt.show()
            self._rep[indices[i]/self._sr] = [10 * log10(r/(1-r))]




def to_pitch_zcd(gt):
    pass
#    import matplotlib.pyplot as plt
#    print(gt.shape)
#    nsamps = gt.shape[0]
#    nbands = get.shape[1]
#    for i in range(1,nsamps-1):
#        pass
#    plt.plot(gt)
#    plt.show()
