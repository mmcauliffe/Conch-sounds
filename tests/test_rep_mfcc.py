
import os
from acousticsim.representations.mfcc import Mfcc

from scipy.io import loadmat

from numpy.testing import assert_array_almost_equal


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
        mfcc = Mfcc(wavpath,freq_lims = (0,8000), num_coeffs = 13 , win_len = 0.025,
                                time_step = 0.01,num_filters=20,
                                use_power=True
                                )
        pspec, aspec = mfcc.process(debug=True)
        #assert_array_almost_equal(m['pspectrum'].T,pspec,decimal=4)
        #assert_array_almost_equal(m['aspectrum'].T,aspec,decimal=4)
        assert_array_almost_equal(m['cepstra'].T,mfcc.to_array())

