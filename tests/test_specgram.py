

import unittest
import os
from acousticsim.representations.specgram import (Spectrogram, to_powerspec)

from acousticsim.representations.helper import preproc

from scipy.io import loadmat

from numpy.testing import assert_array_almost_equal

TEST_DIR = os.path.abspath('tests/data')

filenames = [os.path.splitext(x)[0] for x in os.listdir(TEST_DIR) if x.endswith('.wav')]

class PspecTest(unittest.TestCase):
    def setUp(self):
        self.winLen = 0.025
        self.timeStep = 0.01

    def test_specgram(self):
        for f in filenames:
            print(f)
            wavpath = os.path.join(TEST_DIR,f+'.wav')
            matpath = os.path.join(TEST_DIR,f+'_mfcc.mat')
            if not os.path.exists(matpath):
                continue
            m = loadmat(matpath)
            spec = Spectrogram(wavpath, None ,self.winLen,self.timeStep)
            print(m['pspectrum'].shape, spec.pspec().shape)
            assert_array_almost_equal(m['pspectrum'].T,spec.pspec(),decimal=4)

if __name__ == '__main__':
    unittest.main()
