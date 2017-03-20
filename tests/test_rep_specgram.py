
import os
import pytest
from acousticsim.representations.specgram import Spectrogram
from acousticsim.analysis.specgram import file_to_powerspec

from scipy.io import loadmat

from numpy.testing import assert_array_almost_equal

@pytest.mark.xfail
def test_specgram(base_filenames):
    for f in base_filenames:
        print(f)
        wavpath = f+'.wav'
        matpath = f+'_mfcc.mat'
        if not os.path.exists(matpath):
            continue
        m = loadmat(matpath)
        spec = Spectrogram(wavpath, None , win_len = 0.025, time_step = 0.01)
        print(m['pspectrum'].shape, spec.pspec().shape)
        assert_array_almost_equal(m['pspectrum'].T,spec.pspec(),decimal=4)

