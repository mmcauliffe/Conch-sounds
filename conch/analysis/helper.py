import numpy as np
from numpy.fft import fft, ifft
from scipy.signal import lfilter
from scipy.io import wavfile
import soundfile
from tempfile import TemporaryDirectory, NamedTemporaryFile


def nextpow2(x):
    """Return the first integer N such that 2**N >= abs(x)"""

    return np.ceil(np.log2(np.abs(x)))


def extract_wav(path, outpath, begin_time, end_time):
    sr, sig = wavfile.read(path)

    begin = int(sr * begin_time)
    end = int(sr * end_time)

    newsig = sig[begin:end]
    wavfile.write(outpath, sr, newsig)


def preemphasize(signal, alpha):
    return lfilter([1., -alpha], 1, signal)


def preproc(path, sr=16000, alpha=0.95):
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
    oldsr, sig = wavfile.read(path)

    try:
        sig = sig[:, 0]
    except IndexError:
        pass

    if False and sr != oldsr:
        t = len(sig) / oldsr
        numsamp = int(t * sr)
        proc = resample(sig, numsamp)
    else:
        proc = sig
        sr = oldsr
    # proc = proc / 32768
    if alpha is not None and alpha != 0:
        proc = lfilter([1., -alpha], 1, proc)
    return sr, proc


def erb_rate_to_hz(x):
    y = (10 ** (x / 21.4) - 1) / 4.37e-3
    return y


def hz_to_erb_rate(x):
    y = (21.4 * np.log10(4.37e-3 * x + 1))
    return y


def freq_to_mel(freq):
    """Convert a value in Hertz to a value in mel.

    Parameters
    ----------
    freq : numeric
        Frequency value in Hertz to convert.

    Returns
    -------
    float
        Frequency value in mel.

    """

    return 2595 * np.log10(1 + freq / 700.0)


def mel_to_freq(mel):
    """Convert a value in mel to a value in Hertz.

    Parameters
    ----------
    mel : numeric
        Frequency value in mel to convert.

    Returns
    -------
    float
        Frequency value in Hertz.

    """

    return 700 * (10 ** (mel / 2595.0) - 1)


def make_erb_cfs(freq_lims, num_channels):
    cfs = erb_rate_to_hz(np.linspace(hz_to_erb_rate(freq_lims[0]), hz_to_erb_rate(freq_lims[1]), num_channels))
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
        N_fft = 2 ** nextpow2(n)
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
            N = 2 ** np.arange(np.ceil(np.log2(N_b)), np.floor(np.log2(N_x)))
            cost = np.ceil(N_x / (N - N_b + 1)) * N * (np.log2(N) + 1)
            if len(cost) > 0:
                N_fft = N[np.argmin(cost)]
            else:
                N_fft = 2 ** nextpow2(N_b + N_x - 1)

        else:

            # When the filter length is at least as long as the signal,
            # filter the signal using a single block:
            N_fft = 2 ** nextpow2(N_b + N_x - 1)

    N_fft = int(N_fft)

    # Compute the block length:
    L = int(N_fft - N_b + 1)

    # Compute the transform of the filter:
    H = fft(b, N_fft)

    y = np.zeros(N_x, np.float32)
    i = 0
    while i <= N_x:
        il = np.min([i + L, N_x])
        k = np.min([i + N_fft, N_x])
        yt = ifft(fft(x[i:il], N_fft) * H, N_fft)  # Overlap..
        y[i:k] = y[i:k] + yt[:k - i]  # and add
        i += L
    return y


def fix_time_points(output, begin, padding, duration):
    if isinstance(output, (list, tuple)):
        return [fix_time_points(x, begin, padding, duration) for x in output]
    if begin is not None:
        if padding is not None:
            begin -= padding
        if isinstance(output, dict):
            real_output = {}
            for k, v in output.items():
                if padding is not None and (k < padding or k > duration - padding):
                    continue
                real_output[k + begin] = v
        elif isinstance(output, set):
            real_output = set()
            for k in output:
                if padding is not None and (k < padding or k > duration - padding):
                    continue
                real_output.add(k + begin)
        else:
            return output
        return real_output
    return output


class ASTemporaryWavFile(object):
    def __init__(self, signal, sr):
        self.temp_dir = TemporaryDirectory(prefix='acousticsim')
        self.signal = signal
        #self.signal *= 32768
        self.sr = sr

    def __enter__(self):
        t_wav = NamedTemporaryFile(dir=self.temp_dir.name, delete=False, suffix='.wav')
        soundfile.write(t_wav, self.signal, self.sr)
        t_wav.close()
        self.wav_path = t_wav.name
        return self.wav_path

    def __exit__(self, *args):
        pass
