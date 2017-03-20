
import os
import pytest
from acousticsim.representations.mfcc import Mfcc

from scipy.io import loadmat

from numpy.testing import assert_array_almost_equal

@pytest.mark.xfail
def test(base_filenames):
    for f in base_filenames:
        print(f)
        if f.startswith('silence'):
            continue
        wavpath = f+'.wav'
        matpath = f+'_mfcc.mat'
        if not os.path.exists(matpath):
            continue
        m = loadmat(matpath)
        mfcc = Mfcc(wavpath, min_freq=0, max_freq=8000, num_coeffs = 13 , win_len = 0.025,
                                time_step = 0.01,num_filters=20,
                                use_power=True
                                )
        mfcc.process()
        #assert_array_almost_equal(m['pspectrum'].T,pspec,decimal=4)
        #assert_array_almost_equal(m['aspectrum'].T,aspec,decimal=4)
        assert_array_almost_equal(m['cepstra'].T,mfcc.to_array())

def test_deltas(base_filenames):
    for f in base_filenames:
        print(f)
        if f.startswith('silence'):
            continue
        wavpath = f+'.wav'
        mfcc = Mfcc(wavpath, min_freq=0, max_freq=8000, num_coeffs = 13 , win_len = 0.025,
                                time_step = 0.01,num_filters=20,
                                use_power = False, deltas = True
                                )

@pytest.mark.xfail
def test_norm_amp(base_filenames):
    for f in base_filenames:
        print(f)
        if f.startswith('silence'):
            continue
        wavpath = f+'.wav'
        mfcc = Mfcc(wavpath,min_freq=0, max_freq=8000, num_coeffs = 1 , win_len = 0.025,
                                time_step = 0.01,num_filters=20,
                                use_power = True
                                )
        mfcc.norm_amp([(0,1)])

