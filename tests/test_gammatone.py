
import os
from acousticsim.representations.gammatone import to_gammatone

from scipy.io import loadmat

from numpy.testing import assert_array_almost_equal


def test_gammatone(base_filenames):
    for f in base_filenames:
        wavpath = f+'.wav'
        matpath = f+'_gammatone_env.mat'
        if not os.path.exists(matpath):
            continue

        m = loadmat(matpath)
        bm, env = to_gammatone(wavpath, num_bands = 4, freq_lims = (80,7800))
        assert_array_almost_equal(m['bm'],bm)
        assert_array_almost_equal(m['env'],env)
        break # takes forever!

