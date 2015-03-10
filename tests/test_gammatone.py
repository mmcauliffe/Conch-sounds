

from numpy import array,sum,sqrt
from numpy.linalg import norm
import unittest
import os
from acousticsim.representations.gammatone import to_gammatone

from scipy.io import loadmat

from numpy.testing import assert_array_almost_equal

from matplotlib import pyplot

TEST_DIR = os.path.abspath('tests/data')

filenames = [os.path.splitext(x)[0] for x in os.listdir(TEST_DIR) if x.endswith('.wav')]


class GammatoneTest(unittest.TestCase):
    def setUp(self):
        self.num_bands = 4
        self.freq_lims = (80,7800)


    def test_gammatone(self):
        for f in filenames:
            wavpath = os.path.join(TEST_DIR,f+'.wav')
            matpath = os.path.join(TEST_DIR,f+'_gammatone_env.mat')
            if not os.path.exists(matpath):
                continue
            m = loadmat(matpath)
            bm, env = to_gammatone(wavpath, self.num_bands,self.freq_lims)
            #pyplot.plot(bm)
            #pyplot.show()
            assert_array_almost_equal(m['bm'],bm)
            assert_array_almost_equal(m['env'],env)
            #raise(ValueError)
            break


if __name__ == '__main__':
    unittest.main()
