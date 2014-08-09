
from numpy import zeros
from linghelper.phonetics.representations.amplitude_envelopes import to_gammatone_envelopes
from linghelper.phonetics.representations.mfcc import dct_spectrum


def to_mhec(path, freq_lims,num_coeffs, num_filters, window_length,time_step, use_power = False):
    
    # calculate impulse response
    S = to_gammatone_envelopes(path,num_filters,freq_lims,window_length=window_length,time_step=time_step)
    num_frames = S.shape[0]
    mhecs = zeros((num_frames,num_coeffs))
    for k in range(num_frames):
        dcted = dct_spectrum(S[k,:])
        
        if not use_power:
            dctSpectrum = dctSpectrum[1:]
        mhecs[k,:] = dctSpectrum[:num_coeffs]
    return mhecs
