

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

    def test_filter_coeffs(self):
        b = [[0.0011,0, -0.0022, 0, 0.0011],
            [0.0097, 0, -0.0194, 0, 0.0097],
            [ 0.0741,0,-0.1482 , 0 , 0.0741],
            [0.4629, 0 ,-0.9258 , 0  ,  0.4629]]

        a = [[1.0000, -3.8988 ,  5.7072, -3.7175  ,  0.9092],
            [1.0000  ,-3.6459 ,  5.0421 , -3.1369 ,   0.7415],
            [1.0000 ,-2.6224  , 2.8816 , -1.5936  ,  0.3927],
            [1.0000  , 1.1957 , -0.1477 ,  -0.1166  ,  0.2388],]

    def test_envelope_gen(self):
        for f in filenames:
            print(f)
            wavpath = os.path.join(TEST_DIR,f+'.wav')
            matpath = os.path.join(TEST_DIR,f+'_lewandowski_env.mat')
            if not os.path.exists(matpath):
                continue
            m = loadmat(matpath)
            env = Envelopes(wavpath,self.freq_lims, self.num_bands)
            proc = env.process(debug=True)
            #for i in range(self.num_bands):
            #    denom = sqrt(sum(env[:,i]**2))
            #    env[:,i] = env[:,i]/denom
            assert_array_almost_equal(m['wd1'].reshape((m['wd1'].shape[0],)),proc)
            assert_array_almost_equal(m['env1'],env.to_array())


if __name__ == '__main__':
    unittest.main()
