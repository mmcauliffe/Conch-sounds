from numpy import zeros, arange,argmin,min,abs, log2, ceil,floor, \
                        shape, float,mean,sqrt,log10,linspace,array
from numpy.fft import fft, ifft
from scipy.io import wavfile
from scipy.signal import lfilter,resample

def nextpow2(x):
    """Return the first integer N such that 2**N >= abs(x)"""

    return ceil(log2(abs(x)))

def extract_wav(path,outpath,begin_time,end_time):
    sr, sig = wavfile.read(path)

    begin = int(sr * begin_time)
    end = int(sr * end_time)

    newsig = sig[begin:end]
    wavfile.write(outpath,sr,newsig)

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
    try:
        sig = sig[:,0]
    except IndexError:
        pass

    if sr != oldsr:
        t = len(sig)/oldsr
        numsamp = t * sr
        proc = resample(sig,numsamp)
    else:
        proc = sig
    #proc = proc / 32768
    if alpha != 0:
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

def fftfilt(b, x, *n):
    """Filter the signal x with the FIR filter described by the
    coefficients in b using the overlap-add method. If the FFT
    length n is not specified, it and the overlap-add block length
    are selected so as to minimize the computational cost of
    the filtering operation."""

    N_x = len(x)
    N_b = len(b)

    # Determine the FFT length to use:
    if len(n):

        # Use the specified FFT length (rounded up to the nearest
        # power of 2), provided that it is no less than the filter
        # length:
        n = n[0]
        if n != int(n) or n <= 0:
            raise ValueError('n must be a nonnegative integer')
        if n < N_b:
            n = N_b
        N_fft = 2**nextpow2(n)
    else:

        if N_x > N_b:

            # When the filter length is smaller than the signal,
            # choose the FFT length and block size that minimize the
            # FLOPS cost. Since the cost for a length-N FFT is
            # (N/2)*log2(N) and the filtering operation of each block
            # involves 2 FFT operations and N multiplications, the
            # cost of the overlap-add method for 1 length-N block is
            # N*(1+log2(N)). For the sake of efficiency, only FFT
            # lengths that are powers of 2 are considered:
            N = 2**arange(ceil(log2(N_b)),floor(log2(N_x)))
            cost = ceil(N_x/(N-N_b+1))*N*(log2(N)+1)
            if cost:
                N_fft = N[argmin(cost)]
            else:
                N_fft = 2**nextpow2(N_b+N_x-1)

        else:

            # When the filter length is at least as long as the signal,
            # filter the signal using a single block:
            N_fft = 2**nextpow2(N_b+N_x-1)

    N_fft = int(N_fft)

    # Compute the block length:
    L = int(N_fft - N_b + 1)

    # Compute the transform of the filter:
    H = fft(b,N_fft)

    y = zeros(N_x,float)
    i = 0
    while i <= N_x:
        il = min([i+L,N_x])
        k = min([i+N_fft,N_x])
        yt = ifft(fft(x[i:il],N_fft)*H,N_fft) # Overlap..
        y[i:k] = y[i:k] + yt[:k-i]            # and add
        i += L
    return y

