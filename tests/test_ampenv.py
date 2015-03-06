

from numpy import array,sum,sqrt
from numpy.linalg import norm
import unittest
import os

from acousticsim.representations.amplitude_envelopes import Envelopes


from scipy.io import loadmat

from numpy.testing import assert_array_almost_equal

TEST_DIR = os.path.abspath('tests/data')

filenames = [os.path.splitext(x)[0] for x in os.listdir(TEST_DIR) if x.endswith('.wav')]

class EnvelopeTest(unittest.TestCase):
    def setUp(self):
        self.num_bands = 4
        self.freq_lims = (80,7800)



    def test_envelope_gen(self):
        for f in filenames:
            wavpath = os.path.join(TEST_DIR,f+'.wav')
            matpath = os.path.join(TEST_DIR,f+'_lewandowski_env.mat')
            m = loadmat(matpath)
            env = Envelopes(wavpath,self.freq_lims, self.num_bands)
            #for i in range(self.num_bands):
            #    denom = sqrt(sum(env[:,i]**2))
            #    env[:,i] = env[:,i]/denom
            assert_array_almost_equal(m['env1'],env.to_array())


if __name__ == '__main__':
    unittest.main()
