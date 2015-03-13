

from numpy import array,sum,sqrt,abs
from numpy.linalg import norm
import unittest
import os

from acousticsim.representations.helper import preproc, resample


from scipy.io import loadmat

from numpy.testing import assert_array_almost_equal

TEST_DIR = os.path.abspath('tests/data')




def test_cubic_resample():
    wav44 = 'pink_noise_44.1k.wav'
    wav44_16 = 'pink_noise_cubic_resampled_to_16k.wav'
    expected_sr, expected = preproc(os.path.join(TEST_DIR,wav44_16),alpha=0)
    orig_sr, proc = preproc(os.path.join(TEST_DIR,wav44),alpha=0)
    resampled = resample(proc, 16000/44100, 3)
    assert(abs(resampled - proc) < 0.0001)
