
from numpy import (log10,zeros,abs,arange, hanning, pad, spacing, ceil,
                    log, correlate, max,argmax, argpartition, mean, log2,
                    maximum,empty, inf)
from numpy.fft import fft
from scipy.signal import gaussian, argrelmax


from acousticsim.representations.base import Representation
from .helper import preproc

from .gammatone import to_gammatone

class Intensity(Representation):
    #Praat parameters
    _min_pitch = 100
    _subtract_mean = True

    def __init__(self, filepath, time_step, window_shape = 'gaussian', attributes=None):
        Representation.__init__(self,filepath, None, attributes)
        self._win_len = 3.2/self._min_pitch
        self._window_shape = window_shape
        #if self._window_shape == 'gaussian':
        #    self._win_len *= 2
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

        indices = arange(int(nperseg/2), proc.shape[0] - int(nperseg/2) + 1, nperstep)
        num_frames = len(indices)
        self._rep = dict()

        for i in range(num_frames):
            X = proc[indices[i]-int(nperseg/2):indices[i]+int(nperseg/2)+1]
            X = X ** 2
            X = X * window
            self._rep[indices[i]/self._sr] = 10 * log10(sum(X))
            print(indices[i]/self._sr, 10 * log10(sum(X)))


    def is_voiced(self, time):
        if self[time] is None:
            return False
        return True

def viterbi(obs, states, start_p, trans_p, emit_p):
    V = [{}]
    path = {}

    # Initialize base cases (t == 0)
    for y in states:
        V[0][y] = start_p[y] * emit_p[y][obs[0]]
        path[y] = [y]

    # Run Viterbi for t > 0
    for t in range(1, len(obs)):
        V.append({})
        newpath = {}

        for y in states:
            (prob, state) = max((V[t-1][y0] * trans_p[y0][y] * emit_p[y][obs[t]], y0) for y0 in states)
            V[t][y] = prob
            newpath[y] = path[state] + [y]

        # Don't need to remember the old paths
        path = newpath
    n = 0           # if only one element is observed max is sought in the initialization values
    if len(obs) != 1:
        n = t
    print_dptable(V)
    (prob, state) = max((V[n][y], y) for y in states)
    return (prob, path[state])

def to_pitch_zcd(gt):
    import matplotlib.pyplot as plt
    print(gt.shape)
    nsamps = gt.shape[0]
    nbands = get.shape[1]
    for i in range(1,nsamps-1):
        pass
    plt.plot(gt)
    plt.show()
