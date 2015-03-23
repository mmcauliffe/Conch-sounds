

from numpy import array,sum,sqrt,abs
from numpy.linalg import norm
import unittest
import pytest
import os

from acousticsim.representations.helper import preproc, resample

from scipy.io import loadmat

from numpy.testing import assert_array_almost_equal


@pytest.mark.xfail
def test_decimate():
    from numpy import arange,sin
    from scipy.signal import decimate, resample, cheby1, lfilter, filtfilt
    t = arange(0,30)
    q = 2
    n = 8
    print(t)
    print(decimate(t,2))
    print(resample(t, len(t)/2))
    t2 = sin(t)
    print(t2)
    print(len(t2))
    d2 = decimate(t2,2, ftype='fir')
    print(d2)
    print(len(d2))
    b, a = cheby1(n, 0.05, 0.8 / q)
    print(b,a)
    y = filtfilt(b, a, t2)
    print(y)
    sl = [slice(None)] * y.ndim

    sl[-1] = slice(None, None, -q)
    print(sl)
    print(y[sl])
    print(t2[sl])
    #r2 = resample(t2, len(t2)/2)
    #print(r2)
    #print(len(r2))
    assert(False)

@pytest.mark.xfail
def test_cubic_resample(test_dir):
    wav44 = 'pink_noise_44.1k.wav'
    wav44_16 = 'pink_noise_cubic_resampled_to_16k.wav'
    expected_sr, expected = preproc(os.path.join(test_dir,wav44_16),alpha=0)
    orig_sr, proc = preproc(os.path.join(test_dir,wav44),alpha=0)
    resampled = resample(proc, 16000/44100, 3)
    assert(abs(resampled - proc) < 0.0001)
