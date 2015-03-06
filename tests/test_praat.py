
import unittest
import os
import sys

test_dir = os.path.dirname(os.path.abspath(__file__))
test_path = os.path.split(os.path.split(os.path.split(test_dir)[0])[0])[0]
sys.path.insert(0,test_path)
from acousticsim.praat import to_formants_praat, to_pitch_praat, to_intensity_praat

from numpy.testing import assert_array_almost_equal

TEST_DIR = os.path.abspath('tests/data')

filenames = [os.path.splitext(x)[0] for x in os.listdir(TEST_DIR) if x.endswith('.wav')]

praatpath = 'praatcon.exe'

class PraatFormantsTest(unittest.TestCase):
    def setUp(self):
        self.num_formants = 5
        self.max_freq = 5500
        self.win_len = 0.025
        self.time_step = 0.01

    def test_lpc(self):
        return
        for f in filenames:
            wavpath = os.path.join(TEST_DIR,f+'.wav')
            #print(f)
            formants = to_formants_praat(praatpath,wavpath,self.time_step, self.win_len, self.num_formants,self.max_freq)
            #print(formants.to_array())
            #print(formants.to_array('bandwidth'))
            raise(ValueError)

class PraatPitchTest(unittest.TestCase):
    def setUp(self):
        self.max_freq = 600
        self.min_freq = 75
        self.time_step = 0.01

    def test_ac(self):
        return
        for f in filenames:
            wavpath = os.path.join(TEST_DIR,f+'.wav')
            print(f)
            pitch = to_pitch_praat(praatpath,wavpath,self.time_step,(self.min_freq,self.max_freq))
           # print(pitch.rep)
            #print(sorted(pitch._rep.keys()))
            #print(pitch[0.3])
            #print(pitch.is_voiced(0.105))
            #print(pitch[0.105])
            #print(pitch.to_array())
            #raise(ValueError)

class PraatIntensityTest(unittest.TestCase):
    def setUp(self):
        self.time_step = 0.01

    def test_intensity(self):
        return
        for f in filenames:
            #print(f)
            wavpath = os.path.join(TEST_DIR,f+'.wav')
            intensity = to_intensity_praat(praatpath,wavpath,self.time_step)
            #print(intensity.to_array())


if __name__ == '__main__':
    unittest.main()
