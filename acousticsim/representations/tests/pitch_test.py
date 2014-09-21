

from numpy import array,sum,sqrt
from numpy.linalg import norm
import unittest
import os
try:
    from acousticsim.representations.pitch import to_pitch_zcd
except ImportError:
    import sys

    test_dir = os.path.dirname(os.path.abspath(__file__))
    test_path = os.path.split(os.path.split(os.path.split(test_dir)[0])[0])[0]
    sys.path.append(test_path)
    from acousticsim.representations.pitch import to_pitch_zcd


from numpy.testing import assert_array_almost_equal

TEST_DIR = r'C:\Users\michael\Documents\Testing\acoustic_similarity'

filenames = ['s01_s0101a_big_910','s01_s0101a_care_1188',
            's01_s0101a_chief_831','s01_s0101a_choose_1149',
            's01_s0101a_come_340','s01_s0101a_dad_497',
            's01_s0101a_good_412','s01_s0101a_hall_99']

class ZCDTest(unittest.TestCase):
    def setUp(self):
        self.num_bands = 128
        self.freq_lims = (80,7800)

    def test_zcd(self):
        return
        f = filenames[0]
        path = os.path.join(TEST_DIR,f+'.wav')
        gt, env = to_gammatone(path,self.num_bands,self.freq_lims)
        to_pitch_zcd(gt)


if __name__ == '__main__':
    unittest.main()
