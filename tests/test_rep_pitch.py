
import pytest

from acousticsim.representations.pitch import Pitch#, Harmonicity

from numpy.testing import assert_array_almost_equal



def test_pitch_zcd(base_filenames):
    return
    for f in base_filenames:
        path = f+'.wav'
        gt, env = to_gammatone(path,num_bands = 128, freq_lims = (80,7800))
        to_pitch_zcd(gt)

@pytest.mark.xfail
def test_pitch_ac(base_filenames):
    for f in base_filenames:
        if f.startswith('silence'):
            continue
        wavpath = f+'.wav'
        pitch = Pitch(wavpath, time_step = 0.01, freq_lims = (75,600))

@pytest.mark.xfail
def test_harmonics(base_filenames):
    for f in base_filenames:
        if f.startswith('silence'):
            continue
        wavpath = f+'.wav'
        print(f)
        harms = Harmonicity(wavpath, time_step = 0.01, min_pitch = 75)
        harms.process()
        print(harms.to_array())

