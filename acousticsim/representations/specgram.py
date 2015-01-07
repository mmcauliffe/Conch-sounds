
from numpy import log10,zeros,abs,arange, hanning, pad, spacing, ceil, log
from numpy.fft import fft


from acousticsim.representations.base import Representation
from .helper import preproc


def to_powerspec(x, sr, win_len, time_step):
    nperseg = int(win_len*sr)
    nperstep = int(time_step*sr)
    nfft = int(2**(ceil(log(nperseg)/log(2))))
    window = hanning(nperseg+2)[1:nperseg+1]

    indices = arange(int(nperseg/2), x.shape[0] - int(nperseg/2) + 1, nperstep)
    num_frames = len(indices)

    #pspec = zeros((num_frames,int(nfft/2)+1))
    pspec = dict()
    for i in range(num_frames):
        X = x[indices[i]-int(nperseg/2):indices[i]+int(nperseg/2)]
        X = X * window
        fx = fft(X, n = nfft)
        power = abs(fx[:int(nfft/2)+1])**2
        #pspec[i,:] = power
        pspec[indices[i]/sr] = power
    return pspec

class Spectrogram(Representation):
    def __init__(self, filepath, freq_lims, win_len, time_step, attributes = None):
        Representation.__init__(self,filepath, freq_lims, attributes)
        self._win_len = win_len
        self._time_step = time_step

        self.process()

    def pspec(self):
        times = sorted(self._pspec.keys())
        ex = next(iter(self._pspec.values()))
        try:
            frame_len = len(ex)
        except:
            frame_len = 1

        output = zeros((len(times),frame_len))
        for i, t in enumerate(times):
            output[i,:] = self._pspec[t]
        return output

    def process(self):
        sr, proc = preproc(self._filepath,alpha=0.97)
        self._duration = len(proc) / sr
        if self._time_step is None:
            steps = 100
            time_step = self._duration / steps


        self._pspec = to_powerspec(proc, sr, self._win_len, self._time_step)
        self._rep = dict()
        for k in self._pspec:
            nfft = (len(self._pspec[k])-1) * 2
            self._rep[k] = 10 * log10(self._pspec[k] + spacing(1))

        self._freqs = (sr / nfft) * arange((nfft/2) + 1)

