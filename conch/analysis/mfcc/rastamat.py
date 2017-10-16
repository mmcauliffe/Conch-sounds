import numpy as np
import librosa

from ..specgram import signal_to_powerspec
from ..helper import mel_to_freq, freq_to_mel

from ...exceptions import MfccError

from ..functions import BaseAnalysisFunction


def dct_spectrum(spec):
    """Convert a spectrum into a cepstrum via type-III DCT (following HTK).

    Parameters
    ----------
    spec : array
        Spectrum to perform a DCT on.

    Returns
    -------
    array
        Cepstrum of the input spectrum.

    """
    ncep = spec.shape[0]
    dctm = np.zeros((ncep, ncep))
    for i in range(ncep):
        dctm[i, :] = np.cos(i * np.arange(1, 2 * ncep, 2) / (2 * ncep) * np.pi) * np.sqrt(2 / ncep)
    dctm *= 0.230258509299405
    cep = np.dot(dctm, (10 * np.log10(spec + np.spacing(1))))
    return cep


def construct_filterbank(num_filters, nfft, sr, min_freq, max_freq):
    """Constructs a mel-frequency filter bank.

            Parameters
            ----------
            nfft : int
                Number of points in the FFT.

            Returns
            -------
            array
                Filter bank to multiply an FFT spectrum to create a mel-frequency
                spectrum.

            """

    min_mel = freq_to_mel(min_freq)
    max_mel = freq_to_mel(max_freq)
    mel_points = np.linspace(min_mel, max_mel, num_filters + 2)
    bin_freqs = mel_to_freq(mel_points)
    # bins = round((nfft - 1) * bin_freqs / sr)

    fftfreqs = np.arange(int(nfft / 2 + 1)) / nfft * sr

    fbank = np.zeros((num_filters, int(nfft / 2 + 1)))
    for i in range(num_filters):
        fs = bin_freqs[i + np.arange(3)]
        fs = fs[1] + (fs - fs[1])
        loslope = (fftfreqs - fs[0]) / (fs[1] - fs[0])
        highslope = (fs[2] - fftfreqs) / (fs[2] - fs[1])
        fbank[i, :] = np.maximum(np.zeros(loslope.shape), np.minimum(loslope, highslope))
    return fbank.transpose()


def generate_mfccs(signal, sr, win_len, time_step, min_freq=80, max_freq=7800,
                   num_filters=26, num_coeffs=13, use_power=True, deltas=False, debug=False):
    L = 22
    n = np.arange(num_filters)
    lift = 1 + (L / 2) * np.sin(np.pi * n / L)
    lift = np.diag(lift)

    pspec = signal_to_powerspec(signal, sr, win_len, time_step)

    try:
        nfft = (len(next(iter(pspec.values()))) - 1) * 2
    except StopIteration:
        duration = len(signal) / sr
        raise (
        MfccError('The signal is too short to process (duration: {}; window size: {}).'.format(duration, win_len)))
    filterbank = construct_filterbank(num_filters, nfft, sr, min_freq, max_freq)

    output = {}
    aspec = {}
    for k in pspec:
        filteredSpectrum = np.dot(np.sqrt(pspec[k]), filterbank) ** 2
        aspec[k] = filteredSpectrum
        dctSpectrum = dct_spectrum(filteredSpectrum)
        dctSpectrum = np.dot(dctSpectrum, lift)
        if not use_power:
            dctSpectrum = dctSpectrum[1:]
        output[k] = dctSpectrum[:num_coeffs]
    if debug:
        return pspec, aspec

    # Calculate deltas
    if deltas:
        keys = sorted(output.keys())
        for i, k in enumerate(keys):
            if i == 0 or i == len(output.keys()) - 1:
                output[k] = np.array(list(output[k]) + [0 for x in range(num_coeffs)])
            else:
                deltas = output[keys[i + 1]][:num_coeffs] - output[keys[i - 1]][:num_coeffs]
                output[k] = np.array(list(output[k]) + list(deltas))
        for i, k in enumerate(keys):
            if i == 0 or i == len(output.keys()) - 1:
                output[k] = np.array(list(output[k]) + [0 for x in range(num_coeffs)])
            else:
                deltas = output[keys[i + 1]][num_coeffs:num_coeffs * 2] - output[keys[i - 1]][num_coeffs:num_coeffs * 2]
                output[k] = np.array(list(output[k]) + list(deltas))
    return output


class MfccFunction(BaseAnalysisFunction):
    def __init__(self, window_length=0.025, time_step=0.01, min_frequency=80, max_frequency=7800,
                 num_filters=26, num_coefficients=13, use_power=True, deltas=False):
        super(MfccFunction, self).__init__()
        self.arguments = [window_length, time_step, min_frequency, max_frequency,
                          num_filters, num_coefficients, use_power, deltas]
        self._function = generate_mfccs
