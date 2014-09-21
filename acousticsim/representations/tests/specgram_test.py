

from numpy import array,sum,sqrt
from numpy.linalg import norm
import unittest
import os
try:
    from acousticsim.representations.specgram import (to_specgram, to_powerspec)
except ImportError:
    import sys

    test_dir = os.path.dirname(os.path.abspath(__file__))
    test_path = os.path.split(os.path.split(os.path.split(test_dir)[0])[0])[0]
    sys.path.append(test_path)
    from acousticsim.representations.specgram import (to_specgram, to_powerspec)



from acousticsim.representations.helper import preproc

from scipy.io import loadmat

from numpy.testing import assert_array_almost_equal

TEST_DIR = r'C:\Users\michael\Documents\Testing\acoustic_similarity'

filenames = ['s01_s0101a_big_910','s01_s0101a_care_1188',
            's01_s0101a_chief_831','s01_s0101a_choose_1149',
            's01_s0101a_come_340','s01_s0101a_dad_497',
            's01_s0101a_good_412','s01_s0101a_hall_99']

class PspecTest(unittest.TestCase):
    def setUp(self):
        self.winLen = 0.025
        self.timeStep = 0.01

    def test_specgram(self):
        for f in filenames:
            wavpath = os.path.join(TEST_DIR,f+'.wav')
            matpath = os.path.join(TEST_DIR,f+'_mfcc.mat')
            m = loadmat(matpath)
            sr, proc = preproc(wavpath,alpha=0.97)
            pspec = to_powerspec(proc,sr,self.winLen,self.timeStep)
            assert_array_almost_equal(m['pspectrum'].T,pspec)

if __name__ == '__main__':
    unittest.main()
