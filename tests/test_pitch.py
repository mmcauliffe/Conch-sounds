

from numpy import array,sum,sqrt
from numpy.linalg import norm
import unittest
import os
import sys

from acousticsim.representations.pitch import to_pitch_zcd, Pitch, Harmonicity


from numpy.testing import assert_array_almost_equal

TEST_DIR = os.path.abspath('tests/data')

filenames = [os.path.splitext(x)[0] for x in os.listdir(TEST_DIR) if x.endswith('.wav')]

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

class ACTest(unittest.TestCase):
    def setUp(self):
        self.time_step = 0.01
        self.freq_lims = (75,600)

    def test_ac(self):
        for f in filenames:
            if f.startswith('silence'):
                continue
            wavpath = os.path.join(TEST_DIR,f+'.wav')
            print(f)
            pitch = Pitch(wavpath,self.time_step, self.freq_lims)
            pitch.process()
            print(pitch.to_array())
            #raise(ValueError)

class HarmTest(unittest.TestCase):
    def setUp(self):
        self.time_step = 0.01
        self.min_pitch = 75

    def test_ac(self):
        for f in filenames:
            if f.startswith('silence'):
                continue
            wavpath = os.path.join(TEST_DIR,f+'.wav')
            print(f)
            harms = Harmonicity(wavpath,self.time_step, self.min_pitch)
            harms.process()
            print(harms.to_array())

if __name__ == '__main__':
    unittest.main()
