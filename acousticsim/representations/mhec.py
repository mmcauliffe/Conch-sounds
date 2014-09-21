
from numpy import zeros
from acousticsim.representations.base import Representation
from acousticsim.representations.gammatone import to_gammatone
from acousticsim.representations.amplitude_envelopes import window_envelopes
from acousticsim.representations.mfcc import dct_spectrum


def to_mhec(path, freq_lims,num_coeffs, num_filters, window_length,time_step, use_power = False):

    # calculate impulse response
    S = to_gammatone(path,num_filters,freq_lims)
    S = window_envelopes(S,window_length=window_length,time_step=time_step)
    num_frames = S.shape[0]
    mhecs = zeros((num_frames,num_coeffs))
    for k in range(num_frames):
        dctSpectrum = dct_spectrum(S[k,:])

        if not use_power:
            dctSpectrum = dctSpectrum[1:]
        mhecs[k,:] = dctSpectrum[:num_coeffs]
    return mhecs

class Mhec(Representation):
    pass
