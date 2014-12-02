
import unittest
import os
import sys

test_dir = os.path.dirname(os.path.abspath(__file__))
test_path = os.path.split(os.path.split(os.path.split(test_dir)[0])[0])[0]
sys.path.insert(0,test_path)
from acousticsim.praat import to_formants_praat, to_pitch_praat, to_intensity_praat

from numpy.testing import assert_array_almost_equal


TEST_DIR = r'C:\Users\michael\Documents\Testing\acoustic_similarity'

filenames = ['s01_s0101a_big_910','s01_s0101a_care_1188',
            's01_s0101a_chief_831','s01_s0101a_choose_1149',
            's01_s0101a_come_340','s01_s0101a_dad_497',
            's01_s0101a_good_412','s01_s0101a_hall_99']

praatpath = r'C:\Users\michael\Documents\Praat\praatcon.exe'

class PraatFormantsTest(unittest.TestCase):
    def setUp(self):
        self.num_formants = 5
        self.max_freq = 5500
        self.win_len = 0.025
        self.time_step = 0.01

    def test_lpc(self):

        for f in filenames:
            wavpath = os.path.join(TEST_DIR,f+'.wav')
            print(f)
            formants = to_formants_praat(praatpath,wavpath,self.time_step, self.win_len, self.num_formants,self.max_freq)
            print(formants.rep())

class PraatPitchTest(unittest.TestCase):
    def setUp(self):
        self.max_freq = 600
        self.min_freq = 75
        self.time_step = 0.01

    def test_ac(self):

        for f in filenames:
            wavpath = os.path.join(TEST_DIR,f+'.wav')
            print(f)
            pitch = to_pitch_praat(praatpath,wavpath,self.time_step,self.min_freq,self.max_freq)
            print(pitch.rep())
            print(sorted(pitch._rep.keys()))
            print(pitch[0.3])
            print(pitch.is_voiced(0.105))
            print(pitch[0.105])
            print(pitch.to_array())
            raise(ValueError)

if __name__ == '__main__':
    unittest.main()
