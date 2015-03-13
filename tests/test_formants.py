

from numpy import array,sum,sqrt
from numpy.linalg import norm
import unittest
import os
import sys

from acousticsim.representations.formants import LpcFormants
from acousticsim.processing.speech_detect import SpeechClassifier


from numpy.testing import assert_array_almost_equal

TEST_DIR = os.path.abspath('tests/data')

filenames = [os.path.splitext(x)[0] for x in os.listdir(TEST_DIR) if x.endswith('.wav')]

class LpcFormantsTest(unittest.TestCase):
    def setUp(self):
        self.num_formants = 5
        self.max_freq = 5500
        self.win_len = 0.025
        self.time_step = 0.01

    def test_lpc(self):
        return
        sc_101 = SpeechClassifier('new')
        sc_101.train_range(r'C:\Users\michael\Documents\Data\ATI_new\Shadowers\Male\124')
        for f in filenames:
            wavpath = os.path.join(TEST_DIR,f+'.wav')
            print(f)
            formants = LpcFormants(wavpath,self.max_freq, self.num_formants, self.win_len,self.time_step)
            #print(formants.to_array())
            #print(formants.to_array('bandwidth'))
            sc = SpeechClassifier('timit')
            vowels = sc.find_vowels(wavpath, sc_101._ranges, num_vowels = 1, debug = True)
            print(vowels)
            #vnv = sc.predict_file(wavpath,win_len=self.win_len,
                                #time_step=self.time_step, norm_amp = True,
                                #alg = 'bayes',use_segments=False,new_range = sc_101._ranges)

            #print(vnv)
            #raise(ValueError)

if __name__ == '__main__':
    unittest.main()
