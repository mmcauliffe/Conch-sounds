from numpy import abs, log2, ceil, mean,sqrt,log10,linspace,array
from scipy.io import wavfile
from scipy.signal import lfilter,resample

def nextpow2(x):
    """Return the first integer N such that 2**N >= abs(x)"""

    return ceil(log2(abs(x)))


def preproc(path,sr=16000,alpha=0.95):
    """Preprocess a .wav file for later processing.  Currently assumes a
    16-bit PCM input.  Only returns left channel of stereo files.

    Parameters
    ----------
    path : str
        Full path to .wav file to load.
    sr : int, optional
        Sampling rate to resample at, if specified.
    alpha : float, optional
        Alpha for preemphasis, defaults to 0.97.

    Returns
    -------
    int
        Sampling rate.
    array
        Processed PCM.

    """
    oldsr,sig = wavfile.read(path)
    if len(sig.shape) > 1:
        sig = sig[:,0]

    if sr != oldsr:
        t = len(sig)/oldsr
        numsamp = t * sr
        proc = resample(sig,numsamp)
    else:
        proc = sig
    proc = proc / 32768
    proc = lfilter([1., -alpha],1,proc)
    return sr,proc

def erb_rate_to_hz(x):
    y=(10**(x/21.4)-1)/4.37e-3
    return y

def hz_to_erb_rate(x):
    y=(21.4*log10(4.37e-3*x+1))
    return y

def make_erb_cfs(freq_lims,num_channels):
    cfs = erb_rate_to_hz(linspace(hz_to_erb_rate(freq_lims[0]),hz_to_erb_rate(freq_lims[1]),num_channels))
    return cfs
