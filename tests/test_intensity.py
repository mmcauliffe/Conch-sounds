

from numpy import array,sum,sqrt
from numpy.linalg import norm
import unittest
import os
import sys

test_dir = os.path.dirname(os.path.abspath(__file__))
test_path = os.path.split(os.path.split(os.path.split(test_dir)[0])[0])[0]
sys.path.insert(0,test_path)
from acousticsim.representations.intensity import Intensity


from numpy.testing import assert_array_almost_equal

TEST_DIR = os.path.abspath('tests/data')

filenames = [os.path.splitext(x)[0] for x in os.listdir(TEST_DIR) if x.endswith('.wav')]

class IntensityTest(unittest.TestCase):
    def setUp(self):
        self.time_step = 0.01

    def test_ac(self):
        return
        for f in filenames:
            f = os.path.splitext(f)[0]
            wavpath = os.path.join(TEST_DIR,f+'.wav')
            print(f)
            intensity = Intensity(wavpath,self.time_step)
            intensity.process()
            print(intensity.to_array())
            #raise(ValueError)

if __name__ == '__main__':
    unittest.main()
