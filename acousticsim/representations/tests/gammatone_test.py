

from numpy import array,sum,sqrt
from numpy.linalg import norm
import unittest
import os
try:
    from acousticsim.representations.gammatone import to_gammatone
except ImportError:
    import sys

    test_dir = os.path.dirname(os.path.abspath(__file__))
    test_path = os.path.split(os.path.split(os.path.split(test_dir)[0])[0])[0]
    sys.path.append(test_path)
    from acousticsim.representations.gammatone import to_gammatone

from scipy.io import loadmat

from numpy.testing import assert_array_almost_equal

from matplotlib import pyplot

TEST_DIR = r'C:\Users\michael\Documents\Testing\acoustic_similarity'

filenames = ['s01_s0101a_big_910','s01_s0101a_care_1188',
            's01_s0101a_chief_831','s01_s0101a_choose_1149',
            's01_s0101a_come_340','s01_s0101a_dad_497',
            's01_s0101a_good_412','s01_s0101a_hall_99']


class GammatoneTest(unittest.TestCase):
    def setUp(self):
        self.num_bands = 4
        self.freq_lims = (80,7800)


    def test_gammatone(self):
        for f in filenames:
            wavpath = os.path.join(TEST_DIR,f+'.wav')
            matpath = os.path.join(TEST_DIR,f+'_gammatone_env.mat')
            m = loadmat(matpath)
            bm, env = to_gammatone(wavpath, self.num_bands,self.freq_lims)
            #pyplot.plot(bm)
            #pyplot.show()
            assert_array_almost_equal(m['bm'],bm)
            assert_array_almost_equal(m['env'],env)
            #raise(ValueError)


if __name__ == '__main__':
    unittest.main()
