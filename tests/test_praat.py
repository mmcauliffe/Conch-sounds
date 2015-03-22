
import unittest
import pytest
import os
import sys

from acousticsim.praat import to_formants_praat, to_pitch_praat, to_intensity_praat

from numpy.testing import assert_array_almost_equal

TEST_DIR = os.path.abspath('tests/data')

filenames = [os.path.splitext(x)[0] for x in os.listdir(TEST_DIR) if x.endswith('.wav')]

praatpath = 'praatcon.exe'

@pytest.mark.xfail
def test_lpc(praatpath, base_filenames):
    for f in base_filenames:
        wavpath = f + '.wav'
        formants = to_formants_praat(praatpath, wavpath, time_step = 0.01,
                                win_len = 0.025, num_formants =5, max_freq = 5500)

@pytest.mark.xfail
def test_ac(praatpath, base_filenames):
    for f in base_filenames:
        wavpath = f + '.wav'
        pitch = to_pitch_praat(praatpath,wavpath, time_step = 0.01,
                freq_lims = (75,600))

@pytest.mark.xfail
def test_intensity(praatpath, base_filenames):
    for f in base_filenames:
        wavpath = f + '.wav'
        intensity = to_intensity_praat(praatpath,wavpath,time_step = 0.01)

