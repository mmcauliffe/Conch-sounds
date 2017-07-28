import pytest

from acousticsim.analysis.formants.praat import file_to_formants_praat
from acousticsim.analysis.pitch.praat import file_to_pitch_praat
from acousticsim.analysis.intensity.praat import file_to_intensity_praat
from acousticsim.analysis.mfcc.praat import file_to_mfcc_praat

from numpy.testing import assert_array_almost_equal


def test_lpc(praatpath, base_filenames):
    for f in base_filenames:
        wavpath = f + '.wav'
        formants = file_to_formants_praat(wavpath, praatpath, time_step=0.01,
                                          win_len=0.025, num_formants=5, max_freq=5500)


def test_ac(praatpath, base_filenames):
    for f in base_filenames:
        wavpath = f + '.wav'
        pitch = file_to_pitch_praat(wavpath, praatpath, time_step=0.01,
                                    min_pitch=75, max_pitch=600)


def test_intensity(praatpath, base_filenames):
    for f in base_filenames:
        wavpath = f + '.wav'
        intensity = file_to_intensity_praat(wavpath, praatpath, time_step=0.01)


def test_mfcc(praatpath, base_filenames):
    for f in base_filenames:
        wavpath = f + '.wav'
        mfcc = file_to_mfcc_praat(wavpath, praatpath, num_coeffs=12,
                                  win_len=0.025, time_step=0.01, max_freq=7800)
