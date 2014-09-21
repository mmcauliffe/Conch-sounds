
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

    pspec = zeros((num_frames,int(nfft/2)+1))
    for i in range(num_frames):
        X = x[indices[i]-int(nperseg/2):indices[i]+int(nperseg/2)]
        X = X * window
        fx = fft(X, n = nfft)
        power = abs(fx[:int(nfft/2)+1])**2
        pspec[i,:] = power
    return pspec

def to_specgram(filename,win_len,time_step=None):
    sr, proc = preproc(filename,alpha=0.95)
    if time_step is None:
        tot_dur = len(proc) / sr
        steps = 100
        time_step = tot_dur / steps


    pspec = to_powerspec(proc, sr, win_len, time_step)
    nfft = (pspec.shape[1]-1) * 2
    freqs = (sr / nfft) * arange(pspec.shape[1])
    times = (arange(pspec.shape[0]) * time_step) + (win_len/2)
    dbspec = zeros(pspec.shape)
    for i in range(dbspec.shape[0]):
        dbspec[k,:] = 10 * log10(pspec[k,:] + spacing(1))

    return spec,freqs,times

class Spectrogram(Representation):
    pass
